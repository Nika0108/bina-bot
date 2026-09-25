import time
import requests
from bs4 import BeautifulSoup

# 1. Tənzimləmələr (BotFather-dən aldığınız məlumatlar)
TOKEN = "7964063386:AAE1zcok3upnfM3y165uPweVTIumMrS-xr8"  # Məsələn: "123456789:ABCdef..."
CHAT_ID = "8713102170"        # Məsələn: "987654321"

# Əvvəlcədən göndərilmiş elanların ID-lərini yadda saxlamaq üçün set
sent_ads = set()

def send_telegram_message(text):
    """Telegram-a mesaj göndərən funksiya"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Mesaj göndərilmədi: {e}")

def check_bina_ads():
    """Bina.az saytını yoxlayan və yeni elanları tapan funksiya"""
    # Bina.az mülkiyyətçi (sahibkar) axtarış linki
    url = "https://bina.az/baki/alqi-satqi/menziller?owner=true"
    
    # Saytın bizi bloklamaması üçün brauzer başlığı əlavə edirik
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Sayta qoşulmaq olmadı:", response.status_code)
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Saytdakı elan bloklarını tapırıq
        ads = soup.find_all('div', class_='property')

        for ad in ads:
            # Hər elanın unikal ID-sini götürürük
            ad_id = ad.get('data-item-id')
            
            # Əgər bu elan hələ göndərilməyibsə
            if ad_id and ad_id not in sent_ads:
                # Elanın başlığı, qiyməti və linkini tapırıq
                title_elem = ad.find('div', class_='property__title')
                price_elem = ad.find('div', class_='property__price')
                link_elem = ad.find('a')
                
                title = title_elem.text.strip() if title_elem else "Başlıq yoxdur"
                price = price_elem.text.strip() if price_elem else "Qiymət yoxdur"
                link = "https://bina.az" + link_elem['href'] if link_elem else ""
                
                # Telegram üçün mesaj hazırlayırıq
                message = f"<b>🏠 Yeni Mülkiyyətçi Elanı!</b>\n\n{title}\n<b>💰 Qiymət:</b> {price}\n\n<a href='{link}'>🔗 Elana bax</a>"
                
                # Mesajı göndəririk
                send_telegram_message(message)
                
                # Bu elanı artıq göndərilənlərə əlavə edirik ki, təkrar gəlməsin
                sent_ads.add(ad_id)
                
    except Exception as e:
        print(f"Xəta baş verdi: {e}")

# 4. Sonsuz dövr (Bot hər 5 dəqiqədən bir saytı yoxlayacaq)
print("Bot işə düşdü və elanları izləyir...")
while True:
    check_bina_ads()
    time.sleep(300) # 300 saniyə = 5 dəqiqə gözləmə