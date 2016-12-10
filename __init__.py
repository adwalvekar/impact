from flask import * 
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://impact:helloworld@localhost/impact"
db = SQLAlchemy(app)

class user_login(db.Model):
	__tablename__ = 'user_login'
	ulid = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(50), unique = True)
	password = db.Column(db.String(50))

	def __init__(self, username, password):
		self.username = username
		self.password = password

class Post(db.Model):
	__tablename__ = 'post'
	pid = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(50))
	title = db.Column(db.String(100))
	desc = db.Column(db.String(1500))
	imglink = db.Column(db.String(200))
	location = db.Column(db.String(100))
	active = db.Column(db.Boolean)
	date = db.Column(db.Date)
	x = db.Column(db.Float)
	y = db.Column(db.Float)
	event_type = db.Column(db.Integer)

	def __init__(self, username, title, desc, imglink, location, event_type, date,active = True, x = 0.0, y = 0.0):
		self.username = username
		self.title = title
		self.desc = desc
		self.imglink = imglink
		self.location = location
		self.active = active
		self.date = date
		self.x = x
		self.y = y
		self.event_type = event_type
		
		
@app.route('/login', methods = ['POST'])
def login():
	username = request.form['username']
	password = request.form['password']
	check = user_login.query.filter_by(username = username, password = password).first()
	if check is not None :
		return json.dumps({'status':True,'code':202,'description':'Logged in'})
	else :
		return json.dumps({'status':False, 'description':'Incorrect Credentials','code':401})
@app.route('/register', methods = ['POST'])
def register():
	username = request.form['username']
	password = request.form['password']
	check = user_login.query.filter_by(username = username).first()
	if check is None:
		user = user_login(username, password)
		db.session.add(user)
		db.session.commit()
		return json.dumps({'status':True,'code':201,'description':"Created"})
	else:
		return json.dumps({'status':False, 'description':'User already Exists','code':409})

@app.route('/post', methods = ['POST'])
def post():
	username = request.form['username']
	title = request.form['title']
	desc = request.form['desc']
	imglink = request.form['imglink']
	location = request.form['location']
	active = True
	date = datetime.strptime(request.form['date'] , '%d-%m-%Y')
	event_type = request.form['event_type']
	p = Post(username, title, desc, imglink, location, event_type, date, active = active)
	db.session.add(p)
	db.session.commit()
	return json.dumps({'status':True,'code':201,'description':"Created"})

db.create_all()
if __name__=='__main__':
	app.run(debug=True)