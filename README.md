# Trabajo Práctico 2: Pipeline de Procesamiento de Datos Serverless (OpenFaaS)
### Curso: Programación Unix-Linux II (Variante Cloud, Contenedores y Sockets)

Este repositorio contiene la implementación de un pipeline serverless para la limpieza y análisis estadístico de logs de acceso web masivos, montado sobre una arquitectura de **OpenFaaS** en **Red Hat OpenShift 4.22.10**. 

El proyecto aplica la filosofía Unix original: modularidad estricta mediante flujos de texto en la entrada estándar (`stdin`) y salida estándar (`stdout`), emulando el comportamiento CGI para integrarse en infraestructuras Cloud.

---
## Integrantes:

   -  Antonio Aguero
   -  Victor Martinez
   -  Hernan Silgueira

## Estructura de directorios de proeycto
tp2-serverless-openfaas/
├── access_masivo.log
├── build
│   └── log-analyzer
│       ├── Dockerfile
│       └── handler.py
├── captura
│   ├── Captura de pantalla de 2026-09-13 23-18-15.png
│   ├── Captura de pantalla de 2026-09-13 23-18-50.png
│   ├── Captura de pantalla de 2026-09-13 23-19-03.png
│   └── Captura de pantalla de 2026-09-13 23-26-52.png
├── client
│   ├── access_masivo.log
│   ├── analytics.db
│   ├── analytics.db.lock
│   ├── benchmark.sh
│   ├── benchmark.sh.bkp
│   ├── db_loader.py
│   └── generar_logs_masivos.py
├── function
│   ├── Dockerfile
│   └── handler.py
├── README.md
└── stack.yml


## 1. Preparación de la Infraestructura en OpenShift

Para cumplir con las estrictas políticas de seguridad nativas de OpenShift (RBAC y Security Context Constraints), ejecute los siguientes comandos autenticado en la CLI `oc` como administrador del clúster (`kubeadmin`).

### 1.1. Creación de Proyectos (Namespaces)
```bash
oc new-project openfaas
oc new-project openfaas-fn
```

### 1.2. Configuración de Cuentas de Servicio y RBAC
El controlador de OpenFaaS necesita permisos explícitos para gestionar pods dentro del espacio de funciones:
```bash
oc create sa faas-controller -n openfaas
oc adm policy add-role-to-user admin system:serviceaccount:openfaas:faas-controller -n openfaas-fn
```

### 1.3. Concesión de Privilegios de Seguridad (SCC)
Para permitir que las imágenes minimalistas y el componente `of-watchdog` inicien procesos con sus UIDs definidos sin bloqueos del clúster:
```bash
oc adm policy add-scc-to-user anyuid system:serviceaccount:openfaas:default
oc adm policy add-scc-to-user anyuid system:serviceaccount:openfaas:faas-controller
oc adm policy add-scc-to-user anyuid system:serviceaccount:openfaas-fn:default
```

### 1.4. Instalación de OpenFaaS vía Helm
```bash
helm repo add openfaas https://github.io
helm repo update

# Generar credenciales de acceso
GENERATED_PASS=\$(head -c 12 /dev/urandom | shasum | cut -d' ' -f1)
echo "Guarde su contraseña: \$GENERATED_PASS"

oc create secret generic basic-auth \
  --from-literal=basic-auth-user=admin \
  --from-literal=basic-auth-password="\$GENERATED_PASS" \
  -n openfaas

helm upgrade --install openfaas openfaas/openfaas \
  --namespace openfaas \
  --set basicAuth=true \
  --set functionNamespace=openfaas-fn \
  --set operator.create=true \
  --set serviceAccount=true \
  --set faasController.serviceAccountName=faas-controller
```

### 1.5. Exponer el Gateway (Creación de Ruta)
Cree y aplique la ruta nativa para obtener acceso HTTP externo:
```bash
oc apply -f - <<EOF
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: openfaas-gateway
  namespace: openfaas
spec:
  to:
    kind: Service
    name: gateway
    weight: 100
  port:
    targetPort: http
  tls:
    termination: edge
EOF

# Obtener URL del Gateway
OPENFAAS_URL="https://\$(oc get route openfaas-gateway -n openfaas -o jsonpath='{.spec.host}')"
echo "Gateway URL: \$OPENFAAS_URL"
```

---

## 📦 2. Compilación y Despliegue de la Función

1. Autentíquese en la CLI de OpenFaaS:
   ```bash
   faas-cli login --gateway "\(OPENFAAS_URL" --username admin --password "\)GENERATED_PASS"
   ```
2. Reemplace la URL del gateway y su repositorio de imágenes en el archivo `stack.yml`.
3. Compile, suba y despliegue la función en OpenShift:
   ```bash
   faas-cli build -f stack.yml
   faas-cli push -f stack.yml
   faas-cli deploy -f stack.yml
   ```

---

## 3. Ejecución del Pipeline Local y Pruebas de Estrés

Todos los componentes de persistencia y pruebas se ejecutan localmente desde la carpeta `client/`.

### 3.1. Generar el dataset masivo (1 Millón de registros)
Para cumplir con las pruebas de volumen del TP, ejecute el generador sintético:
```bash
python3 client/generar_logs_masivos.py
```

### 3.2. Lanzar el Benchmark Concurrente
Ejecute el script en Bash. Este enviará múltiples ráfagas HTTP concurrentes a OpenShift mediante `curl`, procesará los JSON devueltos y los guardará atómicamente en SQLite aplicando exclusión mutua (`fcntl`):
```bash
./client/benchmark.sh
```

---

## 4. Monitoreo e Informe de Rendimiento (Cgroups y Caos)

Durante la ejecución del benchmark, abra terminales adicionales para recolectar la información requerida en el reporte técnico:

* **Monitoreo de Cgroups (Límites de CPU/Memoria):**
  ```bash
  oc adm top pods -n openfaas-fn
  ```
* **Comportamiento del Auto-escalado Horizontal (HPA en tiempo real):**
  ```bash
  oc get deployment log-analyzer -n openfaas-fn -w
  ```

