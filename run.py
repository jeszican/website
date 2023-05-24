from ctf.ctf_factory import app, socketio_app

if __name__ == "__main__":
	# app.run()
	socketio_app.run(app, host="0.0.0.0", port=5051, debug=True)
