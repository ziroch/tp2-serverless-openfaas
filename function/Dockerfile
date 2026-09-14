# Stage 1: Extracción del watchdog oficial multi-arquitectura desde su registro nativo
FROM ghcr.io/openfaas/of-watchdog:0.9.11 AS watchdog

# Stage 2: Imagen final ligera de ejecución en Alpine
FROM alpine:3.18
RUN apk add --no-cache python3

# Crear usuario seguro no-root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /home/appuser

# Copiar el binario correcto mapeado automáticamente a la arquitectura destino por el motor
COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

# Copiar el código fuente
COPY function/handler.py .

# Variables de entorno críticas para el modo CGI (E/S Estándar)
ENV mode="serializing"
ENV fprocess="python3 handler.py"

EXPOSE 8080

USER appuser
CMD ["/usr/bin/fwatchdog"]

