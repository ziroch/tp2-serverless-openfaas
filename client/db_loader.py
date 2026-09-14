#!/usr/bin/env python3
import sys
import json
import sqlite3
import fcntl
import os

# --- Definición de rutas absolutas automáticas con el módulo os ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "analytics.db")
LOCK_FILE = os.path.join(BASE_DIR, "analytics.db.lock")

def inicializar_base_datos():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reporte_ips (
            ip TEXT PRIMARY KEY,
            hits INTEGER,
            bytes_transferidos INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def persistir_payload(raw_json):
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        return # Descartar si el JSON no es válido

    # Exclusión mutua (Mutex) a nivel de sistema de archivos Unix
    with open(LOCK_FILE, "w") as lock:
        try:
            # Adquirir un lock exclusivo
            fcntl.flock(lock, fcntl.LOCK_EX)
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            for ip, valores in data.items():
                cursor.execute('''
                    INSERT INTO reporte_ips (ip, hits, bytes_transferidos)
                    VALUES (?, ?, ?)
                    ON CONFLICT(ip) DO UPDATE SET
                        hits = hits + excluded.hits,
                        bytes_transferidos = bytes_transferidos + excluded.bytes_transferidos
                ''', (ip, valores['hits'], valores['bytes_transferidos']))
                
            conn.commit()
            conn.close()
        finally:
            # Liberar el bloqueo Unix de forma segura
            fcntl.flock(lock, fcntl.LOCK_UN)

if __name__ == "__main__":
    inicializar_base_datos()
    payload = sys.stdin.read()
    if payload.strip():
        persistir_payload(payload)
