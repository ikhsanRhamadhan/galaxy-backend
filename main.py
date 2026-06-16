from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
import json
from pathlib import Path
from models import *
from database import db
from routers import auth, customers, destinations, services, shipments, invoices, reports

app = FastAPI(title="PT Galaxy Multi Trans API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(destinations.router, prefix="/api/destinations", tags=["Destinations"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(shipments.router, prefix="/api/shipments", tags=["Shipments"])
app.include_router(invoices.router, prefix="/api/invoices", tags=["Invoices"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

@app.get("/api/dashboard")
async def get_dashboard(current_user: dict = Depends(auth.get_current_user)):
    shipments_list = db.get_all("shipments")
    invoices_list = db.get_all("invoices")
    
    total_shipments = len(shipments_list)
    total_invoices = len(invoices_list)
    total_revenue = sum(inv["total_amount"] for inv in invoices_list if inv["payment_status"] == "lunas")
    pending_payment = sum(inv["total_amount"] for inv in invoices_list if inv["payment_status"] == "belum_bayar")
    
    status_count = {"pending": 0, "dikirim": 0, "selesai": 0}
    for s in shipments_list:
        if s["status"] in status_count:
            status_count[s["status"]] += 1
    
    recent_shipments = sorted(shipments_list, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
    recent_invoices = sorted(invoices_list, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
    
    return {
        "total_shipments": total_shipments,
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "pending_payment": pending_payment,
        "status_count": status_count,
        "recent_shipments": recent_shipments,
        "recent_invoices": recent_invoices
    }

@app.get("/")
async def root():
    return {"message": "PT Galaxy Multi Trans API", "version": "1.0.0"}
