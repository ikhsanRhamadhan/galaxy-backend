from fastapi import APIRouter, HTTPException, Depends
from models import InvoiceCreate, InvoiceUpdate
from database import db
from routers.auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_invoices(current_user: dict = Depends(get_current_user)):
    invoices = db.get_all("invoices")
    shipments = {s["id"]: s for s in db.get_all("shipments")}
    
    for inv in invoices:
        shipment = shipments.get(inv.get("shipment_id", ""), {})
        inv["shipment_detail"] = shipment
    
    return sorted(invoices, key=lambda x: x.get("created_at", ""), reverse=True)

@router.get("/{invoice_id}")
async def get_invoice(invoice_id: str, current_user: dict = Depends(get_current_user)):
    invoice = db.get_by_id("invoices", invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    shipment = db.get_by_id("shipments", invoice.get("shipment_id", ""))
    if shipment:
        service = db.get_by_id("services", shipment.get("service_id", ""))
        destination = db.get_by_id("destinations", shipment.get("destination_id", ""))
        customer = db.get_by_id("customers", shipment.get("customer_id", "")) if shipment.get("customer_id") else None
        
        shipment["service_detail"] = service or {}
        shipment["destination_detail"] = destination or {}
        shipment["customer_detail"] = customer or {}
        invoice["shipment_detail"] = shipment
    
    return invoice

@router.post("/")
async def create_invoice(data: InvoiceCreate, current_user: dict = Depends(get_current_user)):
    # Check if invoice already exists for this shipment
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
    
    invoice_number = db.generate_invoice_number()
    
    invoice_data = {
        "invoice_number": invoice_number,
        "shipment_id": data.shipment_id,
        "resi_number": shipment["resi_number"],
        "subtotal": subtotal,
        "tax_percent": data.tax_percent or 0,
        "tax_amount": tax_amount,
        "discount_amount": discount,
        "total_amount": total_amount,
        "payment_status": "belum_bayar",
        "payment_date": None,
        "notes": data.notes or "",
        "created_by": current_user["id"],
        "created_by_name": current_user["name"],
        "due_date": None,
    }
    
    result = db.insert("invoices", invoice_data)
    # Update shipment status to 'dikirim' if still pending
    if shipment["status"] == "pending":
        db.update("shipments", data.shipment_id, {"status": "dikirim"})
    
    return result

@router.put("/{invoice_id}")
async def update_invoice(invoice_id: str, update: InvoiceUpdate, current_user: dict = Depends(get_current_user)):
    invoice = db.get_by_id("invoices", invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    
    # Recalculate if tax or discount changed
    if "tax_percent" in update_data or "discount_amount" in update_data:
        subtotal = invoice["subtotal"]
        tax_pct = update_data.get("tax_percent", invoice["tax_percent"])
        discount = update_data.get("discount_amount", invoice["discount_amount"])
        tax_amount = subtotal * (tax_pct / 100)
        update_data["tax_amount"] = tax_amount
        update_data["total_amount"] = subtotal + tax_amount - discount
    
    if update_data.get("payment_status") == "lunas" and not update_data.get("payment_date"):
        update_data["payment_date"] = datetime.now().isoformat()
    
    updated = db.update("invoices", invoice_id, update_data)
    return updated

@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "keuangan"]:
        raise HTTPException(status_code=403, detail="Akses ditolak")
    
    invoice = db.get_by_id("invoices", invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    if invoice.get("payment_status") == "lunas":
        raise HTTPException(status_code=400, detail="Tidak bisa menghapus invoice yang sudah lunas")
    
    db.delete("invoices", invoice_id)
    return {"message": "Invoice berhasil dihapus"}
