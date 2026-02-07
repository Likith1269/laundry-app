from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "laundry_secret"

print("App started")


# ------------------------
# Database Initialization
# ------------------------
def init_db():
    conn = sqlite3.connect('laundry.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            clothes INTEGER,
            service TEXT,
            status TEXT,
            latitude TEXT,
            longitude TEXT
        )
    ''')

    # Add columns if missing (safe for existing DB)
    try:
        c.execute("ALTER TABLE orders ADD COLUMN latitude TEXT")
    except:
        pass

    try:
        c.execute("ALTER TABLE orders ADD COLUMN longitude TEXT")
    except:
        pass

    conn.commit()
    conn.close()


init_db()


# ------------------------
# Customer Pages
# ------------------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add_order():
    name = request.form['name']
    phone = request.form['phone']
    clothes = request.form['clothes']
    service = request.form['service']
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    conn = sqlite3.connect('laundry.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO orders (name, phone, clothes, service, status, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, phone, clothes, service, "Pending", latitude, longitude)
    )

    conn.commit()
    conn.close()

    return redirect('/')


# ------------------------
# Customer Order Tracking
# ------------------------
@app.route('/track')
def track_page():
    return render_template('track.html')


@app.route('/track_order', methods=['POST'])
def track_order():
    phone = request.form['phone']

    conn = sqlite3.connect('laundry.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE phone=? ORDER BY id DESC", (phone,))
    orders = c.fetchall()
    conn.close()

    return render_template('track.html', orders=orders)


# ------------------------
# Admin Login
# ------------------------
@app.route('/admin')
def admin():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "1234":
        session['admin'] = True
        return redirect('/dashboard')
    else:
        return "Invalid Login"


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/admin')


# ------------------------
# Admin Dashboard
# ------------------------
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/admin')

    conn = sqlite3.connect('laundry.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM orders")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM orders WHERE status='Pending'")
    pending = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM orders WHERE status='Completed'")
    completed = c.fetchone()[0]

    conn.close()

    return render_template('dashboard.html',
                           total=total,
                           pending=pending,
                           completed=completed)


# ------------------------
# Admin Orders Management
# ------------------------
@app.route('/orders')
def view_orders():
    if not session.get('admin'):
        return redirect('/admin')

    conn = sqlite3.connect('laundry.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    data = c.fetchall()
    conn.close()

    return render_template('orders.html', orders=data)


@app.route('/complete/<int:id>')
def complete_order(id):
    if not session.get('admin'):
        return redirect('/admin')

    conn = sqlite3.connect('laundry.db')
    c = conn.cursor()
    c.execute("UPDATE orders SET status='Completed' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/orders')


@app.route('/delete/<int:id>')
def delete_order(id):
    if not session.get('admin'):
        return redirect('/admin')

    conn = sqlite3.connect('laundry.db')
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/orders')


# ------------------------
# Run Server
# ------------------------
if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)
