from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # admin, staff, keuangan
    name: str
    email: str

class CustomerCreate(BaseModel):
    name: str
    address: str
    phone: str
    email: Optional[str] = ""
    contact_person: Optional[str] = ""
    npwp: Optional[str] = ""

class DestinationCreate(BaseModel):
    city: str
    province: str
    zone: str  # A, B, C
    surcharge: float = 0

class ServiceCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = ""
    price_per_kg: float
    min_weight: float = 1

class ShipmentCreate(BaseModel):
    sender_name: str
    sender_address: str
    sender_phone: str
    receiver_name: str
    receiver_address: str
    receiver_phone: str
    destination_id: str
    service_id: str
    weight: float
    description: Optional[str] = ""
    notes: Optional[str] = ""
    customer_id: Optional[str] = None

class ShipmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class InvoiceCreate(BaseModel):
    shipment_id: str
    tax_percent: Optional[float] = 11.0
    discount_amount: Optional[float] = 0
    notes: Optional[str] = ""

class InvoiceUpdate(BaseModel):
    payment_status: Optional[str] = None
    payment_date: Optional[str] = None
    notes: Optional[str] = None
    tax_percent: Optional[float] = None
    discount_amount: Optional[float] = None
