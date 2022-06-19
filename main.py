import base64
from fastapi import FastAPI, WebSocket

app = FastAPI(title='WebSocket Server')

def predict_command(audio_file):
    command = "command"
    confidence = 0.1
    return command, confidence

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print('Accepting client connection...')
    await websocket.accept()
    while True:
        try:
            # Wait for any message from the client
            value = await websocket.receive_text()
            wav_file = open("command.wav", "wb")
            # mp3_file = open("command.mp3", "wb")
            decode_string = base64.b64decode(value)
            wav_file.write(decode_string)
            # mp3_file.write(decode_string)
            
            command, confidence = predict_command(wav_file)
            # Send message to the client
            resp = {
                'command': command,
                'confidence': confidence
            }
            await websocket.send_json(resp)
        except Exception as e:
            print('error:', e)
            break
    print('Bye..')
