from flask import * 
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
from sqlalchemy.dialects.mysql import *
import urllib2
from pyfcm import FCMNotification

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

class user_token(db.Model):
	__tablename__ = 'user_token'
	tid = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(50), unique = True)
	token = db.Column(db.String(500))

	def __init__(self, username, token):
		self.username = username
		self.token = token

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

class Attending(db.Model):
	__tablename__ = 'Attending'
	aid = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(50))
	pid = db.Column(db.Integer)

	def __init__(self, username, pid):
		self.username = username
		self.pid = pid
		

class Post(db.Model):
	__tablename__ = 'post'
	pid = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(50))
	title = db.Column(db.String(100))
	desc = db.Column(db.String(1500))
	imglink = db.Column(db.Text(4294967295))
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
	username = request.form['username']
	password = request.form['password']
	token = request.form['token']
	check = user_login.query.filter_by(username = username, password = password).first()
	if check is not None :
		data = user_details.query.filter_by(username = username).first()
		t = user_token.query.filter_by(username = username).first()
		if t is None:
			to = user_token(username,token)
			db.session.add(to)
		else :
			t.token = token
		db.session.commit()
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
	username = request.form['username']
	password = request.form['password']
	img = request.form['picture']
	fullname = request.form['fullname']
	token = request.form['token']
	elevation = 1
	check = user_login.query.filter_by(username = username).first()
	if check is None:
		user = user_login(username, password)
		db.session.add(user)
		ud = user_details(username,fullname,elevation,img)
		db.session.add(ud)
		t = user_token(username,token)
		db.session.add(t)
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

@app.route('/tacotest', methods = ['POST','GET'])
def tacotest():
	if request.method == 'GET':
		message = "Test"
		title = "SUZY SUX"
	else:
		message = request.form['message']
		title = request.form['title']
	return "OK"

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
	sendNotification(username,p)
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
	sendNotification(username,p)
	return json.dumps({'status':True,'code':201,'description':"Created"})

@app.route('/getImagesGivenPost', methods = ['POST'])
def getImages():
	pid = request.form['pid']
	pos = Post.query.filter_by(pid = pid).first()
	user = pos.username
	userret = user_details.query.filter_by(username = user).first()
	userimage = userret.picture
	postimage = pos.imglink
	print str(json.dumps({'status': True, 'userimage': userimage, 'postimage' : postimage, "code" : 200}))
	return json.dumps({'status': True, 'userimage': userimage, 'postimage' : postimage, "code" : 200})

@app.route('/feed', methods = ['POST'])
def feed():
	username = request.form['username']
	length = request.form['length']
	if username is not None:
		attendlist = Attending.query.filter_by(username = username)
		attend = []
		for i in attendlist:
			attend.append(i.pid)
		follow_list = Follows.query.filter_by(username = username)
		fp =0
		followed_posts=[]
		fe =0
		followed_events = []
		ie =0
		inactive_events = []
		if follow_list is not None:
			for i in follow_list:
				events_temp = Post.query.filter_by(username = i.follows).order_by(Post.date.desc())
				for j in events_temp:
					if j.event_type == 1 and j.active == True:
						followed_posts.append(j)
						fp+=1
					elif j.event_type == 2 and j.active == True:
						followed_events.append(j)
						fe+=1
					elif j.event_type == 2 and j.active == False:
						inactive_events.append(j)
						ie+=1
		common_events = Post.query.filter_by(event_type = 3).order_by(Post.date.desc())
		ce = Post.query.filter_by(event_type = 3).count()
		feed_post = {}
		feed_post['status'] = True
		feed_post['code'] = 200
		feed_post['feed'] = []
		ife = 0
		ifp = 0
		ice = 0
		iie = 0
		for i in range(0,int(length)):
			if i%10 <= 2 and fp>0 and ifp < fp: 
				poster = followed_posts[ifp]
				name_get = user_details.query.filter_by(username = poster.username).first()
				name = name_get.fullname
				image = name_get.picture
				if poster.pid in attend:
					attending = True
				else :
					attending = False
				temp  = {'pid':poster.pid,'username':poster.username,'desc':poster.desc, 'date':poster.date.strftime("%Y-%m-%d %H:%M:%S"), 'name':name,'event_type':poster.event_type, 'active':poster.active, 'userimage':image, 'attending' : attending}
				feed_post['feed'].append(temp)
				ifp +=1
			elif i%10 >= 3 and i%10 <= 5 and fe>0 and ife <fe: 
				poster = followed_events[ife]
				name_get = user_details.query.filter_by(username = poster.username).first()
				name = name_get.fullname
				image = name_get.picture
				if poster.pid in attend:
					attending = True
				else :
					attending = False
				temp  = {'pid':poster.pid,'username':poster.username,'title':poster.title.replace('"', '\\"'),'desc':poster.desc.replace('"', '\\"'),'location':poster.location.replace('"', '\\"'), 'date':poster.date.strftime("%Y-%m-%d %H:%M:%S"), 'name':name, 'event_type':poster.event_type, 'active':poster.active,'userimage':image, 'postimage':poster.imglink, 'attending':attending}
				feed_post['feed'].append(temp)
				ife+=1
			elif i%10 >= 6 and i%10 <= 8 and ce>0 and ice<ce: 
				poster = common_events[ice]
				name_get = user_details.query.filter_by(username = poster.username).first()
				name = name_get.fullname
				image = name_get.picture
				if poster.pid in attend:
					attending = True
				else :
					attending = False
				temp  = {'pid':poster.pid,'username':poster.username,'title':poster.title.replace('"', '\\"'),'desc':poster.desc.replace('"', '\\"'),'location':poster.location.replace('"', '\\"'), 'date':poster.date.strftime("%Y-%m-%d %H:%M:%S"), 'name':name, 'event_type':poster.event_type, 'active':poster.active, 'userimage':image, 'postimage':poster.imglink, 'attending' : attending}
				feed_post['feed'].append(temp)
				ice+=1
			elif i%10==9 and ie>0 and iie<ie: 
				poster = inactive_events[iie]
				name_get = user_details.query.filter_by(username = poster.username).first()
				name = name_get.fullname
				image = name_get.picture
				if poster.pid in attend:
					attending = True
				else :
					attending = False
				temp  = {'pid':poster.pid,'username':poster.username,'title':poster.title.replace('"', '\\"'),'desc':poster.desc.replace('"', '\\"'),'location':poster.location.replace('"', '\\"'), 'date':poster.date.strftime("%Y-%m-%d %H:%M:%S"), 'name':name, 'event_type':poster.event_type, 'active':poster.active, 'userimage':image, 'postimage':poster.imglink, 'attending' : attending}
				feed_post['feed'].append(temp)
				iie+=1
		return json.dumps(feed_post)
	else:
		return json.dumps({'status':False,'description': 'User not found', 'code':404})

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
def unfollow():
	username = request.form['username']
	follows = request.form['follows']
	check = Follows.query.filter_by(username = username, follows = follows).first()
	if check is not None:	
		Follows.query.filter_by(username = username, follows = follows).delete()
		db.session.commit()
		return json.dumps({'status':True, 'code': 202})
	else :
		return json.dumps({'status':False, 'code': 409, 'description':"Not Following"})

@app.route('/search', methods=['POST'])
def search():
	fullname = request.form['fullname']
	username = request.form['username']
	user = user_details.query.filter(user_details.fullname.like("%"+str(fullname)+"%")).all()
	data = {}
	users = []
	if user is not None:
		for i in user:
			image = i.picture
			susername = i.username
			fullname = i.fullname
			follow = False
			followret = Follows.query.filter_by(username = username, follows = susername).first()
			if followret is not None:
				follow = True
			temp = {}
			temp['username'] = susername
			temp['image'] = image
			temp['fullname'] = fullname
			temp['follows'] =follow
			users.append(temp)
		data['status'] = True
		data['code'] = 200
		data['users'] = users
		return json.dumps(data)
	else:
		data['status'] = False
		data['code'] = 404
		data['description'] = 'User not Found'
		return json.json.dumps(data)

@app.route('/followlist',methods = ['POST'])
def followlist():
	username = request.form['username']
	flist = Follows.query.filter_by(username = username)
	data = {}
	data['list'] = []
	data['count'] = Follows.query.filter_by(username = username).count()
	for i in flist:
		dataret = user_details.query.filter_by(username = i.follows).first()
		temp = {}
		temp['picture'] = dataret.picture
		temp['fullname'] = dataret.fullname
		temp['username'] = dataret.username
		data['list'].append(temp)
	data['status'] = True
	data['code'] = 200
	return json.dumps(data)
@app.route('/followerlist',methods = ['POST'])
def followerlist():
	username = request.form['username']
	flist = Follows.query.filter_by(follows = username)
	data = {}
	data['list'] = []
	data['count'] = Follows.query.filter_by(follows = username).count()
	for i in flist:
		dataret = user_details.query.filter_by(username = i.username).first()
		temp = {}
		temp['picture'] = dataret.picture
		temp['fullname'] = dataret.fullname
		temp['username'] = dataret.username
		data['list'].append(temp)
	data['status'] = True
	data['code'] = 200
	return json.dumps(data)

@app.route('/attend', methods = ['POST'])
def attend():
	username = request.form['username']
	pid = request.form['pid']
	check = Attending.query.filter_by(username = username, pid = pid).first()
	if check is None:	
		a = Attending(username,pid)
		db.session.add(a)
		db.session.commit()
		return json.dumps({'status':True, 'code': 202})
	else :
		return json.dumps({'status':False, 'code': 409, 'description':"Already Attending"})

@app.route('/unattend',methods = ['POST'])
def unattend():
	username = request.form['username']
	pid = request.form['pid']
	check = Attending.query.filter_by(username = username, pid = pid).first()
	if check is not None:	
		Attending.query.filter_by(username = username, pid = pid).delete()
		db.session.commit()
		return json.dumps({'status':True, 'code': 202})
	else :
		return json.dumps({'status':False, 'code': 409, 'description':"Not Attending"})

@app.route('/attendlistforevent',methods = ['POST'])
def attendlistforevent():
	pid = request.form['pid']
	alist = Attending.query.filter_by(pid = pid)
	data = {}
	data['list'] = []
	data['count'] = Attending.query.filter_by(pid = pid).count()
	for i in alist:
		dataret = user_details.query.filter_by(username = i.username).first()
		temp = {}
		temp['picture'] = dataret.picture
		temp['fullname'] = dataret.fullname
		temp['username'] = dataret.username
		data['list'].append(temp)
	data['status'] = True
	data['code'] = 200
	return json.dumps(data)

@app.route('/attendlistforuser',methods = ['POST'])
def attendlistforuser():
	username = request.form['username'] 
	alist = Attending.query.filter_by(username = username)
	data = {}
	data['list'] = []
	data['count'] = Attending.query.filter_by(username = username).count()
	for i in alist:
		dataret = Post.query.filter_by(pid = i.pid).first()
		temp = {}
		name_get = user_details.query.filter_by(username = dataret.username).first()
		name = name_get.fullname
		image = name_get.picture
		temp  = {'pid':dataret.pid,'username':dataret.username,'title':dataret.title.replace('"', '\\"'),'desc':dataret.desc.replace('"', '\\"'),'location':dataret.location.replace('"', '\\"'), 'date':dataret.date.strftime("%Y-%m-%d %H:%M:%S"), 'name':name, 'event_type':dataret.event_type, 'active':dataret.active, 'userimage':image, 'postimage':dataret.imglink}
		data['list'].append(temp)
	data['status'] = True
	data['code'] = 200
	return json.dumps(data)

def sendNotification(username,post):
	flist = Follows.query.filter_by(follows = username)
	nameret = user_details.query.filter_by(username = username).first()
	name = nameret.fullname
	registration_ids= []
	usernames = []
	for i in flist:
		dataret = user_token.query.filter_by(username = i.username).first()
		registration_ids.append(dataret.token)
		usernames.append(dataret.username)
	push_service = FCMNotification(api_key="AAAAFXEDMyw:APA91bHARuwO7X7Y5I_lLwkbEiQ3bCzt3TVS6awj6iqFolpd_YXMKKhevsoMsdx-cCWPkaXMR7iFuJB0X3TrVXqUcOgqSIfTO898PgWEsWZQrdZbDt8RILtgicYOS836jypqnMdAbsG4J170Fvj0tOdtB_USzhqj-g")
	message_title = "New Post from "+name
	message_body = post.desc
	result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)
	print message_title
	print message_body
	print str(registration_ids)
	print str(usernames)
	print str(result)	
	
db.create_all()
if __name__=='__main__':
	app.run(debug=True)
