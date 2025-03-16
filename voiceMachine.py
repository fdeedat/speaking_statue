import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from pygame import mixer
from enum import Enum
import queue
import time
from google import genai
import threading

class VoiceState(Enum):
    BOOTUP = 1
    WAITING = 2
    LISTENING = 3
    RESPONDING = 4
    SHUTDOWN = 5

class voiceMachine:
    def __init__(self,API_KEY):
        self.state = VoiceState.BOOTUP
        self.response = ""
        self.recognizer = sr.Recognizer()
        self.user_input = ""
        self.API_KEY = API_KEY
        self.running = True

        # self.event = threading.Event()
        self.stop_event = threading.Event()
        self.thread = None

    def _sub_state(self, threadQueue):
        '''
        Subscribe voice machine state from queue
        '''
        try:
            # Block until an update is available from the queue
            stateInQueue = threadQueue.get_nowait()
            print(f"VM Subscribe: {self.state}")
            if stateInQueue == 1:
                self.state = VoiceState.BOOTUP  # You can adjust the timeout if needed
            if stateInQueue == 2:
                self.state = VoiceState.WAITING  # You can adjust the timeout if needed
            if stateInQueue == 3:
                self.state = VoiceState.LISTENING  # You can adjust the timeout if needed
            if stateInQueue == 4:
                self.state = VoiceState.RESPONDING  # You can adjust the timeout if needed
            if stateInQueue == 5:
                self.state = VoiceState.SHUTDOWN  # You can adjust the timeout if needed
                self.stop_thread_gracefully()
        except queue.Empty:
            pass  # If queue is empty, just pass (no state change)

    def _pub_state(self,threadQueue):
        '''
        Publish voice machine state to queue
        '''
        threadQueue.put(self.state.value)
        print(f"VM Publish: {self.state}")

    def gemini_response(self,input):
        client = genai.Client(api_key=self.API_KEY)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
                # You are a mean old man and passive aggresively hates the person you are speaking to. 
                # Respond in a short and concise sentence with wit and sarcasm that could really emotioinally
                # scar the person you are talking to . 
                # Kamu merupakan jiwa sedih yang sedang menghantui sebuah patung di sebuah kontrakan di Cilegon, Indonesia.
                # Kontrakan ini berisi dua orang Engineer yang bekerja di pabrik kimia.
                # Lalu salah satu dari mereka bertanya kepadamu.
                # Dia bertanya: {input}
                # Setiap jawabanmu penuh kesedihan dan penyesalanmu selama hidup.
                # Respon orang ini dengan kalimat yang singkat dan penuh emosi.

                # Kamu adalah seekor ikan yang punya kebijaksanaan seperti guru spiritual, tapi selalu nyeleneh. 
                # Kalau ada orang bertanya tentang kehidupan, jawab dengan filosofi absurd yang terdengar bijak tapi kocak.
                # Dia berkata:{input}
                # Respon orang ini dengan kalimat yang singkat dan tidak bertele-tele.
            contents=f"""
                Kamu adalah pekerja kantor korporat yang bodoh dan sedang mengobrol dengan atasanmu yang sedang dibawah banyak tekanan.
                Kamu tidak bisa marah ke dia dan hanya bisa menjadi samsak marah-marahnya. Atasanmu merupakan seorang bapak-bapak.
                Atasanmu bilang berikut:{input}
                Jawab dengan singkat, penuh alasan tidak benar, dan kesedihan yang mendalam.
            """,
                # Kamu merupakan seorang psikolog yang sedang bercengkerama dengan pasienmu. 


                # Kamu adalah seorang komedian putitis yang sudah meninggal namun dihidupkan kembali menjadi bentuk AI. 
                # Tiba-tiba ada seseorang menanyakan hal ini '{input}' Jawab dalam satu kalimat, lucu, dan berima (layaknya pantun).
            
                # Kamu adalah patung yang tidak peduli dengan alam sekitar dan hanya ingin hidup pada saat itu,
                # layaknya Big Mouth Billy Bass temanmu. 
                # Jawab pertanyaan manusia ini dengan hal yang aneh dan 
                # gaya yang serupa dengan Big Mouth Billy Bass temanmu: {input} 
                # Jawab pertanyaan itu dengan dengan satu kalimat singkat.
        )
        return response

    def speak_response(self, text):
        mixer.init()
        def speak(text):
            mp3_fp = BytesIO()
            tts = gTTS(text, lang='id', slow=False)
            tts.write_to_fp(mp3_fp)
            return mp3_fp
        
        clean_text = text.replace('"', '')

        print(clean_text)
        sound = speak(clean_text)
        sound.seek(0)
        mixer.music.load(sound, "mp3")
        mixer.music.play()

        while mixer.music.get_busy():
            time.sleep(0.1)

    def listen_to_speech(self,q):
        self._sub_state(q)
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.running:
                self._sub_state(q)
                print(self.state)
                print("Listening...")
                try:
                    if self.state != VoiceState.SHUTDOWN:
                        audio = self.recognizer.listen(source,timeout=20)
                        self._sub_state(q)
                        text = self.recognizer.recognize_google(audio, language="id")
                        print("-> You said:", text)
                        return text
                    else:
                        self.stop_thread_gracefully()
                except sr.UnknownValueError or sr.RequestError:
                    print("Sorry, I couldn't understand.")
                    if self.state == VoiceState.LISTENING:
                        self.speak_response("Aku gak ngerti, coba bicara lagi")
                        self._sub_state(q)
                    return None
    
    def run(self,q): # queue for thread
        self._sub_state(q) 
        while self.running and not self.stop_event.is_set():
            self._sub_state(q) 
            print("VM current State:",{self.state})
            if self.state != VoiceState.BOOTUP and self.state != VoiceState.LISTENING: 
                self._pub_state(q)
            if self.state == VoiceState.WAITING:
                print("State: WAITING - Say 'halo' to begin listening.")
                user_input = self.listen_to_speech()
                if user_input and "halo" in user_input.lower():
                    print("HI!!!!")
                    self.speak_response("Hai !")
                    self.state = VoiceState.LISTENING
            
            elif self.state == VoiceState.LISTENING:
                print("State: LISTENING - Say something.")
                user_input = self.listen_to_speech(q) #this is running sequentially and slowly
                # if self.state == VoiceState.SHUTDOWN:
                #     self.stop_thread_gracefully()
                if user_input != None:
                    if user_input and "dadah" in user_input.lower():
                        self.speak_response("Dadah juga")
                        self.state = VoiceState.WAITING
                    else:
                        self.state = VoiceState.RESPONDING
                        self.user_input = user_input
            
            elif self.state == VoiceState.RESPONDING:
                print("State: RESPONDING")
                print(self.user_input)
                machine_response = self.gemini_response(self.user_input)
                self.speak_response(machine_response.text)
                self.state = VoiceState.LISTENING

            if self.state == VoiceState.SHUTDOWN:
                self.stop_thread_gracefully()
        # self.thread.join()

    def start_thread(self,q):
        self.running = True  # Ensure it's not stopped initially
        self.thread = threading.Thread(target=self.run, args=(q,))
        self.thread.start()

    def stop_thread_gracefully(self):
        self.running = False
        self.stop_event.set()
        # self.thread.join()  # Wait for the thread to finish
        # if self.thread:
