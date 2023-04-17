import smtplib
from email.message import EmailMessage

class EmailHandler:
    def __init__(self, host: str, port: int, email: str, password: str) -> None:
        self.host = host
        self.port = port
        self.email = email
        self.password = password

    async def send(self, receiver: str, subject: str, message: str) -> None:
        with smtplib.SMTP(self.host) as server:
            msg = EmailMessage()
            msg["From"] = self.email
            msg["To"] = receiver
            msg["Subject"] = subject 
            msg.set_content(message)
            
            server.starttls()
            server.login(self.email, self.password)
            server.sendmail(self.email, receiver, msg.as_string())