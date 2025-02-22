from fastapi import APIRouter, HTTPException
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


@router.get("/{inventory_id}", response_model=InventoryPublic)
def read_inventory_by_id(*, session: SessionDep, inventory_id: int):
    db_inventory = session.get(Inventory, inventory_id)
    if not db_inventory:
        raise HTTPException(
            status_code=404,
            detail="The inventory with this id does not exist in the system",
        )
    return db_inventory
