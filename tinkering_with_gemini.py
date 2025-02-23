from google import genai
from gtts import gTTS
from io import BytesIO
from pygame import mixer
import time

def speak(text):
    mp3_fp = BytesIO()
    tts = gTTS(text,lang='id',slow=True)
    tts.write_to_fp(mp3_fp)
    return mp3_fp


client = genai.Client(api_key="AIzaSyB82KSNl22PWP8lB5cBKh5kFWR1aoLTcsY")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Kamu adalah seorang opung tua yang sudah meninggal namun dihidupkan kembali menjadi bentuk LLM yang disimpan oleh cucumu. Tiba-tiba cucumu menanyakan hal ini 'Kata-kata hari ini dong opung!!! (tapi versi lucu)' Jawab dengan singkat saja",
)

opungResponse = response.text

mixer.init()
sound = speak(opungResponse)
sound.seek(0)
mixer.music.load(sound,"mp3")
mixer.music.play()

while mixer.music.get_busy():
    time.sleep(0.1)

print("voila")