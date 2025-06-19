from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "✅ Bot está rodando com sucesso!"

def run():
    app.run(host='0.0.0.0', port=10000)

def manter_online():
    t = Thread(target=run)
    t.start()

manter_online()

# Aqui você pode importar e rodar seu BOT normalmente
import time

while True:
    print("⏱ Bot rodando...")
    time.sleep(600)
