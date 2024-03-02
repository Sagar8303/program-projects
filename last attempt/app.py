from flask import Flask, render_template, request, redirect, url_for, session,send_file,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/datatest'
db = SQLAlchemy(app)
app.secret_key = '5337844627274642'

# Ensure the creation of all tables inside the application context
with app.app_context():
    db.create_all()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

def is_logged_in():
    return 'username' in session

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            if user.role == 'staff':
                session['username'] = username
                session['role']  = user.role
                return redirect(url_for('staff_dashboard'))
            
            elif user.role == 'student':
                session['username'] = username
                session['role'] = user.role
                print(session['role'])
                return redirect(url_for('student_dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'

    return render_template('login.html', error=error)

@app.route('/staff/dashboard')
def staff_dashboard():
    if is_logged_in():
        return render_template('staff_dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/student/dashboard')
def student_dashboard():
    if is_logged_in(): 
        return render_template('student_dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    if is_logged_in():
        session.pop('username', None)
        session.pop('role', None)
    return redirect(url_for('login'))


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
'''
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    subject = request.args.get('subject', 'math')
    filenames = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith(subject)]
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('upload', subject=subject))
    # files = defaultdict(list)
    # for filename in filenames:
    #     subject = filename.split('_')[0]
    #     files[subject].append(filename)
    return render_template('upload.html', subject=subject, filenames=filenames)
'''

# ...

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    subject = request.args.get('subject', 'math')
    filenames = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith(subject)]
    files_by_subject = {subject: filenames}
    
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # After uploading, update the filenames list
        #filenames = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith(subject)]
        return redirect(url_for('upload', subject=subject))
    
    return render_template('upload.html', subject=subject, filenames=filenames)

# ...

'''
@app.route('/view_files')
def view_files():
    file_list = os.listdir(app.config['UPLOAD_FOLDER'])
    files_by_subject = {}
    for filename in file_list:
        subject = filename.split('_')[0]
        if subject not in files_by_subject:
            files_by_subject[subject] = []
        files_by_subject[subject].append(filename)
    return render_template('file_list.html', files_by_subject=files_by_subject)
'''

@app.route('/view_files')
def view_files():
    file_list = os.listdir(app.config['UPLOAD_FOLDER'])
    subjects = set(filename.split('_')[0] for filename in file_list)
    selected_subject = request.args.get('subject', 'all')

    if selected_subject == 'all':
        files_by_subject = {subject: [] for subject in subjects}
        for filename in file_list:
            subject = filename.split('_')[0]
            files_by_subject[subject].append(filename)
    else:
        files_by_subject = {selected_subject: []}
        for filename in file_list:
            subject = filename.split('_')[0]
            if subject == selected_subject:
                files_by_subject[selected_subject].append(filename)

    return render_template('file_list.html', files_by_subject=files_by_subject, subjects=subjects, selected_subject=selected_subject)


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('view_files'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)