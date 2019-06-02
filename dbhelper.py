import sqlite3, cfg
from flask_login import UserMixin

class DB:
	def __init__(self):
		self.db = cfg.DB_FILENAME

	def connect(self):
		return sqlite3.connect(self.db)

	def add_video(self, video):
		with self.connect() as conn:
			conn.execute("""INSERT INTO videos
					VALUES (?, ?, ?, ?, ?)
					""", video)

	def update_video(self, rowid, hls, status="old"):
		with self.connect() as conn:
			conn.execute("""UPDATE videos
					SET hls_path=?, status=?
					WHERE rowid=?;
					""", (hls, status, rowid))

	def del_video(self, rowid):
		with self.connect() as conn:
			conn.execute("""DELETE FROM videos
					WHERE rowid=?;
					""", rowid)

	def getNewVideos(self):
		with self.connect() as conn:
			cur = conn.cursor()
			cur.execute("""SELECT *,rowid FROM videos
					WHERE status='new' OR status="in_progress";""")

			return cur.fetchall()

	def get_video(self, rowid):
		with self.connect() as conn:
			cur = conn.cursor()
			cur.execute("""SELECT * FROM videos
				WHERE rowid=?;
				""", (rowid, ))
			return cur.fetchone()

	def add_user(self, user):
		with self.connect() as conn:
			conn.execute("""INSERT INTO users
					VALUES (?, ?, ?, ?, ?, ?, ?, ?)
					""", user)

	def del_user(self, email):
		with self.connect() as conn:
			conn.execute("""DELETE FROM users
				WHERE email=?;
				""", (email, ))

	def get_user(self, email):
		with self.connect() as conn:
			cur = conn.cursor()
			cur.execute("""SELECT * FROM users
				WHERE email=?;
				""", (email, ))
			data = cur.fetchone()
			if data:
				return self.User(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])

	def count(self, table):
		with self.connect() as conn:
			cur = conn.cursor()
			cur.execute("""SELECT count(*) 
				FROM %s;
				""" % (table,))

			return cur.fetchone()[0]

	def getRange(self, table, start, end):
		with self.connect() as conn:
			cur = conn.cursor()
			cur.execute("""SELECT *, ROWID FROM %s LIMIT %s OFFSET %s;
				""" % (table, end, start))

			return cur.fetchall()

	def countAdmins(self):
		with self.connect() as conn:
			cur = conn.cursor()
			cur.execute("""SELECT count(*) 
				FROM users WHERE role="admin";
				""")

			return cur.fetchone()[0]



	class User(UserMixin):
		def __init__(self, first, last, patronymic, email, phone, other, passwh, role):
			self.first = first
			self.last = last
			self.patronymic = patronymic
			self.email = email
			self.phone = phone
			self.other = other
			self.passwh = passwh
			self.role = role

		def get_id(self):
			return self.email