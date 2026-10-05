import { ScanResult } from "../types";

// Get Gemini API key from Vite environment
const GEMINI_API_KEY =
  (import.meta as any).env?.VITE_GEMINI_API_KEY ||
  (import.meta as any).env?.GEMINI_API_KEY ||
  "";

const API_URL = "http://localhost:5000";

// --- DATABASE FOR OFFLINE FALLBACK ---
const FOOD_KNOWLEDGE_BASE = [
  // Fruits
  { name: "Apple", category: "Fruit", calories: "52 kcal", shelfLife: "3-4 weeks (Fridge)", condition: "Fresh" },
  { name: "Banana", category: "Fruit", calories: "89 kcal", shelfLife: "3-7 days", condition: "Fresh" },
  { name: "Orange", category: "Fruit", calories: "47 kcal", shelfLife: "2 weeks", condition: "Fresh" },
  { name: "Mango", category: "Fruit", calories: "60 kcal", shelfLife: "5-7 days", condition: "Fresh" },
  { name: "Grapes", category: "Fruit", calories: "67 kcal", shelfLife: "2 weeks", condition: "Fresh" },
  { name: "Pineapple", category: "Fruit", calories: "50 kcal", shelfLife: "3 days (cut)", condition: "Fresh" },
  { name: "Papaya", category: "Fruit", calories: "43 kcal", shelfLife: "3-5 days", condition: "Fresh" },
  { name: "Watermelon", category: "Fruit", calories: "30 kcal", shelfLife: "2 weeks (Whole)", condition: "Fresh" },
  { name: "Melon", category: "Fruit", calories: "34 kcal", shelfLife: "1 week", condition: "Fresh" },
  { name: "Strawberry", category: "Fruit", calories: "32 kcal", shelfLife: "3-7 days", condition: "Fresh" },
  { name: "Blueberry", category: "Fruit", calories: "57 kcal", shelfLife: "1-2 weeks", condition: "Fresh" },
  { name: "Peach", category: "Fruit", calories: "39 kcal", shelfLife: "3-5 days", condition: "Fresh" },
  { name: "Pear", category: "Fruit", calories: "57 kcal", shelfLife: "5 days", condition: "Fresh" },
  { name: "Guava", category: "Fruit", calories: "68 kcal", shelfLife: "2-3 days", condition: "Fresh" },
  { name: "Kiwi", category: "Fruit", calories: "61 kcal", shelfLife: "1 week", condition: "Fresh" },
  { name: "Pomegranate", category: "Fruit", calories: "83 kcal", shelfLife: "1-2 months", condition: "Fresh" },
  { name: "Plum", category: "Fruit", calories: "46 kcal", shelfLife: "3-5 days", condition: "Fresh" },
  { name: "Apricot", category: "Fruit", calories: "48 kcal", shelfLife: "3-5 days", condition: "Fresh" },
  { name: "Coconut", category: "Fruit", calories: "354 kcal", shelfLife: "2-3 months", condition: "Fresh" },
  { name: "Lemon", category: "Fruit", calories: "29 kcal", shelfLife: "3-4 weeks", condition: "Fresh" },
  { name: "Cherry", category: "Fruit", calories: "50 kcal", shelfLife: "4-7 days", condition: "Fresh" },
  { name: "Fig", category: "Fruit", calories: "74 kcal", shelfLife: "2-3 days", condition: "Fresh" },
  { name: "Dates", category: "Fruit", calories: "282 kcal", shelfLife: "6 months", condition: "Fresh" },
  { name: "Lychee", category: "Fruit", calories: "66 kcal", shelfLife: "5-7 days", condition: "Fresh" },
  { name: "Avocado", category: "Fruit", calories: "160 kcal", shelfLife: "3-4 days", condition: "Fresh" },
  // Vegetables
  { name: "Potato", category: "Vegetable", calories: "77 kcal", shelfLife: "2-3 months", condition: "Fresh" },
  { name: "Tomato", category: "Vegetable", calories: "18 kcal", shelfLife: "1 week", condition: "Fresh" },
  { name: "Onion", category: "Vegetable", calories: "40 kcal", shelfLife: "2-3 months", condition: "Fresh" },
  { name: "Garlic", category: "Vegetable", calories: "149 kcal", shelfLife: "3-6 months", condition: "Fresh" },
  { name: "Carrot", category: "Vegetable", calories: "41 kcal", shelfLife: "3-4 weeks", condition: "Fresh" },
  { name: "Cabbage", category: "Vegetable", calories: "25 kcal", shelfLife: "2 weeks", condition: "Fresh" },
  { name: "Cauliflower", category: "Vegetable", calories: "25 kcal", shelfLife: "1-2 weeks", condition: "Fresh" },
  { name: "Spinach", category: "Vegetable", calories: "23 kcal", shelfLife: "5-7 days", condition: "Fresh" },
  { name: "Broccoli", category: "Vegetable", calories: "34 kcal", shelfLife: "3-5 days", condition: "Fresh" },
  { name: "Peas", category: "Vegetable", calories: "81 kcal", shelfLife: "3-5 days", condition: "Fresh" },
  { name: "Corn", category: "Vegetable", calories: "86 kcal", shelfLife: "1-2 days", condition: "Fresh" },
  { name: "Ginger", category: "Vegetable", calories: "80 kcal", shelfLife: "3-4 weeks", condition: "Fresh" },
  { name: "Eggplant", category: "Vegetable", calories: "25 kcal", shelfLife: "5-7 days", condition: "Fresh" },
  { name: "Cucumber", category: "Vegetable", calories: "15 kcal", shelfLife: "1 week", condition: "Fresh" },
  { name: "Capsicum", category: "Vegetable", calories: "20 kcal", shelfLife: "1-2 weeks", condition: "Fresh" },
  { name: "Green Beans", category: "Vegetable", calories: "31 kcal", shelfLife: "5-7 days", condition: "Fresh" },
  { name: "Radish", category: "Vegetable", calories: "16 kcal", shelfLife: "1-2 weeks", condition: "Fresh" },
  { name: "Lettuce", category: "Vegetable", calories: "15 kcal", shelfLife: "5-7 days", condition: "Fresh" },
  { name: "Beetroot", category: "Vegetable", calories: "43 kcal", shelfLife: "2-3 weeks", condition: "Fresh" },
  { name: "Pumpkin", category: "Vegetable", calories: "26 kcal", shelfLife: "2-3 months", condition: "Fresh" },
  { name: "Bitter Gourd", category: "Vegetable", calories: "17 kcal", shelfLife: "3-4 days", condition: "Fresh" },
  { name: "Bottle Gourd", category: "Vegetable", calories: "14 kcal", shelfLife: "3-4 days", condition: "Fresh" },
  { name: "Okra", category: "Vegetable", calories: "33 kcal", shelfLife: "2-3 days", condition: "Fresh" },
  { name: "Turnip", category: "Vegetable", calories: "28 kcal", shelfLife: "2 weeks", condition: "Fresh" },
  { name: "Sweet Potato", category: "Vegetable", calories: "86 kcal", shelfLife: "3-5 weeks", condition: "Fresh" }
];

// --- GEMINI DIRECT VISION ENGINE ---

async function analyzeWithGeminiDirect(base64Image: string): Promise<ScanResult> {
  let mimeType = 'image/jpeg';
  let cleanBase64 = base64Image;

  if (base64Image.startsWith('data:')) {
    const match = base64Image.match(/^data:([^;]+);base64,/);
    if (match) {
      mimeType = match[1];
    }
    cleanBase64 = base64Image.replace(/^data:[^;]+;base64,/, '');
  } else if (cleanBase64.includes(',')) {
    cleanBase64 = cleanBase64.split(',')[1];
  }
  cleanBase64 = cleanBase64.trim();

  const prompt = `You are an expert food scientist, botanist, and culinary nutritionist.
Analyze the attached food image carefully and identify the exact food item.

Instructions:
1. Identify the primary food item accurately (e.g. Red Apple, Cavendish Banana, Roma Tomato, Fresh Broccoli, Sliced Bread, Pepperoni Pizza, Biryani, Grilled Chicken, etc.).
2. Determine its freshness and condition:
   - 'Fresh': Crisp, vibrant, unblemished, peak quality.
   - 'Eatable': Ripe, slightly softened, or minor natural marks, but safe and good to eat.
   - 'Expired': Stale, past peak freshness, overripe, wilted, or souring.
   - 'Spoiled': Visibly rotten, moldy, decomposed, bruised severely, or unsafe to consume.
3. Estimate realistic shelf life based on condition (e.g. '3-4 weeks (fridge)', '2-3 days at room temp', 'Consume immediately', 'Discard safely').
4. Estimate calories per standard portion or 100g (e.g. '95 kcal (medium)', '52 kcal / 100g').
5. Provide a confidence rating between 0.0 and 1.0.
6. Provide a concise 1-2 sentence description of appearance and freshness markers observed.

Respond strictly with valid JSON matching this schema:
{
  "name": "Exact Name of Food",
  "category": "Fruit or Vegetable or Prepared Food or Bakery or Dairy or Meat or Beverage",
  "condition": "Must be exactly one of: Fresh, Eatable, Expired, Spoiled",
  "shelfLife": "Realistic shelf life",
  "calories": "Calories with unit (e.g. 95 kcal)",
  "confidence": 0.95,
  "details": "Description of freshness and visual characteristics observed."
}`;

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              { text: prompt },
              {
                inline_data: {
                  mime_type: mimeType,
                  data: cleanBase64
                }
              }
            ]
          }
        ],
        generationConfig: {
          response_mime_type: 'application/json'
        }
      })
    }
  );

  if (!response.ok) {
    const errorJson = await response.json().catch(() => null);
    throw new Error(errorJson?.error?.message || `Gemini API HTTP ${response.status}`);
  }

  const data = await response.json();
  const rawText = data?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!rawText) {
    throw new Error("No response generated from Gemini Vision API");
  }

  let parsed: any;
  try {
    let cleaned = rawText.trim();
    if (cleaned.startsWith('```')) {
      cleaned = cleaned.replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, '').trim();
    }
    const match = cleaned.match(/\{[\s\S]*\}/);
    parsed = match ? JSON.parse(match[0]) : JSON.parse(cleaned);
  } catch (err: any) {
    console.error("Failed to parse Gemini JSON:", rawText);
    throw new Error("Invalid JSON from Gemini: " + err.message);
  }

  // Normalize condition
  let condition: 'Fresh' | 'Eatable' | 'Expired' | 'Spoiled' = 'Fresh';
  const c = String(parsed.condition || '').toLowerCase();
  if (c.includes('spoil') || c.includes('rot') || c.includes('mold') || c.includes('decay')) {
    condition = 'Spoiled';
  } else if (c.includes('expir') || c.includes('stale') || c.includes('bad') || c.includes('wilt')) {
    condition = 'Expired';
  } else if (c.includes('eat') || c.includes('ripe') || c.includes('soft')) {
    condition = 'Eatable';
  } else {
    condition = 'Fresh';
  }

  return {
    id: `scan-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    timestamp: Date.now(),
    imageUrl: base64Image.startsWith('data:') ? base64Image : `data:${mimeType};base64,${cleanBase64}`,
    name: parsed.name || "Identified Food",
    category: parsed.category || "Food",
    condition,
    shelfLife: parsed.shelfLife || "3-5 days",
    calories: typeof parsed.calories === 'number' ? `${parsed.calories} kcal` : (parsed.calories || "100 kcal"),
    confidence: typeof parsed.confidence === 'number' ? parsed.confidence : 0.95,
    source: "Gemini 2.5 Flash Vision AI",
    details: parsed.details || "",
    isSimulation: false
  };
}

// --- PYTHON BACKEND FALLBACK ENGINE ---

async function analyzeWithBackend(base64Image: string): Promise<ScanResult> {
  const cleanBase64 = base64Image.includes(',') ? base64Image.split(',')[1] : base64Image;
  const response = await fetch(`${API_URL}/scan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({ image: cleanBase64 }),
  });

  if (!response.ok) throw new Error(`Backend server error: ${response.status}`);
  const data = await response.json();
  if (data.error) throw new Error(data.error);

  let condition: 'Fresh' | 'Eatable' | 'Expired' | 'Spoiled' = 'Fresh';
  const c = String(data.condition || '').toLowerCase();
  if (c.includes('spoil')) condition = 'Spoiled';
  else if (c.includes('expir')) condition = 'Expired';
  else if (c.includes('eat')) condition = 'Eatable';

  return {
    id: `scan-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    timestamp: Date.now(),
    imageUrl: base64Image.startsWith('data:') ? base64Image : `data:image/jpeg;base64,${cleanBase64}`,
    name: data.name || "Food Item",
    category: data.category || "Food",
    condition,
    shelfLife: data.shelfLife || "Unknown",
    calories: String(data.calories || "100 kcal"),
    confidence: typeof data.confidence === 'number' ? data.confidence : 0.9,
    source: data.source || "Python AI Backend",
    isSimulation: false
  };
}

// --- OFFLINE KNOWLEDGE BASE FALLBACK ---

function offlineFallbackScan(base64Image: string): ScanResult {
  let hash = 0;
  for (let i = 0; i < Math.min(base64Image.length, 500); i++) {
    hash = ((hash << 5) - hash) + base64Image.charCodeAt(i);
    hash |= 0;
  }
  const index = Math.abs(hash) % FOOD_KNOWLEDGE_BASE.length;
  const item = FOOD_KNOWLEDGE_BASE[index];

  return {
    id: `sim-${Date.now()}-${Math.floor(Math.random() * 10000)}`,
    timestamp: Date.now(),
    imageUrl: base64Image.startsWith('data:') ? base64Image : `data:image/jpeg;base64,${base64Image}`,
    name: item.name,
    category: item.category,
    condition: item.condition as any,
    shelfLife: item.shelfLife,
    calories: item.calories,
    confidence: 0.6,
    source: "Offline Knowledge Base",
    isSimulation: true
  };
}

// --- EXPORTED SCAN API ---

/**
 * Accurately analyzes food images using Gemini 2.5 Flash Vision AI.
 * Falls back to Python backend, then offline knowledge base if network is unavailable.
 */
export const analyzeFoodImage = async (base64Image: string): Promise<ScanResult> => {
  console.log("📷 [API] Analyzing image with Gemini Vision AI...");

  // Primary: Direct Gemini 2.5 Flash Vision AI (High accuracy, no local server required)
  try {
    const geminiResult = await analyzeWithGeminiDirect(base64Image);
    console.log("✅ [API] Gemini Vision AI Scan successful:", geminiResult.name, `(${geminiResult.condition})`);
    return geminiResult;
  } catch (geminiError: any) {
    console.warn("⚠️ [API] Direct Gemini Vision failed:", geminiError.message);
    console.log("🔄 [API] Trying Python backend as fallback...");
  }

  // Secondary: Python Backend if available
  try {
    const backendResult = await analyzeWithBackend(base64Image);
    console.log("✅ [API] Backend Scan successful:", backendResult.name);
    return backendResult;
  } catch (backendError: any) {
    console.warn("⚠️ [API] Python Backend unavailable:", backendError.message);
  }

  // Tertiary: Offline Knowledge Base
  console.warn("📷 [API] Using Offline Knowledge Base as fallback.");
  return offlineFallbackScan(base64Image);
};

// --- GEMINI DIRECT CHAT ENGINE ---

async function chatWithGeminiDirect(message: string, history: any[] = []): Promise<string> {
  const systemPrompt = `You are SmartFood AI, an intelligent, helpful food and nutrition expert assistant.
You provide clear, accurate guidance on:
- Freshness signs and identification of fruits, vegetables, and foods.
- Shelf life and safe storage guidelines (fridge, freezer, room temperature).
- Nutritional value (calories, carbs, vitamins, minerals, fiber).
- Health benefits, seasonal availability, and food waste reduction tips.
Keep answers structured, concise, and friendly with markdown formatting when appropriate.`;

  const contents: any[] = [];

  // Pass conversation history (last 6 messages)
  if (history && history.length > 0) {
    for (const msg of history.slice(-6)) {
      if (msg.text && msg.role) {
        contents.push({
          role: msg.role === 'model' ? 'model' : 'user',
          parts: [{ text: msg.text }]
        });
      }
    }
  }

  contents.push({
    role: 'user',
    parts: [{ text: message }]
  });

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        systemInstruction: {
          parts: [{ text: systemPrompt }]
        },
        contents: contents
      })
    }
  );

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.error?.message || `Gemini API HTTP ${response.status}`);
  }

  const data = await response.json();
  const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error("Empty response from Gemini");
  return text;
}

// --- EXPORTED CHAT API ---

/**
 * Sends a chat message to Gemini 2.5 Flash AI.
 * Falls back to Python server or local regex matching if offline.
 */
export const sendChatMessage = async (
  message: string,
  history: any[] = []
): Promise<string> => {
  console.log("📡 [API] Sending chat message:", message);

  // Primary: Gemini AI Direct
  try {
    const reply = await chatWithGeminiDirect(message, history);
    console.log("✅ [API] Gemini chat reply received.");
    return reply;
  } catch (geminiError: any) {
    console.warn("⚠️ [API] Direct Gemini chat failed:", geminiError.message);
  }

  // Secondary: Python Flask server
  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ message }),
    });

    if (response.ok) {
      const data = await response.json();
      if (data.response) return data.response;
    }
  } catch (backendError: any) {
    console.warn("⚠️ [API] Backend chat unavailable:", backendError.message);
  }

  // Tertiary: Local offline chat logic
  return localChatLogic(message);
};

// --- LOCAL LOGIC HELPERS ---

function localChatLogic(message: string): string {
  const lower = message.toLowerCase();

  if (lower.includes('hello') || lower.includes('hi')) {
    return "Hello! I am your SmartFood AI assistant. I can help identify 50+ fruits and vegetables and answer your nutrition questions.";
  }

  for (const item of FOOD_KNOWLEDGE_BASE) {
    if (lower.includes(item.name.toLowerCase())) {
      let response = `**${item.name}** (${item.category}) is usually ${item.condition}. Approx ${item.calories}. Shelf life: ${item.shelfLife}.`;
      if (lower.includes('calorie')) response = `${item.name} has about ${item.calories}.`;
      if (lower.includes('shelf') || lower.includes('last')) response = `${item.name} lasts about ${item.shelfLife}.`;
      return response;
    }
  }

  if (lower.includes('fresh') || lower.includes('scan')) {
    return "Use the SmartScan camera button to take a picture of any food, and Gemini AI will analyze its freshness and calories.";
  }

  if (lower.includes('bye')) {
    return "Goodbye! Eat healthy!";
  }

  return "I can help you analyze food freshness, shelf life, and nutrition facts. Try taking a photo in SmartScan or asking about any fruit or vegetable!";
}