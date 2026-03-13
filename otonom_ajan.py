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

# AJANIN KENDİ IP ADRESİ (Asla engellenmemesi gereken IP)
ajan_ip = "192.168.56.1" 

url_resource = f"http://{mikrotik_ip}/rest/system/resource"
url_traffic = f"http://{mikrotik_ip}/rest/interface/monitor-traffic"
url_firewall = f"http://{mikrotik_ip}/rest/ip/firewall/filter"
url_connections = f"http://{mikrotik_ip}/rest/ip/firewall/connection"

print("🧠 Gelişmiş Yapay Zeka Modeli (V2) Yükleniyor...")
model = DQN.load("mikrotik_dqn_model_v2")
print("✅ Dinamik Avcı Ajan Aktif! Ağ 7/24 İzleniyor...\n")

saldiri_altinda = False
engellenen_ip = None

def en_aktif_saldirgani_bul():
    """Ağdaki bağlantıları analiz edip en çok trafik üreten IP'yi tespit eder."""
    try:
        res = requests.get(url_connections, auth=HTTPBasicAuth(username, password), timeout=3)
        baglantilar = res.json()
        
        ip_sayaclari = {}
        if isinstance(baglantilar, list):
            for b in baglantilar:
                src = b.get("src-address", "")
                if src:
                    ip = src.split(":")[0] 
                    if ip != ajan_ip and ip != mikrotik_ip and ip != "127.0.0.1":
                        ip_sayaclari[ip] = ip_sayaclari.get(ip, 0) + 1
                        
        if ip_sayaclari:
            en_saldirgan_ip = max(ip_sayaclari, key=ip_sayaclari.get)
            baglanti_sayisi = ip_sayaclari[en_saldirgan_ip]
            print(f"🕵️‍♂️ [HEDEF TESPİTİ] Ağ tarandı! Şüpheli IP: {en_saldirgan_ip} ({baglanti_sayisi} aktif bağlantı)")
            return en_saldirgan_ip
    except Exception as e:
        print(f"⚠️ Bağlantı tablosu okunamadı: {e}")
    return None

def saldirgani_engelle(supheli_ip):
    print(f"[🤖 DİNAMİK MÜDAHALE] {supheli_ip} adresine Firewall Drop kuralı yazılıyor...")
    payload = {
        "chain": "input",
        "src-address": supheli_ip,
        "action": "drop",
        "comment": f"AI Ajan Tarafindan Engellendi: {supheli_ip}"
    }
    try:
        # MikroTik API kural eklemek için PUT kullanır
        res = requests.put(url_firewall, auth=HTTPBasicAuth(username, password), json=payload, timeout=3)
        if res.status_code in [200, 201]:
            print(f"🛡️ Başarılı! {supheli_ip} IP'si Firewall'a gömüldü. Sistem güvende.")
        else:
            print(f"❌ Kural Yazılamadı! MikroTik Hatası: {res.text}")
    except Exception as e:
        print(f"Hata (Firewall İletişimi): {e}")

try:
    while True:
        try:
            res_resource = requests.get(url_resource, auth=HTTPBasicAuth(username, password), timeout=3)
            data_resource = res_resource.json() if isinstance(res_resource.json(), dict) else {}
            cpu_load = int(data_resource.get('cpu-load', 0))
            free_ram_mb = int(data_resource.get('free-memory', 0)) / (1024 * 1024)

            payload_traf = {"interface": izlenecek_port, "once": ""}
            res_traffic = requests.post(url_traffic, auth=HTTPBasicAuth(username, password), json=payload_traf, timeout=3)
            json_yanit = res_traffic.json()
            
            if isinstance(json_yanit, list) and len(json_yanit) > 0:
                data_traffic = json_yanit[0]
            else:
                time.sleep(1); continue 
            
            rx_mbps = int(data_traffic.get('rx-bits-per-second', 0)) / 1_000_000
            tx_mbps = int(data_traffic.get('tx-bits-per-second', 0)) / 1_000_000
            rx_pps = int(data_traffic.get('rx-packets-per-second', 0))
            tx_pps = int(data_traffic.get('tx-packets-per-second', 0))

            current_state = np.array([cpu_load, free_ram_mb, rx_mbps, tx_mbps, rx_pps, tx_pps], dtype=np.float32)

            action, _states = model.predict(current_state, deterministic=True)
            zaman = datetime.now().strftime("%H:%M:%S")

            if action == 1: 
                if not saldiri_altinda:
                    print(f"\n🚨 [ANOMALİ TESPİTİ] {zaman} - Yapay Zeka saldırı seziyor! (CPU: %{cpu_load} | PPS: {rx_pps})")
                    hedef_ip = en_aktif_saldirgani_bul()
                    
                    if hedef_ip:
                        saldirgani_engelle(hedef_ip)
                        engellenen_ip = hedef_ip
                        saldiri_altinda = True
                    else:
                        print("⚠️ Şüpheli IP bulunamadı, ağ izlenmeye devam ediyor...")
                else:
                    print(f"⚠️ [MÜCADELE SÜRÜYOR] {zaman} - Sistem toparlanmaya çalışıyor (CPU: %{cpu_load})")
            else: 
                if not saldiri_altinda:
                    print(f"✅ [NORMAL] {zaman} - Ağ güvende. (CPU: %{cpu_load} | Trafik: {rx_mbps:.2f} Mbps)")
                else:
                    print(f"\n♻️ [DÜZELME] {zaman} - Yapay zeka ağın tamamen normale döndüğünü teyit etti.")
                    print(f"🎯 Etkisiz hale getirilen tehdit: {engellenen_ip}\n")
                    saldiri_altinda = False
            
            time.sleep(1)

        except requests.exceptions.RequestException:
            pass 
        except Exception as e:
            pass

except KeyboardInterrupt:
    print("\n🛑 Otonom Ajan durduruldu.")