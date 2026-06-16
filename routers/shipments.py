from fastapi import APIRouter, HTTPException, Depends
from models import ShipmentCreate, ShipmentUpdate
from database import db
from routers.auth import get_current_user

router = APIRouter()

# ── Role Matrix ──────────────────────────────────────────
# Lihat pengiriman  : admin, staff, keuangan
# Buat pengiriman   : admin, staff
# Update status     : admin, staff
# Hapus pengiriman  : admin only
# ─────────────────────────────────────────────────────────

def require_role(user: dict, allowed: list, action: str = "melakukan aksi ini"):
    if user["role"] not in allowed:
        role_labels = {"admin": "Admin", "staff": "Staff", "keuangan": "Keuangan"}
        allowed_str = " dan ".join(role_labels.get(r, r) for r in allowed)
        raise HTTPException(status_code=403, detail=f"Akses ditolak. Hanya {allowed_str} yang dapat {action}.")

def calculate_cost(weight: float, service: dict, destination: dict) -> float:
    actual_weight = max(weight, service.get("min_weight", 1))
    base_cost = actual_weight * service["price_per_kg"]
    surcharge = destination.get("surcharge", 0) * actual_weight
    return base_cost + surcharge

@router.get("/")
async def get_shipments(current_user: dict = Depends(get_current_user)):
    shipments = db.get_all("shipments")
    services = {s["id"]: s for s in db.get_all("services")}
    destinations = {d["id"]: d for d in db.get_all("destinations")}
    customers = {c["id"]: c for c in db.get_all("customers")}
    for s in shipments:
        s["service_detail"] = services.get(s.get("service_id"), {})
        s["destination_detail"] = destinations.get(s.get("destination_id"), {})
        if s.get("customer_id"):
            s["customer_detail"] = customers.get(s["customer_id"], {})
    return sorted(shipments, key=lambda x: x.get("created_at", ""), reverse=True)

@router.get("/{shipment_id}")
async def get_shipment(shipment_id: str, current_user: dict = Depends(get_current_user)):
    shipment = db.get_by_id("shipments", shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Pengiriman tidak ditemukan")
    service = db.get_by_id("services", shipment.get("service_id", ""))
    destination = db.get_by_id("destinations", shipment.get("destination_id", ""))
    if service: shipment["service_detail"] = service
    if destination: shipment["destination_detail"] = destination
    return shipment

@router.post("/")
async def create_shipment(shipment: ShipmentCreate, current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["admin", "staff"], "membuat pengiriman")
    service = db.get_by_id("services", shipment.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Layanan tidak ditemukan")
    destination = db.get_by_id("destinations", shipment.destination_id)
    if not destination:
        raise HTTPException(status_code=404, detail="Tujuan tidak ditemukan")
    total_cost = calculate_cost(shipment.weight, service, destination)
    data = {
        **shipment.dict(),
        "resi_number": db.generate_resi(),
        "total_cost": total_cost,
        "status": "pending",
        "created_by": current_user["id"],
        "created_by_name": current_user["name"],
    }
    return db.insert("shipments", data)

@router.put("/{shipment_id}")
async def update_shipment(shipment_id: str, update: ShipmentUpdate, current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["admin", "staff"], "mengubah status pengiriman")
    shipment = db.get_by_id("shipments", shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Pengiriman tidak ditemukan")
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    return db.update("shipments", shipment_id, update_data)

@router.delete("/{shipment_id}")
async def delete_shipment(shipment_id: str, current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["admin"], "menghapus pengiriman")
    invoices = db.get_all("invoices")
    if any(inv["shipment_id"] == shipment_id for inv in invoices):
        raise HTTPException(status_code=400, detail="Tidak bisa menghapus pengiriman yang sudah memiliki invoice")
    deleted = db.delete("shipments", shipment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pengiriman tidak ditemukan")
    return {"message": "Pengiriman berhasil dihapus"}
