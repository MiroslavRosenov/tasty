import os
import dotenv
import logging

from mysql.connector import MySQLConnection
from a2wsgi import ASGIMiddleware

from quart import Quart, render_template, send_from_directory
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

@app.get("/")
async def index() -> None:
    return await render_template("index.html")

@app.get("/favicon.ico")
async def favicon():
    return await send_from_directory(app.root_path, "favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.errorhandler(Unauthorized)
async def redirect_to_login(exception: Unauthorized) -> None:
    return await render_template("exception.html", details={
        "title": "Не можахте да извършите това действие!",
        "message": "Влезте в акаунта си, за да продължите"
    })

@app.errorhandler(NotFound)
async def not_found(exception: NotFound) -> None:
    return await render_template("exception.html", details={
        "title": "Не можахме да намерим тази страница!",
        "message": "Страницата, до която се опитвате да отворите, е недостъпна или временно деактивирана"
    })

@app.before_first_request
async def setup() -> None:
    dotenv.load_dotenv()
    app.db = MySQLConnection(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        database=os.getenv("MYSQL_DATABASE"),
        password=os.getenv("MYSQL_PASSWORD")
    )

    app.mail = EmailHandler(
        os.getenv("SMTP_HOST"),
        os.getenv("SMTP_PORT"),
        os.getenv("SMTP_EMAIL"),
        os.getenv("SMTP_PASSWORD")
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=logging.BASIC_FORMAT)
    app.run(port=8000, debug=True)
else:
    app.asgi_app = ASGIMiddleware(app.asgi_app)