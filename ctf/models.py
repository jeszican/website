from sqlalchemy.orm import relationship
import hashlib
import datetime
from flask_login import UserMixin
import random
import os
import string

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# which team has completed which challenge
team_completion_log = db.Table("team_completion_log", db.Model.metadata,
	db.Column('challenge_id', db.Integer, db.ForeignKey('challenges.id')),
	db.Column('team_id', db.Integer, db.ForeignKey('teams.id')),
	db.Column('time_completed',db.DateTime, default=datetime.datetime.now())   
)

# which user actually submitted the flag for the challenge
user_completion_log = db.Table("user_completion_log", db.Model.metadata,
	db.Column('challenge_id', db.Integer, db.ForeignKey('challenges.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
)

# which team has bought which hint
hint_log = db.Table("hint_log", db.Model.metadata,
	db.Column('challenge_id', db.Integer, db.ForeignKey('challenges.id')),
	db.Column('team_id', db.Integer, db.ForeignKey('teams.id')),
)

class Average_Loading_Times(db.Model):
	__tablename__ = "average_loading_times"
	id = db.Column(db.Integer, primary_key=True)
	challenge_name = db.Column(db.String(128), index=True)
	time = db.Column(db.Float)

class Challenge_Launch_Log(db.Model):
	__tablename__ = "challenge_launch_log"
	id = db.Column(db.Integer, primary_key=True)
	challenge_id = db.Column('challenge_id', db.Integer, db.ForeignKey('challenges.id'))
	team_id = db.Column('team_id', db.Integer, db.ForeignKey('teams.id'))
	time_launched = db.Column('time_launched',db.DateTime, default=datetime.datetime.now())   

class Challenge_to_Url(db.Model):
	__tablename__ = "challenges_to_urls"
	# a table to store the config key values
	id = db.Column(db.Integer, primary_key=True)
	# the address of the challenge
	challenge_address = db.Column(db.String(128), index=True)
	# the launching message
	message = db.Column(db.String(128), index=True)
	# the region the instance is in
	region = db.Column(db.String(128), index=True)
	# the type of challenge it is // ansible or docker
	type = db.Column(db.String(128))
	# id of aws / docker container
	remote_id = db.Column(db.String(128), index=True, nullable=True)
	# the challenge the route is for
	challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
	# the team the challenge is for
	team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))

class Config(db.Model):
	# a table to store the config key values
	__tablename__ = "config"
	id = db.Column(db.Integer, primary_key=True)
	key = db.Column(db.String(128), index=True, unique=True)
	value = db.Column(db.String(128), index=True)

class Scores(db.Model):
	# a table to track to scores over time
	__tablename__ = "scores_over_time"
	id = db.Column(db.Integer, primary_key=True)
	# the team
	team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
	# the score of the team
	score = db.Column(db.Integer, default=0)
	# the time the score was recorded
	time = db.Column(db.DateTime, default=datetime.datetime.now())

class Team(db.Model):
	__tablename__ = "teams"
	id = db.Column(db.Integer, primary_key=True)
	# the team name
	team_name = db.Column(db.String(128), index=True, unique=True)
	# the invite code for the team
	team_code = db.Column(db.String(480))
	# the total points the team has 
	total_points = db.Column(db.Integer, default=0)
	# the team logo
	logo = db.Column(db.String(120))
	# the team color
	color = db.Column(db.String(120))
	# the team sound
	sound = db.Column(db.String(120))
	# the users that are in that team
	team_members = relationship("User")

	def __init__(self , team_name):
		self.team_name = team_name
		self.set_invite_code()
		self.set_logo()
		self.set_sound()
		self.set_color()

	def set_invite_code(self):
		## set a random string to be the invite code
		self.team_code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(20))

	def set_color(self):
		## get colors already in use
		already_used_colors = [t.color for t in db.session.query(Team).all()]
		## a list of web safe colors
		colors = ["IndianRed","LightCoral","Salmon","DarkSalmon","LightSalmon","Crimson","Red","FireBrick","DarkRed","Pink","LightPink","HotPink","DeepPink","MediumVioletRed","PaleVioletRed","Coral","Tomato","OrangeRed","DarkOrange","Orange","Gold","Yellow","LightYellow","LemonChiffon","LightGoldenrodYellow","PapayaWhip","Moccasin","PeachPuff","PaleGoldenrod","Khaki","DarkKhaki","Lavender","Thistle","Plum","Violet","Orchid","Fuchsia","Magenta","MediumOrchid","MediumPurple","BlueViolet","DarkViolet","DarkOrchid","DarkMagenta","Purple","RebeccaPurple","Indigo","MediumSlateBlue","SlateBlue","DarkSlateBlue","GreenYellow","Chartreuse","LawnGreen","Lime","LimeGreen","PaleGreen","LightGreen","MediumSpringGreen","SpringGreen","MediumSeaGreen","SeaGreen","ForestGreen","Green","DarkGreen","YellowGreen","OliveDrab","Olive","DarkOliveGreen","MediumAquamarine","DarkSeaGreen","LightSeaGreen","DarkCyan","Teal","Aqua","Cyan","LightCyan","PaleTurquoise","Aquamarine","Turquoise","MediumTurquoise","DarkTurquoise","CadetBlue","SteelBlue","LightSteelBlue","PowderBlue","LightBlue","SkyBlue","LightSkyBlue","DeepSkyBlue","DodgerBlue","CornflowerBlue","RoyalBlue","Blue","MediumBlue","DarkBlue","Navy","MidnightBlue"]
		color = random.choice(colors)		
		if color in already_used_colors:
			self.set_color()
		else: 
			self.color = color

	def set_sound(self):
		## get sounds already in use
		already_used_sounds = [t.sound for t in db.session.query(Team).all()]
		## set a random logo from the logo directory
		sound = random.choice(os.listdir("ctf/static/flags"))
		if sound in already_used_sounds:
			self.set_sound()
		else:
			self.sound = sound

	def set_logo(self):
		## get logos already in use
		already_used_logos = [t.logo for t in db.session.query(Team).all()]
		## set a random logo from the logo directory
		logo = random.choice(os.listdir("ctf/static/img/icons"))
		if logo in already_used_logos:
			self.set_logo()
		else:
			self.logo = logo

class User(db.Model, UserMixin):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	# the username
	username = db.Column(db.String(128), index=True, unique=True)
	# the email of the user
	email = db.Column(db.String(480), index=True, unique=True)
	# the password hash of the user
	password = db.Column(db.String(480))
	# the team they are in
	team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
	# what challenges this user submit the flag for
	challenges_completed = db.relationship("Challenge", secondary=user_completion_log)

	def __init__(self , username, password, email, team):
		self.username = username
		self.team_id = team.id
		self.email = email
		self.set_password(password)

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.id

	def set_password(self, password):
		# set the password has
		hash = hashlib.sha512(password.strip().encode('utf-8')).hexdigest()
		self.password = hash

	def check_password(self, password_to_check):
		# this function checks if the password is correct
		if hashlib.sha512(password_to_check.strip().encode('utf-8')).hexdigest() == self.password:
			return True
		else:
			return False

class Announcement(db.Model):
	__tablename__ = "announcements"
	id = db.Column(db.Integer, primary_key=True)
	# the content of the announcement
	announcement = db.Column(db.String(1024), index=True, unique=False)
	# the time the announcement was sent
	time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

class Event(db.Model):
	__tablename__ = "events"
	id = db.Column(db.Integer, primary_key=True)
	# the team the event concerns
	team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
	# the challenge they completed
	challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))

class Challenge_Resources(db.Model):
	__tablename__ = "challenge_resources"
	id = db.Column(db.Integer, primary_key=True)
	resource_id = db.Column(db.String(264), unique=True)
	resource_path = db.Column(db.String(264), unique=False)

class Challenge(db.Model):
	__tablename__ = "challenges"
	## id of challenge
	id = db.Column(db.Integer, primary_key=True)
	## the country code of the challenge
	country_code = db.Column(db.String(128), unique=True)
	## the challenge name
	name = db.Column(db.String(128), unique=False)
	## the challenge color
	color = db.Column(db.String(128), unique=False)
	## the description
	description = db.Column(db.String(1024), unique=False)
	## the hint
	hint = db.Column(db.String(1024), unique=False)
	## a python list of links
	links = db.Column(db.String(2048), unique=False)
	## the docker file of the challenge // if there is one
	docker_file = db.Column(db.String(2048), unique=False)
	## the ami for the challenge // if there is one
	ami = db.Column(db.JSON)
	## the answer/flag
	flag = db.Column(db.String(1024))
	## if it needs audio
	audio = db.Column(db.String(2048), unique=False)
	## if it needs a downloadable
	downloadables = db.Column(db.String(2048), unique=False)
	# email address - the email to send the uploads too
	email = db.Column(db.String(1024), unique=False)
	## the answer/flag
	a = db.Column(db.String(1024), default="")
	## the answer/flag
	b = db.Column(db.String(1024), default="")
	## the answer/flag
	c = db.Column(db.String(1024), default="")
	## the answer/flag
	d = db.Column(db.String(1024), default="")
	## the type (jeopardy, multiple, timed etc)
	type = db.Column(db.String(128), index=True, unique=False)
	## the category (reveng, forensics, web, etc)
	category = db.Column(db.String(128), index=True, unique=False)	
	## the challenge that it depends on
	depends_on = db.Column(db.String(128)) ## the country code of the challenge
	## the points for getting it right
	points = db.Column(db.Integer)
	## the deadline for the challenge
	deadline = db.Column(db.DateTime, default=datetime.datetime.now())   	
	## the penalty if a hint is given
	hint_penalty = db.Column(db.Integer)
	## the penalty if a wrong flag is entered
	flag_penalty = db.Column(db.Integer)
	# is it hidden
	hidden = db.Column(db.Boolean, default=False)
	# is it hidden
	advanced = db.Column(db.Boolean, default=False)
	## teams completed
	teams_completed = db.relationship("Team", secondary=team_completion_log, backref="challenges_completed")
	## hints used
	teams_hints_used = db.relationship("Team", secondary=hint_log, backref="hints_used")
	## information
	information = db.Column(db.JSON)

	def __repr__(self):
		return '<Challenge {}>'.format(self.id)

	def check_flag(self, flag_input):
		# check if the flag is correct
		if self.flag.lower().strip() == flag_input.lower().strip():
			# make it lower so some error is allowed
			return True
		else:
			return False
