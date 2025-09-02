from flask import Flask, request, jsonify
import numpy as np
import soundfile as sf
import io
import tensorflow as tf
import librosa
import time
from datetime import datetime

app = Flask(__name__)

# Load model
model = tf.keras.models.load_model("horn_detection_model1.h5")

def predict_from_raw_bytes(raw_bytes):
    audio_np = np.frombuffer(raw_bytes, dtype=np.int16)
    audio = audio_np.astype(np.float32) / 32768.0

    buffer = io.BytesIO()
    sf.write(buffer, audio, samplerate=16000, format='WAV')
    buffer.seek(0)

    y, sr = librosa.load(buffer, sr=16000)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T

    if mfcc.shape[0] < 32:
        pad_width = 32 - mfcc.shape[0]
        mfcc = np.pad(mfcc, ((0, pad_width), (0, 0)))
    else:
        mfcc = mfcc[:32, :]

    mfcc_input = np.expand_dims(mfcc, axis=0)

    start_time = time.time()
    pred = model.predict(mfcc_input)[0][0]
    end_time = time.time()

    is_klakson = pred > 0.9
    latency = round((end_time - start_time) * 1000, 2)

    now = datetime.now().strftime("%H:%M:%S.%f")
    print(f"[LOG] Waktu: {now} | Skor: {pred:.4f} | Hasil: {'Klakson' if is_klakson else 'Non-Klakson'} | Proses: {latency} ms", flush=True)

    return {"klakson": bool(is_klakson), "skor": float(pred), "latency_ms": latency}

@app.route("/predict", methods=["POST"])
def predict():
    if request.data:
        result = predict_from_raw_bytes(request.data)
        return jsonify(result)
    else:
        return jsonify({"error": "No audio file received"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
