from ctf.models import db, User, Team, Config
from flask_login import login_user
from flask import redirect, url_for, make_response
import os

username_blacklist = [i.strip() for i in open(os.path.dirname(os.path.realpath(__file__))+"/username_blacklist.txt").readlines()]

class Login():

	def try_user(self, username, password):
		# check user exists
		registered_user = User.query.filter_by(username=username).first()
		if registered_user is None:
			return False, "Username or password incorrect"
		else:
			if registered_user.check_password(password):
				# log them in
				login_user(registered_user)
				# redirect them to the main page
				resp = make_response(redirect(url_for('game.blueprint.map')))
				# set their user level to basic
				resp.set_cookie('user_level',"Basic")
				return True, resp
			else:
				return False, "Username or password incorrect"

	def get_team_required(self):
		try: 
			# if team required config value set in db
			team_required = Config.query.filter(Config.key=="team_required").first().value
			return False if team_required == "False" else True
		except:
			return True

	def get_team(self, team_code, username):
		# get team with that team code
		team = Team.query.filter_by(team_code=team_code).first()
		# if the team exists
		if team is None:
			if not self.get_team_required():
				# if a team is not required
				# make the user their own team
				# check team with that name doesnt exist
				team = Team.query.filter_by(team_name=username).first()					
				if team:
					# if team with that username already exists
					raise Exception("Team '%s' already exists" % username)
				else:
					# make new team
					team = Team(team_name=username)
					db.session.add(team)
					db.session.commit()
					db.session.flush()			
			else:
				# if a team is required
				# and team with that code doesn't exist
				raise Exception("Team with code '%s' doesn't exist" % team_code)
		return team

	def register_user(self, username, password, email, team_code):
		# check user exists
		registered_user = User.query.filter_by(username=username).first()
		email_exists = User.query.filter_by(email=email).first()
		if registered_user is None:
			if email_exists is None:
				try:
					team = self.get_team(team_code, username)
					# now make the new user
					new_user = User(username, password, email, team)
					db.session.add(new_user)
					db.session.commit()
					db.session.flush()
					# log them in
					login_user(new_user)
					# redirect them to the main page
					resp = make_response(redirect(url_for('game.blueprint.map')))
					# set their user level to basic
					resp.set_cookie('user_level',"Basic")
					return True, resp								
				except Exception as e:
					return False, str(e)
			else:
				return False, "User with email '%s' already exists"	% email
		else:
			return False, "Username '%s' is already taken" % username	

	def check_username_and_password(self, username, password, confirm_password):
		# if its a not good username
		if username in username_blacklist:
			# current_app.logger.info("USERNAME IN BLACKLIST: " + username)		
			return False, "Please choose a suitable username"
		# if the username is blank
		if username.strip() == "":
			# current_app.logger.info("USERNAME BLANK")		
			return False, "Username can't be blank"
		# check passwords the same
		if password != confirm_password:
			# current_app.logger.info("PASSWORDS NO MATCH")
			return False, "Those passwords do not match"
		# check password blank
		if password.strip() == "":
			# current_app.logger.info("PASSWORD BLANK")
			return False, "Password can't be blank"
		# if all succeed return true
		return True,""

