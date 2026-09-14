#!/usr/bin/env python3
import sys
import json
import re
from collections import defaultdict

def main():
    # Regex para parsear Common Log Format (CLF)
    log_regex = re.compile(
        r'(?P<ip>\S+)\s+\S+\s+\S+\s+\[.*?\]\s+"(?:GET|POST|PUT|DELETE|HEAD)\s+\S+\s+\S+"\s+(?P<status>\d{3})\s+(?P<bytes>\d+|-)'
    )
    
    # Estructura para agrupar por IP
    metricas = defaultdict(lambda: {"hits": 0, "bytes_transferidos": 0})

    # Procesar flujo continuo por la entrada estándar (stdin)
    for linea in sys.stdin:
        linea = linea.strip()
        if not linea:
            continue
            
        match = log_regex.match(linea)
        if match:
            datos = match.groupdict()
            status = int(datos["status"])
            
            # Requisito Técnico A.2: Filtrar peticiones fallidas
            if status >= 400:
                continue
                
            ip = datos["ip"]
            raw_bytes = datos["bytes"]
            bytes_val = int(raw_bytes) if raw_bytes != '-' else 0
            
            metricas[ip]["hits"] += 1
            metricas[ip]["bytes_transferidos"] += bytes_val

    # Requisito Técnico A.1: Retornar reporte estructurado en stdout
    print(json.dumps(metricas))

if __name__ == "__main__":
    main()
