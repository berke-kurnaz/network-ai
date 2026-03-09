import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class MikrotikEnv(gym.Env):
    """
    MikroTik router loglarını kullanarak oluşturulmuş özel bir Derin Pekiştirmeli Öğrenme ortamı.
    """
    def __init__(self, csv_file):
        super(MikrotikEnv, self).__init__()
        
        # CSV dosyasını okuyoruz
        self.df = pd.read_csv(csv_file)
        self.current_step = 0
        self.max_steps = len(self.df) - 1
        
        # Eylem Uzayı (Action Space): Ajanın yapabileceği hamleler
        # 0: İzin Ver (Normal akışa dokunma)
        # 1: Engelle (Firewall Drop kuralı yaz)
        self.action_space = spaces.Discrete(2)
        
        # Gözlem Uzayı (Observation Space): Ajanın göreceği veriler
        # Sırasıyla: CPU_Yuku_Yuzde, Bos_RAM_MB, Rx_Mbps, Tx_Mbps, Rx_PPS, Tx_PPS
        self.observation_space = spaces.Box(
            low=0, high=np.inf, shape=(6,), dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        """Eğitim her baştan başladığında ortamı sıfırlar."""
        super().reset(seed=seed)
        self.current_step = 0
        
        # İlk gözlemi (state) ve boş bir info sözlüğü döndürür (Gymnasium formatı)
        obs = self._get_obs()
        return obs, {}

    def _get_obs(self):
        """Mevcut adımdaki (satırdaki) router verilerini dizi olarak döndürür."""
        row = self.df.iloc[self.current_step]
        
        # Sadece sayısal metrikleri alıyoruz (Tarih_Saat kolonunu atlıyoruz)
        obs = np.array([
            row['CPU_Yuku_Yuzde'], 
            row['Bos_RAM_MB'], 
            row['Rx_Mbps'], 
            row['Tx_Mbps'], 
            row['Rx_PPS'], 
            row['Tx_PPS']
        ], dtype=np.float32)
        
        return obs

    def step(self, action):
        """Ajanın bir eylem (action) aldığı ve sonucunu gördüğü adım."""
        obs = self._get_obs()
        cpu_load = obs[0]
        rx_pps = obs[4]
        
        # Gerçekte bir saldırı var mı? (api.py'deki kuralına göre belirliyoruz)
        is_attack = (cpu_load > 80) or (rx_pps > 100)
        
        # Ödül / Ceza Mekanizması
        reward = 0
        if action == 1: # Ajan engelleme (Drop) yapmayı seçti
            if is_attack:
                reward = 10  # Başarılı! Saldırıyı doğru zamanda durdurdu.
            else:
                reward = -5  # Hatalı! Ağ normalken gereksiz yere trafiği kesti (False Positive).
        elif action == 0: # Ajan izin vermeyi (Pass) seçti
            if is_attack:
                reward = -10 # Kritik Hata! Saldırı altındayken müdahale etmedi, router tehlikede.
            else:
                reward = 1   # Doğru karar. Ağ normal akışında, her şey yolunda.

        # Bir sonraki adıma geç
        self.current_step += 1
        
        # Veri setinin sonuna gelindi mi?
        terminated = self.current_step >= self.max_steps
        truncated = False # Eğitim süresini manuel kesmek için kullanılır, şu an gerek yok
        
        # Yeni gözlem, ödül, bitiş durumları ve ek bilgileri döndür
        return self._get_obs(), reward, terminated, truncated, {}