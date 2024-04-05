import hashlib
import logging
import os
import re
from logging import WARNING

import flask
from flask import Flask
from flask import render_template, redirect, url_for, flash
from flask import request

from flask_mysqldb import MySQL
import mysql.connector
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from flask_wtf.file import FileField, FileAllowed
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from wtforms import validators
from wtforms.fields import RadioField
from wtforms.fields.simple import StringField, PasswordField, EmailField

import pickle

import joblib
import pandas as pd
import mysql.connector
import csv

from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

mysql = MySQL()

app = Flask(__name__, template_folder='template', static_folder='staticFiles')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'aak20f031'
app.config['MYSQL_DB'] = 'dbms_project'
app.secret_key = "0fc8fecf330c2fcc7869c1169638d5a7626e827d9d22bede66e51ebdc57a9e74"
app.config['SECRET_KEY'] = "0fc8fecf330c2fcc7869c1169638d5a7626e827d9d22bede66e51ebdc57a9e74"
mysql.init_app(app)

app.app_context().push()

ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]


#Validation For Filename To Make Sure its an image
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



#Validation for Email Formatting
def EmailRegexValidation(form, field):
    email_regex = r"^\S+@\S+\.\S+$"
    if re.match(email_regex, form.email.data) is None:
        message = field.gettext("Invalid email syntax")
        raise validators.ValidationError(message=message)
    else:
        return


#Class Based Registration Form Using WTForm
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25), ], render_kw={"placeholder": "Username"})
    email = EmailField('Email Address', [validators.Length(min=6, max=35)], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', [validators.Length(min=6, max=35)],
                             render_kw={"placeholder": "Password", "id": "password"})
    accounttype = RadioField('Account Type', [validators.input_required()],
                              choices=[('user', "User"), ('seller', "Seller")], render_kw={"class": "account_form"})
    profile_pic = FileField("Profile Pic", [FileAllowed(['jpg', 'png'])])


csrf = CSRFProtect(app)


def predict(product_id):
    onehot = joblib.load("onehotencoder")
    minmax = joblib.load("minmaxscaler")
    model = pickle.load(open('bestknn.pkl', 'rb'))


    df = pd.read_sql_query(f"""select * from products where ProductID = {product_id}""", con=mysql.connection)

    print(df)

    X = df.iloc[:, [True,True,False,False,True,True,True,False,False,True,True,True,True,False,True]]
    Y = df.iloc[:, [False,False,False,False,False,False,False,True,False,False,False,False,False,False,False]]
    num_columns = X.select_dtypes(exclude=['object']).columns

    cat_columns = X[["Category", "Brand"]].columns

    df = onehot.transform(X[cat_columns])
    df2 = minmax.transform(X[num_columns])

    df = pd.DataFrame(df.toarray())
    df2 = pd.DataFrame(df2)

    clean_data = pd.concat([df2, df], axis=1, ignore_index=True)

    print(clean_data.columns)

    prediction = model.predict(clean_data)

    return prediction


@app.route("/",methods=["GET"])
def mainpage():
    if request.cookies.get('session_id') is not None:
        session_id = request.cookies.get('session_id')
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT AccountType from users where Cookie = '{session_id}'")
        row = cursor.fetchone()
        usertype = row[0]


        if usertype =="User":
            cursor.execute(
                f"SELECT * from products")
            data = cursor.fetchall()
            error = None
            return render_template("main_page.html", error=error, data=data)
        else:
            pred = request.args.get("pred")
            if pred == None:
                pred = 0
            print(pred)
            cursor.execute(f"SELECT SellerID from Sellers where Username = (SELECT Username FROM users WHERE Cookie = '{session_id}')")
            row = cursor.fetchone()
            sellerid = row[0]
            print(sellerid)
            cursor.execute(
                f"SELECT * from products where SellerID = '{sellerid}'")
            data = cursor.fetchall()
            return render_template("seller.html", error="", data=data,pred=pred)
    else:
        return render_template("main_page.html",data=None,)
@app.route("/",methods=["POST"])
def product_form():
    if request.method == "POST":
        session_id = request.cookies.get('session_id')
        form = request.form
        product_name = form["product_name"]
        product_price = form["price"]
        product_quantity = form["stock"]
        product_category = form["Category"]
        product_brand = form["brands"]
        product_description = form["description"]
        product_warranty = form["warranty"]
        product_expiry = form["expiry"]
        product_weight = form["weight"]
        product_height = form["height"]
        product_width = form["width"]
        product_breadth = form["breadth"]
        product_country = form["country"]
        cursor = mysql.connection.cursor()
        cursor.execute('''select max(ProductID) from products''')
        product_id = cursor.fetchone()[0] +1
        file = request.files['pfp']
        filename = secure_filename(file.filename)
        if filename == "":
            flash("No file selected")
            return redirect(url_for('register_page'))
        if file and allowed_file(file.filename):
            print("working")
            filename = secure_filename(f"{product_name}")
            file.save(os.path.join(
                r"C:\Users\aakash\Desktop\BCA\4th SEM\DBMS PROJECT\staticFiles\product_images", filename
            ))
        else:
            flash("Invalid File Type")
            return redirect(url_for('register_page'))
        cursor.execute(f"SELECT SellerID from sellers where Username = (select Username from users where Cookie = '{session_id}')")
        row = cursor.fetchone()
        seller_id = row[0]
        print(product_warranty)
        cursor.execute(f''' INSERT INTO PRODUCTS values ({product_id},{seller_id},"{product_name}","{product_description}","{product_category}","{product_brand}",{product_price},{product_quantity},"{filename}","{product_warranty}","{product_expiry}",{product_weight},"{product_height}x{product_width}x{product_breadth}","{product_country}",0) ''')
        mysql.connection.commit()
        prediction = predict(product_id)
        return redirect(f"/?pred={prediction}")
    mainpage()



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
        if form.accounttype.data == "user":
            AccountType = "User"
        else:
            AccountType = "Seller"

        user_pw_hash = generate_password_hash(password, salt_length=1000)
        cursor.execute(
            f"SELECT username from users where email = '{email}' or username = '{username}' limit 1")
        data = cursor.fetchall()
        if data:
            flash('Username or Email Already Exists Please Login to your account')
            return redirect(url_for('login_page'))
        print(filename)
        leng = f"""INSERT INTO users(username,email,password,AccountType,ProfileUrl) values("{username}","{email}","{user_pw_hash}","{AccountType}","{filename}")"""
        logging.log(msg=leng, level=WARNING)
        cursor.execute(
            f"""INSERT INTO users(username,email,password,AccountType,ProfileUrl) values("{username}","{email}","{user_pw_hash}","{AccountType}","{filename}")""")
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
            f"SELECT username,email,password,cookie from users where email = '{email_user}' or username = '{email_user}' limit 1")
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
                        f"UPDATE users SET cookie = '{hashed_user_cookie}' where email = '{email_user}' or username = '{email_user}' limit 1")
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
            f"SELECT username,email,ProfileUrl from users where cookie = '{session_id}' limit 1")
        data = cursor.fetchall()[0]
        mydict = {
            'username': data[0],
            'email': data[1],
            'pfp': data[2]
        }
        return render_template("profile2.html", mydict=mydict)
    else:
        return redirect(url_for('login_page'))


@app.route("/aboutus")
def aboutus_page():
    return render_template("abus.html")

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