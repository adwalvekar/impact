from flask import * 
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
from sqlalchemy.dialects.mysql import *

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

class user_details(db.Model):
	__tablename__ = 'user_details'
	udid = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(50), unique = True)
	fullname = db.Column(db.String(50))
	elevation = db.Column(db.Integer)
	picture = db.Column(db.Text(4294967295))

	def __init__(self, username, fullname, elevation, picture):
		self.username = username
		self.fullname = fullname
		self.elevation = elevation
		self.picture = picture

class Post(db.Model):
	__tablename__ = 'post'
	pid = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(50))
	title = db.Column(db.String(100))
	desc = db.Column(db.String(1500))
	imglink = db.Column(db.LargeBinary)
	location = db.Column(db.String(100))
	active = db.Column(db.Boolean)
	date = db.Column(db.DateTime)
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
		
class Follows(db.Model):
	__tablename__ = "Follows"
	fid = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(50))
	follows = db.Column(db.String(50))

	def __init__(self, username, follows):
		self.follows = follows
		self.username = username


@app.route('/login', methods = ['POST'])
def login():
	print str(request.form)
	username = request.form['username']
	password = request.form['password']
	check = user_login.query.filter_by(username = username, password = password).first()
	if check is not None :
		data = user_details.query.filter_by(username = username).first()
		data_dict = {}
		data_dict['username'] = data.username
		data_dict['fullname'] = data.fullname
		data_dict['elevation'] = data.elevation
		data_dict['picture'] = data.picture
		data_dict['status'] = True
		data_dict['code'] = 202		
		return json.dumps(data_dict)
	else :
		return json.dumps({'status':False, 'description':'Incorrect Credentials','code':401})
@app.route('/register', methods = ['POST'])
def register():
	print str(request.form)
	username = request.form['username']
	password = request.form['password']
	img = request.form['picture']
	fullname = request.form['fullname']
	elevation = 1
	check = user_login.query.filter_by(username = username).first()
	if check is None:
		user = user_login(username, password)
		db.session.add(user)
		ud = user_details(username,fullname,elevation,img)
		db.session.add(ud)
		db.session.commit()
		data_dict= {}
		data_dict['username'] = username
		data_dict['fullname'] = fullname
		data_dict['elevation'] = elevation
		data_dict['picture'] = img
		data_dict['status'] = True
		data_dict['code'] = 201
		return json.dumps(data_dict)
	else:
		return json.dumps({'status':False, 'description':'User already Exists','code':409})

@app.route('/post', methods = ['POST'])
def post():
	username = request.form['username']
	title = None
	desc = request.form['desc']
	imglink = None
	location = None
	active = True
	date = datetime.fromtimestamp(long(request.form['date'])/1000).strftime('%Y-%m-%d %H:%M:%S')
	event_type = request.form['event_type']
	p = Post(username, title, desc, imglink, location, event_type, date, active = active)
	db.session.add(p)
	db.session.commit()
	return json.dumps({'status':True,'code':201,'description':"Created"})

@app.route('/event', methods = ['POST'])
def event():
	username = request.form['username']
	title = request.form['title']
	desc = request.form['desc']
	imglink = request.form['picture']
	location = request.form['location']
	active = True
	date = datetime.fromtimestamp(long(request.form['date'])/1000).strftime('%Y-%m-%d %H:%M:%S')
	event_type = request.form['event_type']
	p = Post(username, title, desc, imglink, location, event_type, date, active = active)
	db.session.add(p)
	db.session.commit()
	return json.dumps({'status':True,'code':201,'description':"Created"})

@app.route('/getImagesGivenPost', methods = ['POST'])
def getImages():
	username = request.form['username']
	pid = request.form['pid']
	user = user_details.query.filter_by(username = username).first()
	userimage = user.picture
	pos = Post.query.filter_by(pid = pid).first()
	postimage = pos.imglink
	return json.dumps({'status': True, 'userimage': userimage, 'postimage' : postimage, "code" : 200})

@app.route('/feed', methods = ['POST'])
def feed():
	username = request.form['username']

@app.route('/follow', methods = ['POST'])
def follow():
	username = request.form['username']
	follows = request.form['follows']
	check = Follows.query.filter_by(username = username, follows = follows).first()
	if check is None:	
		f = Follows(username,follows)
		db.session.add(f)
		db.session.commit()
		return json.dumps({'status':True, 'code': 202})
	else :
		return json.dumps({'status':False, 'code': 409, 'description':"Already Following"})

@app.route('/unfollow',methods = ['POST'])
def unfllow():
	username = request.form['username']
	follows = request.form['follows']
	check = Follows.query.filter_by(username = username, follows = follows).first()
	if check is not None:	
		Follows.query.filter_by(username = username, follows = follows).delete()
		db.session.commit()
		return json.dumps({'status':True, 'code': 202})
	else :
		return json.dumps({'status':False, 'code': 409, 'description':"Not Following"})

db.create_all()
if __name__=='__main__':
	app.run(debug=True)
