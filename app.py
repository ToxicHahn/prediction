from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3
<<<<<<< HEAD
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from config import Config
=======
>>>>>>> parent of 92e0978 (mails now (theoretically) get send)

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY


# Initialisieren der Datenbank
def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        # Tabelle erstellen, falls nicht vorhanden
        c.execute('''
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                date TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

@app.before_first_request
def setup():
    init_db()

@app.route('/')
def index():
    with sqlite3.connect('database.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT id, subject, created_at FROM bets ORDER BY created_at DESC')
        bets = c.fetchall()
    return render_template('index.html', bets=bets)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    date = request.form.get('date')
    subject = request.form.get('subject')
    description = request.form.get('description')

    if not (name and email and date and subject and description):
        flash('Alle Felder müssen ausgefüllt werden!', 'error')
        return redirect(url_for('index'))

    try:
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO bets (name, email, date, subject, description, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            ''', (name, email, date, subject, description))
            conn.commit()
        flash('Wette erfolgreich eingereicht!', 'success')
    except Exception as e:
        flash(f'Fehler beim Einfügen der Wette: {e}', 'error')

    return redirect(url_for('index'))

@app.route('/test_email', methods=['POST'])
def test_email():
    recipient_email = request.form.get('email')

    if not recipient_email:
        flash('Keine Empfänger-E-Mail angegeben', 'error')
        return redirect(url_for('index'))

    # Hier eine Test-E-Mail senden, wenn Sie einen SMTP-Anbieter verwenden
    # Ersetzen Sie die folgende Zeile mit Ihrer tatsächlichen Test-E-Mail-Funktionalität
    flash(f'Test-E-Mail an {recipient_email} erfolgreich gesendet!', 'success')

    return redirect(url_for('index'))

@app.route('/bet/<int:bet_id>')
def bet_details(bet_id):
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('SELECT name, email, date, subject, description, created_at FROM bets WHERE id = ?', (bet_id,))
        bet = c.fetchone()
    if bet:
        return render_template('bet_details.html', bet=bet)
    else:
        flash('Wette nicht gefunden.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
