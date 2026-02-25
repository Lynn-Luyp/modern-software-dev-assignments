from __future__ import annotations

import os
import re
import time
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def extract_action_items_llm(text: str) -> List[str]:
    """Use Ollama LLM to extract action items from the given text."""
    if not text.strip():
        return []

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that extracts action items from meeting notes or text. "
                "Return ONLY the actionable tasks. Each action item should be a concise, "
                "imperative sentence (e.g. 'Set up database', 'Write tests'). "
                "Do not include narrative or non-actionable sentences."
            ),
        },
        {
            "role": "user",
            "content": f"Extract all action items from the following text:\n\n{text}",
        },
    ]
    schema = {
        "type": "object",
        "properties": {
            "action_items": {
                "type": "array",
                "items": {"type": "string"},
            }
        },
        "required": ["action_items"],
    }

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = chat(
                model=os.getenv("OLLAMA_MODEL", "llama3.2-vision"),
                messages=messages,
                format=schema,
            )
            result = json.loads(response.message.content)
            action_items = result.get("action_items", [])
            if isinstance(action_items, list):
                return [str(item).strip() for item in action_items if str(item).strip()]
            break
        except Exception as exc:
            last_error = exc
            # Brief backoff helps with transient 5xx errors from Ollama.
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))

    # Fallback keeps the API/test behavior stable if Ollama is unavailable.
    fallback = extract_action_items(text)
    if fallback:
        return fallback
    if last_error:
        return []
    return []


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
