import requests
from requests.auth import HTTPBasicAuth
import time
from datetime import datetime
import numpy as np
from stable_baselines3 import DQN

mikrotik_ip = "192.168.56.101" 
username = "admin"
password = "123"
izlenecek_port = "ether2"

url_resource = f"http://{mikrotik_ip}/rest/system/resource"
url_traffic = f"http://{mikrotik_ip}/rest/interface/monitor-traffic"
url_firewall = f"http://{mikrotik_ip}/rest/ip/firewall/filter"

# YENİ EĞİTİLEN (V2) YAPAY ZEKA MODELİNİ YÜKLE
print("🧠 Gelişmiş Yapay Zeka Modeli (V2) Yükleniyor...")
model = DQN.load("mikrotik_dqn_model_v2")
print("✅ Otonom Ajan Aktif! Ağ 7/24 İzleniyor...\n")

saldiri_altinda = False

def saldirgani_engelle(supheli_ip):
    print(f"\n[🤖 YAPAY ZEKA MÜDAHALESİ] {supheli_ip} adresi engelleniyor...")
    payload = {
        "chain": "input",
        "src-address": supheli_ip,
        "action": "drop",
        "comment": "AI DQN Ajan Tarafindan Engellendi"
    }
    try:
        requests.put(url_firewall, auth=HTTPBasicAuth(username, password), json=payload, timeout=3)
        print("🛡️ Firewall kuralı başarıyla yazıldı. Ağ korumaya alındı.")
    except Exception as e:
        print(f"Hata (Firewall): {e}")

try:
    while True:
        try:
            # 1. API'den System Resource Verilerini Çek (Hata korumalı)
            res_resource = requests.get(url_resource, auth=HTTPBasicAuth(username, password), timeout=3)
            data_resource = res_resource.json()
            
            if isinstance(data_resource, dict) and 'error' not in data_resource:
                cpu_load = int(data_resource.get('cpu-load', 0))
                free_ram_mb = int(data_resource.get('free-memory', 0)) / (1024 * 1024)
            else:
                cpu_load, free_ram_mb = 0, 0

            # 2. API'den Trafik Verilerini Çek (Hata korumalı)
            payload_traf = {"interface": izlenecek_port, "once": ""}
            res_traffic = requests.post(url_traffic, auth=HTTPBasicAuth(username, password), json=payload_traf, timeout=3)
            
            json_yanit = res_traffic.json()
            
            if isinstance(json_yanit, list) and len(json_yanit) > 0:
                data_traffic = json_yanit[0]
            else:
                # Cihaz aşırı stres altındaysa okuyamayıp es geçer
                time.sleep(1)
                continue 
            
            rx_bps = int(data_traffic.get('rx-bits-per-second', 0))
            tx_bps = int(data_traffic.get('tx-bits-per-second', 0))
            rx_pps = int(data_traffic.get('rx-packets-per-second', 0))
            tx_pps = int(data_traffic.get('tx-packets-per-second', 0))
            
            rx_mbps = rx_bps / 1_000_000
            tx_mbps = tx_bps / 1_000_000

            # Verileri V2 AI modelinin formatına çevir
            current_state = np.array([cpu_load, free_ram_mb, rx_mbps, tx_mbps, rx_pps, tx_pps], dtype=np.float32)

            # 3. YAPAY ZEKA KARARI (Tahmin - V2 Devrede)
            action, _states = model.predict(current_state, deterministic=True)
            zaman = datetime.now().strftime("%H:%M:%S")

            # 4. EYLEM UYGULAMA
            if action == 1: 
                if not saldiri_altinda:
                    print(f"🚨 [ANOMALİ TESPİTİ] {zaman} - Ajan tehdit algıladı! (CPU: %{cpu_load} | PPS: {rx_pps})")
                    saldirgani_engelle("192.168.56.200") 
                    saldiri_altinda = True
                else:
                    print(f"⚠️ [MÜCADELE SÜRÜYOR] {zaman} - Tehdit baskısı devam ediyor (CPU: %{cpu_load} | Trafik: {rx_mbps:.2f} Mbps)")
            else: 
                if not saldiri_altinda:
                    print(f"✅ [NORMAL] {zaman} - Sistem temiz. (CPU: %{cpu_load} | Trafik: {rx_mbps:.2f} Mbps)")
                else:
                    print(f"♻️ [DÜZELME] {zaman} - Yapay zeka ağın tamamen normale döndüğünü teyit etti.")
                    saldiri_altinda = False
            
            time.sleep(1)

        except requests.exceptions.RequestException:
            print("⏳ Hedef router ağır saldırı altında yanıt veremiyor, ajan ayakta ve bekliyor...")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Anlık Veri Kopması, Ajan devam ediyor...")
            time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 Otonom Ajan manuel olarak durduruldu.")