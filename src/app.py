from flask import Flask, url_for, render_template, request, flash, redirect, session
from flask_mysqldb import MySQL
import MySQLdb
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv

load_dotenv()
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = 'examen2'
app.secret_key = getenv('CLAVE_SECRETA')
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if 'logged_in' in session:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pass = generate_password_hash(password)
        confirm_password = request.form['confirm_password']
        name = request.form['name']

        if password != confirm_password:
            flash('¡Las contraseñas no coinciden!')
            return redirect(url_for('register'))
        elif not email and not password and not confirm_password and not name:
            flash('¡Ningún campo debe estar vacío!')
            return redirect(url_for('register'))
        
        try:
            cursor = mysql.connection.cursor()
            # cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            # id INT AUTO_INCREMENT PRIMARY KEY,
            # email VARCHAR(255) UNIQUE NOT NULL,
            # password VARCHAR(255) NOT NULL,
            # name VARCHAR(255) NOT NULL 
            # )''')
            cursor.execute('INSERT INTO usuarios (email, password, name) VALUES (%s, %s, %s)', (email, hashed_pass, name))
            mysql.connection.commit()
            cursor.close()
            flash("¡Usuario registrado correctamente!")
        except Exception as e:
            flash('¡Hubo un error registrando al usuario!')
        
    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM examen2.usuarios WHERE email = %s', [email])
            user = cursor.fetchone()
            cursor.close()

            if check_password_hash(user[2], password):
                session['logged_in'] = True
                session['user_id'] = user[0]
                session['name'] = user[3]
                flash('¡Inicio de sesión exitoso!')
                return redirect(url_for('profile'))
            else:
                flash('¡Contraseña no es correcta!')
                return redirect(url_for('login'))

        except Exception as e:
            flash('¡Hubo un error al iniciar sesión!')
            print('c')
            return redirect(url_for('login'))
            

    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'logged_in' in session:
        return render_template('profile.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/tienda')
def tienda():
    if 'logged_in' in session:
        return render_template('tienda.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('¡Sesión cerrada correctamente!')
    return redirect(url_for('login'))

@app.route('/admin')
def admin_page():
    pass

def error_404(error):
    return '<h1>Error 404: Ha ocurrido un error en la ruta, intenta con otra</h1>'

if __name__ == '__main__':
    app.register_error_handler(404, error_404)
    app.run(debug=True)