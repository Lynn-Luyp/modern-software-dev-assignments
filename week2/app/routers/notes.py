from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from .. import db


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("")
def create_note(payload: Dict[str, Any]) -> Dict[str, Any]:
    content = str(payload.get("content", "")).strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    note_id = db.insert_note(content)
    note = db.get_note(note_id)
    return {
        "id": note["id"],
        "content": note["content"],
        "created_at": note["created_at"],
    }


@router.get("")
def list_all_notes() -> List[Dict[str, Any]]:
    rows = db.list_notes()
    return [
        {
            "id": r["id"],
            "content": r["content"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]


@router.get("/{note_id}")
def get_single_note(note_id: int) -> Dict[str, Any]:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return {"id": row["id"], "content": row["content"], "created_at": row["created_at"]}


