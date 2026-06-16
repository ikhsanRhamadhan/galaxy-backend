from fastapi import APIRouter, HTTPException, Depends
from models import CustomerCreate
from database import db
from routers.auth import get_current_user

router = APIRouter()

# ── Role Matrix ──────────────────────────────────────────
# Lihat pelanggan  : admin, staff, keuangan
# Tambah/edit      : admin only
# Hapus            : admin only
# ─────────────────────────────────────────────────────────

def require_role(user, allowed, action="melakukan aksi ini"):
    if user["role"] not in allowed:
        raise HTTPException(status_code=403, detail=f"Akses ditolak. Hanya Admin yang dapat {action}.")

@router.get("/")
async def get_customers(current_user: dict = Depends(get_current_user)):
    return db.get_all("customers")

@router.get("/{customer_id}")
async def get_customer(customer_id: str, current_user: dict = Depends(get_current_user)):
    c = db.get_by_id("customers", customer_id)
    if not c: raise HTTPException(status_code=404, detail="Pelanggan tidak ditemukan")
    return c

@router.post("/")
async def create_customer(customer: CustomerCreate, current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["admin"], "menambah data pelanggan")
    return db.insert("customers", customer.dict())

@router.put("/{customer_id}")
async def update_customer(customer_id: str, customer: CustomerCreate, current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["admin"], "mengubah data pelanggan")
    updated = db.update("customers", customer_id, customer.dict())
    if not updated: raise HTTPException(status_code=404, detail="Pelanggan tidak ditemukan")
    return updated

@router.delete("/{customer_id}")
async def delete_customer(customer_id: str, current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["admin"], "menghapus data pelanggan")
    if not db.delete("customers", customer_id):
        raise HTTPException(status_code=404, detail="Pelanggan tidak ditemukan")
    return {"message": "Pelanggan berhasil dihapus"}
