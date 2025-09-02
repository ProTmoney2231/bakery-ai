from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.get('/')
def read_root():
    return {'status': 'ok', 'message': 'Simple FastAPI app is running!'}

@app.post('/assistant')
async def assistant(request: Request):
    data = await request.json()
    return {'echo': data.get('message', 'No message received')}

@app.post('/chat')
async def chat(request: Request):
    data = await request.json()
    return {'chat_reply': f"You said: {data.get('message', '')}"}

if __name__ == '__main__':
    uvicorn.run('server:app', host='0.0.0.0', port=10000, reload=True)
