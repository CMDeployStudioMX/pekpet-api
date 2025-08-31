import smtplib
from email.message import EmailMessage
import os

def send_email(code, to_email):
    msg = EmailMessage()

    text = f"""
    Tu codigo de verificación es: {code}
    \n
    Este codigo es valido por 5 minutos. Si no solicitaste este codigo, ponte en contacto con nuestro soporte técnico.
    \n
    Saludos,
    PekPet Team
    """

    msg.set_content(text)
    msg['Subject'] = 'Codigo de Verificacion'
    msg['From'] = os.getenv('SMTP_USER')
    msg['To'] = to_email

    try:
        with smtplib.SMTP(os.getenv('SMTP_HOST'), os.getenv('SMTP_PORT')) as server:
            server.starttls()
            server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    