
from flask import Flask, render_template, g
import os
import sqlite3

app = Flask(__name__, template_folder="../templates", static_folder="../static")
DATABASE = "../database/discounts.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new-discounts")
def new_discounts():
    return render_template("new_discounts.html")

@app.route("/docs")
def docs():
    return render_template("docs.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("✅ LNCC Discounts Monitor 启动完成，服务已就绪。")
    app.run(host="0.0.0.0", port=port)
