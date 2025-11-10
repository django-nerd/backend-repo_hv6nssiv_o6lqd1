import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import User, Project, Message

app = FastAPI(title="Freelance Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Freelance Platform Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Utility to stringify ObjectIds

def _str_id(doc):
    if doc is None:
        return doc
    if isinstance(doc, list):
        return [_str_id(d) for d in doc]
    if isinstance(doc, dict):
        d = dict(doc)
        if d.get("_id"):
            d["_id"] = str(d["_id"])
        return d
    return doc

# -------- Users --------

@app.post("/api/users", response_model=dict)
def create_user(user: User):
    user_id = create_document("user", user)
    return {"id": user_id}

@app.get("/api/users", response_model=List[dict])
def list_users():
    users = get_documents("user")
    return _str_id(users)

# -------- Projects --------

@app.post("/api/projects", response_model=dict)
def create_project(project: Project):
    # Validate referenced user exists (best-effort)
    try:
        _ = db["user"].find_one({"_id": ObjectId(project.user_id)})
    except Exception:
        pass
    pid = create_document("project", project)
    return {"id": pid}

@app.get("/api/projects", response_model=List[dict])
def list_projects(user_id: Optional[str] = None):
    query = {"user_id": user_id} if user_id else {}
    projects = get_documents("project", query)
    return _str_id(projects)

# -------- Messages (Chat) --------

@app.post("/api/messages", response_model=dict)
def create_message(message: Message):
    # Optionally verify project exists
    try:
        _ = db["project"].find_one({"_id": ObjectId(message.project_id)})
    except Exception:
        pass
    mid = create_document("message", message)
    return {"id": mid}

@app.get("/api/messages", response_model=List[dict])
def list_messages(project_id: str):
    msgs = get_documents("message", {"project_id": project_id})
    return _str_id(msgs)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
