from flask import Flask, request, jsonify, render_template, redirect, url_for, session,flash
from flask_pymongo import PyMongo
import gridfs
from werkzeug.utils import secure_filename
import hashlib  # To hash passwords for security
from flask_cors import CORS
from bson.json_util import dumps
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management
CORS(app)  # Enable CORS

# Configure the MongoDB connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/DataScience"
mongo = PyMongo(app)
fs = gridfs.GridFS(mongo.db)

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/test-db')
def test_db():
    try:
        mongo.db.users.find_one()  # Replace 'users' with a collection name
        return jsonify({'msg': 'Database connection successful!'}), 200
    except Exception as e:
        return jsonify({'msg': f'Database connection failed: {str(e)}'}), 500

@app.route('/file')
def file():
    return "Research Papers not Uploaded in System!"

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            gender = request.form.get('gender')
            dob = request.form.get('dob')

            if not all([username, password, email, gender, dob]):
                return jsonify({'msg': 'Please fill in all fields'}), 400

            if mongo.db.users.find_one({'username': username}):
                return jsonify({'msg': 'Username already exists'}), 400

            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            user_data = {
                'username': username,
                'password': hashed_password,
                'email': email,
                'gender': gender,
                'dob': dob
            }
            mongo.db.users.insert_one(user_data)

            return redirect(url_for('login_page'))

        except Exception as e:
            return jsonify({'msg': f'Error during signup: {str(e)}'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        try:
            username = request.form['username']
            password = request.form['password']

            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            user = mongo.db.users.find_one({'username': username, 'password': hashed_password})

            if user:
                session['username'] = username
                return redirect(url_for('home_page'))
            else:
                return jsonify({'msg': 'Invalid username or password'}), 401

        except Exception as e:
            return jsonify({'msg': f'Error during login: {str(e)}'}), 500

@app.route('/home')
def home_page():
    if 'username' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login_page'))

@app.route('/upload', methods=['GET', 'POST'])
def uploadpage():
    if request.method == 'GET':
        return render_template('upload.html')
    else:
        if 'research-paper' not in request.files:
            return jsonify({'msg': 'No file part'}), 400

        file = request.files['research-paper']

        if file.filename == '':
            return jsonify({'msg': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_id = fs.put(file, filename=filename)

            file_data = {
                'username': session['username'],
                'name': request.form['name'],
                'title': request.form['title'],
                'author': request.form['author'],
                'description': request.form['description'],
                'file_id': file_id
            }
            mongo.db.research_papers.insert_one(file_data)
            return jsonify({'msg': 'File successfully uploaded'}), 200
        else:
            return jsonify({'msg': 'File type not allowed'}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/search', methods=['GET', 'POST'])
def search_paper():
    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title', '')
        author = data.get('author', '')
        subject = data.get('name', '')

        # Build the search query based on the input fields
        query = {}
        if title:
            query['title'] = {'$regex': title, '$options': 'i'}
        if author:
            query['author'] = {'$regex': author, '$options': 'i'}
        if subject and subject != 'select':
            query['name'] = {'$regex': subject, '$options': 'i'}

        # Query the database
        papers = mongo.db.research_papers.find(query)
        result = json.loads(dumps(papers))

        return jsonify(result)
    else:
        return render_template('search.html')

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session data
    session.pop('username', None)
    # Flash a success message
    flash('Logout successfully', 'success')
    # Redirect to the home page
    return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
