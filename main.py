import pygame
from enum import Enum
import pygame
from pyvidplayer2 import Video
from enum import Enum
from voiceMachine import voiceMachine
from dotenv import load_dotenv
import threading
import queue
import os
import time

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

pygame.init()
# 1. provide video class with the path to your file
bootVideo = Video(r"C:\Users\LENOVO\Desktop\code4fun\llmAPI\resources\bootup.mp4")

class GameState(Enum):
    BOOTUP = 1
    WAITING = 2
    LISTENING = 3
    RESPONDING = 4
    SHUTDOWN = 5

class SadMan:
    def __init__(self):
        # Load images
        self.sprite_closed = pygame.image.load(r"C:\Users\LENOVO\Desktop\code4fun\llmAPI\resources\closed_mouth_1.png")
        self.sprite_open = pygame.image.load(r"C:\Users\LENOVO\Desktop\code4fun\llmAPI\resources\open_mouth_1.png")
        
        # Resize images (optional)
        self.sprite_closed = pygame.transform.scale(self.sprite_closed, (200, 200))
        self.sprite_open = pygame.transform.scale(self.sprite_open, (200, 200))
        
        self.talking = False
        self.frame_count = 0

    def updateState(self,state):
        if state == GameState.RESPONDING:
            self.talking = True
        else:
            self.talking = False
    
    def update(self, screen):
        # Toggle sprite every 10 frames to simulate talking
        if self.talking:
            if self.frame_count // 10 % 2 == 0:
                screen.blit(self.sprite_closed, (200, 150))
            else:
                screen.blit(self.sprite_open, (200, 150))
        else:
            screen.blit(self.sprite_closed, (200, 150))
        
        self.frame_count += 1

class Game:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.state = GameState.BOOTUP
        self.clock = pygame.time.Clock()
        self.running = True
        self.user_input = ""

        # other class
        self.sadman = SadMan()
        # self.voiceMachine = voiceMachine(API_KEY)

        # self.listening_thread = threading.Thread(target=self.voiceMachine.listen_to_speech)
        # self.listening_thread.daemon = True
        # self.listening_thread.start()

        pygame.display.set_caption("SAMSAK SOSIAL") 

    def _sub_state(self, threadQueue):
        '''
        Subscribe voice machine state from queue
        '''
        try:
            # Block until an update is available from the queue
            stateInQueue = threadQueue.get_nowait()
            if stateInQueue == 2:
                self.state = GameState.WAITING  # You can adjust the timeout if needed
            if stateInQueue == 3:
                self.state = GameState.LISTENING  # You can adjust the timeout if needed
            if stateInQueue == 4:
                self.state = GameState.RESPONDING  # You can adjust the timeout if needed
            print(f"Subscribe: {self.state}")
        except queue.Empty:
            pass  # If queue is empty, just pass (no state change)

    def _pub_state(self,threadQueue):
        '''
        Publish voice machine state to queue
        '''
        threadQueue.put(self.state.value)
        print(f"Publish: {self.state}")

    def run(self,q):
        interval = 0.1
        last_time = time.time()
        while self.running:
            self.screen.fill((255, 255, 255))  # Clear screen with white background
            
            # self.user_input = self.voiceMachine.listen_to_speech()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.state = GameState.SHUTDOWN
                    self._pub_state(q)

            if self.state == GameState.BOOTUP:
                bootVideo.draw(self.screen, (0, 0), force_draw=False)
                # pygame.display.update()
                print(bootVideo.get_pos())
                if bootVideo.get_pos() >= bootVideo.duration:
                    self.state = GameState.LISTENING
                    print(self.state)
                    self._pub_state(q)

            else:
                current_time = time.time()
                if current_time - last_time >= interval:
                    self._sub_state(q)
                    last_time = current_time
                # self._sub_state(q)
                # if self.state == GameState.WAITING:
                #     self._pub_state(q) 
                #     # print("State: WAITING - Say 'halo' to begin listening.")
                #     # if self.user_input and "halo" in self.user_input.lower():
                #     #     self.gameState = GameState.LISTENING
                #         # self.user_input = user_input

                # if self.state == GameState.LISTENING:
                #     # self._pub_state(q) 
                #     # print("State: LISTENING - Say 'halo' to begin listening.")
                #     # # user_input = self.voiceMachine.listen_to_speech()
                #     # if self.user_input and "halo" in self.user_input.lower():
                #     #     self.gameState = GameState.RESPONDING
                #         # self.user_input = user_input

                #         # self.sadman.updateState(self.gameState)
                #         # self.sadman.update(self.screen)
                        
                # if self.state == GameState.RESPONDING:
                #     # print("State: RESPONDING - Say 'halo' to begin listening.")
                #     # machine_response = self.voiceMachine.gemini_response(self.user_input)
                #     # self.voiceMachine.speak_response(machine_response.text)
                #     # self.state = GameState.LISTENING

                # self._pub_state(q)
                self.sadman.updateState(self.state)
                self.sadman.update(self.screen)
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
        # self._pub_state(q)
        # self.stop_thread_gracefully()

    def start_thread(self,q):
        self.running = True  # Ensure it's not stopped initially
        self.thread = threading.Thread(target=self.run, args=(q,))
        self.thread.start()

    def stop_thread_gracefully(self):
        self.running = False
        if self.thread:
            self.thread.join()  # Wait for the thread to finish


if __name__ == "__main__":

    stateQueue = queue.Queue()
    stateQueue.put(GameState.BOOTUP.value)

    game = Game()
    machine = voiceMachine(API_KEY)
    try:
        machine.start_thread(stateQueue)
        game.run(stateQueue)
        # sub.start_thread(stateQueue)

        while True: # stops the program from just dying and letting the thread run
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        machine.stop_thread_gracefully()
        # game.stop_thread_gracefully()
