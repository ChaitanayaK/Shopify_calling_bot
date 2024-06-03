# ngrok http --domain=kid-one-spaniel.ngrok-free.app 5000 

from flask import Flask, request, jsonify, url_for, session
from twilio.twiml.voice_response import VoiceResponse, Gather
import json
import os
from dump.parse_info import Parser
from data_extractor import Extractor
from chatting_model import Model

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

    # TODO: code to fetch all order data using phone number

    model = Model()
    session['model'] = model.serialize()    # chat history data is in string

    print(session['model'])
    print(type(session['model']))

    response.redirect(url_for('botSpeak', prompt="Hi", _external=True))

    return str(response)

@app.route("/botSpeak", methods=['POST', 'GET'])
def botSpeak():
    response = VoiceResponse()

    model_data = session.get('model')
    model = Model.deserialize(model_data) 

    prompt = request.args.get('prompt')

    chat_input = model.chat(prompt)
    # action_url = url_for('handle_speech', _external=True)
    gather = Gather(input='speech', action="/handle_speech", method='POST')
    gather.say(chat_input)

    # TODO: voices = [Ruth]

    session['model'] = model.serialize()  
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