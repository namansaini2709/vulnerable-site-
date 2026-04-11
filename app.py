from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_from_directory, make_response
import sqlite3
import os
import urllib.parse

app = Flask(__name__)
app.secret_key = 'super_secret_session_key' # Insecure static key

DB_PATH = 'shopeasy.db'

# Auto-setup DB if it doesn't exist (Crucial for Render ephemeral deployments)
if not os.path.exists(DB_PATH):
    from db_setup import setup_db
    setup_db()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    query = urllib.parse.escape(request.args.get('q', ''))
    conn = get_db_connection()
    c = conn.cursor()
    
    if query:
        # Simple search
        c.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + query + '%',))
    else:
        c.execute("SELECT * FROM products")
        
    products = c.fetchall()
    conn.close()
    
    # XSS vulnerability: Render query directly to template (we'll implement the actual XSS in the template)
    return render_template('index.html', products=products, query=query)
