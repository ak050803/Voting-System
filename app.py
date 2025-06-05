from flask import Flask, request, redirect, url_for, render_template, jsonify
from flask_mail import Mail, Message
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ansukumar80635@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'achy ocgi pbrw cfic'        # Replace with your App Password

mail = Mail(app)

# Users with voted flag and email
users = {
    '123456789012': {'email': 'voter1@example.com', 'voted': False},
    '2023CSE001': {'email': 'voter2@example.com', 'voted': False},
    '2023CSE002': {'email': 'voter3@example.com', 'voted': False},
    '587071381121': {'email': 'ansukumar80635@gmail.com', 'voted': False}
}

otp_store = {}
votes = {'A': 0, 'B': 0}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        adhaar = request.form['adhaar']
        if adhaar not in users:
            return render_template('error.html', message="❌ Invalid Aadhaar or Roll Number")

        if users[adhaar]['voted']:
            return render_template('already_voted.html')

        otp = str(random.randint(100000, 999999))
        otp_store[adhaar] = otp

        msg = Message('Your OTP for Voting System', sender=app.config['MAIL_USERNAME'], recipients=[users[adhaar]['email']])
        msg.body = f'Your OTP is: {otp}'
        mail.send(msg)

        return render_template('otp_verify.html', adhaar=adhaar)

    return render_template('index.html')


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    adhaar = request.form['adhaar']
    otp_entered = request.form['otp']

    if adhaar not in users:
        return render_template('error.html', message="❌ Invalid Aadhaar or Roll Number")

    if otp_store.get(adhaar) != otp_entered:
        return render_template('error.html', message="❌ Incorrect OTP. Please try again.")

    return render_template('vote.html', adhaar=adhaar)


@app.route('/vote', methods=['POST'])
def vote():
    adhaar = request.form['adhaar']
    candidate = request.form['candidate']

    if adhaar not in users:
        return render_template('error.html', message="❌ Invalid Aadhaar or Roll Number")

    if users[adhaar]['voted']:
        return render_template('already_voted.html')

    if candidate not in votes:
        return render_template('error.html', message="❌ Invalid candidate selected.")

    votes[candidate] += 1
    users[adhaar]['voted'] = True
    otp_store.pop(adhaar, None)

    # After vote, render thank you page (chart.html) with show_results=False
    return render_template('chart.html', show_results=False)


@app.route('/chart')
def chart():
    # Render chart.html with results visible immediately
    return render_template('chart.html', show_results=True)


@app.route('/results_data')
def results_data():
    # API endpoint to get votes counts as JSON for dynamic chart loading
    return jsonify(votes)


@app.route('/chart_data')
def chart_data():
    # This route generates the chart image and returns its path
    candidates = list(votes.keys())
    counts = [votes[c] for c in candidates]

    plt.figure(figsize=(6, 4))
    bars = plt.bar(candidates, counts, color=['skyblue', 'orange'])
    plt.title('📊 Voting Results')
    plt.xlabel('Candidates')
    plt.ylabel('Votes')

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height, str(int(height)), ha='center', va='bottom')

    os.makedirs('static', exist_ok=True)
    chart_path = 'static/votes.png'
    plt.savefig(chart_path)
    plt.close()

    return chart_path


if __name__ == '__main__':
    app.run(debug=True)
