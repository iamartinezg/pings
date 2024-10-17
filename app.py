from flask import Flask, jsonify
import requests
import schedule
import time
import threading

app = Flask(__name__)

# URLs de los microservicios a monitorear
MICROSERVICIOS = {
    "chatgpt": "https://smishguard-chatgpt-ms.onrender.com/ping",
    "modelo_ml": "https://smishguard-modeloml-ms.onrender.com/ping",
    "virustotal": "https://smishguard-virustotal-ms.onrender.com/ping",
    "twitter": "https://smishguard-twitter-ms.onrender.com/ping",
    "backend": "https://smishguard-api-gateway.onrender.com/ping"
}

# Diccionario para almacenar el estado de los microservicios
estado_servicios = {}

def hacer_ping_a_servicios():
    """
    Función para hacer ping a los microservicios y actualizar su estado.
    """
    for nombre, url in MICROSERVICIOS.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                estado_servicios[nombre] = "Online"
            else:
                estado_servicios[nombre] = f"Offline (Código de estado: {response.status_code})"
        except requests.exceptions.RequestException as e:
            estado_servicios[nombre] = f"Offline (Error: {str(e)})"

    print("Ping completado a todos los servicios")

# Programar ping a los microservicios cada 5 minutos
schedule.every(5).minutes.do(hacer_ping_a_servicios)

# Endpoint para ver el estado actual de los microservicios
@app.route("/estado-servicios", methods=["GET"])
def estado_servicios_endpoint():
    return jsonify(estado_servicios)

# Función para correr el scheduler en un hilo separado
def ejecutar_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Ruta principal para saber que el servidor está funcionando
@app.route("/")
def index():
    return "Servicio de monitoreo de microservicios funcionando."

if __name__ == "__main__":
    # Iniciar el scheduler en un hilo separado
    scheduler_thread = threading.Thread(target=ejecutar_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Hacer un ping inicial antes de que inicie el loop
    hacer_ping_a_servicios()

    # Iniciar el servidor Flask
    app.run(debug=True, port=5001)
