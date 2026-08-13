"""Each test here implements one of SPEC §6's three broken authorization approaches
and proves it fails. These tests pass BY demonstrating failure -- if any of them
starts passing for the wrong reason (e.g. the corpus changes and no longer has
restricted content ranking near the top of a query), the assertion in the test
body itself will catch that and fail loudly rather than silently no-op."""

from qdrant_client import QdrantClient
from fastembed import TextEmbedding

from app.core.config import get_settings
from app.rbac.acl import DOC_CLASS_ACL, Role, build_acl_filter

_settings = get_settings()
_client = QdrantClient(url=_settings.qdrant_url, api_key=_settings.qdrant_api_key)
_embedder = TextEmbedding(model_name=_settings.embed_model)


def _embed(text: str):
    return list(_embedder.embed([text]))[0].tolist()


def test_prompt_level_filtering_leaks():
    """Broken approach: retrieve with NO server-side filter, hand every result to
    the LLM, and rely on a system-prompt instruction like 'only mention documents
    this user can see' to hide restricted content.

    Proves the flaw structurally: restricted text is already inside the prompt
    string handed to the model -- and sent to the LLM vendor's servers, and
    written to any trace/log of the request -- before any instruction is even
    applied. An instruction can also be defeated by prompt injection (exercised
    separately in the Phase 5 adversarial suite), but that's secondary: even a
    perfectly-obedient model has already leaked the data by the time it starts
    generating a response.
    """
    query_vector = _embed("What was our Q3 2025 net revenue?")
    results = _client.query_points(
        collection_name=_settings.qdrant_collection,
        query=query_vector,
        limit=20,
        with_payload=True,
        # No query_filter -- this is the bug. Every chunk in the collection is
        # eligible, regardless of who's asking.
    ).points

    restricted_for_employee = [r for r in results if "employee" not in r.payload["allowed_roles"]]
    assert restricted_for_employee, (
        "test setup problem: expected this query's unfiltered top results to include "
        "content an employee isn't authorized for"
    )

    # Simulate the broken approach's prompt assembly: dump every retrieved chunk
    # into the prompt, then rely on an instruction to keep the model well-behaved.
    prompt = (
        "You are PKC's assistant. The current user's role is: employee. "
        "Only answer using documents this user is authorized to see.\n\nCONTEXT:\n"
    )
    prompt += "\n\n".join(r.payload["chunk_text"] for r in results)

    for r in restricted_for_employee:
        assert r.payload["chunk_text"] in prompt, "expected restricted chunk to already be in the prompt"


def test_post_retrieval_filtering_kills_recall():
    """Broken approach: search WITHOUT a server-side filter, get the top_k
    results, THEN drop whichever ones the user isn't authorized for.

    Proves the flaw: top_k slots get consumed by chunks the user will never be
    allowed to see. Authorized results that would have ranked just outside the
    unfiltered top_k never appear at all -- recall silently collapses, and it
    gets worse the more restricted content is semantically relevant to the query
    (exactly the queries where this matters most).
    """
    top_k = 5
    query_vector = _embed("quarterly financial results and revenue numbers")
    user_roles = ["employee"]

    unfiltered = _client.query_points(
        collection_name=_settings.qdrant_collection, query=query_vector, limit=top_k, with_payload=True
    ).points
    post_filtered = [r for r in unfiltered if set(user_roles) & set(r.payload["allowed_roles"])]

    properly_filtered = _client.query_points(
        collection_name=_settings.qdrant_collection,
        query=query_vector,
        query_filter=build_acl_filter(user_roles),
        limit=top_k,
        with_payload=True,
    ).points

    assert len(post_filtered) < len(properly_filtered), (
        "test setup problem: expected this query's unfiltered top_k to be dominated by "
        "content this role can't see, so post-filtering loses results the correct "
        "(server-side-filtered) search would still return"
    )


def test_collection_per_role_breaks_on_overlap():
    """Broken approach: one Qdrant collection per role, each holding only that
    role's authorized documents.

    Proves the flaw using the real access matrix: doc classes like `cloud_costs`
    are authorized for MULTIPLE roles at once (finance_analyst, engineering_lead,
    c_level -- SPEC's whole point about roles being non-hierarchical). Under a
    one-collection-per-role design, such a document can't live in one place --
    it must be embedded and stored once per role that can see it. And because
    `reindex_acl.py`'s entire reason to exist is updating `allowed_roles` on an
    existing payload without re-embedding, an ACL change under this design has no
    equivalent operation: moving a doc's visibility to a different role means
    re-embedding it into a different collection, not a payload update.
    """
    overlap_classes = {
        doc_class: entry["roles"] for doc_class, entry in DOC_CLASS_ACL.items() if len(entry["roles"]) > 1
    }
    assert "cloud_costs" in overlap_classes and "marketing_spend" in overlap_classes, (
        "test setup problem: expected both known overlap doc classes in DOC_CLASS_ACL"
    )

    for doc_class, roles in overlap_classes.items():
        # Every role that can see this doc_class would need its own embedded copy
        # under one-collection-per-role -- one logical document becomes N stored
        # copies, where N grows with how many roles can see it.
        required_copies = len(roles)
        assert required_copies > 1, f"{doc_class} is an overlap class but only maps to one role"

    # c_level can see literally everything (SPEC's structural invariant: c_level
    # in every row) -- so under this design, c_level's collection alone would
    # duplicate the ENTIRE corpus, on top of every other role's copy.
    c_level_visible = sum(1 for entry in DOC_CLASS_ACL.values() if Role.C_LEVEL in entry["roles"])
    assert c_level_visible == len(DOC_CLASS_ACL)
