"""
Whale Tracking Celery Task
Monitors whale movements and triggers alerts
"""
from core import celery_app
import asyncio
from services.whale_tracker import WhaleTracker, DataSource

@celery_app.task(bind=True, name="whale_tracking")
def whale_task(self):
    """
    Celery task to fetch whale movements.
    """
    
    from agents.onchain_agent import onchain_agent
    agent = onchain_agent()
    
    try:
        print("🚀 Starting Whale Watcher"  )
        loop = asyncio.get_event_loop()

        detect_whale =  loop.run_until_complete(
            agent.detect_whale()
        )
        if detect_whale:
            print("✅ Whale movements detected and alerts generated.")
            whale_data = detect_whale.get("data", {})
            return "Whale tracking completed successfully."

    except Exception as e:
        
        print(f"❌ Whale tracking task failed: {e}")
        return 

@celery_app.task(bind=True, name="start_whale_tracker")
def start_whale_tracker(self):
    from data_pipeline.pipeline import Pipeline
    pipe = Pipeline()
    try:
        print("🚀 Starting Whale Tracker Task"  )
        loop = asyncio.get_event_loop()

        watcher =  loop.run_until_complete(
            pipe.watch_transfers()
        )
        print("✅ Whale tracker is running.")
        return "Whale tracker started successfully."

    except Exception as e:
        
        print(f"❌ Whale tracker task failed: {e}")
        return