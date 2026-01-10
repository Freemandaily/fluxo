import asyncio
from typing import List
from dataclasses import asdict
from core import celery_app

# @celery_app.task
# def portfolio_task()->bool:
#     print('Running portfolio task...')
#     return {'portfolio_task':'started'}


@celery_app.task
def portfolio_task()->None:
    print('Fetching User Portfolio')

    # import to avoid circular import erro
    from agents.portfolio_agent import portfolio_agent

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    portfolio = portfolio_agent()
    loop.run_until_complete(
        portfolio.analyze_portfolio()
    )

@celery_app.task
def fetch_portfolio(wallet_address:str)->list:
    from agents.portfolio_agent import portfolio_agent

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    portfolio = portfolio_agent()
    try:
        print( f'Fetching Portfolio Data for Wallet {wallet_address}' )
        portfolio_data = loop.run_until_complete(
            portfolio.retrieve_portfolio_data(wallet_address)
        )
        return [asdict(item) for item in portfolio_data] if portfolio_data else []
    except Exception as e:
        print(f'There is an issue fetching Portfolio Data for Wallet {wallet_address}. Issue:{e}')