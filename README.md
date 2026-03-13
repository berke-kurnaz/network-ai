# Otonom Ağ Yönetimi ve Siber Tehdit Savunma Sistemi 🛡️🤖 ( BERKE KURNAZ)

Bu proje, ağ altyapılarına yönelik siber saldırıları (DDoS, Brute Force, Worm vb.) **Deep Reinforcement Learning (Derin Pekiştirmeli Öğrenme - DQN)** algoritmaları kullanarak tespit eden ve saldırganı otonom olarak ağdan izole eden yapay zeka destekli bir İhlal Önleme Sistemidir (IPS).

## 🚀 Projenin Amacı (Bitirme Tezi)
Sistemin temel amacı; ağ üzerindeki anomaliyi (CPU, RAM, PPS ve Bant Genişliği değişimleri) saniyeler içinde analiz edip, ağa zarar veren hedef IP'yi dinamik olarak bularak Router'ın (MikroTik) güvenlik duvarına otonom müdahale etmektir. Geleneksel kural tabanlı sistemlerin aksine, sistem kendi kararlarını yapay zeka ile alır.

## 🧠 Kullanılan Teknolojiler
* **Yapay Zeka:** Python 3, Stable-Baselines3 (DQN Modeli), NumPy
* **Ağ ve Güvenlik:** MikroTik RouterOS (REST API), Kali Linux (Tehdit Simülasyonu)
* **Sanallaştırma:** VirtualBox (Kapalı devre Host-Only ağ mimarisi)

## 🎯 Temel Özellikler
1. **Otonom Anomali Tespiti:** Sistem CPU yükü, RX/TX paket oranlarını (PPS) 7/24 dinleyerek olağandışı trafik örüntülerini yakalar.
2. **Dinamik Avcı (Dynamic Target Detection):** Ajan körü körüne engelleme yapmaz. Ağdaki aktif bağlantıları (`/ip/firewall/connection`) tarayıp, anomali yaratan asıl IP'yi o an tespit eder.
3. **Self-Lockout Koruması:** Yapay zeka, kendini veya router'ı engellememek için güvenli liste (Whitelist) mantığıyla çalışır.
4. **Otonom Müdahale:** Tespit edilen saldırganın IP adresi, MikroTik REST API (PUT metodu) üzerinden anında Firewall'a `Drop` kuralı olarak yazılır.

## 🛠️ Kurulum ve Kullanım (Simülasyon Ortamı)
1. `192.168.56.x` ağ bloğunda bir MikroTik RouterOS sanal makinesi ayağa kaldırılır.
2. Savunma Ajanı (Windows) üzerinden `otonom_ajan.py` çalıştırılarak yapay zeka nöbete başlatılır.
3. Saldırgan (Kali Linux - 192.168.56.102) üzerinden `tehdit_similatoru.py` çalıştırılarak hedef router'a yüksek yoğunluklu stres testi uygulanır.
4. Yapay Zeka anomaliyi sezer, ağ tablosunu okur ve saniyeler içinde Kali Linux'un IP adresini MikroTik üzerinden banlayarak ağı kurtarır.
