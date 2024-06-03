# ngrok http --domain=kid-one-spaniel.ngrok-free.app 5000 

from flask import Flask, request, jsonify, url_for, session
from twilio.twiml.voice_response import VoiceResponse, Gather, Play
import os
import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate("cred.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'shopifycallbot.appspot.com'
})

bucket = storage.bucket()
local_mp3_file = "Invincible_Theme.mp3"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('TWILIO_ACCOUNT_SID')

@app.route("/")
def hello():
    return "Hello User, you may send requests"

@app.route("/voice", methods=['POST'])
def voice():
    response = VoiceResponse()
    
    caller_number = request.form['From']
    blob_name = f"customer{caller_number}.mp3"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_mp3_file)
    blob.make_public()

    audio_url = blob.public_url
    response.play(audio_url)
    # response.redirect(url_for('botSpeak', link=audio_url, _external=True))

    return str(response)

@app.route("/botSpeak", methods=['POST', 'GET'])
def botSpeak():
    response = VoiceResponse()
    url = request.args.get('link')

    response.play(url)

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)