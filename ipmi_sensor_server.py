import sys
import json
from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

def isfloat(param):
  if not param.isdecimal():
    try:
      float(param)
      return True
    except ValueError:
      return False
  else:
    return True

class IpmiSensors(Resource):
  def get(self):
    with open('/var/cache/ipmi-sensors/sensor_data.txt', 'r') as f:
      sensor_line = f.readlines()
    
    sensor_data = {}
    for data in sensor_line:
      line_data = data.split("|")
      if len(line_data) == 10:
        for k, line_value in enumerate(line_data):
          if isfloat(line_value.strip()):
            line_data[k] = float(line_value.strip())
          elif line_value.strip() == 'na':
            line_data[k] = None
          else:
            line_data[k] = line_value.strip()
        sensor_data[line_data[0]] = {
          "value": line_data[1],
          "unit": line_data[2],
          "status": line_data[3],
          "thresholds": {
            "min": {
              "fatal": line_data[4],
              "crit": line_data[5],
              "warn": line_data[6]
            },
            "max": {
              "warn": line_data[7],
              "crit": line_data[8],
              "fatal": line_data[9]
            }
          }
        }
        if sensor_data[line_data[0]]["status"] == None or not type(sensor_data[line_data[0]]["value"]) == float:
          del(sensor_data[line_data[0]])
    return {"sensors": sensor_data}, 200

api.add_resource(IpmiSensors, '/sensors')
