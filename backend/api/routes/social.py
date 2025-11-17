"""
Social Sentiment API Routes
Enhanced with real data fetching
"""
from fastapi import APIRouter, HTTPException, Query
from tasks.agent_tasks import social_task
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
        task = social_task.delay(timeframe, focus_tokens)
        
        return APIResponse(
            success=True,
            message="Sentiment analysis started",
            data={
                "task_id": task.id,
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
    
    response_data = {
        'task_id': task_id,
        'status': task_result.state.lower()
    }
    
    if task_result.state == 'PENDING':
        response_data['message'] = 'Task is queued'
        
    elif task_result.state == 'PROCESSING':
        info = task_result.info or {}
        response_data['progress'] = info.get('progress', 0)
        response_data['message'] = info.get('status', 'Processing...')
        
    elif task_result.state == 'SUCCESS':
        response_data['result'] = task_result.result
        response_data['message'] = 'Sentiment analysis completed'
        
    elif task_result.state == 'FAILURE':
        response_data['error'] = str(task_result.info)
        response_data['message'] = 'Analysis failed'
    
    return APIResponse(
        success=True,
        message="Task status retrieved",
        data=response_data
    )


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
        from agents.social_agent import SocialAgent
        
        agent = SocialAgent(use_mock=False)
        result = await agent.analyze_sentiment(token_symbol, platforms)
        
        return APIResponse(
            success=True,
            message=f"Sentiment analysis completed for {token_symbol}",
            data=result
        )
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/narratives/{token_symbol}')
async def get_trending_narratives(token_symbol: str):
    """
    Get trending narratives about a token
    
    Path param:
    - token_symbol: Token to analyze
    
    Returns list of trending narratives
    """
    try:
        from agents.social_agent import SocialAgent
        
        agent = SocialAgent(use_mock=False)
        narratives = await agent.get_trending_narratives(token_symbol)
        
        return APIResponse(
            success=True,
            message=f"Retrieved trending narratives for {token_symbol}",
            data={
                "token_symbol": token_symbol,
                "narratives": narratives,
                "total_narratives": len(narratives)
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
        from agents.social_agent import SocialAgent
        
        agent = SocialAgent(use_mock=False)
        breakdown = await agent.get_platform_breakdown(token_symbol)
        
        return APIResponse(
            success=True,
            message=f"Platform breakdown for {token_symbol}",
            data={
                "token_symbol": token_symbol,
                "breakdown": breakdown
            }
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
