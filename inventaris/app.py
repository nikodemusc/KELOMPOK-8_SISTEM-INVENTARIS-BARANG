from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from controllers.item_controller import ItemController

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = 'stock_control'

mysql = MySQL(app)

item_controller = ItemController(mysql)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user:
            flash('Username sudah ada. Gunakan username lain.', 'danger')
        else:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                        (username, hashed_password))
            mysql.connection.commit()
            flash('Registrasi berhasil. Silakan login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user and check_password_hash(user[2], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Login gagal. Periksa username dan password Anda.', 'danger')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']
        cur.execute("INSERT INTO barang (nama_barang, jumlah, harga) VALUES (%s, %s, %s)", (name, quantity, price))
        mysql.connection.commit()
        flash('Barang berhasil ditambahkan!', 'success')
    
    cur.execute("SELECT id, nama_barang AS name, jumlah AS quantity, harga AS price FROM barang")
    items = cur.fetchall()
    return render_template('dashboard.html', items=items)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return item_controller.add_item()

@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nama_barang, jumlah FROM barang WHERE id = %s", (item_id,))
    item = cur.fetchone()

    if request.method == 'POST':
        barang_masuk = int(request.form['barang_masuk'] or 0)
        barang_keluar = int(request.form['barang_keluar'] or 0)
        
        new_quantity = item[2] + barang_masuk - barang_keluar
        if new_quantity < 0:
            flash('Jumlah barang tidak boleh kurang dari 0!', 'danger')
        else:
            cur.execute("UPDATE barang SET jumlah = %s WHERE id = %s", (new_quantity, item_id))
            mysql.connection.commit()
            flash('Data barang berhasil diperbarui!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_item.html', item={'id': item[0], 'name': item[1], 'quantity': item[2]})

@app.route('/delete_item/<int:id>', methods=['GET'])
def delete_item(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return item_controller.delete_item(id)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s", (session['username'],))
        user = cur.fetchone()
        
        if user and check_password_hash(user[0], current_password):
            if new_password == confirm_password:
                hashed_password = generate_password_hash(new_password)
                cur.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password, session['username']))
                mysql.connection.commit()
                flash('Password berhasil diubah.', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = "Password baru dan konfirmasi tidak sama."
        else:
            error = "Password lama tidak sesuai."
    
    return render_template('change_password.html', error=error)


if __name__ == '__main__':
    app.run(debug=True)

