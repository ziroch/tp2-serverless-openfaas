#!/bin/bash

# Configuración Estricta de Rutas de Usuario
RUTA_PROYECTO="/home/victor/Documentos/UCOM/4toAnho/ProgramacionLinuxII/tp2-serverless-openfaas"
ENDPOINT_URL="https://openfaas-gateway-openfaas.apps.ocpvmsno.lab.data.com.py/function/log-analyzer"
CONCURRENCIA_OBJETIVO=60
ARCHIVO_LOGS="$RUTA_PROYECTO/client/access_masivo.log"

echo "Iniciando inyección concurrente: $CONCURRENCIA_OBJETIVO ráfagas en paralelo..."
tiempo_inicio=$(date +%s%N)

# Disparar subprocesos concurrentes en segundo plano usando la sintaxis &
for i in $(seq 1 $CONCURRENCIA_OBJETIVO); do
    (
        # 'shuf' extrae de forma ultra veloz un flujo limpio de 5000 registros 
        # emulando la carga real distribuida solicitada por la cátedra
        shuf -n 5000 "$ARCHIVO_LOGS" | curl -s -k -X POST --data-binary @- "$ENDPOINT_URL" | python3 "$RUTA_PROYECTO/client/db_loader.py"
    ) &
done

wait # Barrera de sincronización Unix (espera a que terminen los 60 subprocesos)

tiempo_fin=$(date +%s%N)
duracion_ms=$(( (tiempo_fin - tiempo_inicio) / 1000000 ))

echo "--------------------------------------------------------"
echo "Prueba de carga finalizada exitosamente."
echo "Tiempo total de ejecución del pipeline: $duracion_ms ms"
echo "--------------------------------------------------------"

# Consultar de manera definitiva sobre la base consolidada con exclusión mutua
echo "Muestra consolidada en SQLite (Top 5 IPs con más tráfico exitoso):"
sqlite3 "$RUTA_PROYECTO/client/analytics.db" "SELECT * FROM reporte_ips ORDER BY hits DESC LIMIT 5;"
