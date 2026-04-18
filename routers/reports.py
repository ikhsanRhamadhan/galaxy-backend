from fastapi import APIRouter, HTTPException, Depends, Query
from database import db
from routers.auth import get_current_user
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.get("/shipments")
async def report_shipments(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    shipments = db.get_all("shipments")
    services = {s["id"]: s for s in db.get_all("services")}
    destinations = {d["id"]: d for d in db.get_all("destinations")}
    
    if start_date:
        shipments = [s for s in shipments if s.get("created_at", "") >= start_date]
    if end_date:
        shipments = [s for s in shipments if s.get("created_at", "") <= end_date + "T23:59:59"]
    if status:
        shipments = [s for s in shipments if s.get("status") == status]
    
    for s in shipments:
        s["service_detail"] = services.get(s.get("service_id", ""), {})
        s["destination_detail"] = destinations.get(s.get("destination_id", ""), {})
    
    total_weight = sum(s.get("weight", 0) for s in shipments)
    total_cost = sum(s.get("total_cost", 0) for s in shipments)
    
    return {
        "data": sorted(shipments, key=lambda x: x.get("created_at", ""), reverse=True),
        "summary": {
            "total": len(shipments),
            "total_weight": total_weight,
            "total_cost": total_cost,
            "by_status": {
                "pending": len([s for s in shipments if s.get("status") == "pending"]),
                "dikirim": len([s for s in shipments if s.get("status") == "dikirim"]),
                "selesai": len([s for s in shipments if s.get("status") == "selesai"]),
            }
        }
    }

@router.get("/invoices")
async def report_invoices(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    invoices = db.get_all("invoices")
    shipments = {s["id"]: s for s in db.get_all("shipments")}
    
    if start_date:
        invoices = [i for i in invoices if i.get("created_at", "") >= start_date]
    if end_date:
        invoices = [i for i in invoices if i.get("created_at", "") <= end_date + "T23:59:59"]
    if payment_status:
        invoices = [i for i in invoices if i.get("payment_status") == payment_status]
    
    for inv in invoices:
        inv["shipment_detail"] = shipments.get(inv.get("shipment_id", ""), {})
    
    total_amount = sum(i.get("total_amount", 0) for i in invoices)
    paid_amount = sum(i.get("total_amount", 0) for i in invoices if i.get("payment_status") == "lunas")
    unpaid_amount = sum(i.get("total_amount", 0) for i in invoices if i.get("payment_status") == "belum_bayar")
    
    return {
        "data": sorted(invoices, key=lambda x: x.get("created_at", ""), reverse=True),
        "summary": {
            "total": len(invoices),
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "unpaid_amount": unpaid_amount,
            "paid_count": len([i for i in invoices if i.get("payment_status") == "lunas"]),
            "unpaid_count": len([i for i in invoices if i.get("payment_status") == "belum_bayar"]),
        }
    }

@router.get("/revenue")
async def report_revenue(
    year: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    invoices = db.get_all("invoices")
    
    if year:
        invoices = [i for i in invoices if i.get("created_at", "").startswith(str(year))]
    
    monthly_data = {}
    for inv in invoices:
        month = inv.get("created_at", "")[:7]  # YYYY-MM
        if month not in monthly_data:
            monthly_data[month] = {"month": month, "total": 0, "paid": 0, "unpaid": 0, "count": 0}
        monthly_data[month]["total"] += inv.get("total_amount", 0)
        monthly_data[month]["count"] += 1
        if inv.get("payment_status") == "lunas":
            monthly_data[month]["paid"] += inv.get("total_amount", 0)
        else:
            monthly_data[month]["unpaid"] += inv.get("total_amount", 0)
    
    return {
        "data": sorted(monthly_data.values(), key=lambda x: x["month"]),
        "summary": {
            "total_revenue": sum(i.get("total_amount", 0) for i in invoices if i.get("payment_status") == "lunas"),
            "total_invoiced": sum(i.get("total_amount", 0) for i in invoices),
        }
    }
