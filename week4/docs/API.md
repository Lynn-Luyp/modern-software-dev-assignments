# API Documentation

**Version:** 0.1.0
**Title:** Modern Software Dev Starter (Week 4)

## Base URL
- Development: `http://localhost:8000`

## Endpoints

### Root
**GET** `/`

Returns a welcome message or redirects to the frontend.

**Response:** `200 OK`

---

### Notes

#### List All Notes
**GET** `/notes/`

Retrieve all notes from the database.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "string",
    "content": "string"
  }
]
```

#### Create Note
**POST** `/notes/`

Create a new note.

**Request Body:**
```json
{
  "title": "string",
  "content": "string"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "title": "string",
  "content": "string"
}
```

#### Search Notes
**GET** `/notes/search/`

Search notes by title or content.

**Query Parameters:**
- `q` (optional): Search query string

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "string",
    "content": "string"
  }
]
```

#### Get Note by ID
**GET** `/notes/{note_id}`

Retrieve a specific note by its ID.

**Path Parameters:**
- `note_id` (integer, required): The note ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "string",
  "content": "string"
}
```

**Error Response:** `404 Not Found` if note doesn't exist

---

### Action Items

#### List All Action Items
**GET** `/action-items/`

Retrieve all action items.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "description": "string",
    "completed": false
  }
]
```

#### Create Action Item
**POST** `/action-items/`

Create a new action item.

**Request Body:**
```json
{
  "description": "string"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "description": "string",
  "completed": false
}
```

#### Complete Action Item
**PUT** `/action-items/{item_id}/complete`

Mark an action item as completed.

**Path Parameters:**
- `item_id` (integer, required): The action item ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "description": "string",
  "completed": true
}
```

**Error Response:** `404 Not Found` if action item doesn't exist

---

## Schemas

### NoteCreate
```json
{
  "title": "string",
  "content": "string"
}
```

### NoteRead
```json
{
  "id": "integer",
  "title": "string",
  "content": "string"
}
```

### ActionItemCreate
```json
{
  "description": "string"
}
```

### ActionItemRead
```json
{
  "id": "integer",
  "description": "string",
  "completed": "boolean"
}
```

---

## Interactive Documentation

When the server is running, you can access:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json
