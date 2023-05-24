from celery import Celery
from celery import shared_task
from ctf.models import db
from celery.decorators import periodic_task
from celery.signals import after_task_publish,task_success,task_prerun,task_postrun
from .admin import Admin

@task_prerun.connect
def task_prerun_handler(signal, sender, task_id, task, args, kwargs, **extras):
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

@shared_task(name="clone_challenges", soft_time_limit=900)
def clone_challenges(url):
	from ctf.ctf_factory import app, celery
	with app.app_context():
		Admin().clone_challenges(url)