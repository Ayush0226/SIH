import sqlite3
import json
import datetime
import hashlib
import os

DB_NAME = "complyscan.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Officers Table
    c.execute('''CREATE TABLE IF NOT EXISTS officers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    name TEXT)''')
                    
    # Scans History Table
    c.execute('''CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    officer_username TEXT,
                    category TEXT,
                    image_filename TEXT,
                    pdf_filename TEXT,
                    status TEXT,
                    timestamp DATETIME,
                    extracted_data TEXT,
                    violations TEXT)''')
    
    # Create the default officer account (Mock for MVP)
    pwd_hash = hashlib.sha256("password".encode()).hexdigest()
    try:
        c.execute("INSERT INTO officers (username, password_hash, name) VALUES (?, ?, ?)", 
                  ("officer123", pwd_hash, "Inspector Ramesh"))
    except sqlite3.IntegrityError:
        pass # Already exists

    conn.commit()
    conn.close()

def verify_officer(username, password):
    conn = get_db()
    c = conn.cursor()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT name FROM officers WHERE username=? AND password_hash=?", (username, pwd_hash))
    user = c.fetchone()
    conn.close()
    return user

def save_scan(officer_username, category, image_filename, pdf_filename, status, extracted_data, violations):
    conn = get_db()
    c = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    c.execute('''INSERT INTO scans 
                 (officer_username, category, image_filename, pdf_filename, status, timestamp, extracted_data, violations)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
              (officer_username, category, image_filename, pdf_filename, status, timestamp, 
               json.dumps(extracted_data), json.dumps(violations)))
    conn.commit()
    scan_id = c.lastrowid
    conn.close()
    return scan_id

def get_officer_scans(username):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM scans WHERE officer_username=? ORDER BY timestamp DESC", (username,))
    rows = c.fetchall()
    conn.close()
    
    scans = []
    for r in rows:
        scans.append({
            "id": r["id"],
            "category": r["category"],
            "image_filename": r["image_filename"],
            "pdf_filename": r["pdf_filename"],
            "status": r["status"],
            "timestamp": r["timestamp"],
            "extracted_data": json.loads(r["extracted_data"]),
            "violations": json.loads(r["violations"])
        })
    return scans
