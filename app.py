import logging
import os
import re
import flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, redirect, url_for, flash
from flask import request
from logging import WARNING
from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from wtforms import validators
from flask_wtf import Form
from wtforms.fields.simple import StringField, PasswordField, EmailField
from wtforms.fields import RadioField
from flask_wtf.file import FileField, FileRequired, FileAllowed, MultipleFileField
from werkzeug.utils import secure_filename
import hashlib
from flask_wtf.csrf import CSRFProtect

login_manager = LoginManager()
mysql = MySQL()

app = Flask(__name__, template_folder='template', static_folder='staticFiles')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'aak20f031'
app.config['MYSQL_DB'] = 'dbmsproject'
app.secret_key = "0fc8fecf330c2fcc7869c1169638d5a7626e827d9d22bede66e51ebdc57a9e74"
app.config['SECRET_KEY'] = "0fc8fecf330c2fcc7869c1169638d5a7626e827d9d22bede66e51ebdc57a9e74"
mysql.init_app(app)



app.app_context().push()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def EmailRegexValidation(form, field):
    email_regex = r"^\S+@\S+\.\S+$"
    if re.match(email_regex, form.email.data) is None:
        message = field.gettext("Invalid email syntax")
        raise validators.ValidationError(message=message)
    else:
        return


ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]

class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25), ], render_kw={"placeholder": "Username"})
    email = EmailField('Email Address', [validators.Length(min=6, max=35)], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', [validators.Length(min=6, max=35)], render_kw={"placeholder": "Password","id":"password"})
    account_type = RadioField('Account Type', [validators.input_required()],
                              choices=[('user', "User"), ('seller', "Seller")], render_kw={"class": "account_form"})
    profile_pic = FileField("Profile Pic",[FileAllowed(['jpg', 'png'])])


csrf = CSRFProtect(app)

@app.route("/", )
def hello():
    error = None
    return render_template("main.html", error=error)


@app.route("/registration", methods=["POST"])
def register_page():
    form = RegisterForm(request.form)

    if form.validate():
        cursor = mysql.connection.cursor()
        username = form.username.data
        email = form.email.data
        password = form.password.data
        file = request.files['profile_pic']
        filename = secure_filename(file.filename)
        if filename == "":
            flash("No file selected")
            return redirect(url_for('register_page'))
        if file and allowed_file(file.filename):
            print("working")
            filename = secure_filename(f"{username}{file.filename}")
            file.save(os.path.join(
                r"C:\Users\aakash\Desktop\BCA\4th SEM\DBMS PROJECT\staticFiles\Profile_Pics", filename
            ))
        else:
            flash("Invalid File Type")
            return redirect(url_for('register_page'))
        if form.account_type.data == "user":
            account_type = "User"
        else:
            account_type = "Seller"

        user_pw_hash = generate_password_hash(password, salt_length=1000)
        cursor.execute(
            f"SELECT username from userdata where email = '{email}' or username = '{username}' limit 1")
        data = cursor.fetchall()
        if data:
            flash('Username or Email Already Exists Please Login to your account')
            return redirect(url_for('login_page'))
        print(filename)
        leng = f"""INSERT INTO userdata(username,email,password,account_type,pfp_url) values("{username}","{email}","{user_pw_hash}","{account_type}","{filename}")"""
        logging.log(msg=leng, level=WARNING)
        cursor.execute(
            f"""INSERT INTO userdata(username,email,password,account_type,pfp_url) values("{username}","{email}","{user_pw_hash}","{account_type}","{filename}")""")
        mysql.connection.commit()
        return redirect(url_for('login_page'))
    else:
        flash("Invalid")
    return render_template('registration2.html', form=form, )


@app.route("/registration", methods=['GET'])
def registration():
    form = RegisterForm(request.form)
    error = None
    return render_template("registration2.html", error=None, form=form)


@app.route("/login", methods=['POST', 'GET'])
def login_page():
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        email_user = request.form['email']
        password = request.form['password']
        cursor.execute(
            f"SELECT username,email,password,cookie from userdata where email = '{email_user}' or username = '{email_user}' limit 1")
        data = cursor.fetchall()
        if data:
            data = data[0]
            username = data[0]
            email = data[1]
            hashed = data[2]
            cookie_data = data[3]

            if check_password_hash(hashed, password):
                res = flask.make_response(redirect(url_for('profile_page')))
                user_cookie = username + password
                hashed_user_cookie = hashlib.sha256(user_cookie.encode()).hexdigest()
                if cookie_data is None:
                    cursor.execute(
                        f"UPDATE userdata SET cookie = '{hashed_user_cookie}' where email = '{email_user}' or username = '{email_user}' limit 1")
                    mysql.connection.commit()
                    cookie_data = hashed_user_cookie
                res.set_cookie('session_id', cookie_data, )

                return res
        else:
            flash('Invalid username or password')
    return render_template("login.html", error=None)


@app.route("/profile")
def profile_page():
    if request.cookies.get('session_id') is not None:
        session_id = request.cookies.get('session_id')
        cursor = mysql.connection.cursor()
        cursor.execute(
            f"SELECT username,email,pfp_url from userdata where cookie = '{session_id}' limit 1")
        data = cursor.fetchall()[0]
        mydict = {
            'username': data[0],
            'email': data[1],
            'pfp': data[2]
        }
        return render_template("profile2.html", mydict=mydict)
    else:
        return redirect(url_for('login_page'))


@app.route("/products")
def products_page():
    if request.cookies.get('session_id') is not None:
        session_id = request.cookies.get('session_id')
        cursor = mysql.connection.cursor()
        cursor.execute(
            f"SELECT name,description,price from product")
        data = cursor.fetchall()

        return render_template("products2.html", data=data)
    else:
        return "Not Logged In"


app.run(debug=True)
