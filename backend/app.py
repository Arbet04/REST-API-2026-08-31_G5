"""
Image Processing Backend (REST API)
Workshop: Edge and Corner Detection

Endpoints:
  GET  /api/health   -> simple health check
  POST /api/process  -> receives an image file + operation type,
                         runs edge or corner detection on the server,
                         and sends the resulting image back to the client.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import io

app = Flask(__name__)

# CORS is enabled because the frontend may run on a different port or another
# machine on the local network. In production, this should normally be limited
# to trusted origins.
CORS(app)


# ---------------------------------------------------------------------------
# Image processing functions
# ---------------------------------------------------------------------------

def apply_edge_detection(img, low_threshold=100, high_threshold=200):
    """Canny edge detection. Returns a 3-channel BGR image so it can be
    encoded/sent the same way as the corner-detection result."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, low_threshold, high_threshold)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def apply_corner_detection(img, block_size=2, ksize=3, k=0.04, thresh_ratio=0.01):
    """Harris corner detection. Draws detected corners in red on top of
    the original image."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)

    corners = cv2.cornerHarris(gray, block_size, ksize, k)
    corners = cv2.dilate(corners, None)  # enlarge corner markers so they're visible

    result = img.copy()
    result[corners > thresh_ratio * corners.max()] = [0, 0, 255]  # BGR red
    return result


OPERATIONS = {
    "edge": apply_edge_detection,
    "corner": apply_corner_detection,
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "Image Processing Backend",
    })


@app.route("/api/process", methods=["POST"])
def process():
    # POST is used because the client is sending a file and parameters as part of
    # the request body. This is the standard pattern for uploads.
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image uploaded"}), 400

    file = request.files["image"]
    operation = request.form.get("operation", "edge")

    if operation not in OPERATIONS:
        return jsonify({
            "success": False,
            "error": f"Unknown operation '{operation}'. Use 'edge' or 'corner'.",
        }), 400

    # Decode the uploaded file into an OpenCV image (numpy array)
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"success": False, "error": "Could not decode image"}), 400

    # Run the requested processing on the server side
    result_img = OPERATIONS[operation](img)

    # Encode the result back to PNG bytes and stream it to the client
    success, buffer = cv2.imencode(".png", result_img)
    if not success:
        return jsonify({"success": False, "error": "Failed to encode result image"}), 500

    return send_file(
        io.BytesIO(buffer.tobytes()),
        mimetype="image/png",
        download_name=f"result_{operation}.png",
    )


if __name__ == "__main__":
    # host="0.0.0.0" so other machines on the local network (e.g. the frontend
    # laptop) can reach this server via its IPv4 address (see: ipconfig / ifconfig)
    app.run(host="0.0.0.0", port=5000, debug=True)
