from ctf.models import Challenge, Announcement, Challenge_to_Url, Config, Event, db
from flask_login import current_user
from flask import current_app
from .email import Email
from discord_webhook import DiscordWebhook
import json

class Game():

	# webhook_url = "https://discordapp.com/api/webhooks/732983319335141386/B8JJjTxrooUq8Fn1KNFuJdPBZ3zV2MMhoF1HdHJ3lrc9NPlQFl8Ip0sNZoqZa8-pGohY"

	def do_flag_incorrect(self, current_team, challenge):
		## do the user flag penalty
		## this is only set for multiple choice questions
		current_team.total_points = int(current_team.total_points) - int(challenge.flag_penalty)
		## update the db immediately
		db.session.commit()
		db.session.flush()
		## log the incurred flag penalty
		current_app.logger.info("%s flag penalty: '%s' - %d" % (current_team.team_name, challenge.name, challenge.flag_penalty))
		## update the total points to TEAM
		current_app.config["SSE"].publish({"points":current_team.total_points}, type="points_update", channel=current_team.team_name)
		## send the wrong message to the USER
		current_app.config["SSE"].publish({"country_code":challenge.country_code}, type="country_flag_wrong", channel=current_user.username)

	def do_submission(self, current_team, challenge, upload):
		## add the challenge to the users and teams completed
		current_team.challenges_completed.append(challenge)
		current_user.challenges_completed.append(challenge)
		## commit and update db immediately
		db.session.commit()
		db.session.flush()
		## send the upload to the marker
		Email().send_submission(current_team, challenge, upload)
		## send a completed message to the log
		current_app.logger.info("%s submitted: %s" % (current_team.team_name, challenge.name))
		## if its the first blood set the color
		self.if_firstblood_set(current_team, challenge)
		## send out country completed by message to ALL
		current_app.config["SSE"].publish({"country_code":challenge.country_code, "team":current_team.team_name}, type="country_completed_by", channel="ALL")
		## send back correct message to TEAM
		current_app.config["SSE"].publish({"country_code":challenge.country_code, "flag":challenge.flag}, type="country_complete", channel=current_team.team_name)
		## send back announcement
		self.do_unlocked_challenges(current_team, challenge)

	def do_flag_correct(self, current_team, challenge):
		## add the challenge to the users and teams completed
		current_team.challenges_completed.append(challenge)
		current_user.challenges_completed.append(challenge)
		## commit and update db immediately
		db.session.commit()
		db.session.flush()
		## update total points
		current_team.total_points = int(current_team.total_points) + int(challenge.points)
		current_app.logger.info("%s completed: %s + %d" % (current_team.team_name, challenge.name, challenge.points))
		## update the db immediately
		db.session.commit()
		db.session.flush()
		## if its the first blood set the color
		self.if_firstblood_set(current_team, challenge)
		## send out country completed by message to ALL
		current_app.config["SSE"].publish({"country_code":challenge.country_code, "team":current_team.team_name}, type="country_completed_by", channel="ALL")
		## send back correct message to TEAM
		current_app.config["SSE"].publish({"country_code":challenge.country_code, "flag":challenge.flag}, type="country_complete", channel=current_team.team_name)
		## update the total points to TEAM
		current_app.config["SSE"].publish({"points":current_team.total_points}, type="points_update", channel=current_team.team_name)
		## send back announcement
		self.do_announcement(current_team, challenge)
		self.do_event_for_eventboard(current_team, challenge)
		self.do_unlocked_challenges(current_team, challenge)

	def do_unlocked_challenges(self, current_team, challenge):
		## get next challenges to unlock
		next_challenges = db.session.query(Challenge).filter(Challenge.depends_on==challenge.country_code).all()
		for nc in next_challenges:
			# for each one push it to the TEAM 
			current_app.config["SSE"].publish({"country_code":nc.country_code,"challenge_info":Game().make_challenge_dict(nc, current_team)}, type="country_unlock", channel=current_team.team_name)

	def do_event_for_eventboard(self, current_team, challenge):
		# create new event obj
		event = Event(team_id=current_team.id, challenge_id=challenge.id)
		# send the event to the eventboard!
		current_app.config["SSE"].publish({"challenge_name":challenge.name,"team_name":current_team.team_name,"team_logo":current_team.logo,"points":challenge.points,"team_sound":"/static/sounds/"+current_team.sound,"team_color":current_team.color}, type="team_event", channel="EVENTS")
		# update the db immediately
		db.session.add(event)
		db.session.commit()
		db.session.flush()
		## if ALL last three team events have been by this team
		# publish a flag streak
		last_two_events = db.session.query(Event).order_by(Event.id.desc()).limit(2).all()
		if len(last_two_events) >= 2:
			if last_two_events[0].team_id == current_team.id:
				if last_two_events[1].team_id == current_team.id:
					# count up how many flags in a row
					last_events = db.session.query(Event).filter(Event.team_id==current_team.id).order_by(Event.id.desc()).all()
					previous_event_id = last_events[0].id
					count = 2
					for event in last_events[1:]:
						event_id_minus = event.id + 1
						if previous_event_id == event_id_minus:
							count = count + 1
							previous_event_id = event.id
						else:
							break
					current_app.config["SSE"].publish({"team_name":current_team.team_name.lower(),"count":str(count), "team_color":current_team.color}, type="team_flag_streak", channel="EVENTS")

	def do_announcement(self, current_team, challenge):
		# create new announcement obj
		announcement = Announcement(announcement="%s has completed '%s'" % (current_team.team_name, challenge.name))
		# update the db immediately
		db.session.add(announcement)
		db.session.commit()
		db.session.flush()
		# publish the announcement
		current_app.config["SSE"].publish({"time":announcement.time.strftime("%a %d %B %-I:%M%p:"), "announcement":announcement.announcement}, type="announcement", channel="ALL")
		# execute the discord announcement
		Game().execute_announcement(current_team.team_name, challenge.name, challenge.points)

	def execute_announcement(self, team_name, challenge_name, points):
		# do discord web hook
		try: 
			# there might nont be onen set up
			webhook_url = Config.query.filter(Config.key=="discord_webhook_url").first().value
			webhook = DiscordWebhook(url=webhook_url, content="Team '%s' has completed '%s' for %d points!" % (team_name, challenge_name, points))
			webhook.execute()
		except: pass
				
	def if_firstblood_set(self, current_team, challenge):
		# if no other team have completed this challenge
		if len(challenge.teams_completed) == 1:
			# set the color of the country
			challenge.color = current_team.color
			# give the team an extra 25 points
			current_team.total_points = int(current_team.total_points) + int(25)
			# update the db immediately
			db.session.commit()
			db.session.flush()
			# echo the color change to ALL the maps
			current_app.config["SSE"].publish({"country_code":challenge.country_code, "color":current_team.color}, type="country_color_change", channel="ALL")

	def buy_hint(self, current_team, challenge):
		## get current eventboard price
		current_app.logger.info("%s hint bought: '%s' - %d" % (current_team.team_name, challenge.name, challenge.hint_penalty))
		## add the challenge to the teams bought hints
		current_team.hints_used.append(challenge)
		## minus the hint penalty
		current_team.total_points = int(current_team.total_points) - int(challenge.hint_penalty)
		# update the db immediately
		db.session.commit()
		db.session.flush()
		# send point update to TEAM
		current_app.config["SSE"].publish({"points":current_team.total_points}, type="points_update", channel=current_team.team_name)
		# publish the hint to the TEAM
		current_app.config["SSE"].publish({"hint":challenge.hint,"country_code":challenge.country_code}, type="hint_bought", channel=current_team.team_name)
		
	def hint_already_bought(self, current_team, challenge):
		# return false if the challenge hint has not already been bought by the team
		return False if challenge not in current_team.hints_used else True

	def is_already_completed(self, current_team, challenge):
		# return false if the challenge has already been completed by the team
		return False if challenge not in current_team.challenges_completed else True

	def check_pratice_flag(self, flag, current_team):
		# return true if the flag matches the team code
		return True if flag.strip() == current_team.team_code.strip() else False

	def make_challenge_dict(self, challenge, current_team):
		## this function creates the dictionary out of the challenge db object
		chal = {}
		chal["id"] = challenge.id
		chal["name"] = challenge.name
		
		## if the challenge as a color 
		if challenge.color:
			chal["color"] = challenge.color

		## if the challenge has links
		if challenge.links:
			## check the list isn't empty
			if (len(json.loads(challenge.links)) > 0):
				chal["links"] = challenge.links
		
		## if the challenge has a dockerfile its launchable
		if challenge.docker_file:
			chal["launchable"] = True

		# if challenge has a deadline format it correctly for js
		if challenge.deadline:
			chal["deadline"] = challenge.deadline.strftime("%a %B %d %Y %H:%M:%S GMT+0000")

		## if the challenge has an ansible playbook its launchable
		if challenge.ami:
			chal["launchable"] = True

		## if the challenge has audio
		if challenge.audio:
			chal["audio"] = challenge.audio

		## if the challenge has a downloadable
		if challenge.downloadables:
			## check the list isn't empty
			if (len(json.loads(challenge.downloadables)) > 0):
				chal["downloadables"] = challenge.downloadables

		chal["description"] = challenge.description

		## if the team already bought the hint
		## the hint should be shown
		if challenge in current_team.hints_used:
			chal["hint"] = challenge.hint

		## if the team already completed the challenge
		## the flag should be shown
		if challenge in current_team.challenges_completed:
			chal["complete"] = True
			chal["flag"] = challenge.flag

		## if the team already has an instance of this challenge running
		r_2_c = Challenge_to_Url.query.filter_by(challenge_id=challenge.id, team_id=current_user.team_id).first()
		if r_2_c:
			# if its a web challenge
			if "http" in r_2_c.challenge_address:
				chal["challenge_url"] = "/challenge/" + r_2_c.container_id
			else:
				chal["challenge_url"] = r_2_c.challenge_address

		chal["teams_completed"] = sorted([t.team_name for t in challenge.teams_completed])
		chal["points"] = challenge.points
		chal["type"] = challenge.type

		## if its a multiple choice
		if challenge.type == "multiple":
			chal["a"] = challenge.a
			chal["b"] = challenge.b
			chal["c"] = challenge.c
			chal["d"] = challenge.d
		
		chal["flag_penalty"] = challenge.flag_penalty 		
		chal["hint_penalty"] = challenge.hint_penalty
		chal["category"] = challenge.category

		return chal

	def get_countries_to_challenges(self, current_team, user_level):
		# get all challenges from the db
		challenges = db.session.query(Challenge).all()
		# put them into a dictionary of country codes
		countries_to_challenges = {}
		# for each challenge
		for challenge in challenges:
			# default dont show
			show = False
			# if the challege is ann advance challennge
			if challenge.advanced == 1:
				# dont show the hidden timed ones
				if not challenge.hidden:
					# ONLY ADD IF THE USER LEVEL IS SET TO ADVANCED
					if user_level == "Advanced":
						if (challenge.depends_on) and (challenge.depends_on.strip() != ""):
							# if the challenge depends on another challenge
							# check that challenge is completed first
							previous_challenge = db.session.query(Challenge).filter(Challenge.country_code==challenge.depends_on).one()
							if previous_challenge in current_team.challenges_completed:
								show = True
						else:
						# if it doesn't depend on any others just add it to the dict
							show = True
			# if its not an advanced challenge show it
			else:
				# dont show the hidden timed ones
				if not challenge.hidden:				
					if (challenge.depends_on) and (challenge.depends_on.strip() != ""):
						# if the challenge depends on another challenge
						# check that challenge is completed first
						previous_challenge = db.session.query(Challenge).filter(Challenge.country_code==challenge.depends_on).one()
						if previous_challenge in current_team.challenges_completed:
							show = True
					else:
						# if it doesn't depend on any others just add it to the dict
						show = True
			# if show ennds up being true
			if show:
				# add it to the challenge dict
				chal = self.make_challenge_dict(challenge, current_team)
				countries_to_challenges[challenge.country_code] = chal
		# return the dict
		return countries_to_challenges

	def get_announcements(self):
		announcements_list = []
		# get announcements from db
		announcements = db.session.query(Announcement).all()	
		for announcement in announcements:
			# strf time them and make them suitable format
			announcements_list.append({"time":announcement.time.strftime("%a %d %B %-I:%M%p:"),"announcement":announcement.announcement})
		return announcements_list
