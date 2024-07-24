from flask import Flask, request, render_template, redirect, url_for, flash
import requests
from config import Config
import sqlite3

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'

def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS bets
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, date TEXT, subject TEXT, description TEXT)''')
        conn.commit()

def add_example_bets():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        example_bets = [
            ("Max Mustermann", "max@example.com", "2024-07-25", "Wettervorhersage", "Es wird sonnig und warm."),
            ("Erika Musterfrau", "erika@example.com", "2024-07-26", "Aktienkurs", "Der Kurs von XYZ wird steigen."),
            ("Hans Wurst", "hans@example.com", "2024-07-27", "Sportergebnis", "Team A gewinnt gegen Team B.")
        ]
        c.executemany('INSERT INTO bets (name, email, date, subject, description) VALUES (?, ?, ?, ?, ?)', example_bets)
        conn.commit()

def get_bets():
    with sqlite3.connect('database.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT id, date, subject FROM bets')
        bets = c.fetchall()
    return bets

@app.before_first_request
def setup():
    init_db()
    add_example_bets()

def send_brevo_email(to, subject, html_content):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "Content-Type": "application/json",
        "api-key": app.config['BREVO_API_KEY']
    }
    data = {
        "sender": {"email": "792fa0001@smtp-brevo.com"},
        "to": [{"email": to}],
        "subject": subject,
        "htmlContent": html_content
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

@app.route('/')
def index():
    bets = get_bets()
    return render_template('index.html', bets=bets)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    date = request.form.get('date')
    subject = request.form.get('subject')
    description = request.form.get('description')

    response = send_brevo_email(
        to=email,
        subject=f"Vorhersage für {subject}",
        html_content=f"<p>Hallo {name},</p><p>{description}</p>"
    )

    if response.get('messageId'):
        flash('E-Mail wurde erfolgreich gesendet!', 'success')
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO bets (name, email, date, subject, description) VALUES (?, ?, ?, ?, ?)',
                      (name, email, date, subject, description))
            conn.commit()
    else:
        flash('Fehler beim Senden der E-Mail.', 'error')

    return redirect(url_for('index'))

@app.route('/test_email', methods=['POST'])
def test_email():
    recipient_email = request.form.get('email')
    
    if not recipient_email:
        flash('Keine Empfänger-E-Mail angegeben', 'error')
        return redirect(url_for('index'))

    response = send_brevo_email(
        to=recipient_email,
        subject='Test-E-Mail',
        html_content='<p>Dies ist eine Test-E-Mail von Brevo.</p>'
    )

    if response.get('messageId'):
        flash('Test-E-Mail erfolgreich gesendet!', 'success')
    else:
        flash('Fehler beim Senden der Test-E-Mail.', 'error')

    return redirect(url_for('index'))

@app.route('/bet/<int:bet_id>')
def bet_detail(bet_id):
    with sqlite3.connect('database.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT date, subject, description FROM bets WHERE id = ?', (bet_id,))
        bet = c.fetchone()
    return render_template('bet_detail.html', bet=bet)

if __name__ == '__main__':
    app.run(debug=True)
