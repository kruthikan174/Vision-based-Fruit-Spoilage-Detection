# 🍌 Banana Freshness Monitoring System  

This project is a **Flask web application** that monitors banana freshness using AI-powered image classification and IoT-based environment tracking.  
It integrates **Roboflow**, **ThingSpeak**, and **email alerts** to provide a complete solution for reducing fruit spoilage.  

---

## 📌 Features  

### 🔹 Image Classification  
- Upload images of bananas to classify as **consumable** or **non-consumable**.  
- Powered by **Roboflow API** (`bananas-para-consumo-humano/2`).  
- Displays prediction with confidence score.  

### 🔹 Real-time Environment Monitoring  
- Monitors **temperature, humidity, gas levels, and stock status** via **ThingSpeak IoT platform**.  
- Embedded charts update dynamically on the dashboard.  
- Includes a live **gas meter gauge** for spoilage indicators.  

### 🔹 Email Alerts  
- Sends an **email with image attachment** when a spoiled (non-consumable) banana is detected.  
- Uses **SMTP (Gmail)** with app password for authentication.  

---

## ⚙️ Tech Stack  

- **Backend:** Flask (Python)  
- **Frontend:** HTML, Bootstrap 5, JavaScript  
- **AI Model:** Roboflow Image Classification API  
- **IoT Integration:** ThingSpeak (temperature, humidity, gas, stock)  
- **Notifications:** SMTP (Gmail Email Alerts)  

