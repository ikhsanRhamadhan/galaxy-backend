from fastapi import APIRouter, HTTPException, Depends
from models import InvoiceCreate, InvoiceUpdate
from database import db
from routers.auth import get_current_user
from datetime import datetime

router = APIRouter()

# ── Role Matrix ──────────────────────────────────────────
# Lihat invoice       : admin, keuangan
# Buat invoice        : admin, keuangan
# Update pembayaran   : admin, keuangan
# Hapus invoice       : admin only
# Staff               : TIDAK BISA akses invoice sama sekali
# ─────────────────────────────────────────────────────────

def require_role(user: dict, allowed: list, action: str = "melakukan aksi ini"):
    if user["role"] not in allowed:
        role_labels = {"admin": "Admin", "staff": "Staff", "keuangan": "Keuangan"}
        allowed_str = " dan ".join(role_labels.get(r, r) for r in allowed)
        raise HTTPException(status_code=403, detail=f"Akses ditolak. Hanya {allowed_str} yang dapat {action}.")

@router.get("/")
async def get_invoices(current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["admin", "keuangan"], "melihat data invoice")
    invoices = db.get_all("invoices")
    shipments = {s["id"]: s for s in db.get_all("shipments")}
    for inv in invoices:
        inv["shipment_detail"] = shipments.get(inv.get("shipment_id", ""), {})
    return sorted(invoices, key=lambda x: x.get("created_at", ""), reverse=True)

@router.get("/{invoice_id}")
async def get_invoice(invoice_id: str, current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["admin", "keuangan"], "melihat invoice")
    invoice = db.get_by_id("invoices", invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    shipment = db.get_by_id("shipments", invoice.get("shipment_id", ""))
    if shipment:
        shipment["service_detail"] = db.get_by_id("services", shipment.get("service_id", "")) or {}
        shipment["destination_detail"] = db.get_by_id("destinations", shipment.get("destination_id", "")) or {}
        shipment["customer_detail"] = db.get_by_id("customers", shipment.get("customer_id", "")) or {} if shipment.get("customer_id") else {}
        invoice["shipment_detail"] = shipment
    return invoice

@router.post("/")
async def create_invoice(data: InvoiceCreate, current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["admin", "keuangan"], "membuat invoice")
    invoices = db.get_all("invoices")
    if any(inv["shipment_id"] == data.shipment_id for inv in invoices):
        raise HTTPException(status_code=400, detail="Invoice untuk pengiriman ini sudah ada")
    shipment = db.get_by_id("shipments", data.shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Pengiriman tidak ditemukan")
    subtotal = shipment["total_cost"]
    tax_amount = subtotal * (data.tax_percent / 100) if data.tax_percent else 0
    discount = data.discount_amount or 0
    total_amount = subtotal + tax_amount - discount
    invoice_data = {
        "invoice_number": db.generate_invoice_number(),
        "shipment_id": data.shipment_id,
        "resi_number": shipment["resi_number"],
        "subtotal": subtotal,
        "tax_percent": data.tax_percent or 0,
        "tax_amount": tax_amount,
        "discount_amount": discount,
        "total_amount": total_amount,
        "dp_percent": data.dp_percent or 0.0,   
        "payment_status": "belum_bayar",
        "payment_date": None,
        "notes": data.notes or "",
        "created_by": current_user["id"],
        "created_by_name": current_user["name"],
        "due_date": None,
    }
    result = db.insert("invoices", invoice_data)
    if shipment["status"] == "pending":
        db.update("shipments", data.shipment_id, {"status": "dikirim"})
    return result

@router.put("/{invoice_id}")
async def update_invoice(invoice_id: str, update: InvoiceUpdate, current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["admin", "keuangan"], "mengubah invoice")
    invoice = db.get_by_id("invoices", invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    if "tax_percent" in update_data or "discount_amount" in update_data:
        subtotal = invoice["subtotal"]
        tax_pct = update_data.get("tax_percent", invoice["tax_percent"])
        discount = update_data.get("discount_amount", invoice["discount_amount"])
        tax_amount = subtotal * (tax_pct / 100)
        update_data["tax_amount"] = tax_amount
        update_data["total_amount"] = subtotal + tax_amount - discount
    if update_data.get("payment_status") == "lunas" and not update_data.get("payment_date"):
        update_data["payment_date"] = datetime.now().isoformat()
        # Otomatis update status pengiriman jadi selesai
        db.update("shipments", invoice["shipment_id"], {"status": "selesai"})
    return db.update("invoices", invoice_id, update_data)

@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: str, current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["admin"], "menghapus invoice")
    invoice = db.get_by_id("invoices", invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    if invoice.get("payment_status") == "lunas":
        raise HTTPException(status_code=400, detail="Tidak bisa menghapus invoice yang sudah lunas")
    db.delete("invoices", invoice_id)
    return {"message": "Invoice berhasil dihapus"}
