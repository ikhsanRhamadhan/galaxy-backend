from fastapi import APIRouter, HTTPException, Depends
from models import DestinationCreate
from database import db
from routers.auth import get_current_user

router = APIRouter()

# Lihat: semua role | Tambah/Edit/Hapus: admin only

def require_admin(user, action="melakukan aksi ini"):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail=f"Akses ditolak. Hanya Admin yang dapat {action}.")

@router.get("/")
async def get_destinations(current_user: dict = Depends(get_current_user)):
    return db.get_all("destinations")

@router.get("/{dest_id}")
async def get_destination(dest_id: str, current_user: dict = Depends(get_current_user)):
    d = db.get_by_id("destinations", dest_id)
    if not d: raise HTTPException(status_code=404, detail="Tujuan tidak ditemukan")
    return d

@router.post("/")
async def create_destination(dest: DestinationCreate, current_user: dict = Depends(get_current_user)):
    require_admin(current_user, "menambah tujuan pengiriman")
    return db.insert("destinations", dest.dict())

@router.put("/{dest_id}")
async def update_destination(dest_id: str, dest: DestinationCreate, current_user: dict = Depends(get_current_user)):
    require_admin(current_user, "mengubah tujuan pengiriman")
    updated = db.update("destinations", dest_id, dest.dict())
    if not updated: raise HTTPException(status_code=404, detail="Tujuan tidak ditemukan")
    return updated

@router.delete("/{dest_id}")
async def delete_destination(dest_id: str, current_user: dict = Depends(get_current_user)):
    require_admin(current_user, "menghapus tujuan pengiriman")
    if not db.delete("destinations", dest_id):
        raise HTTPException(status_code=404, detail="Tujuan tidak ditemukan")
    return {"message": "Tujuan berhasil dihapus"}
