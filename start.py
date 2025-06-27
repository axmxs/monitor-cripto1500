from threading import Thread
import time
import main
import memebot

def iniciar_main():
    main.iniciar()

def iniciar_memebot():
    memebot.iniciar()

if __name__ == '__main__':
    print("🚀 Iniciando monitor de carteira e memebot...")
    Thread(target=iniciar_main).start()
    time.sleep(3)
    Thread(target=iniciar_memebot).start()
