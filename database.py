import json
import os
import hashlib
from datetime import datetime
from config import DB_FILE

def load_db():
    """Loads the local JSON database or initializes default ports and genesis block."""
    if not os.path.exists(DB_FILE):
        initial_data = {
            "ports": [
                {
                    "port_name": "Port of Cochin",
                    "total_berths": 20,
                    "pre_booked": 14,
                    "available_spaces": 6,
                    "contact": "+91 484 2666416 | ops@cochinport.gov.in",
                    "required_docs": "Customs Clearance, Cold-Chain Manifest, Crew Health Cert",
                    "port_details": "Deep-water berth available; 24/7 automated crane & reefer plug-in support."
                },
                {
                    "port_name": "Port of Colombo",
                    "total_berths": 35,
                    "pre_booked": 27,
                    "available_spaces": 8,
                    "contact": "+94 11 2421201 | harbour@slpa.lk",
                    "required_docs": "Bill of Lading, IMO Dangerous Goods Decl, Sanitary Cert",
                    "port_details": "High-speed transshipment hub; fast-track customs via Fluxora."
                }
            ],
            "requests": [],
            "blockchain": [
                {
                    "block": 0,
                    "timestamp": str(datetime.now()),
                    "action": "GENESIS_BLOCK",
                    "details": "Fluxora Maritime Ledger Initialized",
                    "prev_hash": "0" * 64,
                    "hash": hashlib.sha256(b"GENESIS").hexdigest()
                }
            ]
        }
        save_db(initial_data)
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data: dict):
    """Writes updated state to the local JSON file."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def add_blockchain_record(db: dict, action: str, details: str):
    """Appends a tamper-evident SHA-256 block linked to the previous block."""
    prev_block = db["blockchain"][-1]
    block_num = prev_block["block"] + 1
    timestamp = str(datetime.now())
    raw_string = f"{block_num}{timestamp}{action}{details}{prev_block['hash']}"
    block_hash = hashlib.sha256(raw_string.encode()).hexdigest()

    db["blockchain"].append({
        "block": block_num,
        "timestamp": timestamp,
        "action": action,
        "details": details,
        "prev_hash": prev_block["hash"],
        "hash": block_hash
    })
