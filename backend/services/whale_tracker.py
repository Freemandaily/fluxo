"""
Whale Tracker Service - Multi-Source Support
Supports multiple data sources with fallback options
"""

from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(_name_)


class DataSource(str, Enum):
    """Available whale data sources"""
    MOCK = "mock"
    DUNE = "dune"
    FLIPSIDE = "flipside"
    WHALE_ALERT = "whale_alert"
    NANSEN = "nansen"


class WhaleMovement:
    """Represents a large wallet movement"""
    def _init_(self, tx_hash: str, from_addr: str, to_addr: str,
                 token: str, amount: float, usd_value: float,
                 source: str = "unknown"):
        self.tx_hash = tx_hash
        self.from_address = from_addr
        self.to_address = to_addr
        self.token = token
        self.amount = amount
        self.usd_value = usd_value
        self.timestamp = datetime.utcnow()
        self.impact_score = self._calculate_impact(usd_value)
        self.data_source = source
    
    def _calculate_impact(self, usd_value: float) -> float:
        """Calculate impact score 0-10"""
        if usd_value > 10_000_000:
            return 10.0
        elif usd_value > 5_000_000:
            return 8.5
        elif usd_value > 1_000_000:
            return 7.0
        elif usd_value > 500_000:
            return 5.0
        else:
            return 3.0
    
    def to_dict(self):
        return {
            "transaction_hash": self.tx_hash,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "token": self.token,
            "amount": self.amount,
            "usd_value": self.usd_value,
            "timestamp": self.timestamp.isoformat(),
            "impact_score": self.impact_score,
            "data_source": self.data_source
        }


class WhaleTracker:
    """
    Multi-source whale movement tracker
    
    Supports (in priority order):
    1. Dune Analytics (primary)
    2. Flipside Crypto (backup)
    3. Mock data (testing)
    
    Not yet supported (Week 2+):
    - Nansen (if budget approved)
    - Whale Alert (no Mantle support)
    """
    
    def _init_(self, 
                 primary_source: DataSource = DataSource.MOCK,
                 api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize whale tracker with data source
        
        Args:
            primary_source: Primary data source to use
            api_keys: Dict of API keys {"dune": "key", "flipside": "key"}
        """
        self.primary_source = primary_source
        self.api_keys = api_keys or {}
        self.min_threshold_usd = 100_000
        
        # Track which sources are available
        self.available_sources = self._check_available_sources()
        
        logger.info(f"WhaleTracker initialized")
        logger.info(f"Primary source: {primary_source}")
        logger.info(f"Available sources: {self.available_sources}")
    
    def _check_available_sources(self) -> List[str]:
        """Check which data sources are configured"""
        available = [DataSource.MOCK]  # Always available
        
        if self.api_keys.get("dune"):
            available.append(DataSource.DUNE)
        if self.api_keys.get("flipside"):
            available.append(DataSource.FLIPSIDE)
        if self.api_keys.get("whale_alert"):
            available.append(DataSource.WHALE_ALERT)
        
        return [s.value for s in available]
    
    async def get_recent_movements(
        self,
        timeframe: str = "24h",
        min_value_usd: Optional[float] = None
    ) -> List[WhaleMovement]:
        """
        Get recent whale movements from configured source
        
        Falls back to next available source if primary fails
        """
        sources_to_try = [
            self.primary_source,
            DataSource.DUNE,
            DataSource.FLIPSIDE,
            DataSource.MOCK  # Always fallback to mock
        ]
        
        for source in sources_to_try:
            try:
                if source == DataSource.MOCK:
                    return self._get_mock_movements()
                elif source == DataSource.DUNE:
                    if self.api_keys.get("dune"):
                        return await self._fetch_from_dune(timeframe, min_value_usd)
                elif source == DataSource.FLIPSIDE:
                    if self.api_keys.get("flipside"):
                        return await self._fetch_from_flipside(timeframe, min_value_usd)
            except Exception as e:
                logger.warning(f"Source {source} failed: {e}. Trying next...")
                continue
        
        # If all fail, return mock
        logger.warning("All sources failed. Using mock data.")
        return self._get_mock_movements()
    
    def _get_mock_movements(self) -> List[WhaleMovement]:
        """Mock whale movements for testing"""
        logger.info("Using mock whale data")
        
        return [
            WhaleMovement(
                tx_hash="0xa1b2c3d4e5f6...",
                from_addr="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                to_addr="0x28C6c06298d514Db089934071355E5743bf21d60",
                token="mETH",
                amount=1500.0,
                usd_value=5_250_000,
                source="mock"
            ),
            WhaleMovement(
                tx_hash="0xb2c3d4e5f6a7...",
                from_addr="0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549",
                to_addr="0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503",
                token="USDC",
                amount=10_000_000,
                usd_value=10_000_000,
                source="mock"
            ),
            WhaleMovement(
                tx_hash="0xc3d4e5f6a7b8...",
                from_addr="0x1234567890abcdef1234567890abcdef12345678",
                to_addr="0xabcdef1234567890abcdef1234567890abcdef12",
                token="MNT",
                amount=2_000_000,
                usd_value=2_000_000,
                source="mock"
            ),
        ]
    
    async def _fetch_from_dune(self, timeframe: str, min_value: Optional[float]) -> List[WhaleMovement]:
        """Fetch from Dune Analytics - TODO Week 2"""
        raise NotImplementedError("Dune integration pending Week 2")
    
    async def _fetch_from_flipside(self, timeframe: str, min_value: Optional[float]) -> List[WhaleMovement]:
        """Fetch from Flipside Crypto - TODO Week 2"""
        raise NotImplementedError("Flipside integration pending Week 2")
    
    def get_summary(self, movements: List[WhaleMovement]) -> dict:
        """Generate summary with source information"""
        if not movements:
            return {
                "total_movements": 0,
                "total_volume_usd": 0,
                "summary": "No whale movements detected"
            }
        
        total_volume = sum(m.usd_value for m in movements)
        high_impact = [m for m in movements if m.impact_score >= 7.0]
        
        # Group by source
        by_source = {}
        for m in movements:
            by_source[m.data_source] = by_source.get(m.data_source, 0) + 1
        
        return {
            "total_movements": len(movements),
            "total_volume_usd": total_volume,
            "high_impact_movements": len(high_impact),
            "sources_used": by_source,
            "primary_source": self.primary_source.value,
            "summary": (
                f"{len(movements)} whale movements from {self.primary_source.value}. "
                f"Total volume: ${total_volume:,.0f}. "
                f"{len(high_impact)} high-impact transactions."
            )
        }
