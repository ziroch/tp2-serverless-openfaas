# Etapa 1: Descarga del watchdog binario oficial
FROM alpine:3.18 AS builder
RUN apk add --no-cache curl
RUN curl -sSLf https://github.com > /usr/bin/fwatchdog \
    && chmod +x /usr/bin/fwatchdog

# Etapa 2: Imagen final ligera de ejecución
FROM alpine:3.18
RUN apk add --no-cache python3

# Crear usuario seguro no-root exigido por buenas prácticas de Cloud
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /home/appuser

# Copiar artefactos de la etapa anterior y código fuente
COPY --from=builder /usr/bin/fwatchdog /usr/bin/fwatchdog
COPY handler.py .

# Variables de entorno críticas para el modo CGI (E/S Estándar)
ENV mode="cgi"
ENV fprocess="python3 handler.py"
EXPOSE 8080

USER appuser
CMD ["/usr/bin/fwatchdog"]
