def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_get_note_by_id(client):
    # Create a note first
    payload = {"title": "Specific Note", "content": "Content here"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Get the note by ID
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Specific Note"
    assert data["content"] == "Content here"


def test_get_note_not_found(client):
    # Try to get a non-existent note
    r = client.get("/notes/99999")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()
