from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .models import Billing, BillIn, BillingOut, BillUpdate, BillingItem, BillingAuditLog, BillingAuditLogOut
from .database import SessionLocal
from .kafka_producer import kafka
from .logger_config import logger
from .config import ErrorMessages  # Import ErrorMessages
from typing import List, Optional
from datetime import datetime

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

@router.get("/bills", response_model=List[BillingOut])
async def list_bills(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Billing)
        .options(selectinload(Billing.items))
        .where(Billing.deleted == False)
    )
    bills = result.scalars().all()
    return bills

@router.get("/bills/{bill_id}", response_model=BillingOut)
async def get_bill(bill_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Billing)
        .options(selectinload(Billing.items))
        .where(Billing.id == bill_id, Billing.deleted == False)
    )
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.put("/bills/{bill_id}", response_model=BillingOut)
async def update_bill(bill_id: int, update: BillUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Billing)
        .options(selectinload(Billing.items))
        .where(Billing.id == bill_id)
    )
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    if update.status:
        bill.status = update.status
    await db.commit()
    await db.refresh(bill)
    await kafka.send_event({
        "event": "bill_updated",
        "bill": {
            "id": bill.id,
            "status": bill.status
        }
    })
    return bill # ORM object, includes items

@router.get("/bills/by-order/{order_id}", response_model=BillingOut)
async def get_bill_by_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Billing)
        .options(selectinload(Billing.items))
        .where(Billing.order_id == order_id, Billing.deleted == False)
    )
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

@router.get("/bills/by-customer/{customer_id}", response_model=List[BillingOut])
async def get_bills_by_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Billing)
        .options(selectinload(Billing.items))
        .where(Billing.customer_id == customer_id, Billing.deleted == False)
    )
    bills = result.scalars().all()
    return bills  # FastAPI will use the relationship to populate items if orm_mode is set

@router.patch("/bills/{bill_id}/status")
async def update_bill_status(bill_id: int, status: str, db: AsyncSession = Depends(get_db), user: str = "admin"):
    result = await db.execute(
        select(Billing)
        .where(Billing.id == bill_id)
    )
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    old_status = bill.status
    bill.status = status
    await db.commit()
    # Audit log
    audit = BillingAuditLog(billing_id=bill.id, old_status=old_status, new_status=status, changed_by=user )
    db.add(audit)
    await db.commit()
    return {"message": f"Bill {bill_id} status updated to {status}"}

@router.delete("/bills/{bill_id}")
async def soft_delete_bill(bill_id: int, db: AsyncSession = Depends(get_db), user: str = "admin"):
    result = await db.execute(
        select(Billing)
        .where(Billing.id == bill_id)
    )
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    bill.deleted = True
    await db.commit()
    # Optionally audit
    audit = BillingAuditLog(billing_id=bill.id, old_status=bill.status, new_status="deleted", changed_by=user )
    db.add(audit)
    await db.commit()
    return {"message": f"Bill {bill_id} soft-deleted"}

@router.get("/bills/deleted", response_model=List[BillingOut])
async def list_deleted_bills(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Billing)
        .options(selectinload(Billing.items))
        .where(Billing.deleted == True)
    )
    bills = result.scalars().all()
    return bills

@router.get("/bills/{bill_id}/audit", response_model=List[BillingAuditLogOut])
async def get_audit_logs(bill_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BillingAuditLog)
        .where(BillingAuditLog.billing_id == bill_id)
    )
    logs = result.scalars().all()
    return logs

@router.post("/bills", response_model=BillingOut, status_code=status.HTTP_201_CREATED)
async def create_bill(bill: BillIn, db: AsyncSession = Depends(get_db)):
    # ... validation ...
    try:
        db_bill = Billing(order_id=bill.order_id, amount=bill.amount, 
            status="generated"
            # add customer_id, customer_name, payment_method if available
        )
        db.add(db_bill)
        await db.flush()  # To get db_bill.id

        for item in bill.items:
            db_item = BillingItem(billing_id=db_bill.id, product_id=item.product_id, quantity=item.quantity,
                price=item.price
            )
            db.add(db_item)

        await db.commit()
        result = await db.execute(
            select(Billing)
            .options(selectinload(Billing.items))
            .where(Billing.id == db_bill.id)
        )
        db_bill = result.scalar_one()
        logger.info(f"Bill {db_bill.id} created successfully")
        # ... send Kafka event ...
        return db_bill  # ORM object, includes items
    except Exception as e:
        logger.error(f"Failed to create bill: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.BILL_CREATE_FAILED.format(str(e))
        )

@router.get("/bills/search", response_model=List[BillingOut])
async def search_bills(
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db)
):
    query = select(Billing).options(selectinload(Billing.items))
    if status:
        query = query.where(Billing.status == status)
    if start_date:
        query = query.where(Billing.created_at >= start_date)
    if end_date:
        query = query.where(Billing.created_at <= end_date)
    if min_amount:
        query = query.where(Billing.amount >= min_amount)
    if max_amount:
        query = query.where(Billing.amount <= max_amount)
    if not include_deleted:
        query = query.where(Billing.deleted == False)
    result = await db.execute(query)
    return result.scalars().all()



