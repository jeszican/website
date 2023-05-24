from flask import Blueprint, render_template, request, current_app, redirect, url_for
from flask_login import login_required, logout_user
from .login import Login
import html

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

		# the login route
		@bp.route('/login', methods=["GET","POST"])
		def login_page():
			# set message to ""
			response = ""
			if request.method == "POST":
				# get form fields
				username = html.escape(request.form["username"])
				password = request.form["password"]
				# try user
				result, response = Login().try_user(username, password)
				if result:
					# return the logged in response
					return response

			return render_template("landing.html", mode="login", message=response)

		# the login route
		@bp.route('/register', methods=["GET","POST"])
		def register_page():
			# get form fields
			username = html.escape(request.form["username"])
			password = request.form["password"]
			email = request.form["email"]
			confirm_password = request.form["confirm_password"]
			team_code = request.form["invite_code"]

			success, response = Login().check_username_and_password(username, password, confirm_password)
			if success:
				result, response = Login().register_user(username, password, email, team_code)
				if result:
					# return the logged in response
					return response	
			return render_template("landing.html", mode="register", message=response)

		# the logout route
		@bp.route('/logout')
		@login_required
		def logout_page():
			logout_user()
			return redirect(url_for('login.blueprint.login_page'))

		return bp