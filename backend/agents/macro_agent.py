from core.config import REDIS_CONNECT, MONGO_CONNECT
from core.pubsub.channel_manager import ChannelNames
from data_pipeline.schemas.data_schemas import UserPortfolio

from typing import Dict, Any, List, Optional
from dataclasses import asdict


class MacroAgent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT
        self.mongo_db = MONGO_CONNECT

    # Receives macroeconomic data from relevant sources
    async def receive_macro_data(self):
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.MACRO.value)

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            data = message["data"]
            print(f"Received macro data: {data}")
            # Process the macro data as needed

            # publish the processed macro data to other agents listening.
            await self.redis_db.publish("macro_processed_channel", data)

    async def yield_opportunity(self, portfolio_data:List[UserPortfolio] = None) -> Dict[str, Any]:
        """Return yield opportunities based on pipeline artifacts and optional portfolio context.

        This method prefers the precomputed pipeline data stored in MongoDB (collection
        `Yield_Protocol`) and will compute a small set of recommended opportunities.

        The returned structure is a dict with an `opportunities` list and a short `summary`.
        """
        # defensive: ensure mongo is available
        try:
            yield_protocol_collection = self.mongo_db["Yield_Protocol"]
        except Exception:
            return {"opportunities": [], "summary": "mongo_unavailable"}

        store_id = "Mantle_yield_protocol"
        yield_protocol_data = yield_protocol_collection.find_one({"_id": store_id})

        if not yield_protocol_data:
            return {"opportunities": [], "summary": "no_pipeline_data"}

        # pipeline artifact expected to contain a list under `protocols` or `yield_protocols`
        protocols: List[Dict[str, Any]] = (
            yield_protocol_data.get("protocol")
            or yield_protocol_data.get("yield_protocols")
            or []
        )

        # normalize portfolio tokens for quick matching
        portfolio_tokens = set()
        portfolio_addresses = set()
        if portfolio_data:
            assets_data = [asdict(data) for data in portfolio_data]
            for asset in assets_data:
                symbol = (asset.get("symbol") or asset.get("token_symbol") or "").lower()
                address = (asset.get("token_address") or asset.get("address") or "").lower()
                if symbol:
                    portfolio_tokens.add(symbol)
                if address:
                    portfolio_addresses.add(address)

        # compute top opportunities (by APY)
        def apy_of(p: Dict[str, Any]) -> float:
            try:
                return float(p.get("apy", 0) or p.get("estimated_apy", 0) or 0)
            except Exception:
                return 0.0

        top_by_apy = sorted(protocols, key=apy_of, reverse=True)[:20]

        opportunities: List[Dict[str, Any]] = []
        for proto in top_by_apy:
            symbol = (proto.get("symbol") or proto.get("token_symbol") or "").lower()
            
            apy = apy_of(proto)
            match = False
            existing_allocation = 0.0
            if symbol and symbol in portfolio_tokens:
                match = True
           
            # try to detect existing allocation if portfolio provided
            if portfolio_data:
                for a in [asdict(data) for data in portfolio_data]:
                    if  (a.get("symbol") or "").lower() == symbol:
                        existing_allocation = float(a.get("percentage_of_portfolio")  or 0)
                        break

            action = "consider_entering"
            if match:
                action = "consider_rebalancing"

            opportunities.append(
                {
                    "protocol_name": proto.get("project") or proto.get("protocol") or proto.get("protocol_name"),
                    "symbol": proto.get("symbol") or proto.get("token_symbol"),
                    "apy": apy,
                    "existing_allocation": existing_allocation,
                    "matched_with_portfolio": match,
                    "recommended_action": action,
                    "source": "Defillama",
                }
            )

        summary = {
            "num_protocols": len(protocols),
            "num_opportunities": len(opportunities),
            "top_apy": opportunities[0]["apy"] if opportunities else 0,
        }

        return {"opportunities": opportunities, "summary": summary}




