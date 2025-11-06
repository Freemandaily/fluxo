"""
Risk Analysis Celery Task
Integrates Muhammad's Risk Agent with Freeman's Celery infrastructure
"""
from core import celery_app
import asyncio
from agents.risk_agent import RiskAgent
from api.models.schemas import PortfolioInput

@celery_app.task(bind=True, name="risk_analysis")
def risk_task(self, wallet_address: str, network: str = "mantle"):
    """
    Background task for portfolio risk analysis
    
    Args:
        wallet_address: Wallet address to analyze
        network: Blockchain network (default: mantle)
    
    Returns:
        dict: Risk analysis results
    """
    try:
        # Update task state
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Analyzing portfolio risk...', 'progress': 0}
        )
        
        print(f'Running risk analysis for wallet: {wallet_address}')
        
        # Create portfolio input
        portfolio = PortfolioInput(
            wallet_address=wallet_address,
            network=network
        )
        
        # Initialize Risk Agent
        risk_agent = RiskAgent()
        
        # Run async agent code in sync Celery task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Calculating risk factors...', 'progress': 50}
        )
        
        # Execute risk analysis
        risk_score = loop.run_until_complete(
            risk_agent.analyze_portfolio(portfolio)
        )
        loop.close()
        
        print(f'Risk analysis completed: Score {risk_score.score}')
        
        # Return structured result
        return {
            'status': 'completed',
            'wallet_address': wallet_address,
            'network': network,
            'risk_analysis': risk_score.dict(),
            'agent': 'risk'
        }
        
    except Exception as e:
        print(f'Risk analysis failed: {str(e)}')
        
        # Update task state to failure
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'risk'
        }
