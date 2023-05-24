from celery import Celery
from ctf.models import Team, Scores, db, Challenge_to_Url, Config, Challenge, Average_Loading_Times
from retrying import retry
from flask import Flask, current_app
from time import sleep
from celery import shared_task
from celery.decorators import periodic_task
import json
import datetime
import requests
import base64
from datetime import timedelta, datetime
import random
import string
from celery.signals import after_task_publish,task_success,task_prerun,task_postrun
from time import time

import docker

from .AWS import AWS

average_times_in_progress = {}

@task_prerun.connect
def task_prerun_handler(signal, sender, task_id, task, args, kwargs, **extras):
	average_times_in_progress[task_id] = time()
	from ctf.ctf_factory import app, celery
	with app.app_context():
		db.engine.dispose()

@task_postrun.connect
def close_session(signal, sender, task_id, task, args, kwargs, retval, state, **extras):
    # Flask SQLAlchemy will automatically create new sessions for you from 
    # a scoped session factory, given that we are maintaining the same app
    # context, this ensures tasks have a fresh session (e.g. session errors 
    # won't propagate across tasks)
	from ctf.ctf_factory import app, celery
	with app.app_context():
		db.engine.dispose()
		if task.__name__ == "launch_challenge":
			challenge_name = ''.join(e for e in Challenge.query.get(args[1]).name if e.isalnum())
			try:
				cost = time() - average_times_in_progress.pop(task_id)
			except KeyError:
				cost = -1
			avlt = Average_Loading_Times(challenge_name=challenge_name, time=cost)
			db.session.add(avlt)
			db.session.commit()

@periodic_task(name="remove_expired_challenges", run_every=timedelta(minutes=1), queue="scoring_queue")
def remove_expired_challenges():
	from ctf.ctf_factory import app, celery, sse
	with app.app_context():
		timed_challenges = db.session.query(Challenge).filter(Challenge.type=="timed").all()
		for challenge in timed_challenges:
			# if its past the deadline
			if challenge.deadline < datetime.now():
				# then hide it
				challenge.hidden = True
				db.session.commit()
				# hide the challenge on the map
				current_app.config["SSE"].publish({"country_code":challenge.country_code}, type="country_hide", channel="ALL")
				# unlock any challenges that depend on it
				next_challenges = db.session.query(Challenge).filter(Challenge.depends_on==challenge.country_code).all()
				for nc in next_challenges:
					# for each one push it to the TEAM 
					current_app.config["SSE"].publish({"country_code":nc.country_code,"challenge_info":Game().make_challenge_dict(nc, current_team)}, type="country_unlock", channel=current_team.team_name)
		db.session.flush()

def roundTime(dt=None, dateDelta=timedelta(minutes=1)):
    """Round a datetime object to a multiple of a timedelta
    dt : datetime.datetime object, default now.
    dateDelta : timedelta object, we round to a multiple of this, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
            Stijn Nevens 2014 - Changed to use only datetime objects as variables
    """
    roundTo = dateDelta.total_seconds()

    if dt == None : dt = datetime.now()
    seconds = (dt - dt.min).seconds
    # // is a floor division, not a comment on following line:
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + timedelta(0,rounding-seconds,-dt.microsecond)

@periodic_task(name="update_scores_over_time", run_every=timedelta(minutes=10), queue="scoring_queue")
def update_scores():
	from ctf.ctf_factory import app, celery
	with app.app_context():
		# a task to update the scores over time data
		print("TASK: updating 'Scores over Time'")
		# save the current time
		time = datetime.now()
		# get all the teams
		all_teams = db.session.query(Team).all()
		# for each team
		for team in all_teams:
			# get their score at the time
			score_at_time = Scores(team_id=team.id, score=team.total_points, time=roundTime(time))
			db.session.add(score_at_time)
			db.session.commit()

@shared_task(name="launch_challenge", soft_time_limit=900)
def launch_challenge(team_id, challenge_id):
	from ctf.ctf_factory import app, celery
	with app.app_context():
		try:
			# first check if ctf is local (docker only) or can use aws and namecheap
			try: remote = Config.query.filter_by(key="remote").first().value
			except: remote = "False" 
			# add launching to db 
			r_2_c = Challenge_to_Url.query.filter_by(team_id=team_id).filter_by(challenge_id=challenge_id).one()
			# get challenge and team name
			challenge = Challenge.query.get(challenge_id)
			challenge_name = ''.join(e for e in challenge.name if e.isalnum())
			team_name = ''.join(e for e in Team.query.get(team_id).team_name if e.isalnum())
			# if its a remote ctf that requires architect
			if remote == "True":
				# ask architect to deploy a challenge
				print("Deploying challenge %s for team %s" % (challenge_name, team_name))
				# send a progress update
				r_2_c.message = "Deploying server.."
				db.session.commit()
				db.session.flush()
				current_app.config["SSE"].publish({"country_code":challenge.country_code,"update":"Deploying server.."}, type="country_update", channel=team_name)
				# if the challenge doesnt have a custom ami
				if challenge.ami == None:
					# get an unused instance and deploy the docker
					ip_address, remote_id, region = AWS().get_unused_instance()
					# if theres a docker file for this challenge connect to the docker 
					if challenge.docker_file != None:
						print("Deploying docker image %s for team %s" % (challenge.docker_file, team_name))
						deploy_remote_docker_challenge(challenge.docker_file, ip_address, r_2_c, team_name, challenge.country_code)
				else:
					# if the challenge has a custom ami
					if challenge.information != None:
						if "instance_type" in challenge.information:
							ip_address, remote_id, region = AWS().create_server(challenge_name, team_name, challenge.ami, instance_type=challenge.information["instance_type"])
						else:
							ip_address, remote_id, region = AWS().create_server(challenge_name, team_name, challenge.ami)
					else:
						ip_address, remote_id, region = AWS().create_server(challenge_name, team_name, challenge.ami)
			else:
				# if its a local development instance using docker containers
				ip_address, remote_id, region = deploy_local_docker_challenge(challenge.docker_file, challenge.country_code, team_name)
			print("New challenge url (%s) for challenge %d for team %d" % (ip_address, challenge_id, team_id))
			# add challenge to db with remote id
			r_2_c.challenge_address = ip_address
			r_2_c.remote_id = remote_id
			r_2_c.region = region
			# commit the new challenge url
			db.session.commit()
			db.session.flush()
			# tell the user the challenge has been launched
			current_app.config["SSE"].publish({"country_code":challenge.country_code,"challenge_url":ip_address}, type="country_launched", channel=team_name)
		except Exception as e:
			print(e)
			# if theres an exception remove the launching record
			# remove launching record
			db.session.delete(r_2_c)
			db.session.commit()
			db.session.flush()
			current_app.config["SSE"].publish({"country_code":challenge.country_code}, type="country_failed", channel=team_name)
			try:
				# kill the challenge
				kill_challenge(challenge.country_code, remote_id, team_id, region)
			except Exception as e:
				# if it can't kill we probably didnt get that far
				print(str(e))

def deploy_remote_docker_challenge(docker_file, ip_address, r_2_c, team_name, challenge_country_code):
	# update the status
	r_2_c.message = "Pulling docker image.."
	db.session.commit()
	db.session.flush()
	# send the status update to the team
	current_app.config["SSE"].publish({"country_code":challenge_country_code,"update":"Pulling docker image.."}, type="country_update", channel=team_name)
	try:
		# connect to the docker client
		client, api_client = connect_to_docker(ip_address)
		# stop all other containers
		stop_all_docker_containers(client)
		# pull the latest docker image
		pull_docker_image(docker_file, api_client)
		# update status of the challenge url
		r_2_c.message = "Running container.."
		db.session.commit()
		db.session.flush()
		# send the challenge update
		current_app.config["SSE"].publish({"country_code":challenge_country_code,"update":"Running container.."}, type="country_update", channel=team_name)
		# finally run the container
		run_docker_container(docker_file, client)
	except Exception as e:
		# if theres an error
		current_app.config["SSE"].publish({"country_code":challenge_country_code}, type="country_failed", channel=team_name)
		print("Error deploying docker image %s for team %s: %s" % (docker_file, team_name, str(e)))
		raise

@retry(stop_max_attempt_number=7,wait_fixed=2000)
def connect_to_docker(ip_address):
	client = docker.DockerClient(base_url="tcp://%s:2376" % ip_address)
	api_client = docker.APIClient(base_url="tcp://%s:2376" % ip_address)
	return client, api_client

@retry(stop_max_attempt_number=7,wait_fixed=2000)
def pull_docker_image(docker_file, client):
	for line in client.pull(docker_file, stream=True):
		print(json.dumps(json.loads(line), indent=4))

@retry(stop_max_attempt_number=7,wait_fixed=2000)
def stop_all_docker_containers(client):
	for container in client.containers.list():
		container.stop()
	## prune unused containers
	client.containers.prune()
	#for image in client.images.list():
	#	image.remove()
	## prune unused image
	print(client.images.prune(filters={'dangling': False}))
	
@retry(stop_max_attempt_number=7,wait_fixed=2000)
def run_docker_container(docker_file, client):
	container = client.containers.run(docker_file, network_mode="host", detach=True, publish_all_ports=True)

def deploy_local_docker_challenge(docker_file, country_code, team_name):
	try:
		# connect to local docker
		# client = docker.DockerClient(base_url='unix://docker.sock')
		client = docker.DockerClient(base_url='unix://docker.sock')
		# build the image
		random_image_id = 'dctf-'+''.join(random.choice(string.digits + string.ascii_lowercase) for _ in range(7))
		# print progrses
		print("Deploying image %s on host %s" % (docker_file, "127.0.0.1"))
		# build the image
		image = client.images.build(path=docker_file, tag=random_image_id)
		docker_image_id=image[0].id
		# run the image
		print("Running container on host %s" % "127.0.0.1")
		# get container back
		container = client.containers.run(docker_image_id, detach=True, publish_all_ports=True)
		container.reload()
		remote_id = container.id[:15]
		challenge_url = ""
		# get the exposed points
		for f_port,forwarded_ports in container.ports.items():
			for port in forwarded_ports:
				challenge_url = challenge_url + "<li>localhost:%s</li>" % port["HostPort"]
		# return the challenge url
		return challenge_url, remote_id, "local"
	except Exception as e:
		# if theres an error
		current_app.config["SSE"].publish({"country_code":country_code}, type="country_failed", channel=team_name)
		print("Error deploying docker image %s for team %s: %s" % (docker_file, team_name, str(e)))
		raise

@shared_task(name="kill_challenge", soft_time_limit=30000)
def kill_challenge(challenge_country_code, remote_id, team_id, region):
	from ctf.ctf_factory import app, celery
	with app.app_context():
		try:
			try: remote = Config.query.filter_by(key="remote").first().value
			except: remote = "False" 

			if remote == "True":
				AWS().delete_server(remote_id, region)
			else:
				try: 
					# connect to local docker
					client = docker.DockerClient(base_url='unix://docker.sock')
					container = client.containers.get(remote_id)
					print("Killing container with id %s" % remote_id)
					container.kill()
				except:
					# if the container isn't found pass and just say its been stopped
					pass
		except Exception as e:
			pass

		# if exception just tell team its gone anyway
		r_2_c = Challenge_to_Url.query.filter_by(remote_id=remote_id).delete()
		db.session.commit()
		team = Team.query.get(int(team_id))
		# tell the user the challenge has been killed
		current_app.config["SSE"].publish({"country_code":challenge_country_code}, type="country_killed", channel=team.team_name)
