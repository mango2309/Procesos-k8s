import os
import socket

from flask import Flask, jsonify

app = Flask(__name__)

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")


@app.get("/")
def root():
    return jsonify(
        mensaje="Hola desde Flask en Kubernetes",
        pod_hostname=socket.gethostname(),
        version=APP_VERSION,
    )


@app.get("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
