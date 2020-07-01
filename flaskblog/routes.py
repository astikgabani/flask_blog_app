from flask import render_template, request, flash, redirect, url_for, jsonify
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskblog import app, db, bcrypt
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

posts = [{
    "title" : "Custom Blog 1",
    "content" : "Hey there, this is custom blog",
    "author" : "Astik",
    "date_posted" : "Today"
}]


@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", posts=posts)


@app.route('/posts/<string:name>')
def post(name):
    return jsonify({name:posts})


@app.route('/about')
def about():
    return render_template("about.html", title="About")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash(f"Login Successfully for {form.username.data}.", "success")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash(f"Username or Password is wrong.", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Account Created for {form.username.data}!", "success")
        return redirect(url_for("login"))
    return render_template("signup.html", title="Sign Up", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been Updated!', "success")
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("account.html", title="Account", form=form)
