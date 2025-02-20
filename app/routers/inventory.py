from fastapi import APIRouter
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Inventory,
    InventoryPublic
)

router = APIRouter()


@router.get("", response_model=list[InventoryPublic])
def read_inventory(*, session: SessionDep):
    inventories = session.exec(select(Inventory)).all()
    return inventories
