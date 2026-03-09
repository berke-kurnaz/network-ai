import requests
from requests.auth import HTTPBasicAuth
import time
import csv
from datetime import datetime
import os

mikrotik_ip = "192.168.56.101" 
username = "admin"
password = "123"
izlenecek_port = "ether2" 

url_resource = f"http://{mikrotik_ip}/rest/system/resource"
url_traffic = f"http://{mikrotik_ip}/rest/interface/monitor-traffic"

# Kendi bilgisayarındaki doğru yolu kontrol et
csv_dosyasi = r"C:\Users\b\Desktop\network-ai\mikrotik_log.csv"

if not os.path.exists(csv_dosyasi):
    with open(csv_dosyasi, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Tarih_Saat", "CPU_Yuku_Yuzde", "Bos_RAM_MB", "Rx_Mbps", "Tx_Mbps", "Rx_PPS", "Tx_PPS"])

print("MikroTik Gelişmiş Ağ ve Sistem İzleme Başlatıldı...")
print(f"İzlenen Port: {izlenecek_port}")
print("Veriler 'mikrotik_log.csv' dosyasına kaydediliyor...\n")

try:
    while True:
        try: # --- İÇ DÖNGÜ: HATA YAKALAMA BURADA BAŞLIYOR ---
            
            # 1. Kaynak İstemi (Zaman aşımı eklendi)
            res_resource = requests.get(url_resource, auth=HTTPBasicAuth(username, password), timeout=3)
            res_resource.raise_for_status()
            data_resource = res_resource.json()
            
            if isinstance(data_resource, dict) and 'error' not in data_resource:
                cpu_load = int(data_resource.get('cpu-load', 0))
                free_ram_mb = int(data_resource.get('free-memory', 0)) / (1024 * 1024)
            else:
                cpu_load, free_ram_mb = 0, 0

            # 2. Trafik İstemi (Zaman aşımı eklendi)
            payload_traf = {"interface": izlenecek_port, "once": ""}
            res_traffic = requests.post(url_traffic, auth=HTTPBasicAuth(username, password), json=payload_traf, timeout=3)
            res_traffic.raise_for_status()
            
            json_yanit = res_traffic.json()
            
            if isinstance(json_yanit, list) and len(json_yanit) > 0:
                data_traf = json_yanit[0]
            else:
                time.sleep(1)
                continue 
            
            rx_bps = int(data_traf.get('rx-bits-per-second', 0))
            tx_bps = int(data_traf.get('tx-bits-per-second', 0))
            rx_pps = int(data_traf.get('rx-packets-per-second', 0))
            tx_pps = int(data_traf.get('tx-packets-per-second', 0))

            rx_mbps = rx_bps / 1_000_000
            tx_mbps = tx_bps / 1_000_000

            zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # CSV'ye yazma
            with open(csv_dosyasi, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([zaman, cpu_load, round(free_ram_mb, 2), round(rx_mbps, 2), round(tx_mbps, 2), rx_pps, tx_pps])
            
            if cpu_load > 80 or rx_pps > 100: 
                print(f"[{zaman}] ⚠️ ANOMALİ! CPU: %{cpu_load} | PPS: {rx_pps}")
            else:
                print(f"[{zaman}] Normal - CPU: %{cpu_load} | Gelen Trafik: {rx_mbps:.2f} Mbps")
                
            time.sleep(1)

        # HATA DURUMLARINDA ÇÖKMEYİ ENGELLEYEN BLOKLAR
        except requests.exceptions.HTTPError as errh:
            print(f"🚨 Web Servisi Boğuldu (HTTP 400/500): MikroTik cevap veremiyor! Sistem bekleniyor...")
            time.sleep(2)
        except requests.exceptions.Timeout:
            print("⏳ Zaman aşımı. Router stres altında nefes alamıyor...")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Bağlantı koptu. Router yeniden başlatılıyor veya kitlendi. Bekleniyor...")
            time.sleep(2)

except KeyboardInterrupt:
    print("\nİzleme durduruldu.")