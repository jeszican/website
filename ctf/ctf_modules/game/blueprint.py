from flask import Blueprint, render_template, request, current_app, jsonify, send_from_directory
from flask_login import login_required, current_user
from ctf.models import Team, Config, Challenge, db, Average_Loading_Times, Challenge_to_Url, Challenge_Resources
import html
import json
import datetime
from .game import Game
from .game_launcher import GameLauncher
from ctf import themes
from sqlalchemy import func

class blueprint():

	def get_blueprint(self, socketio):
		bp = self.__make_routes(socketio)
		return bp

	def get_info(self):
		return {}

	def __make_routes(self, socketio):	
		"""
		This function creates and returns the blueprint to the get_blueprint function.
		This function is the function where you add your flask routes and socketio events.
		@return: The flask blueprint with our routes in it.
		"""
		# the name of the blueprint will be the name of the module, eg, projects.blueprint
		bp = Blueprint(self.__module__,__name__)

		# context processor get stuff from here
		@current_app.context_processor
		def utility_processor():
			def get_end_date():
				try: 
					end_date = Config.query.filter(Config.key=="end_date").first().value
					return datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M").strftime("%a %B %d %Y %H:%M:%S GMT+0000")
				except: return ""
			def get_objective():
				try: return Config.query.filter(Config.key=="objective").first().value
				except: return ""
			def get_announcements():
				try: return Game().get_announcements()
				except: return []
			def get_gameboard_theme():
				try: 
					return Config.query.filter(Config.key=="map_theme").first().value
				except:	return "purple modern"
			return(dict(game_get_end_date=get_end_date,game_get_objective=get_objective,game_get_announcements=get_announcements,game_get_gameboard_theme=get_gameboard_theme))

		# the challenge resources route
		@bp.route('/challenge_resource/<resource_id>', methods=["GET"])
		@login_required
		def get_challenge_resource(resource_id):
			resource = Challenge_Resources.query.filter_by(resource_id=resource_id).first()
			if resource:
				resource_path = resource.resource_path
				return send_from_directory('/'.join(resource_path.split("/")[:-1]),resource_path.split("/")[-1])

		# the average launch times route
		@bp.route('/get_average_launch_time/<challenge_id>')
		@login_required
		def get_average_launch_time(challenge_id):
			challenge_name = ''.join(e for e in Challenge.query.get(challenge_id).name if e.isalnum())
			## get the average of all the launch times
			average = db.session.query(func.avg(Average_Loading_Times.time).label('average')).filter_by(challenge_name=challenge_name).scalar()
			## if there are none make it 0
			if average == None:
				average = 0
			return jsonify(int(round(average)))

		# the map route
		@bp.route('/', methods=["GET","POST"])
		@login_required
		def map():
			# this user level determines whether they get to see the secret language
			user_level = request.cookies.get('user_level')
			# get team user is in
			current_team = Team.query.get(current_user.team_id)
			# only if the ctf is begun
			begun = Config.query.filter(Config.key=="ctf_begun").first()
			if begun:
				if begun.value == "True":
					# get the challenges and their countries for this team
					countries_to_challenges = Game().get_countries_to_challenges(current_team, user_level)
				else:
					countries_to_challenges = {}
			else:
				countries_to_challenges = {}
			# organize the team information
			team = {}
			team["total_points"] = current_team.total_points
			team["team_name"] = current_team.team_name
			# render the template with the challenge information
			return render_template("map.html", countries_to_challenges_non_json=countries_to_challenges, countries_to_challenges=json.dumps(countries_to_challenges), current_team=team)

		# the launch route
		@bp.route('/launch', methods=["POST"])
		@login_required
		def launch_challenge():
			## get current team
			current_team = Team.query.get(current_user.team_id)
			## get challenge from id
			challenge = Challenge.query.get(request.form["challenge_id"])
			if challenge.type != "timed":
				# if haven't already got running
				if not GameLauncher().already_running(current_team, challenge):
					# if team hasn't reached limit
					if not GameLauncher().not_reached_limit(current_team, challenge):
						# launch challenge
						GameLauncher().launch_challenge(current_team, challenge)
					else:
						current_app.config["SSE"].publish({"message":"You have the maximum number of challenges running already!"}, type="dialog", channel=current_user.username)
						current_app.config["SSE"].publish({"country_code":challenge.country_code}, type="country_failed", channel=current_team.team_name)
				else:
					current_app.config["SSE"].publish({"message":"You have an instance of this challenge running already!"}, type="dialog", channel=current_user.username)
					current_app.config["SSE"].publish({"country_code":challenge.country_code}, type="country_failed", channel=current_team.team_name)
			else:
				current_app.config["SSE"].publish({"message":"This type of challenge is unlaunchable."}, type="dialog", channel=current_user.username)
				current_app.config["SSE"].publish({"country_code":challenge.country_code}, type="country_failed", channel=current_team.team_name)

			return jsonify({"success":True})

		# the kill route
		@bp.route('/kill', methods=["POST"])
		@login_required
		def kill_challenge():
			## get current team
			current_team = Team.query.get(current_user.team_id)
			## get challenge from id
			challenge = Challenge.query.get(request.form["challenge_id"])
			## if they have this challenge running
			r_2_c = Challenge_to_Url.query.filter_by(challenge_id=challenge.id, team_id=current_team.id).first()
			if r_2_c: GameLauncher().kill_challenge(current_team, challenge) 
			else:
				# if they dont just say no and publish it to TEAM back to normal
				current_app.config["SSE"].publish({"message":"You don't have an instance of this challenge running!"}, type="dialog", channel=current_user.username)
				current_app.config["SSE"].publish({"country_code":challenge.country_code}, type="country_killed", channel=current_team.team_name)
			return jsonify({"success":True})

		# the kill route
		@bp.route('/killall', methods=["POST"])
		@login_required
		def killall_challenges():
			## get current team
			current_team = Team.query.get(current_user.team_id)
			GameLauncher().killall_challenges(current_team)
			return jsonify({"success":True})

		# the route to get the currently running
		@bp.route('/running')
		@login_required
		def get_running():
			instances = []
			## get the running instances
			r_2_c = Challenge_to_Url.query.filter_by(team_id=current_user.team_id).all()
			for ins in r_2_c:
				## get the challenge url
				chal = Challenge.query.get(ins.challenge_id)
				instances.append({"challenge_name":chal.name, "url":ins.challenge_address, "message":ins.message, "challenge_id":chal.id, "country_code":chal.country_code})
			return jsonify(instances)

		# the hint route
		@bp.route('/hint', methods=["POST"])
		@login_required
		def buy_hint():
			## get current team
			current_team = Team.query.get(current_user.team_id)
			## get challenge from id
			challenge = Challenge.query.get(request.form["challenge_id"])
			## check hint already bought
			if not Game().hint_already_bought(current_team, challenge):
				## buy hint
				Game().buy_hint(current_team, challenge)
				return jsonify({"success":True})
			else:
				## return already bought to USER
				current_app.config["SSE"].publish({"message":"You already own this hint!"}, type="dialog", channel=current_user.username)
				return jsonify({"success":False, "message":"You already own this hint!"})

		@bp.route('/scores')
		@login_required
		def get_scores():
			## get the latest scores
			teams = db.session.query(Team).order_by(Team.total_points.desc())
			scores = []
			for t in teams:
				# dont include the administrators team
				if t.team_name != "Administrators":
					te = {}
					# organise them into a dict
					te["team_name"] = html.escape(t.team_name)
					te["score"] = t.total_points
					te["logo"] = t.logo
					scores.append(te)

			return jsonify(scores)

		# the map route
		@bp.route('/submit', methods=["POST"])
		@login_required
		def submit_flag():
			## get flag
			flag = request.form["flag"]
			print(request.form)
			## get the team
			current_team = Team.query.get(current_user.team_id)
			## get the challenge
			challenge = Challenge.query.get(request.form["challenge_id"])
			if not Game().is_already_completed(current_team, challenge):
				if challenge.type == "practice":
					if Game().check_practice_flag(flag, current_team):
						# we send through the correct flag
						Game().do_flag_correct(current_team, challenge)
						return jsonify({"success":True})
					else:
						Game().do_flag_incorrect(current_team, challenge)
						return jsonify({"success":False})
				elif challenge.type == "timed":
					current_app.config["SSE"].publish({"message":"You can't submit a flag for a timed challenge!"}, type="dialog", channel=current_user.username)
					## return already complete to USER
					return jsonify({"success":False, "message":"You can't submit a flag for a timed challenge!"})
				elif challenge.type == "timed,upload":
					# get the file
					upload = request.files["upload"]
					# do file upload
					Game().do_submission(current_team, challenge, upload)
					return jsonify({"success":True})
				elif challenge.type == "upload":
					# get the file
					upload = request.files["upload"]
					# do file upload
					Game().do_submission(current_team, challenge, upload)
					return jsonify({"success":True})
				else:
					if challenge.check_flag(flag):
						# if the flag is correct
						Game().do_flag_correct(current_team, challenge)
						return jsonify({"success":True})
					else:
						# if the flag is wrong
						Game().do_flag_incorrect(current_team, challenge)
						return jsonify({"success":False})
			else:
				current_app.config["SSE"].publish({"message":"You have already completed this challenge!"}, type="dialog", channel=current_user.username)
				## return already complete to USER
				return jsonify({"success":False, "message":"You have already completed this challenge!"})

		return bp
