from typing import List
from core.config import REDIS_CONNECT
from core.pubsub.channel_manager import ChannelNames
from data_pipeline.pipeline import Pipeline

class portfolio_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT
        

    # Receives processed market data from market_agent
    async def Receive_portfolio_data(self):
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.PORTFOLIO.value)

        async for message in pubsub.listen():
            if message['type'] != 'message':
                continue
            data = message['data']
            print(f"Received portfolio data: {data}")
            # Process the portfolio data as needed

            """"
                Portfolio management logic can be implemented here
            """

            # publish the final portfolio data to other agents listening.
            await self.redis_db.publish('final_portfolio_channel', data)
    

    
    async def analyze_portfolio(self,wallet_address:str)->List:
        pipeline = Pipeline()
        """
            This is for demonstration purpose,  the actuall fetching should be from db not directly from source
        """
        wallet_portfolio = await pipeline.user_portfolio(wallet_address)
        
        return wallet_portfolio
        