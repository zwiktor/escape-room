from fastapi import APIRouter

router = APIRouter(
    prefix='/story',
    tags=['story']
)

@router.get('/')
def get_all_blogs():
    return {'message': 'Story API'}
