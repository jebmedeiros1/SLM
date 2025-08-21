import psycopg2
from datetime import datetime

def connect():
    return psycopg2.connect(
        dbname="oraculo",
        user="user",
        password="pass",
        host="31.97.172.93"
    )

def initialize_db():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            title TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER REFERENCES conversations(id),
            sender TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def create_conversation(user_id, title):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO conversations (user_id, title) VALUES (%s, %s) RETURNING id", (user_id, title))
    conversation_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return conversation_id

def add_message(conversation_id, sender, content):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (conversation_id, sender, content) VALUES (%s, %s, %s)", (conversation_id, sender, content))
    conn.commit()
    cur.close()
    conn.close()

def list_conversations(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM conversations WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def get_conversation_messages(conversation_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT sender, content FROM messages WHERE conversation_id = %s ORDER BY created_at ASC", (conversation_id,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results
