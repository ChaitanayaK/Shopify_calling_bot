# ngrok http --domain=kid-one-spaniel.ngrok-free.app 5000 

from flask import Flask, request, jsonify, url_for, session
from twilio.twiml.voice_response import VoiceResponse, Gather
import json
import os
import firebase_admin
from firebase_admin import credentials, storage
from dump.parse_info import Parser
from data_extractor import Extractor
from assistant_model import Assistant

cred = credentials.Certificate("cred.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'shopifycallbot.appspot.com'
})

bucket = storage.bucket()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('TWILIO_ACCOUNT_SID')

@app.route("/")
def hello():
    return "Hello User, you may send requests"

@app.route("/voice", methods=['POST'])
def voice():
    response = VoiceResponse()

    caller_number = request.form['From']
    print(f"Incoming call from: {caller_number}")

    extractor = Extractor(caller_number)
    data = extractor.extractData()
    order_data = data[1]
    client_name = data[0]

    with open(f'customer{caller_number}.json', 'w') as json_file:
        json.dump(order_data, json_file, indent=4) 

    # TODO: code to fetch all order data using phone number(wait for results)

    assistant = Assistant.create(caller_number)
    session['assistant_id'] = assistant.id

    thread_id = Assistant.createThreadId()
    session['thread_id'] = thread_id

    response.redirect(url_for('convertAudio', prompt=f"Hi, I am {client_name}.", _external=True))

    return str(response)

@app.route("/convertAudio", methods=['POST', 'GET'])
def convertAudio():
    response = VoiceResponse()

    assistant_id = session.get('assistant_id')
    thread_id = session.get('thread_id')

    prompt = request.args.get('prompt')

    assistant_reply = Assistant.ask(assistant_id, thread_id, prompt)

    gather = Gather(input='speech', action="/handle_speech", method='POST')
    gather.say(assistant_reply)

    # TODO: voices = [Ruth]

    response.append(gather)
    return str(response)

@app.route("/botSpeak", methods=['POST', 'GET'])
def botSpeak():
    response = VoiceResponse()

    assistant_id = session.get('assistant_id')
    thread_id = session.get('thread_id')

    prompt = request.args.get('prompt')

    assistant_reply = Assistant.ask(assistant_id, thread_id, prompt)

    gather = Gather(input='speech', action="/handle_speech", method='POST')
    gather.say(assistant_reply)

    # TODO: voices = [Ruth]

    response.append(gather)
    return str(response)

@app.route("/handle_speech", methods=['POST', 'GET'])
def handle_speech():
    response = VoiceResponse()

    if request.method == 'POST':
        speech_result = request.form.get('SpeechResult', '').strip()
    else:
        speech_result = request.args.get('SpeechResult', '').strip()

    print(f"Method: {request.method}")
    print(f"Speech Result: {speech_result}")

    if speech_result:
        response.redirect(url_for('botSpeak', prompt=speech_result, _external=True))
    else:
        response.say("I didn't catch that. Please try again.")

    response.hangup()
    return str(response)

if __name__ == "__main__":
    app.run(debug=True)