# SmartFood AI

SmartFood AI is a MURN-based (MongoDB, Express, React, Node.js) intelligent food application. 
**Updated:** Now features a custom self-trained Python backend for AI tasks instead of external APIs.

## 🚀 Features

- **Secure Authentication**: Persistent login.
- **AI Chatbot**: Custom NLTK + PyTorch trained neural network for fruit/veg Q&A.
- **Smart Scanning**: 
  - **YOLOv8**: Object detection.
  - **MobileNetV2**: Classification.
  - **EfficientNet**: Freshness analysis.

## ⚠️ Running the AI Backend (REQUIRED)

Since this app now uses custom models, you MUST run the Python backend locally.

### 1. Install Python Dependencies
```bash
cd python_backend
pip install -r requirements.txt
```

### 2. Train the Models
Train the chatbot model (creates `chatbot_model.pth`):
```bash
python train_chatbot.py
```

### 3. Start the Server
```bash

```python server.py
*Server runs on http://localhost:5000*

## 🛠 Tech Stack

### Frontend
- React 19, Tailwind CSS, Lucide Icons

### Backend (AI)
- **Language**: Python 3.9+
- **Framework**: Flask
- **ML Libraries**: PyTorch, NLTK, Torchvision, Ultralytics

### Backend (App Data)
- Node.js, Express, MongoDB

## 📋 Prerequisites

1. **Node.js**: v18+
2. **Python**: v3.8+
3. **MongoDB**

## ⚙️ Full Installation

1. **Clone Repo**
2. **Setup Python AI** (See above)
3. **Setup Frontend**:
   ```bash
   cd client
   npm install
   npm run dev
   ```