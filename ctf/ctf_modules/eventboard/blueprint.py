from flask import current_app, Blueprint, request, render_template, jsonify
from ctf.models import Team, Scores, Event, Challenge, db, Config
from ctf import themes
import os

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
		## the name of the blueprint will be the name of the module, eg, projects.blueprint
		bp = Blueprint(self.__module__,__name__)

		@current_app.context_processor
		def utility_processor():
			def get_eventboard_theme():
				try: 
					return Config.query.filter(Config.key=="eventboard_theme").first().value
				except:	return "purple modern"
			def list_team_icons():
		                ## set a random logo from the logo directory
				try: return os.listdir("app/static/img/icons")
				except: return []
			def list_team_sounds():
		                ## set a random logo from the logo directory
				try: return os.listdir("app/static/sounds")
				except: return []
			return(dict(event_get_eventboard_theme=get_eventboard_theme, list_team_icons=list_team_icons, list_team_sounds=list_team_sounds))

		@bp.route('/eventboard')
		def eventboard_main():
			
			## get the scores over time for each team
			score_history = {}
			score_history["time"] = list(dict.fromkeys([time[0].strftime("%I:%M %p") for time in db.session.query(Scores.time).order_by(Scores.time.asc())]))
			score_times = db.session.query(Scores).order_by(Scores.time.asc()).distinct().all()
			all_teams = db.session.query(Team).filter(Team.team_name!="Administrators").all()
			score_history["teams"] = {}
			# for each team
			for team in all_teams:
				# add team to dictionary
				score_history["teams"][team.team_name] = {}
				score_history["teams"][team.team_name]["color"] = team.color
				score_history["teams"][team.team_name]["score"] = []
				# for each time in the time list
				for time in score_times:
					# get the score of that team at that time
					score_at_time = db.session.query(Scores).filter(Scores.team_id==team.id).filter(Scores.time==time.time).first()
					if score_at_time:
						score_history["teams"][team.team_name]["score"].append(score_at_time.score)

				# [score[0] for score in db.session.query(Scores.score).filter(Scores.team_id==team.id).order_by(Scores.time.asc()).all()]
			max_score = db.session.query(Team.total_points).order_by(Team.total_points.desc()).first()[0]

			## get the leaderboard
			teams = db.session.query(Team).order_by(Team.total_points.desc())
			
			leaderboard = []
			for t in teams:
				if t.team_name != "Administrators":
					te = {}
					te["team_name"] = t.team_name
					te["score"] = t.total_points
					te["logo"] = t.logo
					leaderboard.append(te)

			## get the events 
			events = db.session.query(Event).order_by(Event.id.desc()).all()
			events_list = []
			for e in events:
				ed = {}
				ed["team_name"] = Team.query.get(e.team_id).team_name
				ed["team_logo"] = Team.query.get(e.team_id).logo
				ed["team_color"] = Team.query.get(e.team_id).color
				ed["challenge_name"] = Challenge.query.get(e.challenge_id).name
				ed["points"] = Challenge.query.get(e.challenge_id).points
				events_list.append(ed)

			return render_template("eventboard.html", events=events_list, score_history=score_history, max_score=max_score, leaderboard=leaderboard)

		return bp
