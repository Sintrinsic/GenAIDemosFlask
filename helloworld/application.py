#!flask/bin/python
import json
import optparse

from flask import Flask, render_template, request, jsonify

from helloworld.tools.agents.report_writer import ReportWriter
from helloworld.tools.agents.suggestion_box import SuggestionBox

application = Flask(__name__)

# Mapping of agent identifiers to their respective classes
agent_mapping = {
    "ReportWriter": ReportWriter,
    "SuggestionBox": SuggestionBox
    # Add other agents here as needed
}


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


@application.route('/feedback_analysis', methods=['GET'])
def input_aggregation():
    return render_template('input_aggregation.html')


@application.route('/process_message', methods=['POST'])
def process_message():
    r_data = json.loads(request.data)
    data = r_data
    agent_id = data.get('agent')
    messages = list(data.get('messages'))

    # Instantiate the appropriate agent class
    agent_class = agent_mapping.get(agent_id)
    if not agent_class:
        return jsonify({"error": "Invalid agent identifier"}), 400

    agent = agent_class()

    # Process all but the last message to create history
    for message in messages[:-1]:
        if message['role'] == 'user':
            agent.insert_fake_user_message(message['content'])
        if message['role'] == 'system':
            agent.insert_fake_system_message(message['content'])
        if message['role'] == 'assistant':
            agent.insert_fake_agent_message(message['content'])
            # Process the last message and get the response
    last_message = messages[-1]
    response = agent.send_message_solo(last_message['content'])

    return response


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
