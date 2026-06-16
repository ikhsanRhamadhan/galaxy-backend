from fastapi import APIRouter, HTTPException, Depends
from models import ServiceCreate
from database import db
from routers.auth import get_current_user

router = APIRouter()

# Lihat: semua role | Tambah/Edit/Hapus: admin only

def require_admin(user, action="melakukan aksi ini"):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail=f"Akses ditolak. Hanya Admin yang dapat {action}.")

@router.get("/")
async def get_services(current_user: dict = Depends(get_current_user)):
    return db.get_all("services")

@router.get("/{service_id}")
async def get_service(service_id: str, current_user: dict = Depends(get_current_user)):
    s = db.get_by_id("services", service_id)
    if not s: raise HTTPException(status_code=404, detail="Layanan tidak ditemukan")
    return s

@router.post("/")
async def create_service(service: ServiceCreate, current_user: dict = Depends(get_current_user)):
    require_admin(current_user, "menambah layanan")
    return db.insert("services", service.dict())

@router.put("/{service_id}")
async def update_service(service_id: str, service: ServiceCreate, current_user: dict = Depends(get_current_user)):
    require_admin(current_user, "mengubah layanan")
    updated = db.update("services", service_id, service.dict())
    if not updated: raise HTTPException(status_code=404, detail="Layanan tidak ditemukan")
    return updated

@router.delete("/{service_id}")
async def delete_service(service_id: str, current_user: dict = Depends(get_current_user)):
    require_admin(current_user, "menghapus layanan")
    if not db.delete("services", service_id):
        raise HTTPException(status_code=404, detail="Layanan tidak ditemukan")
    return {"message": "Layanan berhasil dihapus"}
