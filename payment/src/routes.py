from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Payment, PaymentIn, PaymentOut, PaymentUpdate, PaymentItem, PaymentItemSchema
from .database import SessionLocal
from .kafka_producer import kafka
from .utils import custom_error
from datetime import datetime
import uuid
from .config import ( EVENT_PAYMENT_PROCESSED, EVENT_PAYMENT_UPDATED, EVENT_PAYMENT_DELETED )

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

@router.post("/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def process_payment(payment: PaymentIn, db: AsyncSession = Depends(get_db)):
    total_amount = sum(item.quantity * item.price for item in payment.items)
    if abs(payment.amount - total_amount) > 0.01:
        raise HTTPException(status_code=400, detail="Amount does not match sum of items.")
    transaction_id = str(uuid.uuid4())
    db_payment = Payment(
        order_id=payment.order_id,
        customer_id=payment.customer_id,
        amount=payment.amount,
        status="success",
        payment_method=payment.payment_method,
        transaction_id=transaction_id,
        created_at=datetime.utcnow()
    )
    db.add(db_payment)
    await db.flush()  # To get db_payment.id

    # Persist payment items
    db_items = []
    for item in payment.items:
        db_item = PaymentItem(
            payment_id=db_payment.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(db_item)
        db_items.append(db_item)
    await db.commit()
    await db.refresh(db_payment)

    # Fetch items for response
    items_result = await db.execute(select(PaymentItem).where(PaymentItem.payment_id == db_payment.id))
    items = [PaymentItemSchema.from_orm(i) for i in items_result.scalars().all()]

    # Emit Kafka event with error handling
    try:
        await kafka.send_event({
            "event": EVENT_PAYMENT_PROCESSED,
            "payment": {
                "id": db_payment.id,
                "order_id": db_payment.order_id,
                "customer_id": db_payment.customer_id,
                "amount": float(db_payment.amount),
                "status": db_payment.status,
                "payment_method": db_payment.payment_method,
                "transaction_id": db_payment.transaction_id,
                "created_at": db_payment.created_at.isoformat(),
                "items": [item.dict() for item in items]
            }
        })
    except Exception as e:
        # Log and continue; don't block payment creation if Kafka fails
        print(f"Kafka send_event error: {e}")

    return PaymentOut(
        id=db_payment.id,
        order_id=db_payment.order_id,
        customer_id=db_payment.customer_id,
        amount=float(db_payment.amount),
        status=db_payment.status,
        payment_method=db_payment.payment_method,
        transaction_id=db_payment.transaction_id,
        created_at=db_payment.created_at,
        items=items
    )

@router.get("/payments", response_model=list[PaymentOut])
async def list_payments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payment))
    payments = result.scalars().all()
    payment_out_list = []
    for p in payments:
        items_result = await db.execute(select(PaymentItem).where(PaymentItem.payment_id == p.id))
        items = [PaymentItemSchema.from_orm(i) for i in items_result.scalars().all()]
        payment_out_list.append(
            PaymentOut(
                id=p.id,
                order_id=p.order_id,
                customer_id=p.customer_id,
                amount=float(p.amount),
                status=p.status,
                payment_method=p.payment_method,
                transaction_id=p.transaction_id,
                created_at=p.created_at,
                items=items
            )
        )
    return payment_out_list

@router.get("/payments/{payment_id}", response_model=PaymentOut)
async def get_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    items_result = await db.execute(select(PaymentItem).where(PaymentItem.payment_id == payment.id))
    items = [PaymentItemSchema.from_orm(i) for i in items_result.scalars().all()]
    return PaymentOut(
        id=payment.id,
        order_id=payment.order_id,
        customer_id=payment.customer_id,
        amount=float(payment.amount),
        status=payment.status,
        payment_method=payment.payment_method,
        transaction_id=payment.transaction_id,
        created_at=payment.created_at,
        items=items
    )

@router.put("/payments/{payment_id}", response_model=PaymentOut)
async def update_payment(payment_id: int, update: PaymentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if update.status:
        payment.status = update.status
    if update.transaction_id:
        payment.transaction_id = update.transaction_id
    await db.commit()
    await db.refresh(payment)
    items_result = await db.execute(select(PaymentItem).where(PaymentItem.payment_id == payment.id))
    items = [PaymentItemSchema.from_orm(i) for i in items_result.scalars().all()]
    try:
        await kafka.send_event({
            "event": EVENT_PAYMENT_UPDATED,
            "payment": {
                "id": payment.id,
                "status": payment.status,
                "transaction_id": payment.transaction_id
            }
        })
    except Exception as e:
        print(f"Kafka send_event error: {e}")
    return PaymentOut(
        id=payment.id,
        order_id=payment.order_id,
        customer_id=payment.customer_id,
        amount=float(payment.amount),
        status=payment.status,
        payment_method=payment.payment_method,
        transaction_id=payment.transaction_id,
        created_at=payment.created_at,
        items=items
    )

@router.delete("/payments/{payment_id}")
async def delete_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    await db.delete(payment)
    await db.commit()
    try:
        await kafka.send_event({"event": EVENT_PAYMENT_DELETED, "payment_id": payment_id})
    except Exception as e:
        print(f"Kafka send_event error: {e}")
    return {"message": "Payment deleted"}
