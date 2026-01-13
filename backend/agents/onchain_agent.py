import ast
import asyncio
import json
from typing import List
from core.config import get_mongo_connection, get_redis_connection
from core.pubsub.channel_manager import ChannelNames
import logging
from datetime import datetime, UTC,timezone

logger = logging.getLogger(__name__)


class onchain_agent:
    def __init__(self):
        self.redis_db = get_redis_connection()
        self.mongo = get_mongo_connection()
        
        # ADD YOUR LOGIC - Whale thresholds
        self.whale_thresholds = {
            "MNT": 1000000,
            "mETH": 500000,
            "USDC": 2000000,
            "default": 100000
        }
    async def retrieve_transcton_from_db(self,wallet_address:str,limit=None)->list:
        """
            Retrieve User Transaction from db
            Retrieve data if cached in redis
            If not in db fetch from onchain and update db

        """
        try:
            # cache_key = f"user_tx:{wallet_address}"
            # if cached_data := await self.redis_db.get(cache_key):
            #     print('Using Cached Data')
            #     return json.loads(cached_data)

            store_id = "transactions"
            transaction_collection = self.mongo['User_Transaction']
            users_transactions_datas = transaction_collection.find_one({"_id":store_id})

            user_transactions = None
            if users_transactions_datas:
                user_transactions = users_transactions_datas.get(wallet_address)

            if not user_transactions:
                user_transactions = await self.fetch_transaction_and_update_db(wallet_address) 

            # Cache the result in Redis for 10 minutes
            # await self.redis_db.setex(cache_key, 600, json.dumps(user_transactions, default=str))
                
            return user_transactions
        except Exception as e:
            print(f'There is an error Retrieving Wallet {wallet_address} transactions. Issue {e}')
        

    async def fetch_transaction_and_update_db(self,query_wallet_address:str=None)->None:
        """
            Fetch Users Transaction Data And update the db with the Newest data 
            query_wallet_addres denotes the address  searched from th frontend
            There is no need t store the transaction of a random address transaction searc in db
            We store only the transaction of the address we monitored for easier retrival
        """
        from data_pipeline.pipeline import Pipeline
        pipeline = Pipeline()

        try:
            if not query_wallet_address:
                tracked_wallet = await self.redis_db.smembers("tracked_wallets")
            else:
                tracked_wallet = [query_wallet_address]
            
            if not tracked_wallet:
                print('There is No Wallet To Fetch Transactions')
                return 
            
            for wallet_address in tracked_wallet:
                transaction_data = await pipeline.fetch_transactions(wallet_address.decode() if not query_wallet_address else wallet_address )
                if not query_wallet_address:
                    asyncio.create_task(self._update_user_transactions(wallet_address.decode() if not query_wallet_address else wallet_address,transaction_data))
                    # await asyncio.sleep(2)
                else:
                    return transaction_data
        except Exception as e:
            print(f'There is an Issue fetching User wallet {wallet_address} Transactions Isue:{e}')

    async def _update_user_transactions(self,wallet_address:str,transaction_data:list)->None:
        print('Updating Db with Transaction Data')
        """
        Update user Transaction into db
        """
        try:
            if not transaction_data:
                return 
        
            store_id = "transactions"
            update_collection = self.mongo['User_Transaction']
            update_collection.update_one(
                {"_id":f"{store_id}"},
                {
                    "$set":{
                        f"{wallet_address}":transaction_data,
                        'updated_at':datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
        except Exception as e:
            print(f'There is error Updating wallet {wallet_address} Transactions.Issue:{e}')
        
    async def Receive_onchain_transfer(self):
        """
        Recieves Larger token transfer Event From Onchain 
        Pass it to smart money process
        pass it to whale detection Process
        """
        
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.ONCHAIN.value)

        async for message in pubsub.listen():
            try:
                if message['type'] != 'message':
                    print('No Data for onchaiin')
                    continue
                data = message['data']
                print(f"Received onchain transfer data: {data}")
                # Process the onchain transfer data as needed

                whale_threshold = 100_000
                data = data.decode('utf-8')
                data = ast.literal_eval(data)
                if float(data['amount_usd']) > whale_threshold: # TODO change the equality
                    continue
            
                # Lazy Import (Avoid Circular Error)
                from agents.orchestrator import AlertOrchestrator

                # Push To Alert Porcessor 
                alert = AlertOrchestrator()
                asyncio.create_task(alert.process_event(data))
                
            except:
                pass

            # # pubslish the whale data to other agents listening.
            # await self.redis_db.publish(ChannelNames.WHALE_MOVEMENT, data)
            
            # # ===== ADD YOUR WHALE DETECTION LOGIC HERE =====
            # try:
            #     transfer_data = json.loads(data) if isinstance(data, str) else data
                
            #     # YOUR WHALE DETECTION
            #     whale_analysis = await self.detect_whale(transfer_data)
                
            #     # Only publish if whale detected
            #     if whale_analysis["is_whale"]:
            #         await self.redis_db.redis.publish(
            #             'whale_watch_channel',
            #             json.dumps(whale_analysis)
            #         )
            # #         logger.info(f"🐋 Whale detected: {whale_analysis['summary']}")
            # except Exception as e:
            #     logger.error(f"❌ Whale detection failed: {str(e)}")
    
    # ADD YOUR WHALE DETECTION METHOD
    async def detect_whale(self) -> dict:
        """
        Detect if a transfer is a whale movement based on predefined thresholds.
        
        Args:
            transfer_data: The transfer data dictionary.
        """
        store_id = 'Whale_Transfers'
        whale_collection = self.mongo['Whale_Transfer_Data']
        whale_transfers = whale_collection.find_one({"_id":store_id})   

        return whale_transfers if whale_transfers else {}

            
