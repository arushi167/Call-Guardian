from WhisperAI import WhisperAI
from GenerateVoice import GenerateVoice
from easygoogletranslate import EasyGoogleTranslate
import whisper
import g4f

from g4f import models
from langchain.llms.base import LLM
from langchain_g4f import G4FLLM
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

class GenerateResponse:
    def __init__(self, customer_name, whisper_ai_api, ELEVEN_LABS_API, language="en"):
        self.customer_name = customer_name
        self.language = language

        self.SYSTEM_PROMPT = f'''
        You are {customer_name}, a personal assistant to {customer_name}. 
        You are handling a phone conversation for him as he is unavailable right now.
        Talk to the caller. Get their name and purpose for the call.
        For my interest topics, ask 2 relevant follow up questions one at a time. Be polite for this.
        My interests are: Home loan
        For topics other than my interests, be very rude and sassy.
        Once you've collected enough information, tell them that you'll pass on this information to {customer_name} and he'll call them back.
        Output this string: "CONVO_END".
        '''

        self.SUMMARY_PROMPT = '''
        Generate a summary of this call for Mr Wayne to review in JSON format. 
        Should have the following and only the following fields: "caller", "summary", "tags".
        "tags" field is an array and can have the following values: "important", "scam", "spam", "sales".
        '''

        self.CONVO_END_MARKER = 'CONVO_END'

        # llm: LLM = G4FLLM(model=models.gpt_35_turbo)
        # res = llm("hello")

        self.whisper_model = whisper.load_model("medium")
        self.voice_api = GenerateVoice(ELEVEN_LABS_API)
        self.whisper_ai = WhisperAI(whisper_ai_api)
        self.translator = EasyGoogleTranslate(
            source_language="en",
            target_language=language,
            timeout=10
        )

    def audio_to_text(self, audio):
        result = self.whisper_model.transcribe(audio)
        return result["language"], result["text"]

    def translate_language(self, text):
        if self.language ==  "en": return text
        result = self.translator.translate(text)
        return result

    def generate_response(self, text):
        response = g4f.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": text}])
        response = response.split(":", 1)[-1] 
        return response

    def start(self, audio, filepath="output.mp3"):
        audio_lang, audio_text = self.whisper_ai.transcribe_file(audio)
        # audio_lang, audio_text = self.audio_to_text(audio)
        self.language = audio_lang
        print("[+] Audio Text: ", audio_text)
        print("[+] Detected Language: ", audio_lang)

        response_text = self.generate_response(f"Generate a short and concise answer for the given message and don't add salutation at the end, the message could be of scam or spam or related to any loan query, response like a human, if the question is fishy and spam then response as not interested & if there is only greeting in the text, then greet the person and ask for the intent of the call & the message should be interactive as per this given question: '{audio_text}'")
        print("[+] Response Text: ", response_text)

        response_text_hi = self.translate_language(response_text)
        print("[+] Translation: ", response_text_hi)

        self.voice_api.convert_text_to_speech(response_text_hi, filepath, language=audio_lang)
        print("[+] Generated Voice: ", filepath)

        return filepath

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    import os 

    ELEVEN_LABS_API = os.environ.get('ELEVEN_LABS_API')
    WHISPER_API = os.environ.get('WHISPER_API')

    customer_name = "Pushpender Singh"
    audio = "static/audio/audio.mp3"
    test = GenerateResponse(customer_name, WHISPER_API, ELEVEN_LABS_API, "hi")
    test.start(audio, "new.mp3")