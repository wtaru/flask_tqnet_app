from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
import os
# from flask_migrate import Migrate


app = Flask(__name__)
app.config["SECRET_KEY"] = "CF_KEY111"

basedir = os.path.abspath(os.path.dirname(__file__))
# 何のSQLを使用するかパスで記入する
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
print("sqlite:///" + os.path.join(basedir, "data.sqlite"))
# DBの変更履歴は不要にする
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Migrate(app, db)

@app.route('/')
def index():
    return render_template("Top.html")

@app.route('/inquiry')
def inquiry():
    return render_template("Inquiry.html")

@app.route('/main')
def main():
    return render_template("Main.html")

@app.route('/analysis')
def analysis():
    return render_template("Analysis.html")


if __name__ == "__main__":
    app.run(debug=True)
