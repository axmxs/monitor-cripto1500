# start.py

from threading import Thread
import time
import logging

from main import iniciar_main
from memebot import iniciar_memebot

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

if __name__ == "__main__":
    logging.info("🚀 Iniciando monitor de carteira e memebot...")
    Thread(target=iniciar_main, daemon=True).start()
    time.sleep(3)
    Thread(target=iniciar_memebot, daemon=True).start()
    # Mantém o processo vivo
    while True:
        time.sleep(60)
