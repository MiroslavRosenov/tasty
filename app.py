import dotenv
import os

from mysql.connector import MySQLConnection

from quart import Quart, render_template, flash
from werkzeug.exceptions import NotFound
from quart_auth import AuthManager, Unauthorized

from ext.mail import EmailHandler

from blueprints.accounts import accounts
from blueprints.dishes import dishes
from blueprints.api import api

app = Quart(__name__)
app.config["SECURITY_PASSWORD_SALT"] =  "ffe2d77f8f34dd3e382569c525bb854853e2b42a98fb47927d9a7b7a881f0b04"
app.config["SECRET_KEY"] =              "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

app.auth = AuthManager(app)
app.register_blueprint(accounts)
app.register_blueprint(dishes)
app.register_blueprint(api)

@app.errorhandler(Unauthorized)
async def redirect_to_login(*_: Unauthorized) -> None:
    await flash("Влезте в акаунта си, за да продължите", "error")
    return await render_template("signin.html")

@app.errorhandler(NotFound)
async def not_found(*_: NotFound) -> None:
    return await render_template("exception.html", details={
        "title": "Не можахме да намерим тази страница!",
        "message": "Страницата, до която се опитвате да отворите, е недостъпна или временно деактивирана"
    })

if __name__ == "__main__":
    dotenv.load_dotenv()
    app.db = MySQLConnection(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        database=os.getenv("MYSQL_DATABASE")
    )

    app.mail = EmailHandler(
        os.getenv("SMTP_HOST"),
        os.getenv("SMTP_PORT"),
        os.getenv("SMTP_EMAIL"),
        os.getenv("SMTP_PASSWORD")
    )

    app.run(debug=True, use_reloader=True, port=8000)