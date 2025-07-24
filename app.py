from flask import Flask, request, redirect, render_template, url_for, session
from openpyxl import load_workbook
import pandas as pd
import os

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Required for sessions

# Coordinator login credentials
COORDINATOR_USERNAME = 'admin'
COORDINATOR_PASSWORD = 'admin123'

@app.route('/')
def index():
    return render_template('index.html')

# Student Page
@app.route('/students')
def students():
    return render_template("students.html")

@app.route('/coordinator_login', methods=['GET', 'POST'])
def coordinator_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':  # You can customize this
            session['coordinator_logged_in'] = True
            return redirect(url_for('coordinator'))
        else:
            return render_template('coordinator_login.html', error="Invalid credentials")
    return render_template('coordinator_login.html')

@app.route('/coordinator')
def coordinator():
    if not session.get('coordinator_logged_in'):
        return redirect(url_for('coordinator_login'))

    # ✅ Load the submitted data
    try:
        df = pd.read_excel('internship_data.xlsx')  # make sure the path is correct
        data = df.to_dict(orient='records')
    except Exception as e:
        data = []
        print("Error loading submissions:", e)

    # ✅ Pass data to the template
    return render_template('coordinator.html', data=data)


@app.route('/logout')
def logout():
    session.pop('coordinator_logged_in', None)
    return redirect(url_for('index'))



# Student Form Submission
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        department = request.form['department']
        company = request.form['company']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        email = request.form['email']
        phone = request.form['phone']

        file_path = 'internship_data.xlsx'
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
        else:
            df = pd.DataFrame(columns=[
                'Name', 'Roll No', 'Department', 'Company', 'Start Date', 'End Date', 'Email', 'Phone'
            ])

        new_data = pd.DataFrame([{
            'Name': name,
            'Roll No': roll,
            'Department': department,
            'Company': company,
            'Start Date': start_date,
            'End Date': end_date,
            'Email': email,
            'Phone': phone
        }])

        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(file_path, index=False)

        return redirect('/')

# Update Status Button
@app.route('/update_status/<int:row_index>/<status>')
def update_status(row_index, status):
    file_path = 'internship_data.xlsx'
    df = pd.read_excel(file_path)

    if 0 <= row_index < len(df):
        df.at[row_index, 'Status'] = status
        df.to_excel(file_path, index=False)

    return redirect(url_for('coordinator'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

