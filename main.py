import uuid
import time
import json
import os
import bcrypt

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import (
    initialize_database,
    initialize_postgres_database,
    create_user,
    get_user,
    get_all_users,
    create_contact,
    get_contacts_by_user,
    update_contact,
    delete_contact,
    search_contacts,
    get_contact_statistics,
    get_top_contacts,
    create_user_postgres,
    get_user_postgres
)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

# Search improvements branchgit

# --------------------------------------------------
# APP SETUP
# --------------------------------------------------
app = FastAPI(
    title="Amihan AI Contact Assistant",
    description="AI-powered relationship and contact management platform",
    version="1.0.0"
)

initialize_database()

if os.getenv("DATABASE_URL"):
    initialize_postgres_database()

# --------------------------------------------------
# SESSION SETTINGS
# --------------------------------------------------
SESSION_DURATION = 3600

sessions = {}

# --------------------------------------------------
# AI MEMORY STORAGE
# --------------------------------------------------
AI_MEMORY_FILE = "ai_memory.json"


def load_ai_memory():
    if os.path.exists(AI_MEMORY_FILE):
        with open(AI_MEMORY_FILE, "r") as f:
            return json.load(f)

    return {
        "memory": {},
        "conversation_history": {},
        "relationship_profiles": {}
    }


def save_ai_memory():
    data = {
        "memory": memory,
        "conversation_history": conversation_history,
        "relationship_profiles": relationship_profiles
    }

    with open(AI_MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


ai_data = load_ai_memory()

memory = ai_data["memory"]
conversation_history = ai_data["conversation_history"]
relationship_profiles = ai_data["relationship_profiles"]

# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------
class UserRequest(BaseModel):
    username: str
    password: str
    role: str = "user"

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "1234",
                "role": "admin"
            }
        }


class ContactRequest(BaseModel):
    name: str
    phone: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John",
                "phone": "12345"
            }
        }


class MessageRequest(BaseModel):
    name: str
    style: str = "friendly"
    intent: str = "checkin"

# --------------------------------------------------
# PASSWORD SECURITY
# --------------------------------------------------
def hash_password(password):
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(password, password_hash):
    password_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")

    return bcrypt.checkpw(
        password_bytes,
        hash_bytes
    )

# --------------------------------------------------
# SESSION HELPERS
# --------------------------------------------------
def get_session(token):
    session = sessions.get(token)

    if not session:
        return None

    current_time = time.time()

    if current_time - session["created_at"] > SESSION_DURATION:
        del sessions[token]
        return None

    return session


def get_username_from_token(token):
    session = get_session(token)

    if not session:
        return None

    return session["username"]

# --------------------------------------------------
# HOME
# --------------------------------------------------
@app.get(
    "/",
    tags=["Home"]
)
def home():
    return {
        "message": "Amihan AI Contact Assistant API is running 🚀"
    }

# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------
@app.post(
    "/register",
    tags=["Authentication"],
    summary="Register user"
)
def register(user: UserRequest):

    existing_user = get_user(user.username)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    create_user(
        user.username,
        hash_password(user.password),
        user.role
    )

    return {
        "message": "User registered successfully"
    }


@app.post(
    "/login",
    tags=["Authentication"],
    summary="Login user"
)
def login(user: UserRequest):

    db_user = get_user(user.username)

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    username, password_hash, role = db_user

    if verify_password(user.password, password_hash):

        token = str(uuid.uuid4())

        sessions[token] = {
            "username": username,
            "role": role,
            "created_at": time.time()
        }

        return {
            "message": "Login successful",
            "token": token
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid username or password"
    )


@app.post(
    "/logout",
    tags=["Authentication"]
)
def logout(token: str):

    if token in sessions:
        del sessions[token]

        return {
            "message": "Logged out successfully"
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid token"
    )

# --------------------------------------------------
# CONTACTS
# --------------------------------------------------
@app.get(
    "/contacts",
    tags=["Contacts"]
)
def get_contacts(
    token: str,
    limit: int = 10,
    offset: int = 0
):

    username = get_username_from_token(token)

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token"
        )

    contacts = get_contacts_by_user(
        username,
        limit,
        offset
    )

    return [
        {
            "name": c[0],
            "phone": c[1]
        }
        for c in contacts
    ]


@app.post(
    "/contacts",
    tags=["Contacts"]
)
def add_contact(
    token: str,
    contact: ContactRequest
):

    username = get_username_from_token(token)

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token"
        )

    create_contact(
        username,
        contact.name,
        contact.phone
    )

    return {
        "message": "Contact added successfully"
    }


@app.put(
    "/contacts/{name}",
    tags=["Contacts"]
)
def update_contact_route(
    name: str,
    token: str,
    contact: ContactRequest
):

    username = get_username_from_token(token)

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token"
        )

    updated = update_contact(
        username,
        name,
        contact.name,
        contact.phone
    )

    if updated == 0:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return {
        "message": "Contact updated successfully"
    }


@app.delete(
    "/contacts/{name}",
    tags=["Contacts"]
)
def delete_contact_route(
    name: str,
    token: str
):

    username = get_username_from_token(token)

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token"
        )

    deleted = delete_contact(
        username,
        name
    )

    if deleted == 0:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return {
        "message": "Contact deleted successfully"
    }

# --------------------------------------------------
# SEARCH
# --------------------------------------------------
@app.get(
    "/contacts/search",
    tags=["Contacts"]
)
def search_contacts_route(
    token: str,
    query: str,
    sort_by: str = "name"
):

    username = get_username_from_token(token)

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token"
        )

    results = search_contacts(
        username,
        query,
        sort_by
    )

    return [
        {
            "name": r[0],
            "phone": r[1]
        }
        for r in results
    ]

# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------
@app.get(
    "/contacts/stats",
    tags=["Analytics"]
)
def contact_statistics(token: str):

    username = get_username_from_token(token)

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token"
        )

    return get_contact_statistics(username)


@app.get(
    "/contacts/top",
    tags=["Analytics"]
)
def top_contacts(
    token: str,
    limit: int = 5
):

    username = get_username_from_token(token)

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token"
        )

    contacts = get_top_contacts(
        username,
        limit
    )

    return [
        {
            "name": c[0],
            "phone": c[1]
        }
        for c in contacts
    ]


@app.get(
    "/analytics",
    tags=["Analytics"]
)
def get_analytics():

    total_contacts = len(relationship_profiles)

    total_messages = sum(
        profile["total_messages"]
        for profile in relationship_profiles.values()
    )

    return {
        "total_contacts_tracked": total_contacts,
        "total_messages_generated": total_messages,
        "average_messages_per_contact":
            total_messages / total_contacts
            if total_contacts else 0
    }

# --------------------------------------------------
# AI FEATURES
# --------------------------------------------------
@app.post(
    "/suggest-message",
    tags=["AI"]
)
def suggest_message(request: MessageRequest):

    name = request.name

    previous_count = memory.get(name, 0)

    history = conversation_history.get(name, [])

    profile = relationship_profiles.get(name, {
        "total_messages": 0,
        "preferred_style": request.style,
        "common_intent": request.intent
    })

    message = (
        f"{request.style.title()} "
        f"{request.intent} message for {name}: "
        f"Hope you're doing well!"
    )

    memory[name] = previous_count + 1

    history.append(message)

    conversation_history[name] = history

    profile["total_messages"] += 1
    profile["preferred_style"] = request.style
    profile["common_intent"] = request.intent

    relationship_profiles[name] = profile

    save_ai_memory()

    return {
        "message": message,
        "times_suggested": memory[name],
        "history": conversation_history[name],
        "relationship_profile":
            relationship_profiles[name]
    }


@app.get(
    "/ai-memory",
    tags=["AI"]
)
def get_ai_memory():

    return {
        "memory": memory,
        "conversation_history": conversation_history,
        "relationship_profiles": relationship_profiles
    }


@app.get(
    "/relationship-profile/{name}",
    tags=["AI"]
)
def get_relationship_profile(name: str):

    profile = relationship_profiles.get(name)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"No profile found for {name}"
        )

    return profile

# --------------------------------------------------
# ADMIN
# --------------------------------------------------
@app.get(
    "/admin/users",
    tags=["Admin"]
)
def get_all_users_route(token: str):

    session = get_session(token)

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    if session["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    users = get_all_users()

    return [
        {
            "username": u[0],
            "role": u[1]
        }
        for u in users
    ]

@app.get("/postgres-test")
def postgres_test():
    user = get_user_postgres("testuser")

    if not user:
        create_user_postgres(
            "testuser",
            "password",
            "user"
        )

    return {
        "message": "PostgreSQL connection working",
        "user": "testuser"
    }