import os
import streamlit as st
from flask import Flask, send_file, request
from GenerateResponse import GenerateResponse
from dotenv import load_dotenv
import sounddevice as sd
import soundfile as sf
load_dotenv()

app = Flask(__name__)

ELEVEN_LABS_API = os.environ.get('ELEVEN_LABS_API')
WHISPER_API = os.environ.get('WHISPER_API')

def record_audio_and_save(duration=5, sample_rate=44100):
    # Record audio
    print("Recording audio...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2)
    sd.wait()

    # Save audio to file
    print("Saving audio...")
    file_path = os.path.join('static', 'audio', 'audio.mp3')
    sf.write(file_path, audio_data, sample_rate)
    print("Audio saved to", file_path)

    return file_path

def main():
    st.title("Call Guardian")

    if st.button("Record Audio"):
        st.write("Recording audio...")

        file_path = record_audio_and_save()
        # print(file_path)
        # print("wisp: ", WHISPER_API)

        st.write("Audio recorded! Generating Audio Response")

        output_audio_path = "static/output/audio.mp3"
        test = GenerateResponse("Pushpender Singh", WHISPER_API, ELEVEN_LABS_API, "hi")
        test.start(file_path, output_audio_path)

        st.write("Response:")
        st.audio(output_audio_path, format='audio/mp3')

if __name__ == '__main__':
    main()
