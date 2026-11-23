from fastapi import APIRouter

from app.data.source import get_data_source

router = APIRouter()


@router.get("/rankings")
def list_rankings(limit: int = 200):
    source = get_data_source()
    return {"data_source": source.name, "rankings": source.get_rankings(limit=limit)}
