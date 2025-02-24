from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import (
    Inventory,
    InventoryCreate,
    InventoryPublic,
)

router = APIRouter()


@router.post("", response_model=InventoryPublic)
def create_inventory(*, session: SessionDep, inventory: InventoryCreate):
    statement = select(Inventory).where(Inventory.name == inventory.name)
    db_inventory = session.exec(statement).first()
    if db_inventory:
        raise HTTPException(
            status_code=400,
            detail="The inventory with this name already exists in the system",
        )
    db_inventory = Inventory.model_validate(inventory)
    session.add(db_inventory)
    session.commit()
    session.refresh(db_inventory)
    return db_inventory


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
