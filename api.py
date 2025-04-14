from flask import Flask, request, render_template, redirect, url_for, g, Response, make_response
import sqlite3
from xhtml2pdf import pisa
from io import BytesIO

app = Flask(__name__)
db_name = 'egg_management.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(db_name)
        g.db.row_factory = sqlite3.Row  # Makes rows behave like dictionaries
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()

    # Calculate statistics
    cursor.execute('SELECT COUNT(*) FROM orders')
    total_orders = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(price) FROM orders')
    total_revenue = cursor.fetchone()[0] or 0

    cursor.execute('SELECT COUNT(*) FROM orders WHERE due_time > datetime("now")')
    pending_orders = cursor.fetchone()[0]

    # Get the most recent order (last created order)
    cursor.execute('SELECT * FROM orders ORDER BY id DESC LIMIT 1')
    recent_order = cursor.fetchone()

    return render_template('index.html', total_orders=total_orders, total_revenue=total_revenue, pending_orders=pending_orders, recent_order=recent_order)

@app.route('/orders', methods=['GET'])
def get_orders():
    db = get_db()
    cursor = db.cursor()

    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    # Fetch orders with pagination
    cursor.execute('SELECT * FROM orders LIMIT ? OFFSET ?', (per_page, offset))
    orders = cursor.fetchall()

    # Get total number of orders for pagination
    cursor.execute('SELECT COUNT(*) FROM orders')
    total_orders = cursor.fetchone()[0]
    total_pages = (total_orders + per_page - 1) // per_page

    return render_template('orders.html', orders=orders, page=page, total_pages=total_pages)

@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    error = None
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        num_crates = request.form['num_crates']
        price = request.form['price']
        due_time = request.form['due_time']

        # Validation
        if not customer_name or not num_crates or not price or not due_time:
            error = "All fields are required."
        elif not num_crates.isdigit() or int(num_crates) <= 0:
            error = "Number of crates must be a positive integer."
        elif not price.replace('.', '', 1).isdigit() or float(price) <= 0:
            error = "Price must be a positive number."

        if error is None:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO orders (customer_name, num_crates, price, due_time)
                VALUES (?, ?, ?, ?)
            ''', (customer_name, int(num_crates), float(price), due_time))
            db.commit()
            return redirect(url_for('get_orders'))

    return render_template('add_order.html', error=error)

@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    db.commit()
    return redirect(url_for('get_orders'))

@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        num_crates = int(request.form['num_crates'])
        price = float(request.form['price'])
        due_time = request.form['due_time']
        cursor.execute('''
            UPDATE orders
            SET customer_name = ?, num_crates = ?, price = ?, due_time = ?
            WHERE id = ?
        ''', (customer_name, num_crates, price, due_time, order_id))
        db.commit()
        return redirect(url_for('get_orders'))
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    return render_template('edit_order.html', order=order)

@app.route('/export_orders', methods=['GET'])
def export_orders():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()

    # Create CSV response
    def generate():
        data = ['ID,Customer Name,Number of Crates,Price,Due Time\n']
        for order in orders:
            data.append(','.join(map(str, order)) + '\n')
        return data

    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=orders.csv"})

@app.route('/order/<int:order_id>', methods=['GET'])
def order_detail(order_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    if not order:
        return "Order not found", 404
    return render_template('order_detail.html', order=order)

@app.route('/order_pdf/<int:order_id>', methods=['GET'])
def order_pdf(order_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    if not order:
        return "Order not found", 404

    # Render the HTML template for the order
    html = render_template('order_pdf.html', order=order)

    # Create a BytesIO object to hold the PDF data
    pdf = BytesIO()

    # Generate the PDF
    pisa_status = pisa.CreatePDF(html, dest=pdf)

    # Check if PDF generation was successful
    if pisa_status.err:
        return "Error generating PDF", 500

    # Return the PDF as a response
    pdf.seek(0)  # Move the cursor to the beginning of the BytesIO object
    response = make_response(pdf.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment;filename=order_{order_id}.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 