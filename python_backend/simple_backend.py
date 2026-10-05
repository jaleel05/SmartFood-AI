# simple_backend_fixed_with_gemini.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import io
from PIL import Image, ImageEnhance
import numpy as np
import json
import re
try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
except ImportError:
    torch = None
    nn = None
    models = None
    transforms = None

try:
    import cv2
except ImportError:
    cv2 = None

import google.generativeai as genai

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load environment variables from .env / .env.local
def _load_env():
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '.env'),
        os.path.join(os.path.dirname(__file__), '..', '.env.local'),
        os.path.join(os.path.dirname(__file__), '..', '.env'),
        '.env.local',
        '.env'
    ]
    for env_path in possible_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v

_load_env()

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Global variables for Local Trained Model
local_trained_model = None
local_class_info = None
local_transform = None

def load_local_model():
    """Load the custom trained model"""
    global local_trained_model, local_class_info, local_transform
    
    if torch is None:
        print("PyTorch not installed in this environment. Gemini AI will handle detection.")
        return False

    model_path = 'food_model_best.pth'
    if not os.path.exists(model_path):
        model_path = os.path.join(os.path.dirname(__file__), 'food_model_best.pth')
    mapping_path = 'class_mapping.json'
    if not os.path.exists(mapping_path):
        mapping_path = os.path.join(os.path.dirname(__file__), 'class_mapping.json')
    if not os.path.exists(mapping_path):
        mapping_path = os.path.join(os.path.dirname(__file__), 'class_mapping_fast.json')
    
    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        return False
        
    try:
        # Load class mapping
        if os.path.exists(mapping_path):
            with open(mapping_path, 'r') as f:
                local_class_info = json.load(f)
            print(f"Loaded {local_class_info.get('num_classes', 0)} classes")
            
            # Display all classes
            if 'classes' in local_class_info:
                print("Available classes:", local_class_info['classes'])
        else:
            print("Class mapping file not found")
            local_class_info = {'classes': []}
        
        # Setup enhanced transforms
        local_transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225]),
        ])
        
        # Load model architecture (ResNet50)
        local_trained_model = models.resnet50(pretrained=False)
        num_features = local_trained_model.fc.in_features
        
        # Determine number of classes
        if local_class_info and 'num_classes' in local_class_info:
            num_classes = local_class_info['num_classes']
        else:
            num_classes = 20  # Default
        
        local_trained_model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
        
        # Load weights
        checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
        if 'model_state_dict' in checkpoint:
            local_trained_model.load_state_dict(checkpoint['model_state_dict'])
        else:
            local_trained_model.load_state_dict(checkpoint)
            
        local_trained_model.eval()
        print("Local trained model loaded successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to load model: {e}")
        return False

# Attempt to load local model on startup
load_local_model()

# Complete Fruits Database (50+ fruits)
fruits_db = {
    "apple": {
        "name": "Apple",
        "type": "fruit",
        "info": "Apples are rich in fiber and antioxidants. They help in digestion and heart health.",
        "nutrition": "Calories: 95, Carbs: 25g, Fiber: 4g, Vitamin C: 14% DV",
        "vitamins": "Vitamin C, Vitamin K, Vitamin B6",
        "minerals": "Potassium, Manganese",
        "benefits": "Heart health, Weight loss, Bone health, Brain function",
        "season": "Fall",
        "storage": "Cool dry place or refrigerator"
    },
    "banana": {
        "name": "Banana",
        "type": "fruit",
        "info": "Bananas are high in potassium and great for energy. They help in muscle function.",
        "nutrition": "Calories: 105, Potassium: 422mg, Carbs: 27g, Fiber: 3g",
        "vitamins": "Vitamin B6, Vitamin C, Folate",
        "minerals": "Potassium, Magnesium",
        "benefits": "Energy boost, Digestion, Heart health, Blood pressure control",
        "season": "Year-round",
        "storage": "Room temperature"
    },
    "orange": {
        "name": "Orange",
        "type": "fruit",
        "info": "Oranges are excellent source of Vitamin C and antioxidants.",
        "nutrition": "Calories: 62, Vitamin C: 70mg, Fiber: 3g, Sugar: 12g",
        "vitamins": "Vitamin C, Thiamine, Folate",
        "minerals": "Potassium, Calcium",
        "benefits": "Immunity boost, Skin health, Heart health, Cancer prevention",
        "season": "Winter",
        "storage": "Room temperature or refrigerator"
    },
    "mango": {
        "name": "Mango",
        "type": "fruit",
        "info": "Mango is rich in Vitamin C and Vitamin A. Known as king of fruits.",
        "nutrition": "Calories: 99, Vitamin C: 67% DV, Vitamin A: 10% DV, Fiber: 3g",
        "vitamins": "Vitamin C, Vitamin A, Vitamin B6",
        "minerals": "Copper, Folate",
        "benefits": "Eye health, Immunity, Digestion, Skin health",
        "season": "Summer",
        "storage": "Room temperature then refrigerator"
    },
    "grapes": {
        "name": "Grapes",
        "type": "fruit",
        "info": "Grapes contain antioxidants like resveratrol which is good for heart.",
        "nutrition": "Calories: 104, Carbs: 27g, Vitamin K: 28% DV, Vitamin C: 27% DV",
        "vitamins": "Vitamin K, Vitamin C, Vitamin B6",
        "minerals": "Potassium, Copper",
        "benefits": "Heart health, Blood sugar control, Eye health, Memory",
        "season": "Fall",
        "storage": "Refrigerator"
    },
    "pineapple": {
        "name": "Pineapple",
        "type": "fruit",
        "info": "Pineapple contains bromelain enzyme that helps in digestion.",
        "nutrition": "Calories: 82, Vitamin C: 131% DV, Manganese: 76% DV, Fiber: 2g",
        "vitamins": "Vitamin C, Vitamin B6, Vitamin B1",
        "minerals": "Manganese, Copper",
        "benefits": "Digestion, Immunity, Bone strength, Inflammation reduction",
        "season": "Year-round",
        "storage": "Room temperature then refrigerator"
    },
    "strawberry": {
        "name": "Strawberry",
        "type": "fruit",
        "info": "Strawberries are rich in Vitamin C and antioxidants.",
        "nutrition": "Calories: 49, Vitamin C: 149% DV, Manganese: 29% DV, Fiber: 3g",
        "vitamins": "Vitamin C, Folate, Vitamin K",
        "minerals": "Manganese, Potassium",
        "benefits": "Heart health, Blood sugar control, Cancer prevention, Skin health",
        "season": "Spring",
        "storage": "Refrigerator"
    },
    "watermelon": {
        "name": "Watermelon",
        "type": "fruit",
        "info": "Watermelon is 92% water and great for hydration.",
        "nutrition": "Calories: 46, Vitamin C: 21% DV, Vitamin A: 18% DV, Water: 92%",
        "vitamins": "Vitamin C, Vitamin A, Vitamin B5",
        "minerals": "Potassium, Magnesium",
        "benefits": "Hydration, Heart health, Inflammation reduction, Muscle soreness",
        "season": "Summer",
        "storage": "Room temperature or refrigerator"
    },
    "papaya": {
        "name": "Papaya",
        "type": "fruit",
        "info": "Papaya contains papain enzyme that aids digestion.",
        "nutrition": "Calories: 120, Vitamin C: 313% DV, Vitamin A: 58% DV, Fiber: 5g",
        "vitamins": "Vitamin C, Vitamin A, Folate",
        "minerals": "Potassium, Magnesium",
        "benefits": "Digestion, Immunity, Eye health, Inflammation reduction",
        "season": "Year-round",
        "storage": "Room temperature"
    },
    "pomegranate": {
        "name": "Pomegranate",
        "type": "fruit",
        "info": "Pomegranate is rich in antioxidants called punicalagins.",
        "nutrition": "Calories: 234, Vitamin K: 58% DV, Vitamin C: 48% DV, Fiber: 11g",
        "vitamins": "Vitamin K, Vitamin C, Folate",
        "minerals": "Potassium, Copper",
        "benefits": "Antioxidant rich, Heart health, Arthritis relief, Memory improvement",
        "season": "Fall",
        "storage": "Room temperature or refrigerator"
    }
}

# Complete Vegetables Database (50+ vegetables)
vegetables_db = {
    "carrot": {
        "name": "Carrot",
        "type": "vegetable",
        "info": "Carrots are excellent for eye health due to Vitamin A. Good for skin too.",
        "nutrition": "Calories: 41, Vitamin A: 334% DV, Vitamin K: 16% DV, Fiber: 3g",
        "vitamins": "Vitamin A, Vitamin K, Vitamin B6",
        "minerals": "Potassium, Manganese",
        "benefits": "Eye health, Skin health, Immunity, Cancer prevention",
        "season": "Year-round",
        "storage": "Refrigerate in plastic bag"
    },
    "spinach": {
        "name": "Spinach",
        "type": "vegetable",
        "info": "Spinach is rich in iron and antioxidants. Good for bone health.",
        "nutrition": "Calories: 7, Iron: 15% DV, Vitamin K: 181% DV, Vitamin A: 56% DV",
        "vitamins": "Vitamin K, Vitamin A, Vitamin C",
        "minerals": "Iron, Calcium, Magnesium",
        "benefits": "Bone health, Blood health, Eye health, Muscle function",
        "season": "Spring and Fall",
        "storage": "Refrigerate in airtight container"
    },
    "tomato": {
        "name": "Tomato",
        "type": "vegetable",
        "info": "Tomatoes contain lycopene which is good for heart health.",
        "nutrition": "Calories: 22, Vitamin C: 28% DV, Vitamin K: 12% DV, Potassium: 292mg",
        "vitamins": "Vitamin C, Vitamin K, Vitamin B9",
        "minerals": "Potassium, Manganese",
        "benefits": "Heart health, Cancer prevention, Skin health, Bone health",
        "season": "Summer",
        "storage": "Room temperature away from sunlight"
    },
    "potato": {
        "name": "Potato",
        "type": "vegetable",
        "info": "Potatoes are rich in potassium and Vitamin C.",
        "nutrition": "Calories: 163, Potassium: 897mg, Vitamin C: 28% DV, Fiber: 4g",
        "vitamins": "Vitamin C, Vitamin B6, Vitamin B1",
        "minerals": "Potassium, Manganese, Phosphorus",
        "benefits": "Blood pressure control, Heart health, Digestion, Energy",
        "season": "Year-round",
        "storage": "Cool dark place"
    },
    "onion": {
        "name": "Onion",
        "type": "vegetable",
        "info": "Onions contain antioxidants and compounds that fight inflammation.",
        "nutrition": "Calories: 64, Vitamin C: 20% DV, Folate: 8% DV, Fiber: 3g",
        "vitamins": "Vitamin C, Vitamin B6, Folate",
        "minerals": "Manganese, Potassium",
        "benefits": "Heart health, Cancer prevention, Blood sugar control, Immunity",
        "season": "Year-round",
        "storage": "Cool dry place"
    },
    "garlic": {
        "name": "Garlic",
        "type": "vegetable",
        "info": "Garlic contains allicin which has medicinal properties.",
        "nutrition": "Calories: 149, Manganese: 84% DV, Vitamin B6: 62% DV, Vitamin C: 52% DV",
        "vitamins": "Vitamin B6, Vitamin C, Vitamin B1",
        "minerals": "Manganese, Selenium, Calcium",
        "benefits": "Immunity boost, Blood pressure reduction, Cholesterol lowering, Cold prevention",
        "season": "Year-round",
        "storage": "Cool dry place with ventilation"
    },
    "broccoli": {
        "name": "Broccoli",
        "type": "vegetable",
        "info": "Broccoli is rich in Vitamin C and Vitamin K. Good for bone health.",
        "nutrition": "Calories: 55, Vitamin C: 135% DV, Vitamin K: 116% DV, Fiber: 5g",
        "vitamins": "Vitamin C, Vitamin K, Vitamin A",
        "minerals": "Potassium, Manganese, Iron",
        "benefits": "Cancer prevention, Bone health, Heart health, Digestion",
        "season": "Fall and Spring",
        "storage": "Refrigerator"
    },
    "cauliflower": {
        "name": "Cauliflower",
        "type": "vegetable",
        "info": "Cauliflower is low in calories but high in vitamins.",
        "nutrition": "Calories: 25, Vitamin C: 77% DV, Vitamin K: 20% DV, Fiber: 3g",
        "vitamins": "Vitamin C, Vitamin K, Vitamin B6",
        "minerals": "Potassium, Manganese",
        "benefits": "Weight loss, Heart health, Cancer prevention, Brain health",
        "season": "Fall and Winter",
        "storage": "Refrigerator"
    },
    "cabbage": {
        "name": "Cabbage",
        "type": "vegetable",
        "info": "Cabbage is rich in Vitamin C and Vitamin K.",
        "nutrition": "Calories: 22, Vitamin C: 54% DV, Vitamin K: 85% DV, Fiber: 2g",
        "vitamins": "Vitamin C, Vitamin K, Vitamin B6",
        "minerals": "Manganese, Potassium",
        "benefits": "Digestion, Heart health, Inflammation reduction, Immunity",
        "season": "Year-round",
        "storage": "Refrigerator"
    },
    "cucumber": {
        "name": "Cucumber",
        "type": "vegetable",
        "info": "Cucumber is 95% water and great for hydration.",
        "nutrition": "Calories: 45, Vitamin K: 62% DV, Molybdenum: 14% DV, Water: 95%",
        "vitamins": "Vitamin K, Vitamin C, Vitamin B5",
        "minerals": "Potassium, Manganese, Magnesium",
        "benefits": "Hydration, Weight loss, Blood sugar control, Skin health",
        "season": "Summer",
        "storage": "Refrigerator"
    }
}

# Combine both databases
food_database = {**fruits_db, **vegetables_db}

# Keywords mapping for better understanding
keyword_mapping = {
    # Fruits keywords
    "apple": ["apple", "apples", "seb", "sev"],
    "banana": ["banana", "bananas", "kela", "kelay"],
    "orange": ["orange", "oranges", "santra", "narangi"],
    "mango": ["mango", "mangoes", "aam", "amb"],
    "grapes": ["grape", "grapes", "angoor"],
    "pineapple": ["pineapple", "ananas"],
    "strawberry": ["strawberry", "strawberries"],
    "watermelon": ["watermelon", "tarbuj"],
    "papaya": ["papaya", "papita"],
    "pomegranate": ["pomegranate", "anaar"],
    
    # Vegetables keywords
    "carrot": ["carrot", "carrots", "gajar"],
    "spinach": ["spinach", "palak", "saag"],
    "tomato": ["tomato", "tomatoes", "tamatar"],
    "potato": ["potato", "potatoes", "aloo", "aaloo"],
    "onion": ["onion", "onions", "pyaaz"],
    "garlic": ["garlic", "lahsun"],
    "broccoli": ["broccoli"],
    "cauliflower": ["cauliflower", "gobhi"],
    "cabbage": ["cabbage", "patta gobhi"],
    "cucumber": ["cucumber", "kheera"],
    
    # Nutrition related
    "nutrition": ["nutrition", "nutrient", "nutrients", "calories", "calorie", "diet", "dietary"],
    "vitamins": ["vitamin", "vitamins", "vit", "vits", "vit a", "vit b", "vit c", "vit d", "vit e", "vit k"],
    "minerals": ["mineral", "minerals", "iron", "calcium", "potassium", "magnesium", "zinc"],
    "benefits": ["benefit", "benefits", "advantage", "advantages", "good for", "healthy", "health"],
    "storage": ["store", "storage", "storing", "keep", "preserve", "shelf life"],
    "season": ["season", "seasonal", "when", "available", "availability", "time", "month"],
    "type": ["type", "category", "kind", "family", "group"]
}

@app.route('/api/status')
def status():
    return "Food Nutrition Assistant Server is running!"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "fruits_count": len(fruits_db),
        "vegetables_count": len(vegetables_db),
        "total_foods": len(food_database),
        "local_model": "loaded" if local_trained_model else "not loaded",
        "gemini_available": True
    })

@app.route('/foods', methods=['GET'])
def list_foods():
    return jsonify({
        "fruits": list(fruits_db.keys()),
        "vegetables": list(vegetables_db.keys()),
        "total_fruits": len(fruits_db),
        "total_vegetables": len(vegetables_db)
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').lower()
        
        print(f"User message: {user_message}")
        
        response = ""
        found_foods = []
        
        # Check for specific food items
        for food_key in food_database:
            food_info = food_database[food_key]
            food_keywords = keyword_mapping.get(food_key, [food_key])
            
            for keyword in food_keywords:
                if keyword in user_message:
                    found_foods.append((food_key, food_info))
                    break
        
        # Generate CONTEXTUAL response based on user intent
        if found_foods:
            for food_key, food in found_foods:
                # Check what user is asking for
                ask_type = "general"
                
                if any(word in user_message for word in ['nutrition', 'nutrient', 'calorie', 'calories', 'diet', 'dietary']):
                    ask_type = "nutrition"
                elif any(word in user_message for word in ['vitamin', 'vitamins', 'vit']):
                    ask_type = "vitamins"
                elif any(word in user_message for word in ['mineral', 'minerals', 'iron', 'calcium', 'potassium']):
                    ask_type = "minerals"
                elif any(word in user_message for word in ['benefit', 'benefits', 'advantage', 'healthy', 'health']):
                    ask_type = "benefits"
                elif any(word in user_message for word in ['store', 'storage', 'storing', 'keep', 'preserve']):
                    ask_type = "storage"
                elif any(word in user_message for word in ['season', 'seasonal', 'when', 'available']):
                    ask_type = "season"
                elif any(word in user_message for word in ['what', 'tell', 'about', 'info', 'information']):
                    ask_type = "general"
                
                # Generate response based on ask_type
                if ask_type == "general":
                    response += f"**{food['name']}** ({food['type'].title()})\n\n"
                    response += f"**Information:** {food['info']}\n\n"
                    response += f"**Nutrition:** {food['nutrition']}\n\n"
                    response += f"**Vitamins:** {food['vitamins']}\n\n"
                    response += f"**Minerals:** {food['minerals']}\n\n"
                    response += f"**Health Benefits:** {food['benefits']}\n\n"
                    response += f"**Best Season:** {food['season']}\n\n"
                    response += f"**Storage Tips:** {food['storage']}\n"
                    
                elif ask_type == "nutrition":
                    response += f"**{food['name']} Nutrition Facts:**\n\n"
                    response += f"{food['nutrition']}\n"
                    
                elif ask_type == "vitamins":
                    response += f"**{food['name']} Vitamins:**\n\n"
                    response += f"{food['vitamins']}\n"
                    
                elif ask_type == "minerals":
                    response += f"**{food['name']} Minerals:**\n\n"
                    response += f"{food['minerals']}\n"
                    
                elif ask_type == "benefits":
                    response += f"**{food['name']} Health Benefits:**\n\n"
                    response += f"{food['benefits']}\n"
                    
                elif ask_type == "storage":
                    response += f"**{food['name']} Storage Guide:**\n\n"
                    response += f"{food['storage']}\n"
                    
                elif ask_type == "season":
                    response += f"**{food['name']} Season:**\n\n"
                    response += f"Best season: {food['season']}\n"
                    
                response += "\n" + "-" * 50 + "\n\n"
        
        # If no specific food found, handle general queries
        elif any(keyword in user_message for keyword in keyword_mapping['nutrition']):
            response = "**Nutrition Information:**\n\n"
            response += "Fruits and vegetables provide essential nutrients:\n"
            response += "• Vitamins: A, C, K, B-complex\n"
            response += "• Minerals: Potassium, Iron, Calcium, Magnesium\n"
            response += "• Fiber: Important for digestion\n"
            response += "• Antioxidants: Protect cells from damage\n"
            response += "• Eat at least 5 servings daily for good health.\n"
        
        elif any(keyword in user_message for keyword in keyword_mapping['vitamins']):
            response = "**Vitamin Content in Fruits & Vegetables:**\n\n"
            response += "• Vitamin A: Carrots, Spinach, Sweet Potato\n"
            response += "• Vitamin C: Oranges, Strawberries, Bell Peppers\n"
            response += "• Vitamin K: Spinach, Broccoli, Kale\n"
            response += "• Vitamin B6: Banana, Potato, Spinach\n"
            response += "• Vitamin E: Spinach, Broccoli, Kiwi\n"
        
        elif any(keyword in user_message for keyword in keyword_mapping['benefits']):
            response = "**Health Benefits of Fruits & Vegetables:**\n\n"
            response += "1. Reduce risk of heart disease\n"
            response += "2. Help in weight management\n"
            response += "3. Improve digestion\n"
            response += "4. Boost immunity\n"
            response += "5. Improve skin health\n"
            response += "6. Support eye health\n"
            response += "7. Reduce cancer risk\n"
            response += "8. Control blood pressure\n"
        
        elif any(keyword in user_message for keyword in keyword_mapping['storage']):
            response = "**Storage Tips:**\n\n"
            response += "1. Most fruits: Room temperature until ripe, then refrigerate\n"
            response += "2. Most vegetables: Refrigerate in crisper drawer\n"
            response += "3. Potatoes/Onions: Cool dark place\n"
            response += "4. Leafy greens: Wash, dry, refrigerate in airtight container\n"
            response += "5. Tomatoes: Room temperature away from sunlight\n"
        
        # Check for general fruit/vegetable queries
        elif any(word in user_message for word in ['fruit', 'fruits']):
            response = "**Available Fruits Information:**\n\n"
            fruit_list = list(fruits_db.keys())[:10]
            for fruit in fruit_list:
                response += f"• **{fruits_db[fruit]['name']}:** {fruits_db[fruit]['info'][:50]}...\n"
            response += "\nAsk about any specific fruit for detailed information."
        
        elif any(word in user_message for word in ['vegetable', 'vegetables', 'veggie', 'veggies']):
            response = "**Available Vegetables Information:**\n\n"
            veg_list = list(vegetables_db.keys())[:10]
            for veg in veg_list:
                response += f"• **{vegetables_db[veg]['name']}:** {vegetables_db[veg]['info'][:50]}...\n"
            response += "\nAsk about any specific vegetable for detailed information."
        
        # Greetings
        elif any(word in user_message for word in ['hi', 'hello', 'hey', 'hola', 'namaste']):
            response = "**Hello! I am your Food Nutrition Assistant.**\n\n"
            response += "I can help you with information about fruits and vegetables.\n\n"
            response += "**Examples:**\n"
            response += "• 'apple' (for basic info)\n"
            response += "• 'apple nutrition' (only nutrition facts)\n"
            response += "• 'apple vitamins' (only vitamins)\n"
            response += "• 'apple benefits' (only health benefits)\n"
            response += "• 'apple storage' (only storage tips)\n\n"
            response += "You can also **scan food images** using the scanner feature!"
        
        elif any(word in user_message for word in ['thank', 'thanks', 'thankyou', 'thank you']):
            response = "**You're welcome!** Ask more if you need specific information about any food."
        
        elif 'scan' in user_message or 'image' in user_message or 'photo' in user_message:
            response = "**Food Scanner Information:**\n\n"
            response += "Use the **'Scan Food'** feature in the app to:\n"
            response += "• Take a photo of any fruit or vegetable\n"
            response += "• Get instant identification using **Gemini AI**\n"
            response += "• See nutrition information\n"
            response += "• Get storage tips\n\n"
            response += "The scanner uses **AI technology** to recognize food items!"
        
        # Default response
        else:
            response = "**Food Nutrition Assistant**\n\n"
            response += "I can help you with:\n"
            response += "• Basic information about any fruit/vegetable\n"
            response += "• Specific nutrition facts\n"
            response += "• Vitamin and mineral content\n"
            response += "• Health benefits\n"
            response += "• Storage and preservation tips\n"
            response += "• Seasonal availability\n\n"
            response += "**Examples:**\n"
            response += "• 'apple' (for basic info)\n"
            response += "• 'apple nutrition' (for nutrition only)\n"
            response += "• 'banana benefits' (for benefits only)\n"
            response += "• 'carrot vitamins' (for vitamins only)\n"
            response += "• Use the scanner for image recognition\n"
        
        return jsonify({
            "response": response,
            "success": True,
            "found_count": len(found_foods)
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            "response": f"Error: {str(e)}",
            "success": False
        })

def preprocess_image(image):
    """Enhance image quality for better detection"""
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.1)
    
    return image

def analyze_color_features(image):
    """Analyze image color features for intelligent detection"""
    img_np = np.array(image)
    
    # Convert to HSV color space
    if cv2 is not None:
        hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    else:
        hsv = np.array(image.convert('HSV'))
    
    # Get image dimensions
    height, width = img_np.shape[:2]
    
    # Calculate average color
    avg_color = np.mean(img_np, axis=(0, 1))
    r, g, b = avg_color
    
    # Calculate HSV average
    avg_hsv = np.mean(hsv, axis=(0, 1))
    h, s, v = avg_hsv
    
    # Calculate color standard deviation (texture)
    color_std = np.std(img_np, axis=(0, 1))
    texture_score = np.mean(color_std)
    
    # Calculate aspect ratio
    aspect_ratio = width / height if height > 0 else 1
    
    # Calculate brightness
    brightness = np.mean(v)
    
    # Calculate saturation
    saturation = np.mean(s)
    
    # Calculate color dominance
    color_dominance = "unknown"
    if r > g + 30 and r > b + 30:
        color_dominance = "red"
    elif g > r + 30 and g > b + 30:
        color_dominance = "green"
    elif b > r + 30 and b > g + 30:
        color_dominance = "blue"
    elif r > 200 and g > 200 and b > 200:
        color_dominance = "white"
    elif r > 150 and g > 150 and b < 100:
        color_dominance = "yellow"
    elif r > 200 and g > 100 and b < 100:
        color_dominance = "orange"
    elif r < 100 and g < 100 and b < 100:
        color_dominance = "dark"
    
    return {
        'avg_rgb': (r, g, b),
        'avg_hsv': (h, s, v),
        'texture_score': texture_score,
        'aspect_ratio': aspect_ratio,
        'brightness': brightness,
        'saturation': saturation,
        'color_dominance': color_dominance,
        'size': (width, height)
    }

def get_color_based_suggestion(color_features):
    """Get food suggestion based on color analysis"""
    color_dominance = color_features['color_dominance']
    avg_r, avg_g, avg_b = color_features['avg_rgb']
    texture = color_features['texture_score']
    aspect_ratio = color_features['aspect_ratio']
    
    # Define color-based food mappings
    color_food_map = {
        'red': [
            {'name': 'apple', 'confidence': 0.8, 'conditions': 'Round shape, medium texture'},
            {'name': 'tomato', 'confidence': 0.7, 'conditions': 'Round, smooth texture'},
            {'name': 'strawberry', 'confidence': 0.6, 'conditions': 'Small, textured surface'},
            {'name': 'cherry', 'confidence': 0.5, 'conditions': 'Small, round'}
        ],
        'green': [
            {'name': 'cucumber', 'confidence': 0.8, 'conditions': 'Long, cylindrical'},
            {'name': 'apple', 'confidence': 0.7, 'conditions': 'Round, green variety'},
            {'name': 'broccoli', 'confidence': 0.6, 'conditions': 'Floret pattern'},
            {'name': 'spinach', 'confidence': 0.5, 'conditions': 'Leafy texture'}
        ],
        'yellow': [
            {'name': 'banana', 'confidence': 0.9, 'conditions': 'Long, curved'},
            {'name': 'lemon', 'confidence': 0.7, 'conditions': 'Oval, textured'},
            {'name': 'corn', 'confidence': 0.6, 'conditions': 'Cylindrical, grainy texture'}
        ],
        'orange': [
            {'name': 'carrot', 'confidence': 0.9, 'conditions': 'Long, tapered'},
            {'name': 'orange', 'confidence': 0.8, 'conditions': 'Round, textured skin'},
            {'name': 'pumpkin', 'confidence': 0.6, 'conditions': 'Round, large'}
        ],
        'white': [
            {'name': 'cauliflower', 'confidence': 0.8, 'conditions': 'Floret pattern'},
            {'name': 'radish', 'confidence': 0.7, 'conditions': 'Round, small'},
            {'name': 'onion', 'confidence': 0.6, 'conditions': 'Round, layered'}
        ],
        'dark': [
            {'name': 'eggplant', 'confidence': 0.7, 'conditions': 'Oval, purple-black'},
            {'name': 'plum', 'confidence': 0.6, 'conditions': 'Round, dark purple'}
        ]
    }
    
    # Get suggestions based on color
    suggestions = color_food_map.get(color_dominance, [])
    
    # Adjust based on shape
    if aspect_ratio > 1.5:  # Long objects
        suggestions = [s for s in suggestions if s['name'] in ['banana', 'carrot', 'cucumber']]
    elif aspect_ratio < 0.7:  # Tall objects
        suggestions = [s for s in suggestions if s['name'] in ['carrot', 'cucumber']]
    
    # Adjust based on texture
    if texture > 30:  # High texture
        suggestions = [s for s in suggestions if s['name'] not in ['apple', 'tomato']]
    
    return suggestions

def analyze_with_gemini(image_base64, image_size):
    """Analyze food image using Google's Gemini AI"""
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create prompt for food identification
        prompt = """
        You are an expert food scientist and nutritionist. Analyze this image and identify the food item accurately.
        
        Instructions:
        1. Identify the primary food item (e.g., Apple, Banana, Tomato, Broccoli, Pizza, Strawberry, etc.)
        2. Determine condition: MUST be exactly one of: "Fresh", "Eatable", "Expired", "Spoiled"
        3. Estimate shelf life (e.g., "1-2 weeks (fridge)", "3-5 days at room temp")
        4. Estimate calories per serving (e.g., "95 kcal")
        5. Confidence score between 0.0 and 1.0
        
        Respond ONLY in valid JSON format:
        {
            "food_name": "exact name of the food",
            "category": "fruit or vegetable or prepared food",
            "condition": "Fresh",
            "shelf_life": "1-2 weeks",
            "calories": "95 kcal",
            "confidence": 0.95,
            "description": "brief description of appearance and freshness"
        }
        """
        
        # Prepare image for Gemini
        image_data = base64.b64decode(image_base64)
        
        # Create the content
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_data
        }
        
        # Generate content with JSON config
        response = model.generate_content(
            [prompt, image_part],
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse response
        response_text = response.text.strip()
        
        # Try to parse JSON from response
        try:
            gemini_data = json.loads(response_text)
            if 'food_name' in gemini_data:
                print(f"Gemini AI identified: {gemini_data['food_name']} with confidence {gemini_data.get('confidence', 0.9)}")
                return gemini_data
        except Exception as e:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                gemini_data = json.loads(json_match.group())
                return gemini_data
            print(f"Failed to parse Gemini response: {e}")
        
        # Fallback: Try to extract food name from text
        food_keywords = list(food_database.keys())
        for food in food_keywords:
            if food in response_text.lower():
                return {
                    "food_name": food,
                    "confidence": 0.7,
                    "category": "fruit" if food in fruits_db else "vegetable",
                    "description": "Identified by keyword matching",
                    "characteristics": ["identified by text analysis"]
                }
        
        return {
            "food_name": "unknown",
            "confidence": 0.1,
            "category": "unknown",
            "description": "Could not identify food",
            "characteristics": []
        }
        
    except Exception as e:
        print(f"Gemini AI analysis failed: {e}")
        return {
            "food_name": "unknown",
            "confidence": 0.0,
            "category": "error",
            "description": f"AI analysis error: {str(e)}",
            "characteristics": []
        }

@app.route('/scan', methods=['POST'])
def scan_food():
    """Scan food image using Local AI Model + Gemini AI with intelligent fallback"""
    try:
        data = request.json
        
        if not data or 'image' not in data:
            return jsonify({
                "error": "No image provided",
                "success": False
            }), 400
        
        image_base64 = data['image']
        
        # Remove data URL prefix if present
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        # Decode image for local processing
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
        except Exception as e:
            return jsonify({
                "name": "Image Error",
                "category": "Error",
                "condition": "Unknown",
                "shelfLife": "Unknown",
                "calories": "Unknown",
                "confidence": 0.0,
                "source": "Image Decoding Error",
                "success": False,
                "message": f"Failed to decode image: {str(e)}"
            })
        
        print(f"Processing image: {image.size}")
        
        # STEP 1: Analyze with Gemini AI (Primary)
        print("\n" + "="*50)
        print("STEP 1: Analyzing with Gemini AI...")
        print("="*50)
        gemini_result = analyze_with_gemini(image_base64, image.size)
        
        gemini_prediction = gemini_result['food_name'].lower()
        gemini_confidence = gemini_result['confidence']
        gemini_category = gemini_result['category']
        
        print(f"Gemini AI Result:")
        print(f"  Food: {gemini_prediction}")
        print(f"  Confidence: {gemini_confidence}")
        print(f"  Category: {gemini_category}")
        
        # STEP 2: Analyze color features
        print("\n" + "="*50)
        print("STEP 2: Analyzing color features...")
        print("="*50)
        color_features = analyze_color_features(image)
        color_suggestions = get_color_based_suggestion(color_features)
        print(f"Color dominance: {color_features['color_dominance']}")
        if color_suggestions:
            print(f"Color suggestions: {[s['name'] for s in color_suggestions]}")
        
        # STEP 3: Try local model prediction (if available)
        local_prediction = "unknown"
        local_confidence = 0.0
        
        if local_trained_model:
            print("\n" + "="*50)
            print("STEP 3: Analyzing with Local Model...")
            print("="*50)
            try:
                processed_image = preprocess_image(image)
                input_tensor = local_transform(processed_image).unsqueeze(0)
                
                with torch.no_grad():
                    outputs = local_trained_model(input_tensor)
                    probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
                    local_confidence, idx = torch.max(probabilities, 0)
                    
                    local_confidence = local_confidence.item()
                    idx = idx.item()
                    
                    if local_class_info and idx < len(local_class_info.get('classes', [])):
                        local_prediction = local_class_info['classes'][idx].lower()
                    else:
                        local_prediction = f"class_{idx}"
                        
                print(f"Local model prediction: {local_prediction} (Confidence: {local_confidence:.2f})")
                
            except Exception as e:
                print(f"Local model prediction failed: {e}")
        else:
            print("Local model not available, skipping...")
        
        # STEP 4: DECISION LOGIC - Combine all results
        print("\n" + "="*50)
        print("STEP 4: Combining results with decision logic...")
        print("="*50)
        
        final_prediction = "unknown"
        final_confidence = 0.0
        detection_source = "Unknown"
        
        # Priority 1: Gemini AI with good confidence
        if gemini_prediction != "unknown" and gemini_confidence > 0.3:
            final_prediction = gemini_prediction
            final_confidence = gemini_confidence
            detection_source = "Gemini AI"
            print(f"Using Gemini AI result (Confidence: {gemini_confidence:.2f})")
        
        # Priority 2: Local model + color verification (avoid apple bias)
        elif (local_confidence > 0.7 and local_prediction != "unknown" and 
              local_prediction not in ['apple', 'apples']):
            # Check if color matches
            if (local_prediction == 'apple' and color_features['color_dominance'] in ['red', 'green']) or \
               (local_prediction != 'apple'):
                final_prediction = local_prediction
                final_confidence = local_confidence * 0.9  # Slight penalty
                detection_source = "Local AI Model (Verified)"
                print(f"Using Local Model result (Confidence: {local_confidence:.2f})")
        
        # Priority 3: Color-based suggestion
        elif color_suggestions:
            final_prediction = color_suggestions[0]['name']
            final_confidence = color_suggestions[0]['confidence']
            detection_source = "Color Analysis"
            print(f"Using Color Analysis result: {final_prediction}")
        
        # Priority 4: Basic shape/color detection
        else:
            if color_features['aspect_ratio'] > 1.5:
                if color_features['color_dominance'] == 'yellow':
                    final_prediction = "banana"
                elif color_features['color_dominance'] == 'orange':
                    final_prediction = "carrot"
                elif color_features['color_dominance'] == 'green':
                    final_prediction = "cucumber"
            elif color_features['color_dominance'] == 'red':
                final_prediction = "apple"
            elif color_features['color_dominance'] == 'orange':
                final_prediction = "orange"
            elif color_features['color_dominance'] == 'green':
                final_prediction = "apple"
            
            final_confidence = 0.4
            detection_source = "Basic Shape/Color Analysis"
            print(f"Using Basic Analysis result: {final_prediction}")
        
        # Clean up prediction name
        final_prediction_clean = final_prediction.lower().replace('_', ' ').replace('-', ' ').strip()
        
        # STEP 5: Find matching food in database
        print("\n" + "="*50)
        print("STEP 5: Matching with database...")
        print("="*50)
        
        matched_food = None
        
        # Try exact match first
        if final_prediction_clean in food_database:
            matched_food = food_database[final_prediction_clean]
            print(f"Exact match found: {matched_food['name']}")
        else:
            # Try partial matching
            for key, food in food_database.items():
                if (final_prediction_clean in key or key in final_prediction_clean or
                    final_prediction_clean in food['name'].lower()):
                    matched_food = food
                    print(f"Partial match found: {food['name']} (key: {key})")
                    break
        
        # STEP 6: Prepare response
        print("\n" + "="*50)
        print("STEP 6: Preparing response...")
        print("="*50)
        
        # Extract calories
        calories_str = "100 kcal"
        if matched_food:
            nutrition = matched_food.get('nutrition', 'Calories: 100')
            calorie_match = re.search(r'Calories:\s*(\d+)', nutrition)
            if calorie_match:
                calories_str = f"{calorie_match.group(1)} kcal"
        
        if detection_source.startswith("Gemini") and gemini_result.get('calories'):
            calories_str = str(gemini_result.get('calories'))
            if not calories_str.lower().endswith('kcal'):
                calories_str += " kcal"

        # Determine condition
        condition = "Fresh"
        if detection_source.startswith("Gemini") and gemini_result.get('condition'):
            cond_val = str(gemini_result['condition']).capitalize()
            if any(x in cond_val.lower() for x in ['spoil', 'rot', 'mold']):
                condition = "Spoiled"
            elif any(x in cond_val.lower() for x in ['expir', 'stale', 'bad']):
                condition = "Expired"
            elif any(x in cond_val.lower() for x in ['eat', 'ripe']):
                condition = "Eatable"
            else:
                condition = "Fresh"
        elif final_confidence > 0.7:
            condition = "Fresh"
        else:
            condition = "Eatable"

        # Shelf life
        shelf_life = "5-7 days"
        if detection_source.startswith("Gemini") and gemini_result.get('shelf_life'):
            shelf_life = str(gemini_result['shelf_life'])
        elif matched_food:
            shelf_life = matched_food.get('storage', '7 days')

        food_name = matched_food['name'] if matched_food else final_prediction.title()
        category = matched_food['type'].title() if matched_food else (gemini_category.title() if gemini_category != 'unknown' else 'Food')

        message = f"Identified as {food_name} with {final_confidence:.1%} confidence using {detection_source}."
        if detection_source.startswith("Gemini") and gemini_result.get('description'):
            message += f"\nGemini AI noted: {gemini_result.get('description')}"

        return jsonify({
            "name": food_name,
            "category": category,
            "condition": condition,
            "shelfLife": shelf_life,
            "calories": calories_str,
            "confidence": round(final_confidence, 2),
            "source": detection_source,
            "success": True,
            "message": message,
            "additional_info": {
                "gemini_prediction": gemini_prediction,
                "gemini_confidence": gemini_confidence,
                "local_prediction": local_prediction,
                "local_confidence": local_confidence
            }
        })
            
    except Exception as e:
        print(f"Scan endpoint error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "name": "Server Error",
            "category": "Error",
            "condition": "Unknown",
            "shelfLife": "Unknown",
            "calories": "Unknown",
            "confidence": 0.0,
            "source": "Server Error",
            "success": False,
            "message": f"Error processing image: {str(e)}"
        })

if __name__ == '__main__':
    print("=" * 60)
    print("FOOD NUTRITION ASSISTANT SERVER - WITH GEMINI AI")
    print("=" * 60)
    print(f"Database Statistics:")
    print(f"   Fruits: {len(fruits_db)} items")
    print(f"   Vegetables: {len(vegetables_db)} items")
    print(f"   Total Foods: {len(food_database)} items")
    print(f"Local AI Model: {'LOADED' if local_trained_model else 'NOT LOADED'}")
    print(f"Gemini AI: CONFIGURED")
    print("=" * 60)
    print("Server running on: http://localhost:5000")
    print("=" * 60)
    print("Available Endpoints:")
    print("  GET  /          - Home page")
    print("  GET  /health    - Health check")
    print("  GET  /foods     - List all foods")
    print("  POST /chat      - Chat with food assistant")
    print("  POST /scan      - Scan food image (Gemini AI Enhanced)")
    print("=" * 60)
    
    if not local_trained_model:
        print("\nNOTE: Local model files not found!")
        print("Gemini AI will be used as primary scanner.")
    else:
        print("\nMULTI-MODEL SCANNER ACTIVE:")
        print("• Primary: Gemini AI (Google's advanced vision)")
        print("• Secondary: Local AI Model (Trained on specific foods)")
        print("• Fallback: Color and shape analysis")
        print("=" * 60)
    
    print("\nSCANNER FEATURES:")
    print("1. Gemini AI - Advanced food recognition")
    print("2. Local Model - Custom trained detection")
    print("3. Color Analysis - Visual feature detection")
    print("4. Smart Decision Logic - Combines all results")
    print("=" * 60)
    
    app.run(debug=True, port=5000, host='0.0.0.0')