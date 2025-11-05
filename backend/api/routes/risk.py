
# from fastapi import APIRouter

# router = APIRouter()

# @router.get('/risk')
# async def risk():

#     # logic
#     return {'agent':'risk','status':'ok'}



from fastapi import APIRouter
from tasks import risk_task

from celery.result import AsyncResult
from core import celery_app

router = APIRouter()

@router.get('/risk')
async def risk():
    task = risk_task.delay() # adding the background worker
    # logic
    return {'agent':'risk ','task_id': task.id}

# fetching the results
@router.get('/risk/status/{task_id}')
async def get_risk_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
