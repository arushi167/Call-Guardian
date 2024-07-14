import requests
import os 

class WhisperAI:
    def __init__(self, api_key):
        self.api_url = "https://transcribe.whisperapi.com"
        self.headers = {'Authorization': f'Bearer {api_key}'}

    def transcribe_file(self, file_path):
        with open(file_path, 'rb') as file:
            payload = {
                'file': {'file': file},
                'data': {
                    "fileType": "mp3",
                    "diarization": "false",
                    "numSpeakers": "2",
                    "initialPrompt": "",
                    "task": "transcribe",
                    "callbackURL": "",
                }
            }

            response = requests.post(self.api_url, headers=self.headers, files=payload['file'], data=payload['data'])
            response_json = response.json()
            # print(response_json)

            language = response_json['language']
            text = response_json['text']

            return language, text

# Example usage:
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    WHISPER_API = os.environ.get('WHISPER_API')

    file_path = "static/audio/audio.mp3"
    transcriber = WhisperAI(WHISPER_API)
    language, text = transcriber.transcribe_file(file_path)

    print("Language:", language)
    print("Text:", text)