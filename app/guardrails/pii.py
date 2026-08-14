from __future__ import annotations

from dataclasses import dataclass, field

from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from app.rag.generate import CITATION_RE

# presidio-analyzer installed cleanly on Python 3.13 (SPEC §11.1's regex
# fallback was NOT needed) -- confirmed live: `AnalyzerEngine()` auto-fetched
# its spaCy model (en_core_web_lg, ~400MB) on first run. That download only
# happens once per machine/venv.
#
# PKC is an Indian company; Presidio's built-in recognizers cover US-shaped
# IDs (SSN, driver's license, ...) but ship nothing for Indian PAN/Aadhaar
# numbers. Rather than bolt on a second, parallel regex path for just those
# two, we register them as ordinary PatternRecognizers on the SAME
# AnalyzerEngine -- G2/G5 stay on one detection interface, and if Presidio
# ever needs to be swapped for the SPEC §11.1 fallback, these two patterns
# move with it unchanged.
_PAN_RECOGNIZER = PatternRecognizer(
    supported_entity="IN_PAN",
    patterns=[Pattern(name="pan", regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", score=0.85)],
)
_AADHAAR_RECOGNIZER = PatternRecognizer(
    supported_entity="IN_AADHAAR",
    patterns=[Pattern(name="aadhaar", regex=r"\b\d{4}\s\d{4}\s\d{4}\b", score=0.7)],
)

# G2 (input) fires on "any PERSON+ID entity" per SPEC §4.4 -- a person's name
# or anything identifier-shaped.
_ID_ENTITY_TYPES = {
    "PERSON",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "IN_PAN",
    "IN_AADHAAR",
    "CREDIT_CARD",
    "US_SSN",
    "US_PASSPORT",
    "US_DRIVER_LICENSE",
    "US_BANK_NUMBER",
    "IBAN_CODE",
}

# G5 (output) is broader than G2, but NOT Presidio's literal "detect every
# supported entity" default that SPEC §4.4's "any entity" phrasing suggests.
# Confirmed live: DATE_TIME and LOCATION fire constantly on ordinary PKC
# business content -- a holiday-calendar answer IS dates, an office-policy
# answer IS locations -- and redacting them stripped the actual facts an
# answer needed to be verifiable against, which then made G6's groundedness
# judge score a perfectly correct, fully-cited answer as ungrounded (a
# self-inflicted false refusal, the same failure shape the citation-bracket
# and hyphen tolerance in generate.py exist to avoid). Narrowed to entities
# that are actually person-identifying or account/ID-shaped -- the same
# judgment call as G3's threshold recalibration: spec's literal number
# didn't survive contact with the real corpus and model, so it's adjusted
# and the reasoning recorded here (see docs/DESIGN_DECISIONS.md) rather than
# silently diverging.
_OUTPUT_ENTITY_TYPES = _ID_ENTITY_TYPES | {"NRP", "IP_ADDRESS", "US_ITIN", "MEDICAL_LICENSE", "UK_NHS"}

_analyzer: AnalyzerEngine | None = None
_anonymizer: AnonymizerEngine | None = None


def _get_analyzer() -> AnalyzerEngine:
    global _analyzer
    if _analyzer is None:
        engine = AnalyzerEngine()
        engine.registry.add_recognizer(_PAN_RECOGNIZER)
        engine.registry.add_recognizer(_AADHAAR_RECOGNIZER)
        _analyzer = engine
    return _analyzer


def _get_anonymizer() -> AnonymizerEngine:
    global _anonymizer
    if _anonymizer is None:
        _anonymizer = AnonymizerEngine()
    return _anonymizer


@dataclass
class PIIResult:
    text: str
    redacted: bool
    entity_types: list[str] = field(default_factory=list)


def _redact(text: str, entities: list[str] | None, protect_citations: bool = False) -> PIIResult:
    """entities=None asks Presidio to detect (and redact) every entity type it
    knows about -- used for G5. A concrete allowlist restricts detection to
    just those types -- used for G2's narrower PERSON+ID scope.

    protect_citations=True drops any detected entity whose span overlaps a
    citation marker like [doc_id::c02]. Confirmed live: Presidio's
    IP_ADDRESS recognizer matches the "::cNN" chunk suffix as IPv6
    zero-compression shorthand (e.g. "2026::c02" parses the same shape as
    "2001:db8::1"), and redacting that span corrupts the citation marker
    itself -- which then breaks G7's citation check AND confuses G6's
    groundedness judge with a mangled evidence trail. G2 doesn't need this:
    a user's raw question never contains real citation markers.
    """
    if not text.strip():
        return PIIResult(text=text, redacted=False, entity_types=[])

    protected_spans = [m.span() for m in CITATION_RE.finditer(text)] if protect_citations else []

    results = _get_analyzer().analyze(text=text, language="en", entities=entities)
    if protected_spans:
        results = [
            r
            for r in results
            if not any(r.start < span_end and r.end > span_start for span_start, span_end in protected_spans)
        ]
    if not results:
        return PIIResult(text=text, redacted=False, entity_types=[])

    operators = {
        r.entity_type: OperatorConfig("replace", {"new_value": f"<REDACTED:{r.entity_type}>"}) for r in results
    }
    anonymized = _get_anonymizer().anonymize(text=text, analyzer_results=results, operators=operators)
    return PIIResult(text=anonymized.text, redacted=True, entity_types=sorted({r.entity_type for r in results}))


def scan_input(text: str) -> PIIResult:
    """G2: redact PERSON/ID-shaped entities before the text reaches embedding
    or the LLM. Non-blocking -- SPEC's action is "redact ... warn inline",
    not refuse the request."""
    return _redact(text, entities=sorted(_ID_ENTITY_TYPES))


def scan_output(text: str) -> PIIResult:
    """G5: redact identifying entities found in the model's answer before
    it's returned to the user (see _OUTPUT_ENTITY_TYPES for scope), except
    inside citation markers -- see _redact's protect_citations docstring."""
    return _redact(text, entities=sorted(_OUTPUT_ENTITY_TYPES), protect_citations=True)
