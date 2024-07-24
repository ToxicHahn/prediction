from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config
from models import db, Bet

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

def send_smtp2go_email(to, subject, html_content):
    msg = MIMEMultipart()
    msg['From'] = app.config['SMTP2GO_USERNAME']
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP(app.config['SMTP2GO_SMTP_SERVER'], app.config['SMTP2GO_SMTP_PORT'])
        server.starttls()
        server.login(app.config['SMTP2GO_USERNAME'], app.config['SMTP2GO_PASSWORD'])
        server.sendmail(app.config['SMTP2GO_USERNAME'], to, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")
        return False

@app.route('/')
def index():
    bets = Bet.query.order_by(Bet.timestamp.desc()).all()
    return render_template('index.html', bets=bets)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    date = request.form.get('date')
    subject = request.form.get('subject')
    description = request.form.get('description')

    new_bet = Bet(name=name, email=email, date=date, subject=subject, description=description)
    db.session.add(new_bet)
    db.session.commit()

    success = send_smtp2go_email(
        to=email,
        subject=f"Vorhersage für {subject}",
        html_content=f"<p>Hallo {name},</p><p>{description}</p>"
    )

    if success:
        flash('E-Mail wurde erfolgreich gesendet!', 'success')
    else:
        flash('Fehler beim Senden der E-Mail.', 'error')

    return redirect(url_for('index'))

@app.route('/bet/<int:bet_id>')
def bet_detail(bet_id):
    bet = Bet.query.get_or_404(bet_id)
    return render_template('bet_detail.html', bet=bet)

@app.route('/test_email', methods=['POST'])
def test_email():
    recipient_email = request.form.get('email')
    
    if not recipient_email:
        flash('Keine Empfänger-E-Mail angegeben', 'error')
        return redirect(url_for('index'))

    success = send_smtp2go_email(
        to=recipient_email,
        subject='Test-E-Mail',
        html_content='<p>Dies ist eine Test-E-Mail von SMTP2GO.</p>'
    )

    if success:
        flash('Test-E-Mail erfolgreich gesendet!', 'success')
    else:
        flash('Fehler beim Senden der Test-E-Mail.', 'error')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
