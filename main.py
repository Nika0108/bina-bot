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
TOKEN = "7964063386:AAE1zcok3upnfM3y165uPweVTIumMrS-xr8"
CHAT_ID = "8713102170"

# Göndərilən elanların linklərini yadda saxlamaq üçün set
sent_ads = set()


def send_telegram(message):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Telegram xətası: {e}")


def check_bina():
  """Bina.az-ı mütəmadi olaraq yoxlayan əsas dövrə"""
  global sent_ads
  url = "https://bina.az/baki/alqi-satqi/menziller"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  while True:
    print("Elanlar yoxlanılır...")
    try:
      response = requests.get(url, headers=headers)
      if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # Bina.az-dakı elan kartlarını tapırıq
        items = soup.find_all("div", class_="ads-i")

        # Əgər ilk dəfədirsə, mövcud elanları bazaya yığırıq ki, köhnələri göndərməsin
        if not sent_ads and items:
          for item in items:
            link_tag = item.find("a", class_="ads-i__link")
            if link_tag and "href" in link_tag.attrs:
              sent_ads.add(link_tag["href"])
          print(
              "İlkin elanlar yadda saxlanıldı. Yeni elanlar gözlənilir..."
          )
        else:
          # Yeni elanları yoxlayırıq (tərsinə çeviririk ki, köhnədən yeniyə doğru getsin)
          for item in reversed(items):
            link_tag = item.find("a", class_="ads-i__link")
            if link_tag and "href" in link_tag.attrs:
              link = link_tag["href"]
              if not link.startswith("http"):
                link = "https://bina.az" + link

              # Əgər bu elan hələ göndərilməyibsə
              if link not in sent_ads:
                sent_ads.add(link)

                # Qiymət və şəhər/rayon məlumatını çəkməyə çalışırıq
                price_tag = item.find("div", class_="ads-i__price")
                price = (
                    price_tag.get_text(strip=True)
                    if price_tag
                    else "Qiymət yoxdur"
                )

                loc_tag = item.find("div", class_="ads-i__location")
                location = (
                    loc_tag.get_text(strip=True)
                    if loc_tag
                    else "Ünvan yoxdur"
                )

                message = (
                    "<b>Yeni bina.az elanı!</b>\n\n💰"
                    f" <b>Qiymət:</b> {price}\n📍 <b>Yer:</b>"
                    f" {location}\n🔗 <a href='{link}'>Elana keçid</a>"
                )
                send_telegram(message)
                print(f"Yeni elan göndərildi: {link}")
                time.sleep(2)  # Mesajlar arası qısa fasilə
      else:
        print(f"Sayt xəta kodu qaytardı: {response.status_code}")
    except Exception as e:
      print(f"Yoxlama zamanı xəta baş verdi: {e}")

    # Hər 60 saniyədən bir yenidən yoxlayır
    time.sleep(60)


if __name__ == "__main__":
  # 1. Botu arxa planda (Thread ilə) işə salırıq
  bot_thread = Thread(target=check_bina)
  bot_thread.daemon = True
  bot_thread.start()

  # 2. Flask serverini işə salırıq (Render-in tələb etdiyi PORT üzərindən)
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)