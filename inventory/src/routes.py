from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Inventory, InventoryIn, InventoryUpdate, InventoryOut
from .database import SessionLocal
from .kafka_producer import kafka
from .logger_config import logger
from .utils import custom_error
from .config import (EVENT_INVENTORY_CREATED, EVENT_INVENTORY_UPDATED,
                        EVENT_INVENTORY_DELETED
                    )
                

router = APIRouter()


async def get_db():
    async with SessionLocal() as session:
        yield session

# @router.on_event("startup")
# async def startup_event():
#     await kafka.start()

# @router.on_event("shutdown")
# async def shutdown_event():
#     await kafka.stop()

@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

@router.post("/inventory", response_model=InventoryOut, status_code=status.HTTP_201_CREATED)
async def create_inventory(item: InventoryIn, db: AsyncSession = Depends(get_db)):
    inv = Inventory(product_id=item.product_id, stock=item.stock, warehouse=item.warehouse)
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    await kafka.send_event({"event": EVENT_INVENTORY_CREATED, "inventory": {
        "product_id": inv.product_id, "stock": inv.stock, "warehouse": inv.warehouse}})
    return inv

@router.get("/inventory", response_model=list[InventoryOut])
async def list_inventory(store_id: int = None, db: AsyncSession = Depends(get_db)):
    query = select(Inventory)
    if store_id is not None:
        query = query.where(Inventory.store_id == store_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/inventory/{product_id}", response_model=InventoryOut)
async def get_inventory(product_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Inventory).where(Inventory.product_id == product_id))
    inv = result.scalar_one_or_none()
    if not inv:
        return custom_error("Inventory not found", 404)
    return inv

@router.put("/inventory/{product_id}", response_model=InventoryOut)
async def update_inventory(product_id: str, update: InventoryUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Inventory).where(Inventory.product_id == product_id))
    inv = result.scalar_one_or_none()
    if not inv:
        return custom_error("Inventory not found", 404)
    inv.stock = update.stock
    await db.commit()
    await db.refresh(inv)
    await kafka.send_event({"event": EVENT_INVENTORY_UPDATED, "inventory": {
        "product_id": inv.product_id, "stock": inv.stock, "warehouse": inv.warehouse}})
    return inv

@router.delete("/inventory/{product_id}")
async def delete_inventory(product_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Inventory).where(Inventory.product_id == product_id))
    inv = result.scalar_one_or_none()
    if not inv:
        return custom_error("Inventory not found", 404)
    await db.delete(inv)
    await db.commit()
    await kafka.send_event({"event": EVENT_INVENTORY_DELETED, "product_id": product_id})
    return {"message": "Inventory deleted"}
