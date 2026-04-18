import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

class JSONDatabase:
    def __init__(self):
        self._init_collections()
    
    def _init_collections(self):
        collections = ["users", "customers", "destinations", "services", "shipments", "invoices"]
        for col in collections:
            file = DATA_DIR / f"{col}.json"
            if not file.exists():
                file.write_text("[]")
        
        # Seed default data
        self._seed_users()
        self._seed_services()
        self._seed_destinations()
        self._seed_customers()
    
    def _seed_users(self):
        if not self.get_all("users"):
            import hashlib
            users = [
                {"id": str(uuid.uuid4()), "username": "admin", "password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "admin", "name": "Administrator", "email": "admin@galaxymultitrans.com", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "username": "staff", "password": hashlib.sha256("staff123".encode()).hexdigest(), "role": "staff", "name": "Staff Operasional", "email": "staff@galaxymultitrans.com", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "username": "keuangan", "password": hashlib.sha256("keuangan123".encode()).hexdigest(), "role": "keuangan", "name": "Staff Keuangan", "email": "keuangan@galaxymultitrans.com", "created_at": datetime.now().isoformat()},
            ]
            self.save_all("users", users)
    
    def _seed_services(self):
        if not self.get_all("services"):
            services = [
                {"id": str(uuid.uuid4()), "name": "Reguler", "code": "REG", "description": "Pengiriman standar 3-5 hari kerja", "price_per_kg": 15000, "min_weight": 1, "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": "Express", "code": "EXP", "description": "Pengiriman cepat 1-2 hari kerja", "price_per_kg": 35000, "min_weight": 1, "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": "Cargo", "code": "CGO", "description": "Pengiriman barang besar/berat >50kg", "price_per_kg": 8000, "min_weight": 50, "created_at": datetime.now().isoformat()},
            ]
            self.save_all("services", services)
    
    def _seed_destinations(self):
        if not self.get_all("destinations"):
            destinations = [
                {"id": str(uuid.uuid4()), "city": "Jakarta", "province": "DKI Jakarta", "zone": "A", "surcharge": 0, "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "city": "Surabaya", "province": "Jawa Timur", "zone": "B", "surcharge": 5000, "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "city": "Bandung", "province": "Jawa Barat", "zone": "A", "surcharge": 2000, "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "city": "Medan", "province": "Sumatera Utara", "zone": "C", "surcharge": 10000, "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "city": "Makassar", "province": "Sulawesi Selatan", "zone": "C", "surcharge": 12000, "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "city": "Semarang", "province": "Jawa Tengah", "zone": "B", "surcharge": 3000, "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "city": "Yogyakarta", "province": "DI Yogyakarta", "zone": "B", "surcharge": 4000, "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "city": "Palembang", "province": "Sumatera Selatan", "zone": "C", "surcharge": 8000, "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "city": "Denpasar", "province": "Bali", "zone": "B", "surcharge": 6000, "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "city": "Pontianak", "province": "Kalimantan Barat", "zone": "C", "surcharge": 15000, "created_at": datetime.now().isoformat()},
            ]
            self.save_all("destinations", destinations)
    
    def _seed_customers(self):
        if not self.get_all("customers"):
            customers = [
                {"id": str(uuid.uuid4()), "name": "PT Maju Bersama", "address": "Jl. Sudirman No. 45, Jakarta Pusat", "phone": "021-5551234", "email": "info@majubersama.co.id", "contact_person": "Budi Santoso", "npwp": "12.345.678.9-000.000", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": "CV Sumber Rejeki", "address": "Jl. Gatot Subroto No. 12, Bandung", "phone": "022-7778888", "email": "cs@sumberrejeki.com", "contact_person": "Dewi Rahayu", "npwp": "98.765.432.1-000.000", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": "Toko Elektronik Jaya", "address": "Jl. Pahlawan No. 78, Surabaya", "phone": "031-3334444", "email": "order@elektronikjaya.com", "contact_person": "Ahmad Fauzi", "npwp": "11.222.333.4-000.000", "created_at": datetime.now().isoformat()},
            ]
            self.save_all("customers", customers)
    
    def _get_file(self, collection: str) -> Path:
        return DATA_DIR / f"{collection}.json"
    
    def get_all(self, collection: str) -> List[Dict]:
        try:
            return json.loads(self._get_file(collection).read_text())
        except:
            return []
    
    def save_all(self, collection: str, data: List[Dict]):
        self._get_file(collection).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def get_by_id(self, collection: str, id: str) -> Optional[Dict]:
        return next((item for item in self.get_all(collection) if item["id"] == id), None)
    
    def insert(self, collection: str, data: Dict) -> Dict:
        items = self.get_all(collection)
        data["id"] = str(uuid.uuid4())
        data["created_at"] = datetime.now().isoformat()
        items.append(data)
        self.save_all(collection, items)
        return data
    
    def update(self, collection: str, id: str, data: Dict) -> Optional[Dict]:
        items = self.get_all(collection)
        for i, item in enumerate(items):
            if item["id"] == id:
                items[i] = {**item, **data, "id": id, "updated_at": datetime.now().isoformat()}
                self.save_all(collection, items)
                return items[i]
        return None
    
    def delete(self, collection: str, id: str) -> bool:
        items = self.get_all(collection)
        new_items = [item for item in items if item["id"] != id]
        if len(new_items) < len(items):
            self.save_all(collection, new_items)
            return True
        return False
    
    def query(self, collection: str, filters: Dict) -> List[Dict]:
        items = self.get_all(collection)
        for key, value in filters.items():
            items = [item for item in items if str(item.get(key, "")).lower() == str(value).lower()]
        return items
    
    def generate_resi(self) -> str:
        shipments = self.get_all("shipments")
        count = len(shipments) + 1
        date_str = datetime.now().strftime("%Y%m%d")
        return f"GMT{date_str}{count:04d}"
    
    def generate_invoice_number(self) -> str:
        invoices = self.get_all("invoices")
        count = len(invoices) + 1
        date_str = datetime.now().strftime("%Y%m")
        return f"INV/{date_str}/{count:04d}"

db = JSONDatabase()
