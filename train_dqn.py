import gymnasium as gym
from stable_baselines3 import DQN
from mikrotik_env import MikrotikEnv
import os

def main():
    print("MikroTik Simülasyon Ortamı Yükleniyor...")
    env = MikrotikEnv('mikrotik_log.csv')

    # Logların kaydedileceği klasör (Grafikler için)
    log_dir = "./dqn_tensorboard/"
    os.makedirs(log_dir, exist_ok=True)

    print("Gelişmiş DQN Modeli oluşturuluyor...")
    
    # DAHA İYİ BİR EĞİTİM İÇİN OPTİMİZE EDİLMİŞ PARAMETRELER:
    model = DQN(
        "MlpPolicy", 
        env, 
        verbose=1,
        learning_rate=0.0005,      # Öğrenme hızı (Çok yüksek olursa ezberler, çok düşük olursa öğrenemez. 0.0005 idealdir)
        buffer_size=100000,        # Ajanın geçmişte yaşadığı anıların kaç tanesini hafızasında tutacağı
        learning_starts=1000,      # İlk 1000 adımda sadece rastgele takılıp çevreyi keşfedecek
        batch_size=64,             # Her seferinde hafızasından kaç anıyı çağırıp ders çıkaracağı
        gamma=0.99,                # Gelecekteki ödülleri ne kadar önemseyeceği (0.99 standarttır)
        exploration_fraction=0.2,  # Eğitim süresinin %20'si boyunca sürekli yeni şeyler deneyecek (Çok önemli!)
        tensorboard_log=log_dir    # Grafikleri çizdirmek için log tutma özelliği
    )

    # Eğitimi Başlat (Adım sayısını 50.000'den 200.000'e çıkarıyoruz)
    print("\nDerin Öğrenme Başlıyor... Bu işlem biraz sürebilir.")
    model.learn(total_timesteps=200_000, tb_log_name="DQN_Mikrotik_Run_1")

    # Modeli Kaydet
    model.save("mikrotik_dqn_model_v2")
    print("\n✅ Eğitim tamamlandı! 'mikrotik_dqn_model_v2.zip' kaydedildi.")

if __name__ == '__main__':
    main()