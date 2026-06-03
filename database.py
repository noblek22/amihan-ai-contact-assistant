import sqlite3
import os
import psycopg2

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "ammihan.db")

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return sqlite3.connect(DB_NAME)

def get_pstgres_connection():

    return psycopg2.connect(
        DATABASE_URL
    )

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    )
    """)

    # Contacts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        name TEXT,
        phone TEXT
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# USER FUNCTIONS
# -----------------------------
def create_user(username, password_hash, role):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users (username, password_hash, role)
    VALUES (?, ?, ?)
    """, (username, password_hash, role))

    conn.commit()
    conn.close()


def get_user(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, password_hash, role
    FROM users
    WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    conn.close()

    return user


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, role
    FROM users
    """)

    users = cursor.fetchall()

    conn.close()

    return users


# -----------------------------
# CONTACT FUNCTIONS
# -----------------------------
def create_contact(username, name, phone):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO contacts (username, name, phone)
    VALUES (?, ?, ?)
    """, (username, name, phone))

    conn.commit()
    conn.close()


def get_contacts_by_user(
    username,
    limit=10,
    offset=0,
    sort_by="name"
):
    conn = get_connection()
    cursor = conn.cursor()

    # basic safe sorting
    allowed_sort_fields = ["name", "phone"]

    if sort_by not in allowed_sort_fields:
        sort_by = "name"

    query = f"""
    SELECT name, phone
    FROM contacts
    WHERE username = ?
    ORDER BY {sort_by}
    LIMIT ?
    OFFSET ?
    """

    cursor.execute(query, (username, limit, offset))

    contacts = cursor.fetchall()

    conn.close()

    return contacts


def update_contact(username, old_name, new_name, new_phone):
    conn = get_connection() 
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE contacts
    SET name = ?, phone = ?
    WHERE username = ? AND name = ?
    """, (new_name, new_phone, username, old_name))

    conn.commit()

    affected = cursor.rowcount

    conn.close()

    return affected


def delete_contact(username, name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM contacts
    WHERE username = ? AND name = ?
    """, (username, name))

    conn.commit()

    affected = cursor.rowcount

    conn.close()

    return affected


def search_contacts(
    username,
    search_term,
    sort_by="name"
):
    conn = get_connection()
    cursor = conn.cursor()

    allowed_sort_fields = ["name", "phone"]

    if sort_by not in allowed_sort_fields:
        sort_by = "name"

    query = f"""
    SELECT name, phone
    FROM contacts
    WHERE username = ?
    AND (
        name LIKE ?
        OR phone LIKE ?
    )    
    ORDER BY {sort_by}
    """
    
    cursor.execute(
        query,
        (
        
            username,
            f"%{search_term}%",
            f"%{search_term}%"
        )
    )    

    results = cursor.fetchall()

    conn.close()

    return results

def get_contact_statistics(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM contacts
    WHERE username = ?
    """, (username,))

    total_contacts = cursor.fetchone()[0]

    conn.close()

    return {
        "total_contacts": total_contacts
    }

def get_top_contacts(username, limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name, phone
    FROM contacts
    WHERE username = ?
    ORDER BY name
    LIMIT ?
    """, (
        username, 
        limit
    ))

    contacts = cursor.fetchall()

    conn.close()

    return contacts