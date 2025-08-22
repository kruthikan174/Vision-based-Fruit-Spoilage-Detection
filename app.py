from flask import Flask, request, jsonify, render_template, render_template_string, url_for
import os
from datetime import datetime
from PIL import Image
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- Flask App Setup ---
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# --- Roboflow Model Details ---
ROBOFLOW_MODEL_ID = "bananas-para-consumo-humano/2"
ROBOFLOW_API_KEY = "iXJNcsFQHuw4Vtfk6MZ8"

# --- ThingSpeak Info ---
THINGSPEAK_CHANNEL_ID = "2966865"
THINGSPEAK_READ_API_KEY = "W9KJNK0Z51OTUFGN"

# --- Email Settings ---
EMAIL_SENDER = "r174.krishna@gmail.com"
EMAIL_PASSWORD = "zomh fetf bwwy ssfo"  # Gmail App Password
EMAIL_RECEIVER = "kruthika.n174@gmail.com"

latest_result = {"filename": "", "result": ""}

# --- Email Alert with Image Attachment ---
def send_email_alert(prediction_text, image_path):
    try:
        subject = "⚠️ Banana Spoilage Alert"
        body = f"A non-consumable banana has been detected.\n\nPrediction: {prediction_text}"

        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach image file
        with open(image_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(image_path)}")
            msg.attach(part)

        # Send Email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        print("📧 Email sent with image attached.")
    except Exception as e:
        print("❌ Email sending failed:", e)

# --- Roboflow Prediction ---
def predict_image(path):
    try:
        with open(path, "rb") as image_file:
            response = requests.post(
                url=f"https://classify.roboflow.com/{ROBOFLOW_MODEL_ID}?api_key={ROBOFLOW_API_KEY}",
                files={"file": image_file}
            )
        if response.status_code != 200:
            print("❌ Roboflow error:", response.status_code, response.text)
            return "❌ Prediction failed"

        data = response.json()
        predictions = data.get("predictions", {})
        if not predictions:
            return "⚠️ No objects detected"

        top_class = max(predictions.items(), key=lambda x: x[1]['confidence'])
        label = top_class[0]
        confidence = top_class[1]['confidence']
        return f"{label} ({confidence:.2%})"

    except Exception as e:
        print("Prediction error:", e)
        return "❌ Error in prediction"

# --- Routes ---
@app.route('/')
def dashboard():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Banana Freshness Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f5f9ff; font-family: 'Segoe UI', sans-serif; padding: 30px; }
            .preview-img { max-width: 100%; max-height: 300px; border-radius: 10px; }
            .prediction-box { font-size: 1.25rem; padding: 10px 20px; border-radius: 10px; }
            .prediction-fresh { background-color: #d1e7dd; color: #0f5132; }
            .prediction-spoiled { background-color: #f8d7da; color: #842029; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
            <div class="container">
                <a class="navbar-brand" href="/">🍌 Banana Freshness</a>
                <a class="nav-link" href="/environment">🌡️ Environment</a>
            </div>
        </nav>
        <div class="container text-center">
            <h2>🍌 Banana Freshness Dashboard</h2>
            {% if filename %}
                <p><strong>Latest Image:</strong> {{ filename }}</p>
                <img src="{{ url_for('static', filename=filename) }}" class="preview-img mb-3">
                <div class="prediction-box {% if 'consum' in result %}prediction-fresh{% else %}prediction-spoiled{% endif %}">
                    🧠 Prediction: <strong>{{ result }}</strong>
                </div>
            {% else %}
                <div class="alert alert-info mt-4">No image uploaded yet.</div>
            {% endif %}
        </div>
    </body>
    </html>
    """, filename=latest_result["filename"], result=latest_result["result"])

@app.route('/upload', methods=['POST'])
def upload_image():
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        with open(filepath, 'wb') as f:
            f.write(request.data)

        print(f"✅ Image saved: {filename}")
        result = predict_image(filepath)
        print("🧠 Prediction result:", result)
        Image.open(filepath).save(os.path.join(STATIC_FOLDER, filename))

        latest_result["filename"] = filename
        latest_result["result"] = result

        # 🔔 Send email if banana is non-consumable
        if "no-consum" in result.lower():
            send_email_alert(result, os.path.join(STATIC_FOLDER, filename))

        return jsonify({'prediction': result})
    except Exception as e:
        print("❌ Upload error:", e)
        return jsonify({'error': str(e)}), 500

@app.route('/environment')
def environment_dashboard():
    return render_template("environment.html",
                           channel_id=THINGSPEAK_CHANNEL_ID,
                           api_key=THINGSPEAK_READ_API_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
