"""
Unit tests for extract_action_items (regex-based) and extract_action_items_llm (Ollama LLM-based).

The LLM tests call the real Ollama endpoint (no mocking), so assertions are
flexible: we verify structural properties (returns list, items are strings,
reasonable count) and check for key concepts via case-insensitive substring
matching, since the model may paraphrase or reorder items.
"""

import time

import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


# ---------------------------------------------------------------------------
# Helper: case-insensitive check that *any* returned item contains a keyword
# ---------------------------------------------------------------------------
def _any_item_contains(items: list[str], keyword: str) -> bool:
    """Return True if at least one item contains `keyword` (case-insensitive)."""
    keyword_lower = keyword.lower()
    return any(keyword_lower in item.lower() for item in items)


@pytest.fixture(autouse=True)
def _wait_between_llm_tests(request):
    """
    Wait 3 seconds after each LLM test to avoid back-to-back Ollama calls.

    This only applies to tests named `test_llm_*`.
    """
    yield
    if request.node.name.startswith("test_llm_"):
        time.sleep(3)


# ============================= regex-based tests ============================

def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# ==================== LLM-based tests (real Ollama calls) ===================

def test_llm_bullet_list():
    """LLM should extract items from a standard bullet list."""
    text = """
    Notes from meeting:
    - Set up database
    - Implement API endpoint
    - Write tests
    """.strip()

    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) >= 3
    assert all(isinstance(i, str) for i in items)
    assert _any_item_contains(items, "database")
    assert _any_item_contains(items, "API")
    assert _any_item_contains(items, "test")


def test_llm_keyword_prefixed_lines():
    """LLM should extract items from keyword-prefixed lines (todo:, action:, next:)."""
    text = """
    todo: Finish the report
    action: Email client
    next: Review PR #42
    """.strip()

    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) >= 3
    assert _any_item_contains(items, "report")
    assert _any_item_contains(items, "email") or _any_item_contains(items, "client")
    assert _any_item_contains(items, "review") or _any_item_contains(items, "PR")


def test_llm_checkbox_items():
    """LLM should extract unchecked checkbox items as action items."""
    text = """
    - [ ] Set up database
    - [x] Already done task
    - [ ] Deploy to staging
    """.strip()

    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) >= 1
    assert _any_item_contains(items, "database") or _any_item_contains(items, "staging")


def test_llm_empty_input():
    """LLM should return an empty list (or near-empty) when given empty text."""
    items = extract_action_items_llm("")

    assert isinstance(items, list)
    # The model may return [] or a list with empty strings; accept both
    meaningful = [i for i in items if i.strip()]
    assert len(meaningful) == 0


def test_llm_whitespace_only_input():
    """LLM should return an empty list for whitespace-only text."""
    items = extract_action_items_llm("   \n\n\t  ")

    assert isinstance(items, list)
    meaningful = [i for i in items if i.strip()]
    assert len(meaningful) == 0


def test_llm_pure_narrative():
    """LLM should return few or no items for non-actionable narrative text."""
    text = (
        "The weather was nice today. We had a pleasant lunch. "
        "Everyone enjoyed the presentation about company history."
    )

    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    # Narrative has no real action items; allow at most 1 false positive
    assert len(items) <= 1


def test_llm_mixed_content():
    """LLM should extract action items from text mixed with narrative."""
    text = """
    The team discussed the upcoming release.
    - Update the homepage banner
    Everyone agreed the timeline is tight.
    - Fix the login bug
    Great meeting overall.
    """.strip()

    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) >= 2
    assert _any_item_contains(items, "homepage") or _any_item_contains(items, "banner")
    assert _any_item_contains(items, "login") or _any_item_contains(items, "bug")


def test_llm_single_action_item():
    """LLM should handle text with only one action item."""
    text = "Write and send the invoice to the client by Friday."

    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) >= 1
    assert _any_item_contains(items, "invoice")


def test_llm_numbered_list():
    """LLM should extract items from a numbered list."""
    text = """
    1. Research competitors
    2. Draft proposal
    3. Schedule review meeting
    """.strip()

    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) >= 3
    assert _any_item_contains(items, "competitor") or _any_item_contains(items, "research")
    assert _any_item_contains(items, "proposal") or _any_item_contains(items, "draft")
    assert _any_item_contains(items, "meeting") or _any_item_contains(items, "schedule")


def test_llm_special_characters_in_items():
    """LLM should handle action items with special characters."""
    text = """
    - Update README.md (section #3)
    - Fix issue #123
    """.strip()

    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) >= 2
    assert _any_item_contains(items, "README") or _any_item_contains(items, "section")
    assert _any_item_contains(items, "issue") or _any_item_contains(items, "123")


def test_llm_many_items():
    """LLM should handle a larger body of text with many action items."""
    lines = [f"- Complete task number {i}" for i in range(1, 8)]
    text = "Sprint planning notes:\n" + "\n".join(lines)

    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) >= 5  # allow the model to merge/drop a couple
    assert all(isinstance(i, str) for i in items)


def test_llm_returns_list_of_strings():
    """The return value should always be a list of strings."""
    text = "- Write documentation\n- Add error handling"

    result = extract_action_items_llm(text)

    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, str)
        assert len(item) > 0


def test_llm_imperative_sentences():
    """LLM should pick up imperative-style sentences even without bullets."""
    text = (
        "Add input validation to the signup form. "
        "Refactor the database connection pool. "
        "The deployment went smoothly last Friday."
    )

    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) >= 2
    assert _any_item_contains(items, "validation") or _any_item_contains(items, "signup")
    assert _any_item_contains(items, "refactor") or _any_item_contains(items, "database")
