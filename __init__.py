from flask import * 
from flask_sqlalchemy import SQLAlchemy
import json

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
		

@app.route('/login', methods = ['POST'])
def login():
	return "Hello World"

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

db.create_all()
if __name__=='__main__':
	app.run(debug=True)