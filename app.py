from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_from_directory, make_response
import sqlite3
import os

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

# Add security headers
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self';"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/')
def index():
    query = request.args.get('q', '')
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
    response = make_response(render_template('index.html', products=products, query=query))
    return add_security_headers(response)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # SQL Injection vulnerability
        conn = get_db_connection()
        c = conn.cursor()
        
        # VULNERABLE RAW QUERY
        query = f"SELECT * FROM users WHERE email = '{email}' AND password = '{password}'"
        print(f"Executing: {query}") # For observing the payload
        try:
            c.execute(query)
            user = c.fetchone()
        except Exception as e:
            user = None
            print(f"DB Error: {e}")
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            response = make_response(redirect(url_for('index')))
            return add_security_headers(response)
        else:
            response = make_response(render_template('login.html', error="Invalid credentials"))
            return add_security_headers(response)
            
    response = make_response(render_template('login.html'))
    return add_security_headers(response)

@app.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect(url_for('index')))
    return add_security_headers(response)

@app.route('/product/<int:product_id>')
def product(product_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()
    conn.close()
    if not product:
        response = make_response("Not found", 404)
    else:
        response = make_response(render_template('product.html', product=product))
    return add_security_headers(response)

@app.route('/orders')
def orders():
    # IDOR vulnerability
    order_id = request.args.get('id')
    
    if not order_id:
        response = make_response("Please provide an order ID, e.g., /orders?id=1", 400)
        return add_security_headers(response)
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # VULNERABLE: No check if the logged in user actually owns this order
    query = f"SELECT * FROM orders WHERE id = {order_id}"
    try:
        c.execute(query)
        order = c.fetchone()
    except Exception as e:
        order = None
        
    conn.close()
    
    if order:
        response = make_response(render_template('orders.html', order=order))
    else:
        response = make_response("Order not found", 404)
    return add_security_headers(response)

@app.route('/api/user/profile')
def user_profile():
    # Sensitive Data Exposure vulnerability
    if 'user_id' not in session:
        response = make_response(jsonify({"error": "Unauthorized"}), 401)
    else:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        user = c.fetchone()
        conn.close()
        
        # VULNERABLE: Returning full user object including password hash and internal notes
        response = make_response(jsonify(dict(user)))
    return add_security_headers(response)

@app.route('/.env')
def expose_env():
    # Exposed .env vulnerability
    # In a real app, web server config might prevent this, or it's misconfigured.
    # We deliberately serve it to simulate a misconfiguration.
    try:
        response = make_response(send_from_directory('.', '.env', mimetype='text/plain'))
    except Exception:
        response = make_response("File not found", 404)
    return add_security_headers(response)

if __name__ == '__main__':
    # No rate limiting implemented on the app
    app.run(host='0.0.0.0', port=3001, debug=True)
