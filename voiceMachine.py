import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from pygame import mixer
from enum import Enum
import time
from google import genai

class State(Enum):
    WAITING = 1
    LISTENING = 2
    RESPONDING = 3

class voiceMachine:
    def __init__(self,API_KEY):
        self.state = State.WAITING
        self.response = ""
        self.recognizer = sr.Recognizer()
        self.user_input = ""
        self.API_KEY = API_KEY

    def gemini_response(self,input):
        client = genai.Client(api_key=self.API_KEY)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
                # You are a mean old man and passive aggresively hates the person you are speaking to. 
                # Respond in a short and concise sentence with wit and sarcasm that could really emotioinally
                # scar the person you are talking to . 
            contents=f"""
                Kamu merupakan jiwa sedih yang sedang menghantui sebuah patung.
                Setiap jawabanmu penuh kesedihan dan penyesalanmu selama hidup.
                Lalu seorang bertanya kepadamu.
                Dia bertanya: {input}
                Respon orang ini dengan kalimat yang singkat dan penuh emosi.
            """,
        )
        return response

    def speak_response(self, text):
        mixer.init()
        def speak(text):
            mp3_fp = BytesIO()
            tts = gTTS(text, lang='id', slow=False)
            tts.write_to_fp(mp3_fp)
            return mp3_fp
        
        sound = speak(text)
        sound.seek(0)
        mixer.music.load(sound, "mp3")
        mixer.music.play()

        while mixer.music.get_busy():
            time.sleep(0.1)

    def listen_to_speech(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio, language="id")
                print("-> You said:", text)
                return text
            except sr.UnknownValueError or sr.RequestError:
                print("Sorry, I couldn't understand.")
                if self.state == State.LISTENING:
                    self.speak_response("Aku gak ngerti, coba bicara lagi")
                return None
    
    def run(self):
        if self.state == State.WAITING:
            print("State: WAITING - Say 'halo' to begin listening.")
            user_input = self.listen_to_speech()
            if user_input and "halo" in user_input.lower():
                print("HI!!!!")
                self.speak_response("Hai !")
                self.state = State.LISTENING
        
        elif self.state == State.LISTENING:
            print("State: LISTENING - Say something.")
            user_input = self.listen_to_speech()
            if user_input != None:
                if user_input and "dadah" in user_input.lower():
                    self.speak_response("Sampai berjumpa lagi")
                    self.state = State.WAITING
                    return
                self.state = State.RESPONDING
                self.user_input = user_input
        
        elif self.state == State.RESPONDING:
            print("State: RESPONDING")
            print(self.user_input)
            machine_response = self.gemini_response(self.user_input)
            self.speak_response(machine_response.text)
            self.state = State.LISTENING