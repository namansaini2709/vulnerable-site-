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

    # Fixed: Avoid rendering user-supplied input directly to the template
    query = '' if not query else request.args.get('q')
    return render_template('index.html', products=products, query=query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        c = conn.cursor()
        
        query = "SELECT * FROM users WHERE email = ? AND password = ?"
        c.execute(query, (email, password))
        # Use parameterized queries to prevent SQL Injection
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/product/<int:product_id>')
def product(product_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = c.fetchone()
    conn.close()
    if not product:
        return "Not found", 404
    return render_template('product.html', product=product)

@app.route('/orders')
def orders():
    # IDOR vulnerability
    order_id = request.args.get('id')
    
    if not order_id:
        return "Please provide an order ID, e.g., /orders?id=1", 400

    conn = get_db_connection()
    c = conn.cursor()
    # Fixed: Ensure the logged-in user owns the order before accessing it
    query = f"SELECT * FROM orders WHERE id = {order_id} AND user_id = ?"
    user_id = session['user_id'] if 'user_id' in session else None
    try:
        c.execute(query, (user_id,))
        order = c.fetchone()
    except Exception as e:
        order = None

    conn.close()

    if order:
        return render_template('orders.html', order=order)
    else:
        return "Order not found", 404

@app.route('/api/user/profile')
def user_profile():
    # Sensitive Data Exposure vulnerability
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    c = conn.cursor()
    # Fixed: Only return relevant, non-sensitive data for the user profile
    query = "SELECT name, notes FROM users WHERE id = ?" # Removed password hash
    c.execute(query, (session['user_id'],))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({'user': dict(user)})
    return jsonify({"error": "User not found"}), 404

@app.route('/.env')
def expose_env():
    # Exposed .env vulnerability
    # In a real app, web server config might prevent this, or it's misconfigured.
    # We deliberately serve it to simulate a misconfiguration.
    try:
        return send_from_directory('.', '.env', mimetype='text/plain')
    except Exception:
        return "File not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
