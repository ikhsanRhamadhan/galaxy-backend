from fastapi import APIRouter, HTTPException, Depends
from models import DestinationCreate
from database import db
from routers.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_destinations(current_user: dict = Depends(get_current_user)):
    return db.get_all("destinations")

@router.get("/{dest_id}")
async def get_destination(dest_id: str, current_user: dict = Depends(get_current_user)):
    dest = db.get_by_id("destinations", dest_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Tujuan tidak ditemukan")
    return dest

@router.post("/")
async def create_destination(dest: DestinationCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")
    return db.insert("destinations", dest.dict())

@router.put("/{dest_id}")
async def update_destination(dest_id: str, dest: DestinationCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")
    updated = db.update("destinations", dest_id, dest.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Tujuan tidak ditemukan")
    return updated

@router.delete("/{dest_id}")
async def delete_destination(dest_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")
    deleted = db.delete("destinations", dest_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tujuan tidak ditemukan")
    return {"message": "Tujuan berhasil dihapus"}
