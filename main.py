"""
Fluxo - AI Automation-as-a-Service for Web3 Intelligence
"""

import logging
import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from x402.fastapi.middleware import require_payment
from x402.facilitator import FacilitatorConfig

# from api.routes.onchain import user_subscribed_tokens_update

# Import Routes
from api import (
    automation_router,
    execution_router,
    governance_router,
    macro_router,
    market_data_router,
    onchain_router,
    portfolio_router,
    research_router,
    risk_router,
    x402_router,
    yield_router,
    social_router,
    alerts_router,
    system_router,
    digest_router,
    whale_router
)

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    # lifespan=lifespan,
    title="Fluxo API",
    description="AI Automation-as-a-Service for Web3 Intelligence",
    version="0.1.0"
)



# # Attach Al Agent Routes
# app.include_router(automation_router,prefix='/agent')
# app.include_router(execution_router,prefix='/agent')
# app.include_router(governance_router,prefix='/agent')
# app.include_router(macro_router,prefix='/agent')
# app.include_router(market_data_router,prefix='/agent')
# #app.include_router(portfolio_router,prefix='/agent')
# app.include_router(research_router,prefix='/agent')
# app.include_router(risk_router,prefix='/api/agent/risk',tags=['Risk'])
# app.include_router(x402_router,prefix='/agent',tags=['x402'])
# app.include_router(onchain_router,prefix='/api/agent/onchain',tags=['Onchain'])
# app.include_router(yield_router,prefix='/agent')
# app.include_router(social_router,prefix='/agent')
# app.include_router(alerts_router, prefix="/api/alerts", tags=["Alerts"])
# app.include_router(portfolio_router, prefix="/api/v1/agent", tags=["portfolio"])
# app.include_router(system_router, prefix="/api/v1/system", tags=["system"])
# app.include_router(digest_router, prefix="/api/v1/daily", tags=["market-update"])
# app.include_router(whale_router, prefix="/agent/whale", tags=["Whale"])


# # NOTE: Payment middleware commented out for local development
# app.middleware("http")(
#     require_payment(
#         price="$0.01",
#         pay_to_address='0xEd04925173FAD6A8e8939338ccF23244cae1fF12',
#         path='/api/v1/daily/digest',
#         network='base-sepolia',
#         facilitator_config=FacilitatorConfig(
#             url= "https://x402.treasure.lol/facilitator"
#         ),
#         # paywall_config=PaywallConfig(
#         #     cdp_client_key='==',
#         #     app_name='fluxo',
#         # )
#     )
# )


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "success": True,
        "message": "Fluxo API is running",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "status": "healthy"
    }

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



