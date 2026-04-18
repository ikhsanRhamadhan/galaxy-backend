from fastapi import APIRouter, HTTPException, Depends
from models import ServiceCreate
from database import db
from routers.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_services(current_user: dict = Depends(get_current_user)):
    return db.get_all("services")

@router.get("/{service_id}")
async def get_service(service_id: str, current_user: dict = Depends(get_current_user)):
    service = db.get_by_id("services", service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Layanan tidak ditemukan")
    return service

@router.post("/")
async def create_service(service: ServiceCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")
    return db.insert("services", service.dict())

@router.put("/{service_id}")
async def update_service(service_id: str, service: ServiceCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")
    updated = db.update("services", service_id, service.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Layanan tidak ditemukan")
    return updated

@router.delete("/{service_id}")
async def delete_service(service_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")
    deleted = db.delete("services", service_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Layanan tidak ditemukan")
    return {"message": "Layanan berhasil dihapus"}
