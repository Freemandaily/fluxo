from typing import List
from core.config import get_mongo_connection, get_redis_connection
from core.pubsub.channel_manager import ChannelNames
from data_pipeline.pipeline import Pipeline

class yield_agent:
    def __init__(self):
        self.redis_db = get_redis_connection()
        self.mongo_db = get_mongo_connection()


    # Fetch yield protocol and yields
    async def yield_opportunity(self):
        """
            Fetch yield opportunities from the database
        """
        try:
            yield_collection = self.mongo_db['Yield_Protocol']
            store_id = "Mantle_yield_protocol"
            
            yield_data = yield_collection.find_one({"_id": store_id})
            
            if not yield_data:
                return []
            
            return yield_data.get('protocol', [])
        except Exception as e:
            print(f"Error fetching yield opportunities: {e}")
            return []
        
