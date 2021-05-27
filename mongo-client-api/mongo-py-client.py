
from os import name
from flask import Flask
from flask import jsonify
from jaeger_client.constants import TRACE_ID_HEADER
import opentracing
import requests
import json
from opentracing.propagation import Format
from opentracing import tracer
import logging
from jaeger_client import Config
from requests.api import head

app = Flask(__name__)
class Tracer:
    client = None
    service_name = ''
    
    def __init__(self, service_name):
        self.client = None
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

@app.route('/seekstar', methods=['GET'])
def seek_star():
    tracer = opentracing.tracer
    with tracer.start_span('star-seeker') as span:
        span.log_kv({'event': 'star-seeker-log', 'life': 42})
        span.set_tag('seekstars', "star")
        headers = {}
        
        tracer.inject(
            span_context = span.context,
            format = Format.HTTP_HEADERS,
            carrier=headers)
        output = requests.get("http://127.0.0.1:5000/star", headers=headers) #,  headers=headers_dict)

    return {'result': output.json()}

if __name__ == '__main__':
    tracer = Tracer(service_name='seeker')
    tracer.init_tracer()
    app.run(debug=True, port=6000)