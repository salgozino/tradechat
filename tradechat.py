"""
TradeChat

A simple example for web-based chat room baed on Flask and SQLite3

"""

import datetime as dt
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash

# The application object from the main Flask class
app = Flask(__name__)

#Override configure from env variables.
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'tradechat.db'), DEBUG = True, SECRET_KEY= 'password'))

# do not complain of no config file exist
app.config.from_envvar('TC_SETTINGS', silent=True)


def connect_db():
	"'Connects to the TC Dababase'"
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv
	
	
def get_db():
	"'Opens a new connection to the TC Database'"
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

	
def init_db():
	"'Creates the TC database tables'"
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql',mode='r') as f:
			#Creo la base de datos
			query = f.read()
			db.cursor().executescript(query)
			db.commit()

def check_user(db,name):
	"'Verifico si existe el usuario a registrar o no.'"
	query = "SELECT EXISTS(SELECT name FROM users WHERE name = ?)"
	data = db.execute(query,(name,))
	print(data.fetchone())
	return data.fetchone()
			
@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()
	
	
@app.route('/')
def show_entries():
    "'Render all entries of the TC Dababase'"
    db = get_db()
    query = 'select comment, user, time from comments order by id desc'
    cursor = db.execute(query)
    comments = cursor.fetchall()
    return render_template('show_entries.html', comments = comments)	


@app.route('/login', methods=['GET', 'POST'])
def login():
	"'Login existing user'"
	error = None
	if request.method == 'POST':
		db = get_db()
		try:
			query = 'select id from users where name = ? and password = ?' 
			id = db.execute(query,[request.form['username'], request.form['password']]).fetchone()[0]
			session['logged_in'] = True
			flash('You are logged in.')
			app.config.update(dict(USERNAME=request.form['username']))
			return redirect(url_for('show_entries'))
		except:
			error = 'User not found or wrong password'
	return render_template('login.html',error=error)

	
@app.route('/register', methods = ['GET', 'POST'])
def register():
	"'Register new user'"
	error = None
	if request.method == 'POST':
		db = get_db()
		if request.form['username'] == "" or request.form['password'] == "":
			error = 'Provide both a username and password.'
		else:
			exist = check_user(db,request.form['username'])
			if exist:
				error = 'Usuario ya existente, por favor elija un nombre distinto'
			else:
				db.execute('insert into users (name,password) values (?,?)',
					[request.form['username'], request.form['password']])
				db.commit()
				session['logged_in'] = True
				flash('You were succesfully registered.')
				app.config.update(dict(USERNAME=request.form['username']))
				return redirect(url_for('show_entries'))
	return render_template('register.html',error=error)

	
@app.route('/add', methods = ['POST'])
def add_entry():
	"'Add entry to the TC Database'"
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	now = dt.datetime.now()
	db.execute('insert into comments (comment, user, time) values (?,?,?)',
		[request.form['text'], app.config['USERNAME'], str(now)[:-7]])
	db.commit()
	flash('Your comment was successfully added.')
	return redirect(url_for('show_entries'))

	
@app.route('/logout')
def logout():
	"'Logs out the current user'"
	session.pop('logged_in', None)
	flash('You were logged out.')
	return redirect(url_for('show_entries'))

	
# main routine
if __name__ == '__main__':
	init_db()	#Crea una nueva base de datos
	app.run(host='0.0.00', port='5000')