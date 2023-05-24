import pkgutil, sys, os
from termcolor import colored

sys.path.append(os.getcwd()+"/app/ctf_modules")

def load_all_blueprints(socketio):
	blueprint_list = []
	try:
		for loader, name, ispkg in pkgutil.walk_packages(path=__path__):
			module = loader.find_module(name).load_module(name)
			if module != None:
				## if the module has a blueprint
				if ".blueprint" in name:
					klass = getattr(module, "blueprint")()
					if callable(getattr(klass,"get_blueprint",None)):
						# get the blueprint
						blueprint= klass.get_blueprint(socketio)
						# append the blueprint
						blueprint_list.append(blueprint)
					print(colored("Success loading %s" % name, "white", "on_grey"))
		return dict(blueprint_list=blueprint_list)
	except Exception as e:
		print(str(e) + " in " + name)