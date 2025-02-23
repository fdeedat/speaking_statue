from voiceMachine import *
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if __name__ == "__main__":
    machine = voiceMachine(API_KEY)
    while True:
        machine.run()