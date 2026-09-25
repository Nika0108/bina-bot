import os
from threading import Thread
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask

# --- Flask Server (Render portu tanıması və yatmaması üçün) ---
app = Flask(__name__)


@app.route("/")
def home():
  return "Bina.az Bot işləyir!"


# --- Tənzimləmələr (Token və Chat ID) ---
TOKEN = "7964063386:AAE1zcok3upnfM3y165uPweVTIumMrS-xr8"  # Öz bot tokeninizi bura yazın
CHAT_ID = "8713102170"  # Göndəriləcək şəxsin chat id-sini bura yazın
sent_ads = set()


def send_telegram(message):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Telegram xətası: {e}")


def check_bina():
  """Bina.az-ı mütəmadi olaraq yoxlayan əsas dövrə"""
  while True:
    print("Elanlar yoxlanılır...")
    try:
      # Səhifəni yoxlamaq üçün əvvəlcədən yazdığınız kodları
      # və ya sorğuları bu hissəyə əlavə edə bilərsiniz.
      # Məsələn:
      # url = "https://bina.az/baki/alqi-satqi/menziller"
      # ...
      pass
    except Exception as e:
      print(f"Yoxlama zamanı xəta baş verdi: {e}")

    # Hər dəfə yoxlamadan sonra neçə saniyə gözləyəcəyini təyin edin (məsələn: 60 saniyə)
    time.sleep(60)


if _name_ == "_main_":
  # 1. Botu arxa planda (Thread ilə) işə salırıq
  bot_thread = Thread(target=check_bina)
  bot_thread.daemon = True
  bot_thread.start()

  # 2. Flask serverini işə salırıq (Render-in tələb etdiyi PORT üzərindən)
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)