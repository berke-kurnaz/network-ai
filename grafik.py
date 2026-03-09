from tensorboard import program

# TensorBoard'u başlat ve log klasörümüzü göster
tb = program.TensorBoard()
tb.configure(argv=[None, '--logdir', './dqn_tensorboard/'])
url = tb.launch()

print("="*50)
print(f"📊 TensorBoard Başarıyla Başlatıldı!")
print(f"👉 Lütfen tarayıcından şu adrese git: {url}")
print("="*50)

# Programın hemen kapanmaması için bekletiyoruz
input("Kapatmak için ENTER tuşuna basın...")