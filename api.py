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
        res_resource = requests.get(url_resource, auth=HTTPBasicAuth(username, password))
        res_resource.raise_for_status()
        data_res = res_resource.json()
        
        cpu_load = int(data_res.get('cpu-load', 0))
        free_ram_mb = int(data_res.get('free-memory', 0)) / (1024*1024)

        payload = {"interface": izlenecek_port, "once": ""}
        res_traffic = requests.post(url_traffic, auth=HTTPBasicAuth(username, password), json=payload)
        res_traffic.raise_for_status()
        
        data_traf = res_traffic.json()[0] 
        
        rx_bps = int(data_traf.get('rx-bits-per-second', 0))
        tx_bps = int(data_traf.get('tx-bits-per-second', 0))
        rx_pps = int(data_traf.get('rx-packets-per-second', 0))
        tx_pps = int(data_traf.get('tx-packets-per-second', 0))

        rx_mbps = rx_bps / 1_000_000
        tx_mbps = tx_bps / 1_000_000

        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(csv_dosyasi, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([zaman, cpu_load, round(free_ram_mb, 2), round(rx_mbps, 2), round(tx_mbps, 2), rx_pps, tx_pps])
        
        # HATA DÜZELTİLDİ: Anomali anında da tüm veriler ekrana yazdırılıyor
        if cpu_load > 80 or rx_pps > 100: 
            print(f"[⚠️ ANOMALİ TESPİTİ] {zaman} - CPU: %{cpu_load} | İndirme: {rx_mbps:.2f} Mbps ({rx_pps} pps) | Yükleme: {tx_mbps:.2f} Mbps ({tx_pps} pps)")
        else:
            print(f"[OK] {zaman} - CPU: %{cpu_load} | İndirme: {rx_mbps:.2f} Mbps ({rx_pps} pps) | Yükleme: {tx_mbps:.2f} Mbps ({tx_pps} pps)")
            
        time.sleep(5)
        
except requests.exceptions.RequestException as e:
    print(f"Bağlantı hatası: {e}")
except KeyboardInterrupt:
    print("\nİzleme durduruldu. Veriler masaüstüne başarıyla kaydedildi.")