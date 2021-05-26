
from flask import Flask
from flask import jsonify
from jaeger_client.constants import TRACE_ID_HEADER
import requests
import json
from opentracing.propagation import Format
import logging
from jaeger_client import Config

app = Flask(__name__)

@app.route('/seekstar', methods=['GET'])
def seek_star():
    tracer = init_tracer('seeker')
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

def init_tracer(service):
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
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

if __name__ == '__main__':
    app.run(debug=True, port=6000)