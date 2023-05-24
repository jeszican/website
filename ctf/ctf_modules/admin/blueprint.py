from flask import current_app, Blueprint, request, render_template, jsonify
from flask_login import login_required, current_user
from ctf.models import Team
import json
from .admin import Admin
import os

class blueprint():

	def get_blueprint(self, socketio):
		bp = self.__make_routes()
		return bp

	def get_info(self):
		return {
			"functions":{
				# this functions are the ones in admin.py that should be callable from the webapp
				"make_team": {
					"fields" : [
						{"field_name":"team_name", "type":"text", "description":"What is the new teams name?"} 
					],
				},
				"give_points_to_team":{
					"fields" : [
						{"field_name":"team_name","type":"select", "data":[t.team_name for t in Admin().get_all_teams()], "description":"Does a team deserve points for whatever reason?"},
						{"field_name":"points","type":"text"},
						{"field_name":"reason","type":"text"},
					],
				},
				"set_team_required": {
					"fields" : [
						{"field_name":"team_required","type":"radio","description":"Is a team required to sign up?"}
					]
				},				
				"clone_challenge_repository": {
					"fields" : [
						{"field_name":"url","type":"text","description":"If the repo isn't public, remember to include the username:password!"}
					]
				},	
				"load_challenges": {
					"fields" : [
						{"field_name":"challenge_set","type":"select","data":Admin().get_all_challenges()}
					]
				},
				"set_challenge_limit": {
					"fields" : [
						{"field_name":"challenge_limit","type":"text", "description":"How many challenges can a team run at a time?"} 
					],
				},
				"set_docker_ctf": {
					"fields" : [
						{"field_name":"remote","type":"radio","description":"Is this instance for challenge development?"} 
					],
				},
				"set_discord_webhook_url": {
					"fields" : [
						{"field_name":"url","type":"text","description":"The webhook url for your discord channel"} 
					],
				},
				"set_ctf_begun": {
					"fields" : [
						{"field_name":"begun","type":"radio","description":"Should challenges be visible?"} 
					],
				},
				"set_end_date":{
					"fields":[
						{"field_name":"end_date", "type":"datetime", "description":"When should the CTF end?"}
					]
				},
				"set_objective": {
					"fields" : [
						{"field_name":"objective","type":"text", "description":"This message appears in the top bar of the map"} 
					],
				},
				"change_theme": {
					"fields" : [
						{"field_name":"map_theme","type":"select","data":["purple","green"], "description":"The map theme:"},
						{"field_name":"eventboard_theme","type":"select","data":["purple","green"], "description":"The eventboard theme:"},
						{"field_name":"modern","type":"radio","description":"Do you want it to be mordern theme?"}
					]
				},
				"reset_game" :{
					"type": "group", 
					"functions" : {
						"reset_scores": {"fields":[]},
						"clear_scores_over_time":{"fields":[]},
						"delete_challenges_db":{"fields":[]},
						"purge_challenge_folder": {"fields":[]},
					}
				}	
			}
		}

	def __make_routes(self):
		"""
		This function creates and returns the blueprint to the get_blueprint function.
		This function is the function where you add your flask routes and socketio events.
		@return: The flask blueprint with our routes in it.
		"""
		## the name of the blueprint will be the name of the module, eg, projects.blueprint
		bp = Blueprint(self.__module__,__name__)

		@current_app.context_processor
		def utility_processor():
			def get_all_teams():
				try: return Admin().get_all_teams()
				except: return []
			def get_all_functions():
				try: return self.get_info()["functions"]
				except: return {}
			def list_team_icons():
				try: return os.listdir("ctf/static/img/icons")
				except: return []
			def list_team_sounds():
				try: return os.listdir("ctf/static/flags")
				except: return []
			def get_ctf_begun():
				try: return True if Admin().get_ctf_begun().value == "True" else False
				except: return False
			return(dict(admin_get_ctf_begun=get_ctf_begun,admin_get_all_teams=get_all_teams,admin_list_team_icons=list_team_icons,admin_list_team_sounds=list_team_sounds,admin_get_all_functions=get_all_functions))

		@bp.route('/admin', methods=["GET","POST"])
		@login_required
		def admin_page():
			# get team user is in
			current_team = Team.query.get(current_user.team_id)
			# check they in admin team
			if current_team.team_name == "Administrators":
				# only if they are on the administrator team can they post
				if request.method == "POST":
					# call the corresponding function in the admin module
					function_to_call = getattr(Admin(),request.form["action"])
					data = function_to_call(request)
					# return any data returned
					return jsonify(data if data != None else {})
				else:
					# if get return admin dashboard
					return render_template("admin.html")
			else:
				# if they aren't admin kick them out
				abort(403)

		return bp
