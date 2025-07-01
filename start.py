from threading import Thread
import time

from main import iniciar_main
from memebot_teste_loop_unico import main as iniciar_memebot  # CORRETO AGORA

if __name__ == '__main__':
    print("🚀 Iniciando monitor de carteira e memebot (teste loop único)...")
    Thread(target=iniciar_main).start()
    time.sleep(3)
    Thread(target=iniciar_memebot).start()
