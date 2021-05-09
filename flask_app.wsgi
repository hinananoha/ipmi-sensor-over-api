#flask_app.wsgi
import os,sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ipmi_sensor_server import app as application