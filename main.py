import base64
from fastapi import FastAPI, WebSocket
import os
import librosa
from tensorflow import keras
import numpy as np
from sklearn.preprocessing import StandardScaler
import json

scaler = StandardScaler()
app = FastAPI(title='WebSocket Server')
model = keras.models.load_model("./model_30000_without_silent.h5")
classes = ['a', 'ban', 'phai', 'trai']
max_length = 30000
def predict_command(audio_file):
    samples, sample_rate = librosa.load(audio_file, sr=22050)
    # samples, index = librosa.effects.trim(samples, top_db=30, frame_length=256, hop_length=64)
    if len(samples) <= max_length:
        samples = np.pad(samples, (0, max_length - len(samples)%max_length), mode='constant')
    else:
        samples = samples[:max_length]
    samples = scaler.fit_transform(samples.reshape(-1, 1)).reshape(1, max_length, 1)

    prob=model.predict(samples)

    if (max(prob[0]) > 0.8): 
        index=np.argmax(prob[0])
        command = classes[index]
        confidence = prob[0][index]
    else:
      command = 'silent'
      confidence = 1
    
    return command, confidence

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print('Accepting client connection...')
    await websocket.accept()
    while True:
        try:
            # Wait for any message from the client
            value = await websocket.receive_text()
            webm_file = "command.webm"
            webm_content = open("command.webm", "wb")
            decode_string = base64.b64decode(value)
            webm_content.write(decode_string)
            wav_file = "command.wav"

            # convert webm to wav
            print(f"./ffmpeg\ 2 -i ./{webm_file} ./{wav_file} -y")
            os.system(f"./ffmpeg\ 2 -i ./{webm_file} ./{wav_file} -y")
            
            command, confidence = predict_command(wav_file)

            # Send message to the client
            resp = {
                'command': command,
                'confidence': float(confidence)
            }
            await websocket.send_json(json.dumps(resp))
        except Exception as e:
            print('error:', e)
            break
    print('Bye..')
