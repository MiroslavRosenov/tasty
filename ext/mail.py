import smtplib
import ssl
from email.message import EmailMessage

class EmailHandler:
    def __init__(self, host: str, port: int, email: str, password: str) -> None:
        self.host = host
        self.port = port
        self.context = ssl.create_default_context()

        self.email = email
        self.password = password

    async def send(self, receiver: str, subject: str, message: str) -> None:
        with smtplib.SMTP(self.host, self.port) as smtp:
            msg = EmailMessage()
            msg["From"] = self.email
            msg["To"] = receiver
            msg["Subject"] = subject
            msg.set_content(message)

            smtp.connect(self.host, self.port)
            smtp.login(self.email, self.password)
            smtp.sendmail(self.email, receiver, msg.as_string())
            smtp.quit()