# mi-proyecto-k8s (Flask + Docker + Kubernetes en Minikube)

Proyecto de despliegue en Kubernetes (Minikube) siguiendo el enfoque tipico de laboratorios: construir imagen Docker localmente dentro del daemon de Minikube, y desplegar progresivamente con `Pod -> ReplicaSet -> Deployment + Service`.

La API es minima (Python/Flask):

- `GET /` retorna JSON con `mensaje`, `pod_hostname` y `version`.
- `GET /health` retorna `{"status":"ok"}` para health checks.

El `pod_hostname` cambia por replica, permitiendo evidenciar balanceo de carga y escalamiento.

## Stack

- Python 3 + Flask
- Docker
- Kubernetes (Minikube con driver Docker) + kubectl
- Sistema operativo documentado: Windows (PowerShell)

## Estructura

```
mi-proyecto-k8s/
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/
│   ├── 01-pod.yaml
│   ├── 02-replicaset.yaml
│   ├── 03-deployment.yaml
│   └── 04-service.yaml
├── evidencias/
│   └── (aqui iran las capturas de pantalla)
├── .gitignore
├── COMANDOS.md
└── README.md
```

## 0) Instalacion de herramientas

En Windows (opciones comunes):

- Docker Desktop (con Kubernetes desactivado; usaremos Minikube)
- kubectl
  - `winget install Kubernetes.kubectl`
- Minikube
  - `winget install Kubernetes.minikube`

Verifica versiones:

- `docker version`
- `kubectl version --client`
- `minikube version`

## 1) Iniciar el cluster

```powershell
minikube start --driver=docker --cpus=2 --memory=4096
```

## 2) Apuntar al daemon Docker de Minikube

Esto hace que el `docker build` quede dentro del runtime del cluster (no Docker Hub).

Windows PowerShell:

```powershell
minikube docker-env --shell powershell | Invoke-Expression
```

macOS/Linux (bash/zsh):

```bash
eval $(minikube docker-env)
```

## 3) Construir la imagen localmente

Opcion A (recomendada) desde la raiz `mi-proyecto-k8s/`:

```powershell
docker build -t taller-app:1.0.0 -f app/Dockerfile app
```

Opcion B (coincide con el comando clasico `docker build ... .`), entrando a `app/`:

```powershell
cd app
docker build -t taller-app:1.0.0 .
cd ..
```

Opcional (verificar que existe en el daemon actual):

```powershell
docker images | findstr taller-app
```

## 4) Pod standalone (01-pod.yaml) + port-forward

Aplicar:

```powershell
kubectl apply -f k8s/01-pod.yaml
kubectl get pods -o wide
```

Port-forward:

```powershell
kubectl port-forward pod/taller-app-pod 5000:5000
```

Probar endpoints (en otra terminal):

```powershell
curl.exe http://127.0.0.1:5000/
curl.exe http://127.0.0.1:5000/health
```

Salida esperada (ejemplo):

```json
{"mensaje":"Hola desde Flask en Kubernetes","pod_hostname":"taller-app-pod","version":"1.0.0"}
```

## 5) ReplicaSet (02-replicaset.yaml) + autohealing

Aplicar:

```powershell
kubectl apply -f k8s/02-replicaset.yaml
kubectl get rs
kubectl get pods -l managed-by=replicaset -o wide
```

Probar autohealing:

1. Identifica un pod del ReplicaSet:

```powershell
kubectl get pods -l managed-by=replicaset
```

2. Borra 1 pod:

```powershell
kubectl delete pod <pod-name>
```

3. Observa que se recrea automaticamente:

```powershell
kubectl get pods -l managed-by=replicaset
```

## 6) Deployment (03-deployment.yaml) + Service (04-service.yaml)

Aplicar:

```powershell
kubectl apply -f k8s/03-deployment.yaml
kubectl apply -f k8s/04-service.yaml
kubectl get deploy
kubectl get svc
```

Obtener URL del Service en Minikube:

```powershell
$url = minikube service taller-app-svc --url
$url
```

Bucle para evidenciar balanceo (rotacion de `pod_hostname`):

```powershell
1..10 | ForEach-Object {
  curl.exe -s "$url/"
  ""
  Start-Sleep -Seconds 1
}
```

## 7) Escalar a 5 replicas

```powershell
kubectl scale deployment taller-app-deploy --replicas=5
kubectl get pods -l managed-by=deployment
```

Repetir el bucle de `curl` y deberias ver hasta 5 hostnames distintos a lo largo de varias solicitudes.

## 8) Reducir a 2 replicas

```powershell
kubectl scale deployment taller-app-deploy --replicas=2
kubectl get pods -l managed-by=deployment
```

## 9) Limpieza

```powershell
kubectl delete -f k8s/
minikube stop
```

---

## Seccion teorica obligatoria

| Objeto     | Funcion principal              | Caso de uso real              |
|-----------|--------------------------------|-------------------------------|
| Pod       | Unidad atomica de ejecucion    | Debug, jobs puntuales         |
| ReplicaSet| Mantiene N replicas vivas      | Base del Deployment           |
| Deployment| Rollout, rollback, escalado    | Apps stateless en produccion  |
| Service   | Red estable ante pods efimeros | Exposicion de cualquier app   |

Explicacion rapida:

- Pod: es la unidad minima programable. Si muere, Kubernetes puede recrearlo, pero tu no tienes estrategia de versiones/rollouts.
- ReplicaSet: garantiza que existan exactamente N pods con un selector. Si borras un pod, se recrea. No maneja bien cambios declarativos de version/imagens.
- Deployment: es la capa recomendada para aplicaciones stateless. Gestiona ReplicaSets, actualizaciones graduales (rollout) y rollback.
- Service: expone una IP/DNS estable y balancea trafico hacia pods seleccionados por labels (los pods son efimeros).

---

## Evidencias del entregable

Tabla de comandos y salida esperada (ejemplos). Usa esta seccion para pegar capturas en `evidencias/`.

| Evidencia | Comando | Salida esperada (resumen) |
|----------|---------|----------------------------|
| Pods corriendo | `kubectl get pods -o wide` | Pods en `Running` con IPs y nodos |
| ReplicaSet activo | `kubectl get replicaset` | `taller-app-rs` con `DESIRED/CURRENT/READY = 3` |
| Deployment con replicas | `kubectl get deployments` | `taller-app-deploy` con `READY 3/3` (o segun escalado) |
| Service NodePort | `kubectl get services` | `taller-app-svc` tipo `NodePort` |
| Balanceo | `curl $URL/` (varias veces) | `pod_hostname` alterna entre pods |
| Escalado a 5 | `kubectl scale ... --replicas=5` + `kubectl get pods` | 5 pods `Running` |
| Escalado a 2 | `kubectl scale ... --replicas=2` + `kubectl get pods` | 2 pods `Running` |
| Dashboard (opcional) | `minikube dashboard` | Vista web de workloads y recursos |

Notas:

- Si `curl` no esta disponible, en PowerShell puedes usar `Invoke-RestMethod $url/`.
- Los manifiestos usan `imagePullPolicy: Never` para forzar el uso de la imagen local construida dentro de Minikube.
