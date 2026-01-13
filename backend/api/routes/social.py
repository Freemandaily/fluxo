"""
Social Sentiment API Routes
Enhanced with real data fetching
"""
from fastapi import APIRouter, HTTPException, Query
from celery.result import AsyncResult
from core import celery_app
from api.models.schemas import APIResponse
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/analyze')
async def analyze_sentiment(
    timeframe: str = "24h",
    focus_tokens: Optional[List[str]] = None
):
    """
    Start social sentiment analysis background task
    
    Query params:
    - timeframe: "1h", "24h", "7d" (default: "24h")
    - focus_tokens: Optional list of tokens to focus on
    
    Returns task_id to check progress
    """
    try:
        # Start background task
        # task = social_task.delay(timeframe, focus_tokens)
        
        return APIResponse(
            success=True,
            message="Sentiment analysis started",
            data={
                "task_id": 'This Endpoint is Disabled',
                "status": "processing",
                "timeframe": timeframe,
                "check_status": f"/agent/social/status/{task.id}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")


@router.get('/status/{task_id}')
async def get_social_status(task_id: str):
    """
    Get sentiment analysis task status and results
    """
    
    task_result = AsyncResult(task_id, app=celery_app)

    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.ready():
            return APIResponse(
                success=True,
                message='Task completed',
                data={
                    'task_id': task_id,
                    'status': 'completed',
                    'result': task_result.result
                }
            )
        elif task_result.failed():
            return APIResponse(
                success=False,
                message='Task failed',
                data={
                    'task_id': task_id,
                    'status': 'failed',
                    'error': str(task_result.info)
                }
            )
        else:
            return APIResponse(
                success=True,
                message='Task in progress',
                data={
                    'task_id': task_id,
                    'status': 'processing',
                    'message': 'Transaction  fetching in progress...'
                }
            )
    except Exception as e:
        logger.error(f"Failed to get task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post('/sentiment')
async def analyze_token_sentiment(
    token_symbol: str = Query(..., description="Token symbol (e.g., MNT, ETH)"),
    platforms: Optional[List[str]] = Query(None, description="Platforms to analyze")
):
    """
    Analyze social sentiment for a specific token (synchronous)
    
    Query params:
    - token_symbol: Token to analyze
    - platforms: Optional list of platforms (twitter, farcaster, reddit)
    
    Returns immediate sentiment analysis
    """
    try:
        # from agents.social_agent import SocialAgent
        
        # agent = SocialAgent(use_mock=False)
        # result = await agent.analyze_sentiment(token_symbol, platforms)
        
        return APIResponse(
            success=True,
            message=f"This endpoint is disabled",
            # data=result
        )
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/narratives/{token_symbol}')
async def get_trending_narratives(token_symbol: str):
    if "$" not in token_symbol:
        token_symbol = f"${token_symbol}"
    from tasks.agent_tasks.social_task import social_task,social_narrative_task
    """
    Get trending narratives about a token
    
    Path param:
    - token_symbol: Token to analyze
    
    Returns list of trending narratives
    """
    try:
        task = social_narrative_task.delay(token_symbol)
        return APIResponse(
            success=True,
            message=f"Narrative detection started for {token_symbol}",
            data={
                'task_id': task.id,
                'check_status': f"/agent/social/status/{task.id}"
            }
        )
                
    except Exception as e:
        logger.error(f"Failed to get narratives: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get('/platforms/{token_symbol}')
async def get_platform_breakdown(token_symbol: str):
    """
    Get sentiment breakdown by platform
    
    Path param:
    - token_symbol: Token to analyze
    
    Returns platform-specific sentiment analysis
    """
    try:
        # from agents.social_agent import SocialAgent
        
        # agent = SocialAgent(use_mock=False)
        # breakdown = await agent.get_platform_breakdown(token_symbol)
        
        return APIResponse(
            success=True,
            message=f"This endpoint is disabled",
            # data={
            #     "token_symbol": token_symbol,
            #     "breakdown": breakdown
            # }
        )
    except Exception as e:
        logger.error(f"Failed to get platform breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/supported-platforms')
async def get_supported_platforms():
    """Get list of supported social media platforms"""
    return APIResponse(
        success=True,
        message="Supported platforms",
        data={
            "platforms": [
                {
                    "name": "twitter",
                    "description": "Twitter/X posts and tweets",
                    "status": "active",
                    "data_points": ["tweets", "likes", "retweets", "replies"]
                },
                {
                    "name": "farcaster",
                    "description": "Farcaster decentralized social network",
                    "status": "active",
                    "data_points": ["casts", "mentions", "authors"]
                },
                {
                    "name": "reddit",
                    "description": "Reddit crypto subreddits",
                    "status": "active",
                    "data_points": ["posts", "comments", "upvotes", "subreddits"]
                }
            ]
        }
    )


@router.get('/social')
async def social_health():
    """Health check endpoint"""
    return {
        'agent': 'social',
        'status': 'operational',
        'version': '2.0_with_data_fetching',
        'features': [
            'Twitter sentiment analysis',
            'Farcaster sentiment analysis',
            'Reddit sentiment analysis',
            'Multi-platform aggregation',
            'Real-time data fetching',
            'Narrative detection',
            'Platform breakdown'
        ],
        'endpoints': [
            'POST /agent/social/analyze - Start async analysis',
            'GET /agent/social/status/{task_id} - Check task status',
            'POST /agent/social/sentiment - Analyze token sentiment (sync)',
            'GET /agent/social/narratives/{token} - Get trending narratives',
            'GET /agent/social/platforms/{token} - Platform breakdown',
            'GET /agent/social/supported-platforms - List platforms'
        ]
    }
