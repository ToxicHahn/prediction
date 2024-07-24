from flask import Flask, request, render_template, redirect, url_for, flash
import requests
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

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
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)
