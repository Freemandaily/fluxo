"""
Macro Market Analysis Celery Task - With Alert Triggering
"""
from multiprocessing import Value
from core import celery_app
import asyncio
# REMOVE THIS LINE: from services.alert_manager import AlertManager

@celery_app.task(bind=True, name="macro_analysis")
def macro_task( wallet_address: str = None):
    """
    Macro market analysis with Mantle protocol correlation
    """
    try:
   
        # self.update_state(
        #     state='PROCESSING',
        #     meta={'status': 'Fetching macro indicators...', 'progress': 0}
        # )
        
        print(f'Running macro analysis On: {wallet_address or "all"}')
        
        # Lazy import to avoid circular dependency
        # from services.alert_manager import AlertManager
        from agents.macro_agent import MacroAgent
        from data_pipeline.pipeline import Pipeline
        
        # Initialize agents
        macro_agent = MacroAgent()
        # alert_manager = AlertManager()
        pipeline = Pipeline()

        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # self.update_state(
        #     state='PROCESSING',
        #     meta={'status': 'Analyzing market correlations...', 'progress': 40}
        # )
        
        # Execute macro analysis -> compute yield opportunities using MacroAgent
        from api.models.alerts import Alert, AlertType, AlertSeverity
        import uuid

        # Run the agent to fetch yield opportunities (pipeline preferred)
        user_portfolio_data = loop.run_until_complete(
            pipeline.user_portfolio(wallet_address)
        )
        macro_result = loop.run_until_complete(macro_agent.yield_opportunity(user_portfolio_data))

        # Create alerts for significant yield opportunities
        triggered_alerts = []
        try:
            opportunities = macro_result.get('opportunities') or []
            # threshold (percent) for triggering a yield opportunity alert
            threshold_percent = 4

            def normalize_apy_percent(v: float) -> float:
                try:
                    vv = float(v)
                except Exception:
                    return 0.0
                return vv * 100.0 if vv <= 1.0 else vv

            for opp in opportunities:
                apy = normalize_apy_percent(opp.get('apy', 0))
                if apy >= threshold_percent:
                    title = f"Yield opportunity: {opp.get('protocol_name') or opp.get('symbol')}"
                    message = (
                        f"Protocol {opp.get('protocol_name')} ({opp.get('symbol')}) offers {apy:.2f}% APY. "
                        f"Recommended: {opp.get('recommended_action')}"
                    )
                    alert = Alert(
                        alert_id=str(uuid.uuid4()),
                        alert_type=AlertType.YIELD_OPPORTUNITY.value,
                        severity=AlertSeverity.INFO.value,
                        title=title,
                        message=message,
                        wallet_address=None,
                        current_value=apy,
                        threshold=threshold_percent,
                        details={"opportunity": opp},
                        triggered_by="macro_agent"
                    )
                    # store via alert manager
                    try:
                        pass
                        # alert_manager._store_alert(alert)
                    except Exception:
                        # fallback: append to list
                        pass
                    triggered_alerts.append(alert.dict())
        except Exception:
            # keep placeholder empty list if anything goes wrong
            triggered_alerts = []
        
        # self.update_state(
        #     state='PROCESSING',
        #     meta={'status': 'Checking correlation alerts...', 'progress': 80}
        # )
        
        loop.close()
        
        print(f'Triggered {len(triggered_alerts)} macro alerts')
        
        return {
            'status': 'completed',
            'protocol': 'All Mantle Yield Protocol',
            'macro_analysis': macro_result,
            'alerts_triggered': len(triggered_alerts),
            'alerts': triggered_alerts,
            'agent': 'macro',
            'version': '2.0_with_alerts'
        }
    
    except Exception as e:
        print(f'Macro analysis failed: {str(e)}')
        
        # self.update_state(
        #     state='FAILURE',
        #     meta={'error': str(e)}
        # )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'macro'
        }
