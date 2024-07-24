from flask import Flask, request, render_template, redirect, url_for, flash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
import sqlite3

app = Flask(__name__)
app.config.from_object(Config)

def send_email(to, subject, html_content):
    """Send an email using SMTP2GO"""
    smtp_server = 'mail.smtp2go.com'
    smtp_port = 587
    smtp_username = app.config['SMTP2GO_USERNAME']
    smtp_password = app.config['SMTP2GO_PASSWORD']
    
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f'Error sending email: {e}')
        return False

@app.route('/')
def index():
    bets = get_bets()  # Holt die Wetten aus der Datenbank
    return render_template('index.html', bets=bets)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    date = request.form.get('date')
    subject = request.form.get('subject')
    description = request.form.get('description')

    html_content = f"<p>Hallo {name},</p><p>{description}</p>"

    if send_email(to=email, subject=f"Vorhersage für {subject}", html_content=html_content):
        flash('E-Mail wurde erfolgreich gesendet!', 'success')
        save_bet(name, email, date, subject, description)  # Speichern der Wette
    else:
        flash('Fehler beim Senden der E-Mail.', 'error')

    return redirect(url_for('index'))

@app.route('/bet/<int:bet_id>')
def bet_detail(bet_id):
    """Zeigt die Details einer bestimmten Wette an"""
    with sqlite3.connect('database.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM bets WHERE id = ?', (bet_id,))
        bet = c.fetchone()

    if bet is None:
        flash('Wette nicht gefunden', 'error')
        return redirect(url_for('index'))

    return render_template('bet_detail.html', bet=bet)


@app.route('/test_email', methods=['POST'])
def test_email():
    recipient_email = request.form.get('email')

    if not recipient_email:
        flash('Keine Empfänger-E-Mail angegeben', 'error')
        return redirect(url_for('index'))

    if send_email(to=recipient_email, subject='Test-E-Mail', html_content='<p>Dies ist eine Test-E-Mail von SMTP2GO.</p>'):
        flash('Test-E-Mail erfolgreich gesendet!', 'success')
    else:
        flash('Fehler beim Senden der Test-E-Mail.', 'error')

    return redirect(url_for('index'))

def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS bets
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, date TEXT, subject TEXT, description TEXT)''')
        conn.commit()

def save_bet(name, email, date, subject, description):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('INSERT INTO bets (name, email, date, subject, description) VALUES (?, ?, ?, ?, ?)',
                  (name, email, date, subject, description))
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

if __name__ == '__main__':
    app.run(debug=True)
