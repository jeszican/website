from ctf.models import Team, Challenge, Announcement, Challenge_Resources, Event, Challenge_to_Url, Config, User, Scores, team_completion_log, user_completion_log, db
from flask import current_app
from flask_login import current_user
from os import listdir, getcwd, mkdir
from shutil import move, copyfile, rmtree
from ctf.ctf_modules.game.game import Game
from os.path import isfile, join, isdir, exists
from ctf import themes
import random, string
from datetime import datetime, timedelta
import json
from .countries import ccs
from git import Repo

class Admin():

	def get_all_challenges(self):
		# if challenge directory doesn't exist
		if exists("./challenges"):
			directory = "./challenges"
			challenge_sets = sorted([join(directory, o).split("/")[-1] for o in listdir(directory) if isdir(join(directory,o))])
			return challenge_sets
		else: return []

	def purge_challenge_folder(self, request):
		try:
			if exists("./challenges"): rmtree("./challenges")	
		except Exception as e: return {"error":str(e)}

	def clone_challenges(self, url):
		# create challenge directory if not there
		if not exists("./challenges"): mkdir("./challenges")	
		# delete challenge tmp directory 
		if exists("./challenges_tmp"): rmtree("./challenges_tmp")	
		# if theres already a cloned repo
		tmp = "./challenges_tmp"
		# clone it to a tmp directory
		Repo.clone_from(url, tmp)
		# move the contents to the challenges folder
		contents = listdir(tmp)
		for f in contents:
			if f != ".git":
				move(tmp+"/"+f, "./challenges/"+f)
		# delete challenge tmp directory 
		if exists("./challenges_tmp"): rmtree("./challenges_tmp")		

	def clone_challenge_repository(self, request):
		from ctf.ctf_factory import celery
		try:  
			# create challenge directory if not there
			self.clone_challenges(request.form["url"])
			# also make sure the celerys clone the challenges
			task_id = celery.send_task("clone_challenges", args=(request.form["url"],), queue='launching_queue')
			return {"reload":True}
		except Exception as e: return {"error":str(e)}

	def set_docker_ctf(self, request):
		# reverse it, because its NOT a remote ctf
		remote = Config.query.filter(Config.key=="remote").first()
		if remote:
			remote.value = "False" if request.form["remote"] == "True" else "True"
		else:
			# if its not there add it
			remote = Config(key="remote", value="False" if request.form["remote"] == "True" else "True")
		db.session.add(remote)
		db.session.commit()
		db.session.flush()

	def set_challenge_limit(self, request):
		# is a team required to sign up, or is it a free for all of users
		challenge_limit = Config.query.filter(Config.key=="challenge_limit").first()
		if challenge_limit:
			challenge_limit.value = request.form["challenge_limit"]
		else:
			# if its not there add it
			challenge_limit = Config(key="challenge_limit", value=request.form["challenge_limit"])
		db.session.add(challenge_limit)
		db.session.commit()
		db.session.flush()

	def get_ctf_begun(self):
		return Config.query.filter(Config.key=="ctf_begun").first()

	def set_ctf_begun(self, request):
		# is a team required to sign up, or is it a free for all of users
		begun = Config.query.filter(Config.key=="ctf_begun").first()
		if begun:
			begun.value = request.form["begun"]
		else:
			# if its not there add it
			begun = Config(key="ctf_begun", value=request.form["begun"])
		db.session.add(begun)
		db.session.commit()
		db.session.flush()
		return {"reload":True}

	def make_team(self, request):
		# make a team
		existing_team = Team.query.filter(Team.team_name==request.form["team_name"]).first()
		if existing_team is None:
			new_team = Team(team_name=request.form["team_name"])
			db.session.add(new_team)
			db.session.commit()
			db.session.flush()
			current_app.logger.info("%s invite code: %s " % (new_team.team_name, new_team.team_code))		
		return {"reload":True}

	def assign_random_country(self):
		# get countries in use 
		countries_in_use = Challenge.query.with_entities(Challenge.country_code).all()
		countries_in_use = [cc[0] for cc in countries_in_use]
		# select one from the countries list
		countries_not_in_use = [cc for cc in ccs if cc not in countries_in_use]
		# take random country
		cc = random.choice(countries_not_in_use)
		return cc

	def give_points_to_team(self, request):
		points = request.form["points"]
		reason = request.form["reason"]
		team_name = request.form["team_name"]
		existing_team = Team.query.filter(Team.team_name==team_name).first()
		if existing_team:
			# if team exists give them the points
			existing_team.total_points = existing_team.total_points + int(points)
			# update db immediately
			db.session.commit()
			db.session.flush()
			# send them the points awarded
			current_app.config["SSE"].publish({"points":points,"reason":reason}, type="points_awarded", channel=team_name)
			## update the total points to TEAM
			current_app.config["SSE"].publish({"points":existing_team.total_points}, type="points_update", channel=team_name)

	def load_challenges(self, request):
		try:
			# load challenges into the platform
			path_to_challenges = getcwd()+"/challenges/"+request.form["challenge_set"]
			# get the folder full of challenges to load
			challenges = [f for f in listdir(path_to_challenges) if isfile(join(path_to_challenges, f))]
			for challenge in challenges:
				# only if its a json file
				if challenge.endswith(".json"):
					try:
						with open(join(path_to_challenges, challenge)) as f:
							# open the file
							# load the json
							data = json.load(f)
							# if the challenge ISN'T a multiple choice
							# remove the flag penalty
							data["flag_penalty"] = data["flag_penalty"] if data["type"] == "multiple" else 0
							# create the db object
							# if the country code isn't assigned in the json
							if "country_code" not in data:
								data["country_code"] = self.assign_random_country()
							# if the challenge has a corresponding docker image in the repository
							if "docker_image" in data:
								# check if its a remote ctf
								try: remote = Config.query.filter_by(key="remote").first().value
								except: remote = "False"
								if remote == "True":
									# set the docker_file to this
									# images are pulled from the repository
									data["docker_file"] = data["docker_image"]
								else:
									if "docker_file" in data:
										# if its not remote then use the docker file path to build fresh
										# on local
										data["docker_file"] = join(path_to_challenges)
							else:
								# if not corresponding docker image
								if "docker_file" in data:
									data["docker_file"] = join(path_to_challenges)
							# remove docker image file from dict
							data.pop('docker_image', None)
							# if the challenge has an audio file
							if "audio" in data:
								# copy the audio file into the static challenges file
								path_to_audio = join(path_to_challenges, data["audio"])
								# make a challenge resource
								new_resource = Challenge_Resources(resource_id=''.join(random.choice(string.digits + string.ascii_lowercase) for _ in range(10)),resource_path=path_to_audio)
								db.session.add(new_resource)
								db.session.commit()
								db.session.flush()
								data["audio"] = new_resource.resource_id
							# if theres a downloadable resource
							if "downloadables" in data:
								list_of_downloadables = json.loads(data["downloadables"])
								download_list = []
								for download in list_of_downloadables:
									# copy the audio file into the static challenges file
									path_to_file = join(path_to_challenges, download)
									# make a challenge resource
									new_resource = Challenge_Resources(resource_id=''.join(random.choice(string.digits + string.ascii_lowercase) for _ in range(10)),resource_path=path_to_file)
									db.session.add(new_resource)
									db.session.commit()
									db.session.flush()
									download_list.append(new_resource.resource_id)
								data["downloadables"] = json.dumps(download_list)
							# if the challenge is a timed challenge
							if data["type"] == "timed":
								# make the deadline the amount of hours specified from now	
								data["deadline"] = datetime.now() + timedelta(hours=data["deadline"])
							# add the challenge using the data fields
							db_challenge = Challenge(**data)
							# add the challenge to the db
							db.session.add(db_challenge)
							db.session.flush()
							# get current team from user
							current_team = Team.query.get(current_user.team_id)
							current_app.config["SSE"].publish({"country_code":db_challenge.country_code,"challenge_info":Game().make_challenge_dict(db_challenge, current_team)}, type="country_unlock", channel="ALL")
					except Exception as e:
						current_app.logger.info("%s error: %s " % (challenge, str(e)))		

			db.session.commit()
			db.session.flush()
		except Exception as e: return {"error":str(e)}

	def set_team_required(self, request):
		# is a team required to sign up, or is it a free for all of users
		required = Config.query.filter(Config.key=="team_required").first()
		if required:
			required.value = request.form["team_required"]
		else:
			# if its not there add it
			required = Config(key="team_required", value=request.form["team_required"])
		db.session.add(required)
		db.session.commit()
		db.session.flush()

	def reset_scores(self, request):
		# delete all the scores, events and challenges completed
		teams = Team.query.all()
		users = User.query.all()

		# delete all announcements and events
		announcements = Announcement.query.delete()
		events = Event.query.delete()

		# delete all points, challenges and hints for team
		for team in teams:
			team.total_points = 0
			team.challenges_completed = []
			team.hints_used = []
			# readd modified team
			db.session.add(team)

		# delete all challenges for users
		for user in users:
			user.challenges_completed = []
			db.session.add(user)

		db.session.commit()
		db.session.flush()

	def clear_scores_over_time(self, request):
		# delete all the scores over time
		db.session.query(Scores).delete()
		db.session.commit()
		db.session.flush()

	def delete_challenges_db(self, request):
		# delete all the challenges
		challenges = Challenge.query.all()
		for challenge in challenges:
			db.session.delete(challenge)
		for row in Challenge_to_Url.query.all():
			db.session.delete(row)	
		db.session.commit()
		db.session.flush()

	def set_end_date(self, request):
		# set the end date of the ctf
		end_date = Config.query.filter(Config.key=="end_date").first()
		if end_date:
			end_date.value = request.form["end_date"]
		else:
			# if not there make it
			end_date = Config(key="end_date", value=request.form["end_date"])
		db.session.add(end_date)
		db.session.commit()
		db.session.flush()


	def set_discord_webhook_url(self, request):
		# set the end date of the ctf
		url = Config.query.filter(Config.key=="discord_webhook_url").first()
		if url:
			url.value = request.form["url"]
		else:
			# if not there make it
			url = Config(key="discord_webhook_url", value=request.form["url"])
		db.session.add(url)
		db.session.commit()
		db.session.flush()

	def set_objective(self, request):
		# set the 'welcome to deloitte ctf message'
		objective = Config.query.filter(Config.key=="objective").first()
		if objective:
			objective.value = request.form["objective"]
		else:
			# if not there add it
			objective = Config(key="objective", value=request.form["objective"])
		db.session.add(objective)
		db.session.commit()
		db.session.flush()

	def change_theme(self, request):
		# change the team of the map
		map_theme = Config.query.filter(Config.key=="map_theme").first()
		eventboard_theme = Config.query.filter(Config.key=="eventboard_theme").first()
		# check if its modern or retro
		if "modern" in request.form:
			type = "modern" if request.form["modern"] == "True" else "retro"
		else: type = "retro"
		if map_theme:
			map_theme.value = request.form["map_theme"] + " %s" % type
		else:
			# if not there add it
			map_theme = Config(key="map_theme", value=request.form["map_theme"] + " %s" % type)
		db.session.add(map_theme)

		if eventboard_theme:
			eventboard_theme.value = request.form["eventboard_theme"] + " %s" % type
		else:
			# if not there add it
			eventboard_theme = Config(key="eventboard_theme", value=request.form["eventboard_theme"] + " %s" % type)
		db.session.add(eventboard_theme)

		# set the theme using values from the themes files
		# themes.chosen_eventboard_theme = themes.eventboard_themes[eventboard_theme.value]
		# themes.chosen_map_theme = themes.map_themes[map_theme.value]

		db.session.commit()
		db.session.flush()

	def get_all_teams(self):
		teams = db.session.query(Team).order_by(Team.total_points.desc()).all()
		return teams


