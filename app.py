from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time, random, string

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('total_requests', 'Total number of requests')
PROCESSING_TIME = Histogram('processing_time', 'Time taken to process requests')
AVG_REQUEST_SIZE = Gauge('average_request_size', 'Average size of incoming requests')
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
ERROR_RATE = Counter('error_rate', 'Number of errors')
REQUEST_LATENCY = Histogram('request_latency', 'Latency of requests')
TOTAL_ITEMS_CREATED = Counter('total_items_created', 'Total number of items created by users')
USER_ACTIVITY = Counter('user_activity', 'Number of actions taken by users', ['user_id'])

# Data stores
active_users = set()
items_store = {}

# Helper function to simulate processing delay
def simulate_processing():
    delay = random.uniform(0.1, 0.5)
    time.sleep(delay)
    PROCESSING_TIME.observe(delay)
    return delay

# Generate random token for demo purposes
def generate_token():
    return ''.join(random.choice(string.ascii_letters) for _ in range(10))

@app.route('/metrics')
def metrics():
    return generate_latest()

@app.route('/api/items', methods=['POST'])
def create_item():
    start_time = time.time()
    user_id = request.headers.get('User-ID', 'guest')
    token = request.headers.get('Token')

    if not token:
        ERROR_RATE.inc()
        return jsonify({"error": "Unauthorized"}), 403

    try:
        active_users.add(user_id)
        ACTIVE_USERS.set(len(active_users))
        REQUEST_COUNT.inc()
        size = len(request.data) if request.data else 0
        AVG_REQUEST_SIZE.set(size)
        
        simulate_processing()

        item_id = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        items_store[item_id] = {"created_by": user_id, "timestamp": time.time()}
        TOTAL_ITEMS_CREATED.inc()
        USER_ACTIVITY.labels(user_id=user_id).inc()

        latency = time.time() - start_time
        REQUEST_LATENCY.observe(latency)

        return jsonify({"status": "item created", "item_id": item_id}), 201
    except Exception as e:
        ERROR_RATE.inc()
        return jsonify({"error": str(e)}), 500
    finally:
        if user_id in active_users:
            active_users.remove(user_id)
        ACTIVE_USERS.set(len(active_users))

@app.route('/api/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    user_id = request.headers.get('User-ID', 'guest')
    token = request.headers.get('Token')

    if not token:
        ERROR_RATE.inc()
        return jsonify({"error": "Unauthorized"}), 403

    if item_id in items_store:
        del items_store[item_id]
        return jsonify({"status": "item deleted"}), 200
    else:
        ERROR_RATE.inc()
        return jsonify({"error": "Item not found"}), 404

@app.route('/api/token', methods=['POST'])
def get_token():
    user_id = request.headers.get('User-ID', 'guest')
    token = generate_token()
    return jsonify({"token": token})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)