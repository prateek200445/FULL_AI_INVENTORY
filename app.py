from flask import Flask, request, jsonify, Response, stream_with_context, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import model
import threading
import queue
import json

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "Flask Inventory Forecast API running"})


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from the static directory."""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_dir, filename)


@app.route('/retrain-page')
def retrain_page():
    """Direct route to the retrain HTML page."""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_dir, 'retrain.html')


@app.route('/retrain', methods=['POST'])
def retrain():
    # Expects a file in form field 'file' and returns a streaming response with progress
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(save_path)

    q = queue.Queue()

    # Start background thread to run retraining and push progress messages to queue
    t = threading.Thread(target=model.retrain_model_with_queue, args=(save_path, q), daemon=True)
    t.start()

    def generate():
        # Yield progress messages as they arrive from queue until thread finishes
        while True:
            try:
                item = q.get(timeout=0.5)
            except queue.Empty:
                if not t.is_alive():
                    break
                continue

            # If final result dict is sent, emit JSON with type 'result'
            if isinstance(item, dict):
                yield json.dumps({'type': 'result', 'data': item}) + '\n'
            else:
                yield json.dumps({'type': 'progress', 'data': item}) + '\n'

        # Drain any remaining messages
        while not q.empty():
            item = q.get()
            if isinstance(item, dict):
                yield json.dumps({'type': 'result', 'data': item}) + '\n'
            else:
                yield json.dumps({'type': 'progress', 'data': item}) + '\n'

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/forecast', methods=['POST'])
def forecast():
    # Accepts JSON body with optional filters and days
    payload = request.get_json() or {}
    days = payload.get('days', 7)
    product_id = payload.get('product_id')
    category = payload.get('category')
    region = payload.get('region')
    min_rating = payload.get('min_rating')
    max_price = payload.get('max_price')
    min_discount = payload.get('min_discount')

    try:
        result = model.forecast(
            days=days,
            product_id=product_id,
            category=category,
            region=region,
            min_rating=min_rating,
            max_price=max_price,
            min_discount=min_discount
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    # Run without auto-reload to prevent interruption during long-running training
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
