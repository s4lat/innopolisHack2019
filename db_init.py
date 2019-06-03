from string import ascii_letters, digits
import random as rand
import sqlite3, json, bcrypt, cfg

conn = sqlite3.connect(cfg.DB_FILENAME)



conn.execute("DROP TABLE IF EXISTS users")
conn.execute( """CREATE TABLE users (
					first text NOT NULL,
					last text NOT NULL,
					patronymic text NOT NULL,
					email text NOT NULL UNIQUE,
					phone text NOT NULL UNIQUE,
					other text, 
					passwh BLOB NOT NULL,
					role text NOT NULL)
				""")

conn.commit()

conn.execute("DROP TABLE IF EXISTS videos")
conn.execute( """CREATE TABLE videos (
					title text NOT NULL,
					description text NOT NULL,
					source text NOT NULL,
					hls_path text NOT NULL,
					status text NOT NULL)
				""")

conn.commit()

admin_pass = "SECret21672"
passh = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt())

user = ('Аминистратор', 'Аминистраторов', 'Аминистраторович', 'admin@gmail.com',
					'+79123456789', "Просто админ", passh, 'admin')

conn.execute( """INSERT INTO users
					VALUES (?, ?, ?, ?, ?, ?, ?, ?)
				""", user)
conn.commit()
conn.close()

with open("admin_auth.json", 'w') as f:
	f.write(json.dumps({"admin_email": "admin@gmail.com", 
						"admin_pass":admin_pass
						}))

print("""Данные для авторизации администратора сохранены в файле admin_auth.json:
	Email: admin@gmail.com
	Пароль: %s""" % admin_pass)

