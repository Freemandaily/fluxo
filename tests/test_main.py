# import time
# from fastapi.testclient import TestClient
# from backend.main import app

# client = TestClient(app)


def test_portfolio():
    
    url = "http://0.0.0.0:8000/agent/portfolio/?address=0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64"
    response = client.get(url)
    print(response.status_code)
    time.sleep(30)

    # task= response.json()
    # url = f"http://0.0.0.0:8000/agent/portfolio/status/task/{task['task_id']}"
    # response = client.get(url)
    # print(response.json())
    assert response.status_code == 200

# fetch all the yield on mantle protocol
def test_mantle_protocols_yield(): 
    url = "http://0.0.0.0:8000/agent/yield"
    response = client.get(url)
    print(response.status_code)

    task = response.json()
    if response.status_code == 200:
        time.sleep(60*2) # allow background task to finish

        url = f"http://0.0.0.0:8000/agent/yield/status/{task['task_id']}"
        response = client.get(url)
        result = response.json()

# fetch all the protocol on mantle
def test_mantle_protocols():
    url = "http://0.0.0.0:8000/agent/protocols"
    response = client.get(url)
    print(response.status_code)

    task = response.json()
    if response.status_code == 200:
        time.sleep(60*2) # allow background task to finish

        url = f"http://0.0.0.0:8000/agent/protocols/status/{task['task_id']}"
        response = client.get(url)
        result = response.json()
    

import asyncio
from web3 import Web3,AsyncHTTPProvider,AsyncWeb3,WebSocketProvider


transfer_event_signature = "Transfer(address,address,uint256)"
tranfer_topic = [ AsyncWeb3.keccak(text=transfer_event_signature)]
    
async def tranfers_event() :
    
    async with AsyncWeb3(WebSocketProvider('wss://mantle.drpc.org')) as w3:
        

        params = {
            "address": '0x201EBa5CC46D216Ce6DC03F6a759e8E766e956aE',
            "topics": [tranfer_topic]
        }
        subscription_id = await w3.eth.subscribe("logs", params)
        print(f"Subscribed to Transfer events with subscription ID: {subscription_id}")

        async for payload in w3.socket.process_subscriptions():
            print(payload)

asyncio.run(tranfers_event())