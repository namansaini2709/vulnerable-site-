from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_from_directory, make_response
import sqlite3
import os
from flask import escape

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
    
    # Validate and escape query to prevent XSS
    return render_template('index.html', products=products, query=escape(query))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # SQL Injection vulnerability: Use parameterized query instead
        conn = get_db_connection()
        c = conn.cursor()
        
        query = "SELECT * FROM users WHERE email = ? AND password = ?"
        try:
            c.execute(query, (email, password))
            user = c.fetchone()
        except Exception as e:
            user = None
            print(f"DB Error: {e}")
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
    # IDOR vulnerability: Validate user ownership
    order_id = request.args.get('id')
    
    if not order_id:
        return "Please provide an order ID, e.g., /orders?id=1", 400
        
    conn = get_db_connection()
    c = conn.cursor()
    
    query = "SELECT * FROM orders WHERE id = ? AND user_id = ?"
    try:
        c.execute(query, (order_id, session.get('user_id')))
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
    # Sensitive Data Exposure vulnerability: Only return necessary user data
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name, email FROM users WHERE id = ?", (session['user_id'],))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({'name': user['name'], 'email': user['email']})
    return jsonify({"error": "User not found"}), 404

@app.route('/.env')
def expose_env():
    # Exposed .env vulnerability: Remove this route or restrict access
    return "Access denied", 403

if __name__ == '__main__':
    # No rate limiting implemented on the app
    app.run(host='0.0.0.0', port=3001, debug=True)
