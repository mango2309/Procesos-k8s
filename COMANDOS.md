# COMANDOS.md (Referencia rapida)

Asume que estas ubicado en `mi-proyecto-k8s/`.

## 0) Minikube

- Iniciar cluster (driver Docker):
  - `minikube start --driver=docker --cpus=2 --memory=4096`

- Ver estado:
  - `minikube status`

- Apuntar Docker local al daemon de Minikube:
  - Windows PowerShell:
    - `minikube docker-env --shell powershell | Invoke-Expression`
  - macOS/Linux (bash/zsh):
    - `eval $(minikube docker-env)`

- Deshacer docker-env:
  - Windows PowerShell:
    - `minikube docker-env --shell powershell --unset | Invoke-Expression`
  - macOS/Linux:
    - `eval $(minikube docker-env -u)`

- Abrir dashboard (opcional):
  - `minikube dashboard`

## 1) Docker

- Build de la imagen (usando el Dockerfile dentro de `app/`):
  - Opcion A (recomendada, sin cambiar de carpeta):
    - `docker build -t taller-app:1.0.0 -f app/Dockerfile app`
  - Opcion B:
    - `cd app`
    - `docker build -t taller-app:1.0.0 .`
    - `cd ..`

- Ver imagenes:
  - `docker images | findstr taller-app`

## 2) Kubernetes (kubectl)

- Aplicar manifiestos:
  - Pod:
    - `kubectl apply -f k8s/01-pod.yaml`
  - ReplicaSet:
    - `kubectl apply -f k8s/02-replicaset.yaml`
  - Deployment + Service:
    - `kubectl apply -f k8s/03-deployment.yaml`
    - `kubectl apply -f k8s/04-service.yaml`
  - Todo el folder:
    - `kubectl apply -f k8s/`

- Inspeccion:
  - `kubectl get pods -o wide`
  - `kubectl get rs`
  - `kubectl get deploy`
  - `kubectl get svc`
  - `kubectl describe pod taller-app-pod`
  - `kubectl logs pod/taller-app-pod`

- Port-forward (para Pod standalone):
  - `kubectl port-forward pod/taller-app-pod 5000:5000`

- Probar endpoints:
  - `curl.exe http://127.0.0.1:5000/`
  - `curl.exe http://127.0.0.1:5000/health`

- Borrar un pod (autohealing del ReplicaSet/Deployment):
  - `kubectl delete pod <pod-name>`

- Escalado:
  - `kubectl scale deployment taller-app-deploy --replicas=5`
  - `kubectl scale deployment taller-app-deploy --replicas=2`

- Service URL en Minikube:
  - `minikube service taller-app-svc --url`

- Limpieza:
  - `kubectl delete -f k8s/`
  - `minikube stop`
