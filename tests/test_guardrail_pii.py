"""G2 (input PII) / G5 (output PII) -- PLAN.md Phase 4 tasks 4.2 / 4.4.

Presidio installed cleanly on this machine's Python 3.13 venv (the SPEC
§11.1 regex fallback was NOT needed), but PKC is an Indian company and
Presidio ships no built-in PAN/Aadhaar recognizers -- those are the two
custom PatternRecognizers registered in app/guardrails/pii.py, and the
reason this suite specifically exercises them rather than trusting
Presidio's defaults alone.
"""

from app.guardrails.pii import scan_input, scan_output


def test_scan_input_redacts_person_and_indian_ids():
    text = (
        "Please contact Rohan Mehta at rohan.mehta@pkc.com or +91 9876543210. "
        "His PAN is ABCDE1234F and Aadhaar is 1234 5678 9012."
    )
    result = scan_input(text)

    assert result.redacted
    for raw in ["Rohan Mehta", "rohan.mehta@pkc.com", "ABCDE1234F", "1234 5678 9012"]:
        assert raw not in result.text, f"expected {raw!r} to be redacted out of G2 output"
    assert "IN_PAN" in result.entity_types
    assert "IN_AADHAAR" in result.entity_types


def test_scan_input_is_a_noop_on_pii_free_text():
    result = scan_input("What is the company holiday calendar for 2026?")
    assert result.redacted is False
    assert result.text == "What is the company holiday calendar for 2026?"


def test_scan_output_redacts_entities_outside_g2s_scope():
    # IP_ADDRESS is deliberately outside G2's PERSON+ID allowlist -- proves G5
    # covers more than a copy of G2's input scope. NOT testing with
    # LOCATION/DATE_TIME here: those are excluded from G5 on purpose (see
    # _OUTPUT_ENTITY_TYPES in pii.py) because they're pervasive in ordinary
    # PKC business content (holiday dates, office locations) rather than
    # actually sensitive, and redacting them was observed to strip real
    # facts out of otherwise-correct answers.
    text = "The suspicious login came from IP address 203.0.113.42, flagged by security."
    result = scan_output(text)

    assert result.redacted
    assert "203.0.113.42" not in result.text
    assert "IP_ADDRESS" in result.entity_types

    # And G2 must NOT flag it -- IP addresses aren't PERSON/ID-shaped input.
    input_result = scan_input(text)
    assert input_result.redacted is False


def test_scan_output_does_not_redact_dates_or_locations():
    # The specific failure this test guards against: an answer built from
    # PKC's own holiday-calendar corpus IS mostly dates and office locations.
    # If G5 redacted those, groundedness checking (G6) would score a
    # perfectly correct, fully-cited answer as ungrounded, because the
    # actual verifiable facts had already been stripped out of it.
    text = "The Mumbai office is closed on 05 Nov 2026 for Diwali."
    result = scan_output(text)
    assert "Mumbai" in result.text
    assert "05 Nov 2026" in result.text


def test_scan_output_is_a_noop_on_pii_free_text():
    result = scan_output("The office is closed on national holidays.")
    assert result.redacted is False
