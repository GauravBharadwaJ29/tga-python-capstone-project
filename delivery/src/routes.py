from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Delivery, DeliveryItem, DeliveryIn, DeliveryOut, DeliveryUpdate, DeliveryItemSchema
from .database import SessionLocal
from .kafka_producer import kafka
from .logger_config import logger
from datetime import datetime
from .config import (
    EVENT_DELIVERY_CREATED, EVENT_DELIVERY_UPDATED, EVENT_DELIVERY_DELETED
)

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/health", tags=["Health"])
async def health_check():
    logger.debug("Health check endpoint called")
    return {"status": "ok"}

@router.post("/deliveries", response_model=DeliveryOut, status_code=status.HTTP_201_CREATED)
async def create_delivery(delivery: DeliveryIn, db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating delivery for order: {delivery.order_id}")
    try:
        existing_delivery = (await db.execute(select(Delivery).where(Delivery.order_id == delivery.order_id))).scalar_one_or_none()
        if existing_delivery:
            raise HTTPException(status_code=409, detail="Delivery for this order already exists.")
        db_delivery = Delivery(
            order_id=delivery.order_id,
            customer_id=delivery.customer_id,
            delivery_address=delivery.delivery_address,
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(db_delivery)
        await db.flush()  # To get db_delivery.id

        # Persist items if provided
        items = []
        if delivery.items:
            db.add_all([
                DeliveryItem(
                    delivery_id=db_delivery.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.price
                ) for item in delivery.items
            ])
            await db.flush()
            items_result = await db.execute(select(DeliveryItem).where(DeliveryItem.delivery_id == db_delivery.id))
            items = [DeliveryItemSchema.from_orm(i) for i in items_result.scalars().all()]
        await db.commit()
        await db.refresh(db_delivery)

        # Fetch items for response

        delivery_data = {
            "event": EVENT_DELIVERY_CREATED,
            "delivery": {
                "id": db_delivery.id,
                "order_id": db_delivery.order_id,
                "customer_id": db_delivery.customer_id,
                "status": db_delivery.status,
                "created_at": db_delivery.created_at.isoformat(),
                "items": [item.dict() for item in items],
                "delivery_address": db_delivery.delivery_address,
                "assigned_to": db_delivery.assigned_to,
            }
        }
        await kafka.send_event(delivery_data)

        return DeliveryOut(**delivery_data["delivery"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating delivery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deliveries", response_model=list[DeliveryOut])
async def list_deliveries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Delivery))
    deliveries = result.scalars().all()
    delivery_out_list = []
    for d in deliveries:
        items_result = await db.execute(select(DeliveryItem).where(DeliveryItem.delivery_id == d.id))
        items = [DeliveryItemSchema.from_orm(i) for i in items_result.scalars().all()]
        delivery_out_list.append(
            DeliveryOut(
                id=d.id,
                order_id=d.order_id,
                customer_id=d.customer_id,
                status=d.status,
                assigned_to=d.assigned_to,
                created_at=d.created_at,
                items=items,
                delivery_address=d.delivery_address
            )
        )
    return delivery_out_list

class ErrorMessages:
    DELIVERY_NOT_FOUND = "Delivery not found"
    CREATE_FAILED = "Failed to create delivery: {}"
    UPDATE_FAILED = "Failed to update delivery: {}"
    DELETE_FAILED = "Failed to delete delivery: {}"

@router.get("/deliveries/{delivery_id}", response_model=DeliveryOut)
async def get_delivery(delivery_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Delivery).where(Delivery.id == delivery_id))
        delivery = result.scalar_one_or_none()
        if not delivery:
            logger.warning(f"Delivery not found with id: {delivery_id}")
            raise HTTPException(status_code=404, detail=ErrorMessages.DELIVERY_NOT_FOUND)
        items_result = await db.execute(select(DeliveryItem).where(DeliveryItem.delivery_id == delivery.id))
        items = [DeliveryItemSchema.from_orm(i) for i in items_result.scalars().all()]
        return DeliveryOut(
            id=delivery.id,
            order_id=delivery.order_id,
            customer_id=delivery.customer_id,
            status=delivery.status,
            assigned_to=delivery.assigned_to,
            created_at=delivery.created_at,
            items=items,
            delivery_address=delivery.delivery_address
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving delivery {delivery_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/deliveries/{delivery_id}", response_model=DeliveryOut)
async def update_delivery(delivery_id: int, update: DeliveryUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Delivery).where(Delivery.id == delivery_id))
        delivery = result.scalar_one_or_none()
        if not delivery:
            raise HTTPException(status_code=404, detail=ErrorMessages.DELIVERY_NOT_FOUND)

        for field in ["status", "assigned_to", "shipped_at", "delivered_at", "tracking_number"]:
            value = getattr(update, field)
            if value is not None:
                setattr(delivery, field, value)

        await db.commit()
        await db.refresh(delivery)
        items_result = await db.execute(select(DeliveryItem).where(DeliveryItem.delivery_id == delivery.id))
        items = [DeliveryItemSchema.from_orm(i) for i in items_result.scalars().all()]

        update_event = {
            "event": EVENT_DELIVERY_UPDATED,
            "delivery": {
                "id": delivery.id,
                "order_id": delivery.order_id,
                "customer_id": delivery.customer_id,
                "status": delivery.status,
                "assigned_to": delivery.assigned_to,
                "shipped_at": delivery.shipped_at.isoformat() if delivery.shipped_at else None,
                "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None,
                "tracking_number": delivery.tracking_number,
                "created_at": delivery.created_at.isoformat(),
                "items": [item.dict() for item in items],
                "delivery_address": delivery.delivery_address
            }
        }
        await kafka.send_event(update_event)
        return DeliveryOut(
            id=delivery.id,
            order_id=delivery.order_id,
            customer_id=delivery.customer_id,
            status=delivery.status,
            assigned_to=delivery.assigned_to,
            created_at=delivery.created_at,
            items=items,
            delivery_address=delivery.delivery_address
        )
    except Exception as e:
        logger.error(f"Error updating delivery {delivery_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorMessages.UPDATE_FAILED.format(str(e))
        )

@router.delete("/deliveries/{delivery_id}")
async def delete_delivery(delivery_id: int, db: AsyncSession = Depends(get_db)):
    delivery = (await db.execute(select(Delivery).where(Delivery.id == delivery_id))).scalar_one_or_none()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    await db.delete(delivery)
    await db.commit()

    delete_event = {
        "event":  EVENT_DELIVERY_DELETED,
        "delivery_id": delivery_id
    }
    await kafka.send_event(delete_event)

    return {"message": "Delivery deleted"}
