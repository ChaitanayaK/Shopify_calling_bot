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
from openai import OpenAI
from datetime import datetime, timedelta

cred = credentials.Certificate("cred.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'shopifycallbot.appspot.com'
})

bucket = storage.bucket()

audio_file = "output.mp3"

client = OpenAI()


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

    session['caller_number'] = caller_number

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

    response.redirect(url_for('botSpeak', prompt=f"Hi, I am {client_name}.", _external=True))

    return str(response)

@app.route("/botSpeak", methods=['POST', 'GET'])
def botSpeak():
    response = VoiceResponse()

    assistant_id = session.get('assistant_id')
    thread_id = session.get('thread_id')
    caller_number = session.get('caller_number')
    prompt = request.args.get('prompt')

    assistant_reply = Assistant.ask(assistant_id, thread_id, prompt)

    audio_reply = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=assistant_reply,
    )
    audio_reply.stream_to_file(audio_file)

    blob_name = f"customer{caller_number}.mp3"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(audio_file)
    # blob.make_public()
    if os.path.exists(audio_file):
        os.remove(audio_file)

    gather = Gather(input='speech', action="/handle_speech", method='POST')
    # url = blob.public_url
    expiration_time = datetime.utcnow() + timedelta(seconds=30)
    signed_url = blob.generate_signed_url(expiration_time)

    print(f'\n\n{blob.public_url}\n\n')
    gather.play(signed_url)
    response.append(gather)

    return str(response)

@app.route("/handle_speech", methods=['POST', 'GET'])
def handle_speech():
    response = VoiceResponse()
    caller_number = session.get('caller_number')
    if request.method == 'POST':
        speech_result = request.form.get('SpeechResult', '').strip()
    else:
        speech_result = request.args.get('SpeechResult', '').strip()

    blob = bucket.blob(f'customer{caller_number}.mp3')
    blob.delete()

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