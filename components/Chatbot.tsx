// Updated Chatbot.tsx with Dynamic Keywords for ALL Foods
import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '../types';
import { Send, Bot, User as UserIcon, Trash2, AlertCircle, Zap, Heart, Shield, Calendar, Package, Apple } from 'lucide-react';
import { sendChatMessage } from '../services/api';

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const saved = localStorage.getItem('chatHistory');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      } catch (e) {
        console.error('Error parsing saved messages:', e);
      }
    }
    return [{
      id: crypto.randomUUID(),
      role: 'model',
      text: 'Hello! I am your SmartFood Assistant. I can help you with information about fruits, vegetables, their nutrition, benefits, and recipes!',
      timestamp: Date.now()
    }];
  });

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFood, setSelectedFood] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // List of all fruits and vegetables supported
  const allFoods = [
    // Fruits
    'apple', 'banana', 'orange', 'mango', 'grapes', 'pineapple', 'strawberry', 
    'watermelon', 'papaya', 'pomegranate', 'kiwi', 'guava', 'lychee', 'pear', 
    'peach', 'apricot', 'plum', 'cherry', 'fig', 'dates', 'coconut', 'lemon',
    'blueberry', 'raspberry', 'blackberry', 'cranberry', 'avocado', 'melon',
    
    // Vegetables
    'carrot', 'spinach', 'tomato', 'potato', 'onion', 'garlic', 'broccoli',
    'cauliflower', 'cabbage', 'cucumber', 'bell pepper', 'eggplant', 'ginger',
    'pumpkin', 'radish', 'beetroot', 'sweet potato', 'turnip', 'okra',
    'bitter gourd', 'bottle gourd', 'green beans', 'peas', 'corn', 'lettuce',
    'asparagus', 'zucchini', 'brussels sprouts', 'celery', 'mushroom'
  ];

  // Save to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('chatHistory', JSON.stringify(messages));
    } catch (e) {
      console.error('Error saving to localStorage:', e);
    }
  }, [messages]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    // Clear any previous errors
    setError(null);

    // Extract ANY food name from input for keyword buttons
    const words = trimmedInput.toLowerCase().split(/\s+/);
    
    let detectedFood = '';
    for (const word of words) {
      // Check if word matches any food (exact match or contains)
      for (const food of allFoods) {
        if (food === word || 
            (word.includes(food) && food.length > 3) || 
            (food.includes(word) && word.length > 3)) {
          detectedFood = food;
          break;
        }
      }
      if (detectedFood) break;
    }
    
    if (detectedFood) {
      // Capitalize first letter
      setSelectedFood(detectedFood.charAt(0).toUpperCase() + detectedFood.slice(1));
    } else {
      setSelectedFood('');
    }

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      text: trimmedInput,
      timestamp: Date.now()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      // Prepare chat history (last 5 messages for context)
      const recentHistory = messages.slice(-5).map(msg => ({
        role: msg.role,
        content: msg.text
      }));

      // Send to backend
      const responseText = await sendChatMessage(trimmedInput, recentHistory);
      
      const botMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'model',
        text: responseText,
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (error: any) {
      console.error('Chat error:', error);
      
      const errorMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'model',
        text: "I apologize, but I'm having trouble connecting to my knowledge base. Please try again in a moment.",
        timestamp: Date.now()
      };
      
      setMessages(prev => [...prev, errorMsg]);
      setError('Connection error. Please check if the Python server is running.');
    } finally {
      setIsLoading(false);
      // Focus back to input
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const clearHistory = () => {
    if (window.confirm('Are you sure you want to clear all chat history?')) {
      setMessages([{
        id: crypto.randomUUID(),
        role: 'model',
        text: 'Chat history cleared! How can I help you with fruits and vegetables today?',
        timestamp: Date.now()
      }]);
      setSelectedFood('');
    }
  };

  // Suggested questions
  const suggestedQuestions = [
    "What are the health benefits of apples?",
    "How to store vegetables properly?",
    "Tell me about banana nutrition",
    "Best fruits for weight loss",
    "Seasonal vegetables this month"
  ];

  const handleSuggestionClick = (question: string) => {
    setInput(question);
  };

  // Keyword buttons click handler
  const handleKeywordClick = (keyword: string) => {
    if (selectedFood) {
      setInput(`${selectedFood} ${keyword}`);
      // Auto focus on input after setting value
      setTimeout(() => {
        inputRef.current?.focus();
        inputRef.current?.setSelectionRange(
          inputRef.current.value.length,
          inputRef.current.value.length
        );
      }, 10);
    }
  };

  // Also detect food when input changes
  useEffect(() => {
    const trimmedInput = input.trim().toLowerCase();
    if (!trimmedInput) {
      setSelectedFood('');
      return;
    }

    const words = trimmedInput.split(/\s+/);
    let detectedFood = '';
    
    for (const word of words) {
      for (const food of allFoods) {
        // Check for exact match or word contains food name
        if (food === word || 
            (word.length > 2 && food.includes(word)) || 
            (food.length > 2 && word.includes(food))) {
          detectedFood = food;
          break;
        }
      }
      if (detectedFood) break;
    }
    
    if (detectedFood) {
      setSelectedFood(detectedFood.charAt(0).toUpperCase() + detectedFood.slice(1));
    } else {
      setSelectedFood('');
    }
  }, [input]);

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] bg-white dark:bg-zinc-800 rounded-2xl shadow-lg border border-gray-200 dark:border-zinc-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-zinc-700 flex justify-between items-center bg-gradient-to-r from-brand-50 to-green-50 dark:from-zinc-800 dark:to-zinc-900">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-brand-100 dark:bg-brand-900 rounded-lg">
            <Bot className="text-brand-600 dark:text-brand-400" size={20} />
          </div>
          <div>
            <h2 className="font-bold text-gray-800 dark:text-white">SmartFood Assistant</h2>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Trained on fruits & vegetables knowledge
            </p>
          </div>
        </div>
        <button
          onClick={clearHistory}
          className="text-sm text-gray-600 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 flex items-center gap-1 px-3 py-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          title="Clear chat history"
        >
          <Trash2 size={16} /> Clear
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700 text-sm">
          <AlertCircle size={16} />
          <span>{error}</span>
          <button onClick={() => setError(null)} className="ml-auto text-red-500 hover:text-red-700">
            ×
          </button>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
          >
            <div
              className={`max-w-[85%] rounded-2xl p-4 shadow-sm flex gap-3 ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-brand-500 to-brand-600 text-white rounded-br-none'
                  : 'bg-gray-100 dark:bg-zinc-700/50 text-gray-800 dark:text-gray-200 rounded-bl-none border border-gray-200 dark:border-zinc-600'
              }`}
            >
              <div className={`mt-0.5 flex-shrink-0 ${msg.role === 'user' ? 'text-white/80' : 'text-gray-500 dark:text-gray-400'}`}>
                {msg.role === 'user' ? <UserIcon size={18} /> : <Bot size={18} />}
              </div>
              <div className="flex-1">
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.text}</p>
                <span className="text-xs opacity-60 mt-1 block">
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          </div>
        ))}
        
        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-zinc-700 rounded-2xl p-4 rounded-bl-none">
              <div className="flex items-center gap-3">
                <div className="p-1.5 bg-gray-200 dark:bg-zinc-600 rounded-lg">
                  <Bot size={16} className="text-gray-500 dark:text-gray-400" />
                </div>
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Suggestions for new chat */}
        {messages.length === 1 && !isLoading && (
          <div className="space-y-3 mt-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 text-center">Try asking:</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {suggestedQuestions.map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestionClick(question)}
                  className="px-3 py-2 bg-white dark:bg-zinc-700 border border-gray-300 dark:border-zinc-600 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-zinc-600 transition-colors shadow-sm"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Keywords Buttons Section - Shows when ANY food is detected */}
      {selectedFood && (
        <div className="px-4 py-3 bg-gradient-to-r from-gray-50 to-blue-50 dark:from-zinc-900/30 dark:to-zinc-800/30 border-t border-gray-200 dark:border-zinc-700">
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
            Quick actions for <span className="font-semibold text-brand-600 dark:text-brand-400">{selectedFood}</span>:
          </p>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleKeywordClick('nutrition')}
              className="px-3 py-2 bg-white dark:bg-zinc-800 border border-gray-300 dark:border-zinc-600 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 hover:border-yellow-300 dark:hover:border-yellow-700 transition-all flex items-center gap-2 hover:shadow-sm group"
            >
              <Zap size={14} className="text-yellow-500 group-hover:text-yellow-600" />
              Nutrition
            </button>
            <button
              onClick={() => handleKeywordClick('vitamins')}
              className="px-3 py-2 bg-white dark:bg-zinc-800 border border-gray-300 dark:border-zinc-600 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300 dark:hover:border-blue-700 transition-all flex items-center gap-2 hover:shadow-sm group"
            >
              <Shield size={14} className="text-blue-500 group-hover:text-blue-600" />
              Vitamins
            </button>
            <button
              onClick={() => handleKeywordClick('benefits')}
              className="px-3 py-2 bg-white dark:bg-zinc-800 border border-gray-300 dark:border-zinc-600 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:border-red-300 dark:hover:border-red-700 transition-all flex items-center gap-2 hover:shadow-sm group"
            >
              <Heart size={14} className="text-red-500 group-hover:text-red-600" />
              Benefits
            </button>
            <button
              onClick={() => handleKeywordClick('storage')}
              className="px-3 py-2 bg-white dark:bg-zinc-800 border border-gray-300 dark:border-zinc-600 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-green-900/20 hover:border-green-300 dark:hover:border-green-700 transition-all flex items-center gap-2 hover:shadow-sm group"
            >
              <Package size={14} className="text-green-500 group-hover:text-green-600" />
              Storage
            </button>
            <button
              onClick={() => handleKeywordClick('season')}
              className="px-3 py-2 bg-white dark:bg-zinc-800 border border-gray-300 dark:border-zinc-600 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-purple-50 dark:hover:bg-purple-900/20 hover:border-purple-300 dark:hover:border-purple-700 transition-all flex items-center gap-2 hover:shadow-sm group"
            >
              <Calendar size={14} className="text-purple-500 group-hover:text-purple-600" />
              Season
            </button>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 bg-gray-50/50 dark:bg-zinc-900/30 border-t border-gray-200 dark:border-zinc-700">
        <div className="flex items-center gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Type any fruit or vegetable name..."
            className="flex-1 px-4 py-3 rounded-xl border border-gray-300 dark:border-zinc-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none transition-shadow"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="p-3 bg-gradient-to-r from-brand-500 to-brand-600 text-white rounded-xl hover:from-brand-600 hover:to-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg active:scale-95"
            title="Send message"
          >
            <Send size={20} />
          </button>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
          Type any fruit or vegetable name to see quick action buttons
        </p>
      </div>
    </div>
  );
};

export default Chatbot;