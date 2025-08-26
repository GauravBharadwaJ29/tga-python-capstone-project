from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .models import Order, OrderIn, OrderOut, OrderItem, OrderItemIn, OrderUpdate, OrderItemOut
from .database import SessionLocal
from .kafka_producer import kafka  # Use the same instance
# import httpx
from .config import ErrorMessages  # Import ErrorMessages
import json

# Configure logging (you can adjust level and format as needed)
from .logger_config import logger
from .config import EVENT_ORDER_CREATED, EVENT_ORDER_UPDATED, EVENT_ORDER_CANCELLED, EVENT_ORDER_DELETED


router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}    

@router.post("/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderIn, db: AsyncSession = Depends(get_db)):
    try:
        logger.debug(f"order {order}")
        logger.info(f"Received create_order request for customer: {order.customer_name}")
        db_order = Order(
            customer_id=order.customer_id,
            customer_name=order.customer_name,
            customer_contact=order.customer_contact,
            delivery_address=order.delivery_address,
            amount=order.amount,
            payment_method=order.payment_method,
            store_id=int(order.store_id),  # <-- Added store_id here
        )
        db.add(db_order)
        await db.flush()  # to get db_order.id before commit

        db_items = [
            OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in order.items
        ]
        db.add_all(db_items)
        await db.commit()
        logger.info(f"Order {db_order.id} committed to database")
    

        # --- CHANGED: Eagerly load items relationship after commit ---
        result = await db.execute(
            select(Order).options(selectinload(Order.items)).where(Order.id == db_order.id)
        )
        db_order = result.scalar_one()
        # --- END CHANGED ---
        event_payload = {
            "event":  EVENT_ORDER_CREATED,
            "order": {
                "id": db_order.id,
                "customer_id": db_order.customer_id,
                "customer_name": db_order.customer_name,
                "customer_contact": db_order.customer_contact,
                "delivery_address": db_order.delivery_address,
                "amount": float(db_order.amount),
                "payment_method": db_order.payment_method,                
                "status": db_order.status,
                "created_at": db_order.created_at.isoformat(),
                "store_id": int(db_order.store_id),  # <-- Added store_id in event
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": float(item.price),
                    }
                    for item in db_order.items
                ],
            }
        }

        await kafka.send_event( event_payload)

        logger.info(f"Sending Kafka event: {event_payload['event']} for order_id={db_order.id}")
        logger.debug(f"Kafka event payload: {event_payload}")
   
            # Convert items to Pydantic models
        order_items = [
            OrderItemOut(
                product_id=item.product_id,
                quantity=item.quantity,
                price=float(item.price)
            )
            for item in db_order.items
        ]
        return OrderOut(
            id=db_order.id,
            customer_id=db_order.customer_id,
            customer_name=db_order.customer_name,
            customer_contact=db_order.customer_contact,
            delivery_address=db_order.delivery_address,
            amount=float(db_order.amount),
            payment_method=db_order.payment_method,
            status=db_order.status,
            created_at=db_order.created_at,
            store_id=db_order.store_id,  # Should be int if model expects int
            items=order_items
        )
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)    

@router.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == "cancelled":
        return {"message": "Order already cancelled"}
    order.status = "cancelled"
    await db.commit()
    await kafka.send_event({"event": EVENT_ORDER_CANCELLED, "order_id": order_id})
    return {"message": "Order cancelled"}

@router.get("/orders", response_model=list[OrderOut])
async def list_orders(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Order).options(selectinload(Order.items)))
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

@router.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    try:
        if order_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid order ID")
        logger.info(f"Fetching order with id: {order_id}")
        result = await db.execute(select(Order).where(Order.id == order_id).options(selectinload(Order.items)))
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:  
        logger.error(f"Error fetching order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

@router.put("/orders/{order_id}", response_model=OrderOut)
async def update_order(order_id: int, update: OrderUpdate, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Updating order with id: {order_id}")
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        # Only update fields provided
        for field, value in update.dict(exclude_unset=True).items():
            setattr(order, field, value)
        await db.commit()
        logger.info(f"Order {order_id} committed to database")
        await db.refresh(order)
        await kafka.send_event({"event": EVENT_ORDER_UPDATED, "order": {"id": order.id, "status": order.status}})
        return order
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR) 

@router.patch("/orders/{order_id}", response_model=OrderOut)
async def patch_order(order_id: int, update: OrderUpdate, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Patching order with id: {order_id}")
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        # Only update fields that are provided
        for field, value in update.dict(exclude_unset=True).items():
            setattr(order, field, value)
        await db.commit()
        logger.info(f"Order {order_id} patched in database")
        await db.refresh(order)
        await kafka.send_event({"event": EVENT_ORDER_UPDATED, "order": {"id": order.id, "status": order.status}})
        return order
    except Exception as e:
        logger.error(f"Error patching order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)    

@router.delete("/orders/{order_id}")
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Deleting order with id: {order_id}")      
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        await db.delete(order)
        await db.commit()
        await kafka.send_event({"event": EVENT_ORDER_DELETED, "order_id": order_id})
        return {"message": "Order deleted"}
    except Exception as e:
        logger.error(f"Error deleting order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)
    

    