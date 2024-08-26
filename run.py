from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)

app.config["SECRET_KEY"] = "CF_KEY123"

Login_manager = LoginManager()
Login_manager.init_app(app)
Login_manager.login_view = "login"

def localize_callback(*args, **kwargs):
    return "このページにアクセスするにはログインが必要です"
Login_manager.localize_callback = localize_callback

# 絶対パスでapp.pyのディレクトリパスを取得
basedir = os.path.abspath(os.path.dirname(__file__))
# 何のSQLを使用するかパスで記入する
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
print("sqlite:///" + os.path.join(basedir, "data.sqlite"))
# DBの変更履歴は不要にする
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

Migrate(app, db)

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean, default=False)
    
    def __init__(self, email, username, password_hash, admin
):
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.admin = admin
        
    def __repr__(self):
        return f"UserName: {self.username}"
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # passwordプロパティの参照をできなくする
    @property
    def password(self):
        raise AttributeError("password is not a read attribute")
    
    # self.passwordが作成されたら実行される
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        

class RegistrationFrom(FlaskForm):
    email = StringField("メールアドレス")
    username = StringField("従業員コード")
    password = PasswordField("パスワード", validators=[DataRequired(), EqualTo("pass_confirm", message="パスワードが一致していません")])
    pass_confirm = PasswordField("パスワード(確認)")
    submit = SubmitField("登 録")
    
class LoginForm(FlaskForm):
    username = StringField("従業員コード", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("ログイン")

@Login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def index():
    return render_template("Top.html")

@app.route('/resister', methods=["post", "get"])
def resister():
    form = RegistrationFrom()
    # form入力に問題がなければ
    if form.validate_on_submit():
        session["email"] = form.email.data
        session["username"] = form.username.data
        session["password"] = form.password.data
        password_hash = generate_password_hash(form.password.data) 
        user = User(
            email=form.email.data, 
            username=form.username.data, password_hash=password_hash, 
            admin=True
        )
        db.session.add(user)
        db.session.commit()
        flash("ユーザーが登録されました")
        # redirect : 処理を別のページに転送する
        return redirect(url_for("main"))
    return render_template("Resister.html", form=form)

@app.route("/user_maintenance")
def user_maintenance():
    users = User.query.order_by(User.id).all()
    return render_template("UserMaintenance.html", users=users)

@app.route("/login", methods=["get", "post"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            # ユーザーが存在すれば、パスワードをチェック
            if user.check_password(form.password.data):
                # loginする
                login_user(user)
                # login指定ない場合にはlogin=>nextに格納した本来行きたいURLが設定される
                next = request.args.get("next")
                if next == None or not next[0] == "/":
                    next = url_for("main")
                return redirect(next)
            else:
                flash("パスワードが一致しません")
        else:
            flash("入力されたユーザーは存在しません")
    return render_template("Login.html", form=form)

@app.route('/inquiry')
def inquiry():
    return render_template("Inquiry.html")

@app.route('/main')
@login_required
def main():
    return render_template("Main.html")

@app.route('/analysis')
@login_required
def analysis():
    return render_template("Analysis.html")

@app.route("/logout")
def logout():
    logout_user()
    # session.pop('_user_id', None)     
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
