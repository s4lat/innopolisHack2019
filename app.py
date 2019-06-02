from flask import Flask, request, render_template, redirect, url_for, send_file, flash
from flask_login import (LoginManager, login_required, login_user,
	current_user, logout_user)
from jinja2.environment import Environment
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.utils import secure_filename
from string import ascii_letters, digits
from functools import partial
from dbhelper import DB
from math import ceil
import random as rand
import bcrypt, cfg, os, shutil

try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO

app = Flask(__name__)
app.secret_key = "omgitsosecret"
app.wsgi_app = ProxyFix(app.wsgi_app)
login_manager = LoginManager()
login_manager.init_app(app)
db = DB()

from utils import runHlsThread
runHlsThread()


app.jinja_env.globals['cfg'] = cfg

@app.route("/videos", methods=["GET"])
@login_required
def videos():
	count = db.count("videos")

	n_pages = ceil(count/cfg.V_PAGE_ROWS)
	page = request.args.get('page')
	try:
		page = int(page)

		if page > n_pages:
			page = n_pages
		elif page < 1:
			page = 1

	except (TypeError, ValueError):
		page = 1

	videos = db.getRange('videos', start=(page-1)*cfg.V_PAGE_ROWS, 
								end=cfg.V_PAGE_ROWS)

	return render_template("videos.html", videos=videos, n_pages=n_pages, 
		current_page=page, count=count)

	return render_template("videos.html")

@app.route('/upload_video', methods=['POST'])
@login_required
def upload_video():
	if current_user.role != "admin":
		return redirect(url_for("videos"))

	if 'file' not in request.files:
		flash('No file part')
		return redirect(url_for("videos"))
	file = request.files['file']

	if file.filename == '':
		flash('No selected file')
		return redirect(url_for("videos"))

	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		videos = os.listdir(cfg.SOURCE_VIDEOS_FOLDER)
		if filename in videos:
			filename = "("+"".join(rand.choice(ascii_letters+digits) for i in range(4))+") " + filename

		file.save(os.path.join(cfg.SOURCE_VIDEOS_FOLDER, filename))
		db.add_video((filename[:-4], "Описание", cfg.SOURCE_VIDEOS_FOLDER+filename, "in_progress", "new"))

	return redirect(url_for('videos'))

@app.route('/del_video', methods=['POST'])
def del_video():
	if current_user.role != "admin":
		return redirect(url_for("videos"))

	_id = request.form.get('_id')

	video = db.get_video(_id)
	if video and video[-1] != "new":
		try:
			shutil.rmtree(video[3], ignore_errors=True)
			os.remove(video[2])
			db.del_video(_id)
		except Exception as e:
			print(e)

	return redirect(url_for("videos"))


@app.route("/users")
@login_required
def users(errors=[], user=None):
	if current_user.role != "admin":
		return redirect(url_for("videos"))

	count = db.count("users")

	n_pages = ceil(count/cfg.U_PAGE_ROWS)
	page = request.args.get('page')
	try:
		page = int(page)

		if page > n_pages:
			page = n_pages
		elif page < 1:
			page = 1
	except (TypeError, ValueError):
		page = 1

	users = db.getRange('users', start=(page-1)*cfg.U_PAGE_ROWS, 
								end=cfg.U_PAGE_ROWS)

	return render_template("users.html", users=users, n_pages=n_pages, 
		current_page=page, count=count, errors=errors, user=user)


@app.route("/add_user", methods=["POST"])
@login_required
def add_user():

	if current_user.role != "admin":
		return redirect(url_for("videos"))

	first = request.form.get("first")
	last = request.form.get("last")
	patronymic = request.form.get("patronymic")
	email = request.form.get("email")
	phone = request.form.get("phone")
	other = request.form.get("other")
	role = request.form.get("role")

	errors = []
	 
	if not all((first, last, patronymic, email, phone, other, role)):
		errors.append("Пожалуйста заполните все поля для регистрации пользователя")

	if not errors:
		if not db.get_user(email):
			passw = "".join(rand.choice(ascii_letters+digits) for i in range(16))
			passwh = bcrypt.hashpw(passw.encode('utf-8'), bcrypt.gensalt())
			user = (first, last, patronymic, email, phone, other, passwh, role)
			db.add_user(user)
			return users(user=(*user[:5], passw))
		else:
			errors.append("Пользователь с таким эл.адресом уже существует")

	return users(errors)

@app.route("/del_user", methods=["POST"])
@login_required
def del_user():
	if current_user.role != "admin":
		return redirect(url_for("videos"))

	email = request.form.get("email")

	if email:
		try:
			adminCount = db.countAdmins()
			user = db.get_user(email)
			if user and (user.role == "admin" and adminCount > 1 or user.role == "user"):
				db.del_user(email)

		except Exception as e:
			print(e)

	return redirect(url_for("users"))

@app.route("/login", methods=["GET", "POST"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for("videos"))

	if request.method == "POST":
		email = request.form.get('email')
		passw = request.form.get('passw')

		remember = request.form.get('remember')

		remember = True if remember == "on" else False

		errors = []
		
		if not all((email, passw)):
			errors.append("Пожалуйста заполните все поля для входа")

		if not errors:
			user = db.get_user(email)
			if user:
				if bcrypt.checkpw(passw.encode('utf-8'), user.passwh):
					login_user(user, remember=remember)
					return redirect(url_for('videos'))

			errors.append("Неверный Email/Пароль")

		return render_template('login.html', errors=errors)

	return render_template('login.html')

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
	logout_user()
	return redirect(url_for("login"))

@login_manager.user_loader
def load_user(email):
    return db.get_user(email)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('videos'))

def allowed_file(filename):
    return '.' in filename and \
    	filename.rsplit('.', 1)[1].lower() in cfg.ALLOWED_EXTENSIONS



