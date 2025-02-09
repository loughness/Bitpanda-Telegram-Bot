import sqlite3
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv


load_dotenv()
SECRET_KEY = os.getenv("ENCRYPTION_KEY")

cipher = Fernet(SECRET_KEY.encode())

DB_PATH = 'users.db'

def setup_database():
    """
    Creates the users table if it does not exist.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users (
                   user_id TEXT PRIMARY KEY,
                   api_key TEXT
                   )
    """)
    conn.commit()
    conn.close()

def encrypt_api_key(api_key):
    """
    Encrypt an API key using Fernet.
    """
    return cipher.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_api_key):
    """
    Decrypts an API key using Fernet.
    """
    if not encrypted_api_key:
        return None
    return cipher.decrypt(encrypted_api_key.encode()).decode()

def store_api_key(user_id, api_key):
    """
    Stores or updates a user's encrypted API key securely in the database.
    """
    encrypted_key = encrypt_api_key(api_key)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO users (user_id, api_key) VALUES (?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET api_key = ?
                   """, (user_id, encrypted_key, encrypted_key))
    conn.commit()
    conn.close()

def get_api_key(user_id):
    """
    Retrieves and decrypts a stored API key for a user.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT api_key FROM users WHERE user_id = ?", (str(user_id),))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:  # Ensure there's data before trying to decrypt
        return decrypt_api_key(result[0])
    return None  # Return None if user has no API key stored

def delete_api_key(user_id):
    """
    Delete a user's API key from database.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = ?", (str(user_id),))
    conn.commit()
    conn.close()