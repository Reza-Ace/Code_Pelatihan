import requests

# URL ngrok kamu
url = "https://b0ad8dbdce0c.ngrok-free.app/predict"

# Baca file wav lalu ambil data byte mentahnya
with open("test2.wav", "rb") as f:
    audio_bytes = f.read()

# Kirim request
resp = requests.post(url, data=audio_bytes)

# Tampilkan hasil
print(resp.status_code, resp.text)
