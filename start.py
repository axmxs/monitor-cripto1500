from threading import Thread
import time

from main import iniciar_main
from memebot import iniciar_memebot

if __name__ == '__main__':
    print("🚀 Iniciando monitor de carteira e memebot...")
    Thread(target=iniciar_main).start()
    time.sleep(3)
    Thread(target=iniciar_memebot).start()
