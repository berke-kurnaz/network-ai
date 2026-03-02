import requests
from requests.auth import HTTPBasicAuth
import time
from datetime import datetime

mikrotik_ip = "192.168.56.101" 
username = "admin"
password = "123"
izlenecek_port = "ether2"

# API Uç Noktaları
url_resource = f"http://{mikrotik_ip}/rest/system/resource"
url_traffic = f"http://{mikrotik_ip}/rest/interface/monitor-traffic"
url_firewall = f"http://{mikrotik_ip}/rest/ip/firewall/filter"

# Ajanın durumu takip etmesi için bayrak (Sürekli aynı kuralı yazmasın diye)
saldiri_altinda = False

def saldirgani_engelle(supheli_ip):
    """Ajanın Firewall'a kural yazdığı Aktüatör fonksiyonu"""
    print(f"\n[🛡️ AJAN DEVREDE] {supheli_ip} adresi için engelleme kuralı oluşturuluyor...")
    
    payload = {
        "chain": "input",
        "src-address": supheli_ip,
        "action": "drop",
        "comment": "Otonom Ajan tarafindan anomali tespiti uzerine engellendi!"
    }
    
    try:
        # Firewall'a POST isteği atarak kuralı ekliyoruz
        res = requests.put(url_firewall, auth=HTTPBasicAuth(username, password), json=payload)
        res.raise_for_status()
        print("[✅ BAŞARILI] Saldırgan IP'si Firewall üzerinden tamamen bloklandı!\n")
    except requests.exceptions.RequestException as e:
        print(f"[❌ HATA] Kural eklenemedi: {e}\n")


print("🤖 Otonom Güvenlik Ajanı Başlatıldı...")
print("Ağ trafiği ve sistem kaynakları analiz ediliyor...\n")

try:
    while True:
        # 1. SENSÖR AŞAMASI (Veri Toplama)
        res_resource = requests.get(url_resource, auth=HTTPBasicAuth(username, password)).json()
        cpu_load = int(res_resource.get('cpu-load', 0))

        payload_traf = {"interface": izlenecek_port, "once": ""}
        res_traffic = requests.post(url_traffic, auth=HTTPBasicAuth(username, password), json=payload_traf).json()[0]
        rx_pps = int(res_traffic.get('rx-packets-per-second', 0))

        zaman = datetime.now().strftime("%H:%M:%S")

        # 2. BEYİN AŞAMASI (Karar Verme - Eşik tabanlı model)
        if cpu_load > 80 or rx_pps > 100:
            if not saldiri_altinda:
                print(f"[⚠️ ANOMALİ] {zaman} - CPU: %{cpu_load} | PPS: {rx_pps} -> Kritik seviye aşıldı!")
                saldiri_altinda = True
                
                # 3. AKTÜATÖR AŞAMASI (Eylem)
                # Temsili bir saldırgan IP'sini engelliyoruz
                saldirgani_engelle("192.168.56.200") 
            else:
                print(f"[⚠️ DEVAM EDİYOR] {zaman} - Sistem hala yüksek yük altında (CPU: %{cpu_load})")
        else:
            if saldiri_altinda:
                print(f"\n[🕊️ NORMALE DÖNDÜ] {zaman} - Sistem stabil duruma geçti. (CPU: %{cpu_load})")
                saldiri_altinda = False
            else:
                print(f"[OK] {zaman} - Sistem Normal | CPU: %{cpu_load} | PPS: {rx_pps}")
                
        time.sleep(3) # Ajan 3 saniyede bir karar döngüsünü çalıştırır

except KeyboardInterrupt:
    print("\nAjan kapatıldı.")