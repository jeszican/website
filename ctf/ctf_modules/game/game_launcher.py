from ctf.models import Challenge_to_Url, Config, db, Challenge_Launch_Log, Challenge
from flask_login import current_user

class GameLauncher():

	def already_running(self, current_team, challenge):
		r_2_c = Challenge_to_Url.query.filter_by(challenge_id=challenge.id).filter_by(team_id=current_user.team_id).all()
		# return false if they dont already have a challenge to url of this challenge
		return False if len(r_2_c) == 0 else True			

	def not_reached_limit(self, current_team, challenge):
		try: challenge_limit = Config.query.filter(Config.key=="challenge_limit").first().value
		except: challenge_limit = 3 # default is 3
		rs_2_cs = Challenge_to_Url.query.filter(Challenge_to_Url.team_id == current_user.team_id).all()
		# return false if they are under the challenge limit
		return False if len(rs_2_cs) < int(challenge_limit) else True			

	def launch_challenge(self, current_team, challenge):
		from ctf.ctf_factory import celery
		# add challenge url to database
		new_url_to_chal = Challenge_to_Url(challenge_id=challenge.id,team_id=current_team.id,challenge_address="launching",message="Queued.")
		db.session.add(new_url_to_chal)
		# put it into the launch log
		launch_record = Challenge_Launch_Log(challenge_id=challenge.id,team_id=current_team.id)
		db.session.add(launch_record)
		# update db
		db.session.commit()
		db.session.flush()	
		# run the task here
		task_id = celery.send_task("launch_challenge", args=(current_team.id, challenge.id), queue='launching_queue')

	def kill_challenge(self, current_team, challenge):
		from ctf.ctf_factory import celery
		# remove challenge url from database
		r_2_cs = Challenge_to_Url.query.filter_by(team_id=current_team.id).filter_by(challenge_id=challenge.id).all()
		for r_2_c in r_2_cs:
			if r_2_c.challenge_address != "launching":
				# get challenge from r2c
				challenge = Challenge.query.get(r_2_c.challenge_id)
				# run task here
				task_id = celery.send_task("kill_challenge", args=(challenge.country_code,r_2_c.remote_id,current_team.id,r_2_c.region), queue='killing_queue')

	def killall_challenges(self, current_team):
		from ctf.ctf_factory import celery
		# get all challenges for this team
		r_2_cs = Challenge_to_Url.query.filter_by(team_id=current_team.id).all()
		for r_2_c in r_2_cs:
			if r_2_c.challenge_address != "launching":
				# get challenge from r2c
				challenge = Challenge.query.get(r_2_c.challenge_id)
				# run the task here
				task_id = celery.send_task("kill_challenge", args=(challenge.country_code,r_2_c.remote_id,current_team.id,r_2_c.region), queue='killing_queue')
