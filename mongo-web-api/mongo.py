from flask import Flask, json
from flask import jsonify
from flask import request
import opentracing
from flask_pymongo import PyMongo
import logging
from jaeger_client import Config
from opentracing.propagation import Format
from opentracing import tracer

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://ricardo:password@localhost:27017/josalys'

mongo = PyMongo(app)
class Tracer:
    service_name = ''
    
    def __init__(self, service_name):
        self.service_name = service_name

    def init_tracer(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(format='%(message)s', level=logging.DEBUG)

        config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=self.service_name,
        )

        # this call also sets opentracing.tracer
        return config.initialize_tracer()

@app.route('/star', methods=['GET'])
def get_all_stars():
    tracer = opentracing.tracer
    father_span = tracer.extract(Format.HTTP_HEADERS, request.headers)
    with tracer.start_span('star-seeker', child_of=father_span) as span:
      star = mongo.db.stars
      span.log_kv({"operation": star})
      output = []
      for s in star.find():
          output.append({'name': s['name']})
      jsonOutput = jsonify({'result': output})
      span.log_kv({"result": jsonOutput})
    span.finish()
    return jsonOutput

@app.route('/star/<name>', methods=['GET'])
def get_one_star(name):
  star = mongo.db.stars
  s = star.find_one({'name' : name})
  if s:
    output = {'name' : s['name'], 'distance' : s['distance']}
  else:
    output = "No such name"
  return jsonify({'result' : output})

@app.route('/star', methods=['POST'])
def add_star():
  star = mongo.db.stars
  name = request.json['name']
  distance = request.json['distance']
  star_id = star.insert({'name': name, 'distance': distance})
  new_star = star.find_one({'_id': star_id })
  output = {'name' : new_star['name'], 'distance' : new_star['distance']}
  return jsonify({'result' : output})

if __name__ == '__main__':
    tracer = Tracer(service_name='star-seeker')
    tracer.init_tracer()
    app.run(debug=True)