#!/usr/bin/env python3
import random
import time

def generar_logs(filename="client/access_masivo.log", total_lineas=1000000):
    ips = [f"192.168.1.{random.randint(10, 250)}" for _ in range(50)] + \
          [f"10.0.0.{random.randint(5, 100)}" for _ in range(30)]
    
    recursos = ["/index.html", "/api/v1/resource", "/login", "/dashboard", "/styles.css", "/js/main.js"]
    metodos = ["GET", "POST", "PUT", "DELETE"]
    
    # Pesos para simular realismo (85% éxitos, 15% fallos >= 400 para probar el filtro del TP)
    statuses = [200, 201, 304, 400, 401, 404, 500]
    weights = [60, 15, 10, 5, 3, 5, 2]

    print(f"Generando {total_lineas} registros en {filename}...")
    start_time = time.time()

    with open(filename, "w") as f:
        for _ in range(total_lineas):
            ip = random.choice(ips)
            metodo = random.choice(metodos)
            recurso = random.choice(recursos)
            status = random.choices(statuses, weights=weights)[0]
            bytes_sz = random.randint(100, 5000) if status < 400 else random.randint(20, 300)
            
            # Formato estándar de log: IP - - [Fecha] "METODO RECURSO HTTP" STATUS BYTES
            log_line = f'{ip} - - [09/Sep/2026:20:00:00 -0300] "{metodo} {recurso} HTTP/1.1" {status} {bytes_sz}\n'
            f.write(log_line)

    print(f"¡Listo! Archivo creado en {time.time() - start_time:.2f} segundos.")

if __name__ == "__main__":
    generar_logs()
