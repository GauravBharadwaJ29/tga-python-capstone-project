from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Store, StoreIn, StoreUpdate, StoreOut, StoreOnboardingIn
from .database import SessionLocal
from .kafka_producer import kafka
from .config import (EVENT_STORE_ONBOARDED, EVENT_STORE_UPDATED,
                      EVENT_STORE_DELETED, EVENT_PRODUCT_ONBOARDED)

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

@router.post("/stores/onboard", response_model=StoreOut, status_code=status.HTTP_201_CREATED)
async def onboard_store(store: StoreOnboardingIn, db: AsyncSession = Depends(get_db)):
    db_store = Store(
        name=store.name,
        address=store.address,
        contact_email=store.contact_email,
        contact_phone=store.contact_phone,
        status="active"
    )
    db.add(db_store)
    await db.commit()
    await db.refresh(db_store)
    # Optionally handle initial catalog (multi-item)
    if store.catalog:
        for product in store.catalog:
            # Here you could send a Kafka event or call product service API to create products
            await kafka.send_event({
                "event": EVENT_PRODUCT_ONBOARDED,
                "store_id": db_store.id,
                "product": product.dict()
            })
    await kafka.send_event({
        "event": EVENT_STORE_ONBOARDED,
        "store": {
            "id": db_store.id,
            "name": db_store.name,
            "address": db_store.address,
            "contact_email": db_store.contact_email,
            "contact_phone": db_store.contact_phone,
            "status": db_store.status,
            "onboarded_at": db_store.onboarded_at.isoformat(),
            "catalog": [p.dict() for p in store.catalog] if store.catalog else []
        }
    })
    return db_store

@router.get("/stores", response_model=list[StoreOut])
async def list_stores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Store))
    return result.scalars().all()

@router.get("/stores/{store_id}", response_model=StoreOut)
async def get_store(store_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

@router.put("/stores/{store_id}", response_model=StoreOut)
async def update_store(store_id: int, update: StoreUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(store, field, value)
    await db.commit()
    await db.refresh(store)
    await kafka.send_event({
        "event": EVENT_STORE_UPDATED,
        "store": {
            "id": store.id,
            "status": store.status
        }
    })
    return store

@router.delete("/stores/{store_id}")
async def delete_store(store_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    await db.delete(store)
    await db.commit()
    await kafka.send_event({"event": EVENT_STORE_DELETED, "store_id": store_id})
    return {"message": "Store deleted"}
