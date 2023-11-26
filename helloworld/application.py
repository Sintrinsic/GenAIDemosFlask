#!flask/bin/python
import json
from flask import Flask, Response, render_template
import optparse

application = Flask(__name__)

@application.route('/', methods=['GET'])
def index():
    return render_template('main.html')

@application.route('/home', methods=['GET'])
def alt_index():
    return render_template('main.html')

@application.route('/report', methods=['GET'])
def report():
    return render_template('report.html')

@application.route('/utility_outage', methods=['GET'])
def utility_outage():
    return render_template('outage.html')

@application.route('/input_aggregation', methods=['GET'])
def input_aggregation():
    return render_template('input_aggregation.html')




if __name__ == '__main__':
    default_port = "80"
    default_host = "0.0.0.0"
    parser = optparse.OptionParser()
    parser.add_option("-H", "--host",
                      help=f"Hostname of Flask app {default_host}.",
                      default=default_host)

    parser.add_option("-P", "--port",
                      help=f"Port for Flask app {default_port}.",
                      default=default_port)

    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug",
                      help=optparse.SUPPRESS_HELP)

    options, _ = parser.parse_args()

    application.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port)
    )
