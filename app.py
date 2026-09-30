from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import time, random

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route('/')
def home():
    return jsonify({"status": "ok", "service": "devops-case-study-amazon"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/work')
def work():
    time.sleep(random.uniform(0.1, 0.5))
    if random.random() < 0.1:
        return jsonify({"error": "random failure"}), 500
    return jsonify({"result": "done"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)