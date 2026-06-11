from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.secret_key = "mysecretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Create Database
with app.app_context():
    db.create_all()

# Home Page
@app.route('/')
def home():
    return '''
    <h2>Secure Login System</h2>
    <a href="/register">Register</a><br><br>
    <a href="/login">Login</a>
    '''

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        # Password Validation
        if len(password) < 8:
            return "Password must be at least 8 characters"

        # Check Existing User
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return "Username already exists"

        # Hash Password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Save User
        new_user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):

            session['user'] = username

            return redirect('/dashboard')

        return "Invalid Username or Password"

    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():

    if 'user' in session:
        return render_template(
            'dashboard.html',
            username=session['user']
        )

    return redirect('/login')

# Logout Route
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')

# Run Application
if __name__ == '__main__':
    app.run(debug=True)