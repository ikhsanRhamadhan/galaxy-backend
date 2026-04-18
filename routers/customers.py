from fastapi import APIRouter, HTTPException, Depends
from models import CustomerCreate
from database import db
from routers.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_customers(current_user: dict = Depends(get_current_user)):
    return db.get_all("customers")

@router.get("/{customer_id}")
async def get_customer(customer_id: str, current_user: dict = Depends(get_current_user)):
    customer = db.get_by_id("customers", customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Pelanggan tidak ditemukan")
    return customer

@router.post("/")
async def create_customer(customer: CustomerCreate, current_user: dict = Depends(get_current_user)):
    return db.insert("customers", customer.dict())

@router.put("/{customer_id}")
async def update_customer(customer_id: str, customer: CustomerCreate, current_user: dict = Depends(get_current_user)):
    updated = db.update("customers", customer_id, customer.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Pelanggan tidak ditemukan")
    return updated

@router.delete("/{customer_id}")
async def delete_customer(customer_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")
    deleted = db.delete("customers", customer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pelanggan tidak ditemukan")
    return {"message": "Pelanggan berhasil dihapus"}
