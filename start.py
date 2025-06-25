from threading import Thread
import time
import os

# Roda o monitoramento da carteira pessoal (main.py)
def iniciar_main():
    os.system("python main.py")

# Roda o Memebot para novas moedas (memebot.py)
def iniciar_memebot():
    os.system("python memebot.py")

if __name__ == '__main__':
    print("🚀 Iniciando monitor de carteira e memebot...")
    Thread(target=iniciar_main).start()
    time.sleep(3)  # pequeno delay para não colidir inicializações
    Thread(target=iniciar_memebot).start()
