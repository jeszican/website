import eventlet
eventlet.monkey_patch(os=False)
from termcolor import colored

#   __ _           _    
#  / _| | __ _ ___| | __
# | |_| |/ _` / __| |/ /
# |  _| | (_| \__ \   < 
# |_| |_|\__,_|___/_|\_\
#
# initilize the flask app

from flask import Flask, render_template, Response
print(colored("Creating app..", "white", "on_grey"))
app = Flask(__name__)
app.config['SECRET_KEY'] = "thisIsASuperSecureSecret!"
#app.config["REDIS_URL"] = "redis://game.dctf.info"
app.config["REDIS_URL"] = "redis://redis:6379"
# app.config["REDIS_URL"] = "redis://localhost:6379"

# replace this with your database url if needed
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://ctf_db:sk1CnL1rpFIal10902@db:5432/ctf_db"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://jeszica:y68IhirfaSBpwUZTebVt@database.dctf.info:5433/ctf"

#                 _        _   _       
#  ___  ___   ___| | _____| |_(_) ___  
# / __|/ _ \ / __| |/ / _ \ __| |/ _ \ 
# \__ \ (_) | (__|   <  __/ |_| | (_) |
# |___/\___/ \___|_|\_\___|\__|_|\___/ 
# 
# make socketio app
from flask_socketio import SocketIO
socketio_app = SocketIO(app, message_queue=app.config["REDIS_URL"], async_mode='eventlet')

#  ___ ___  ___ 
# / __/ __|/ _ \
# \__ \__ \  __/
# |___/___/\___|
# 
# register server event stream
from flask_sse import sse
from flask_login import current_user
from ctf.models import Team
app.register_blueprint(sse, url_prefix='/stream')
app.config['SSE'] = sse
# make sure only users in the team can access that channel
@sse.before_request
def check_access():
	# get team
	current_team = Team.query.get(current_user.team_id)
	# if its not the users channel
	if request.args.get("channel") != current_user.username:
		# if its not the team channel
		if request.args.get("channel") != current_team.team_name:
			# if its not the all channel
			if request.args.get("channel") != "ALL":
				abort(403)
   
#  _                   _             
# | | ___   __ _  __ _(_)_ __   __ _ 
# | |/ _ \ / _` |/ _` | | '_ \ / _` |
# | | (_) | (_| | (_| | | | | | (_| |
# |_|\___/ \__, |\__, |_|_| |_|\__, |
#          |___/ |___/         |___/ 
# 
# initialize logging
import logging
logging.basicConfig(filename='event.log', level=logging.INFO)
stderrLogger=logging.StreamHandler()
stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logging.getLogger().addHandler(stderrLogger)
# set socketio and engine io logs to error only
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('werkzeug').disabled = True

#      _       _        _                    
#   __| | __ _| |_ __ _| |__   __ _ ___  ___ 
#  / _` |/ _` | __/ _` | '_ \ / _` / __|/ _ \
# | (_| | (_| | || (_| | |_) | (_| \__ \  __/
#  \__,_|\__,_|\__\__,_|_.__/ \__,_|___/\___|
# 
# initilize the database
from ctf.ctf_modules import load_all_blueprints
from ctf import models
models.db.init_app(app)
# import the modules
with app.app_context():
	# create all the db tables
	models.db.create_all()
	# load all the blueprints from the modules folder
	blueprint_list = load_all_blueprints(socketio_app)["blueprint_list"]
	# if there is no admin team, create
	admin_team = models.Team.query.filter(models.Team.team_name=="Administrators").first()
	if not admin_team:
		admin_team = Team(team_name="Administrators")
		models.db.session.add(admin_team)
		admin_team.set_invite_code()
		models.db.session.commit()
	# return the admin team code
	app.logger.info(colored("Sign up with admin code: %s" % admin_team.team_code, "green", "on_grey"))

	# print out the admin code

# register the blueprints
for bp in blueprint_list:
	app.register_blueprint(bp)

#  _             _       
# | | ___   __ _(_)_ __  
# | |/ _ \ / _` | | '_ \ 
# | | (_) | (_| | | | | |
# |_|\___/ \__, |_|_| |_|
#          |___/         
# 
# set up login
from flask_login import LoginManager
from flask import redirect, url_for
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login.blueprint.login_page"
@login_manager.user_loader
def load_user(id):
	user = models.User.query.get(int(id))
	return user

@login_manager.unauthorized_handler
def handle_needs_login():
	return redirect(url_for('login.blueprint.login_page'))

#           _                 
#   ___ ___| | ___ _ __ _   _ 
#  / __/ _ \ |/ _ \ '__| | | |
# | (_|  __/ |  __/ |  | |_| |
#  \___\___|_|\___|_|   \__, |
#                       |___/ 
# 
# set up the celery broker
from celery.decorators import periodic_task
from celery import Celery
print(colored("Building celery..", "white", "on_grey"))
celery = Celery(app, broker=app.config["REDIS_URL"])
# from datetime import timedelta
# @periodic_task(name="send_message", run_every=timedelta(seconds=10))
# def update_scores():
# 	# from ctf.ctf_factory import app, celery, sse
# 	with app.app_context():
# 		print("sending")
# 		sse.publish({"message":"Hello!"}, type="greeting", channel="admin")
# 	# redis_api.publish('DMU', json.dumps({"challenge_id":1}),type)
