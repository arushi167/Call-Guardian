import requests
from gtts import gTTS

class GenerateVoice:
    def __init__(self, api, character="Daniel"):
        character_dict = {
            "Daniel": "onwK4e9ZLuTAKqWW03F9",
            "Female": "21m00Tcm4TlvDq8ikWAM"
        }

        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{character_dict[character]}"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api
        }

    def convert_text_to_speech(self, text, output_file='output.mp3', chunk_size=1024, language="en"):
        model_id = "eleven_multilingual_v2"
        
        voice_settings = {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": voice_settings
        }

        response = requests.post(self.url, json=data, headers=self.headers)
        try:
            response.raise_for_status()
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            print("[+] Generated Voice Using ElevenLabs")
        except:
            print("[+] Generated Voice Using GTTS")
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(output_file)        


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    import os 

    ELEVEN_LABS_API = os.environ.get('ELEVEN_LABS_API')

    api = GenerateVoice(ELEVEN_LABS_API)
    text = "Born and raised in the charming south, I can add a touch of sweet southern hospitality to your audiobooks and podcasts"
    api.convert_text_to_speech(text, "static/output/output.mp3")