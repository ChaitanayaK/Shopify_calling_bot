# ngrok http --domain=kid-one-spaniel.ngrok-free.app 5000 

from flask import Flask, request, jsonify, url_for, session, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Gather
import json
import os
from groq import Groq
from openai import OpenAI
import requests
from data_extractor import Extractor
import time

url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
headers = {
    "Authorization": f"Token {os.environ.get('DEEPGRAM_AI_API_KEY')}",
    "Content-Type": "application/json"
}

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

    if os.path.exists(f'assets/callvoice/customer{caller_number}.mp3'):
        os.remove(f'assets/callvoice/customer{caller_number}.mp3')

    session['caller_number'] = caller_number

    extractor = Extractor(caller_number)
    data = extractor.extractData()
    order_data = data[1]
    client_name = data[0]

    systemPrompt = {"role" : "system", "content" : f'You are Allina from Melody Beanie Store. You are talking to "{client_name}", they are a customer. You must answer the question related only to their order related queries. Your responses are quick and precise. You take context from the following data about the user\'s orders:\n{order_data}'}

    session['history'] = [systemPrompt]

    response.redirect(url_for('botSpeak', prompt=f"Hi, I am {client_name}, who are you?."))
    return str(response)

@app.route("/botSpeak", methods=['POST', 'GET'])
def botSpeak():
    response = VoiceResponse()

    caller_number = session.get('caller_number')
    prompt = request.args.get('prompt')

    session['history'].append({
                "role": "user",
                "content": prompt,
            })

    messages = session['history']

    chat_completion = Groq().chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
        max_tokens=1024,
    )
    assistant_reply = chat_completion.choices[0].message.content

    session['history'].append({
                "role": "assistant",
                "content": assistant_reply,
            })

    payload = {
        "text": assistant_reply
    }
    response_d = requests.post(url, headers=headers, json=payload)
    if response_d.status_code == 200:
        with open(f"assets/callvoice/customer{caller_number}.mp3", "wb") as f:
            f.write(response_d.content)
        print("File saved successfully.")
    else:
        print(f"Error: {response_d.status_code} - {response_d.text}")

    gather = Gather(input='speech', action="/handle_speech", method='POST', enhanced="true", speechModel="phone_call", speechTimeout='5', timeout='5')

    # gather.play(f'http://66.179.252.25/audio/customer{caller_number}.mp3')
    gather.play(f'https://kid-one-spaniel.ngrok-free.app/audio/customer{caller_number}.mp3')
    response.append(gather)

    return str(response)

@app.route("/handle_speech", methods=['POST', 'GET'])
def handle_speech():
    response = VoiceResponse()
    caller_number = session.get('caller_number')

    if os.path.exists(f'assets/callvoice/customer{caller_number}.mp3'):
        os.remove(f'assets/callvoice/customer{caller_number}.mp3')

    if request.method == 'POST':
        speech_result = request.form.get('SpeechResult', '').strip()
    else:
        speech_result = request.args.get('SpeechResult', '').strip()

    print(f"Method: {request.method}")
    print(f"Speech Result: {speech_result}")

    if speech_result:
        response.redirect(url_for('botSpeak', prompt=speech_result))
    else:
        response.say("I didn't catch that. Please try again.")

    response.hangup()
    return str(response)

@app.route('/audio/<filename>')
def serve_static(filename):
    return send_from_directory(directory='assets/callvoice/', path=filename)

if __name__ == "__main__":
    app.run(debug=True)