import sqlite3
import os
import ssl


# Define TLS version to use
TLS_VERSION = ssl.PROTOCOL_TLSv1_2

DB_PATH = 'shopeasy.db'

def setup_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_verify_locations(None)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.protocol = TLS_VERSION
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # ... (rest of the file remains unchanged)