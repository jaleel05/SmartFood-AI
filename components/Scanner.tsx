import React, { useState, useRef, useEffect } from 'react';
import { Camera, Upload, RefreshCw, Clock, Activity, Info, ChevronRight, ChevronDown, X, Zap, WifiOff, Wifi, Sparkles } from 'lucide-react';
import { analyzeFoodImage } from '../services/api';
import { ScanResult } from '../types';

const LOADING_STEPS = [
  "Preprocessing Image...",
  "Connecting to Gemini AI Vision...",
  "Analyzing Freshness & Quality...",
  "Calculating Nutrition & Calories...",
  "Generating Smart Report..."
];

const Scanner: React.FC = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [currentResult, setCurrentResult] = useState<ScanResult | null>(null);
  const [history, setHistory] = useState<ScanResult[]>(() => {
    const saved = localStorage.getItem('scanHistory');
    return saved ? JSON.parse(saved) : [];
  });
  const [showHistory, setShowHistory] = useState(false);
  
  // Camera State
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    localStorage.setItem('scanHistory', JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  useEffect(() => {
    if (isScanning) {
      const interval = setInterval(() => {
        setLoadingStep(prev => (prev < LOADING_STEPS.length - 1 ? prev + 1 : prev));
      }, 600);
      return () => clearInterval(interval);
    } else {
      setLoadingStep(0);
    }
  }, [isScanning]);

  const startCamera = async () => {
    try {
      setIsCameraOpen(true);
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      }, 100);
    } catch (err) {
      console.error("Camera Error:", err);
      setIsCameraOpen(false);
      alert("Unable to access camera. Please check permissions or use Upload Image.");
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraOpen(false);
  };

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const context = canvas.getContext('2d');
      if (context) {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
        const base64String = dataUrl.split(',')[1];
        
        stopCamera();
        processImage(base64String);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();

      reader.onloadend = () => {
        const base64String = (reader.result as string).split(',')[1];
        processImage(base64String);
      };
      
      reader.readAsDataURL(file);
    }
  };

  const processImage = async (base64String: string) => {
    setIsScanning(true);
    setCurrentResult(null);
    setLoadingStep(0);
    
    try {
      const result = await analyzeFoodImage(base64String);
      setCurrentResult(result);
      setHistory(prev => [result, ...prev]);
    } catch (error: any) {
      alert("Analysis failed. Please try again.");
    } finally {
      setIsScanning(false);
    }
  };

  const getConditionColor = (cond: string) => {
    switch (cond) {
      case 'Fresh': return 'text-green-700 bg-green-100 border-green-200 dark:bg-green-900/30 dark:border-green-800 dark:text-green-400';
      case 'Eatable': return 'text-yellow-700 bg-yellow-100 border-yellow-200 dark:bg-yellow-900/30 dark:border-yellow-800 dark:text-yellow-400';
      case 'Expired': return 'text-orange-700 bg-orange-100 border-orange-200 dark:bg-orange-900/30 dark:border-orange-800 dark:text-orange-400';
      case 'Spoiled': return 'text-red-700 bg-red-100 border-red-200 dark:bg-red-900/30 dark:border-red-800 dark:text-red-400';
      default: return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-4xl mx-auto">
      <canvas ref={canvasRef} className="hidden"></canvas>

      {/* Input Area */}
      <div className="bg-white dark:bg-zinc-800 rounded-3xl shadow-xl p-8 md:p-12 text-center border-2 border-dashed border-gray-200 dark:border-zinc-700 transition-all duration-300 relative overflow-hidden">
        <input 
          type="file" 
          accept="image/*" 
          className="hidden" 
          ref={fileInputRef}
          onChange={handleFileSelect}
        />
        
        {isCameraOpen ? (
          <div className="fixed inset-0 z-50 bg-black flex flex-col items-center justify-center">
             <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover" />
             <div className="absolute bottom-10 left-0 right-0 flex justify-center items-center gap-8">
               <button onClick={stopCamera} className="p-4 bg-white/20 backdrop-blur-md rounded-full text-white hover:bg-white/30 transition-all"><X size={24} /></button>
               <button onClick={captureImage} className="p-1 rounded-full border-4 border-white/50"><div className="w-16 h-16 bg-white rounded-full active:scale-90 transition-transform"></div></button>
               <div className="w-14"></div>
             </div>
          </div>
        ) : isScanning ? (
          <div className="flex flex-col items-center justify-center py-6 space-y-6">
            <div className="relative">
              <div className="w-20 h-20 rounded-full border-4 border-gray-100 dark:border-zinc-700 border-t-brand-500 animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <RefreshCw className="text-brand-500 w-8 h-8 animate-pulse" />
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-lg font-bold text-gray-900 dark:text-white">{LOADING_STEPS[loadingStep]}</p>
            </div>
          </div>
        ) : currentResult ? (
          <div className="animate-fade-in text-left">
             <div className="flex flex-col md:flex-row gap-8 items-start">
               <div className="w-full md:w-1/3">
                 <div className="relative rounded-2xl overflow-hidden shadow-lg border-4 border-white dark:border-zinc-700">
                   <img src={currentResult.imageUrl} alt="Scanned" className="w-full h-auto object-cover aspect-square" />
                   {/* Status Badge */}
                   <div className={`absolute bottom-0 left-0 right-0 p-2 text-center text-xs font-bold text-white ${currentResult.isSimulation ? 'bg-orange-500/90' : 'bg-brand-600/90'}`}>
                     {currentResult.isSimulation ? (
                       <span className="flex items-center justify-center gap-1"><WifiOff size={12} /> Offline Simulation</span>
                     ) : (
                       <span className="flex items-center justify-center gap-1"><Sparkles size={12} /> {currentResult.source || 'Gemini Vision AI Verified'}</span>
                     )}
                   </div>
                 </div>
               </div>
               
               <div className="flex-1 w-full grid grid-cols-1 sm:grid-cols-2 gap-4">
                 <div className="col-span-1 sm:col-span-2 bg-gradient-to-br from-brand-50 to-white dark:from-zinc-700/50 dark:to-zinc-800 p-5 rounded-2xl border border-brand-100 dark:border-zinc-600">
                   <h4 className="text-xs text-brand-600 dark:text-brand-400 font-bold uppercase tracking-wider mb-1">Result</h4>
                   <div className="flex items-center justify-between">
                      <p className="text-3xl font-extrabold text-gray-900 dark:text-white">{currentResult.name}</p>
                      <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-200 text-sm font-semibold">{currentResult.category}</span>
                   </div>
                   {currentResult.details && (
                     <p className="text-xs text-gray-600 dark:text-gray-300 mt-2 font-medium">
                       {currentResult.details}
                     </p>
                   )}
                   {currentResult.isSimulation && (
                     <p className="text-xs text-orange-500 mt-2 font-medium">
                       * Result approximated offline. Connect to internet for full Gemini AI accuracy.
                     </p>
                   )}
                 </div>

                 <div className={`p-5 rounded-2xl border ${getConditionColor(currentResult.condition)}`}>
                   <h4 className="text-xs opacity-70 font-bold uppercase tracking-wider mb-2">Condition</h4>
                   <div className="flex items-center gap-2 text-xl font-bold"><Activity size={24} /> {currentResult.condition}</div>
                 </div>

                 <div className="bg-gray-50 dark:bg-zinc-700/30 p-5 rounded-2xl border border-gray-100 dark:border-zinc-700">
                   <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-2">Shelf Life</h4>
                   <div className="flex items-center gap-2 text-xl font-semibold text-gray-900 dark:text-white"><Clock size={24} className="text-brand-500" /> {currentResult.shelfLife}</div>
                 </div>

                 <div className="bg-gray-50 dark:bg-zinc-700/30 p-5 rounded-2xl border border-gray-100 dark:border-zinc-700">
                   <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-2">Calories</h4>
                   <div className="flex items-center gap-2 text-xl font-semibold text-gray-900 dark:text-white"><Zap size={24} className="text-yellow-500" /> {currentResult.calories}</div>
                 </div>
               </div>
             </div>

             <div className="mt-8 flex justify-center">
               <button 
                 onClick={startCamera}
                 className="px-8 py-3 bg-brand-600 hover:bg-brand-700 text-white font-bold rounded-xl transition-all shadow-lg shadow-brand-500/20 active:scale-95 flex items-center gap-2"
               >
                 <Camera size={20} />
                 Scan Another Item
               </button>
             </div>
          </div>
        ) : (
          <div className="py-10 space-y-8">
            <div className="flex flex-col items-center">
              <div className="w-20 h-20 bg-brand-100 dark:bg-brand-900/20 rounded-full flex items-center justify-center mb-6">
                 <Camera size={40} className="text-brand-600 dark:text-brand-400" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">SmartFood AI Scanner</h3>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
                Powered by Google Gemini Vision AI to identify any food, analyze freshness, and calculate calories accurately.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <button 
                onClick={startCamera}
                className="flex items-center justify-center gap-3 px-8 py-4 bg-brand-600 text-white rounded-xl hover:bg-brand-700 transition-all shadow-lg hover:shadow-xl font-semibold"
              >
                <Camera size={20} />
                Take Photo
              </button>
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center justify-center gap-3 px-8 py-4 bg-white dark:bg-zinc-700 text-gray-900 dark:text-white border border-gray-200 dark:border-zinc-600 rounded-xl hover:bg-gray-50 dark:hover:bg-zinc-600 transition-all font-semibold"
              >
                <Upload size={20} />
                Upload Image
              </button>
            </div>
          </div>
        )}
      </div>

      {history.length > 0 && (
        <div className="bg-white dark:bg-zinc-800 rounded-3xl shadow-lg overflow-hidden border border-gray-100 dark:border-zinc-700">
          <button 
            onClick={() => setShowHistory(!showHistory)}
            className="w-full px-8 py-5 flex items-center justify-center md:justify-between font-bold text-lg text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-zinc-700/50 transition-colors"
          >
            <span className="flex items-center gap-2"><Clock size={20} className="text-brand-500" /> Scan History</span>
            <span className="hidden md:block">{showHistory ? <ChevronDown size={20} /> : <ChevronRight size={20} />}</span>
          </button>
          
          {showHistory && (
            <div className="p-4 bg-gray-50 dark:bg-zinc-900/50 max-h-96 overflow-y-auto space-y-3">
              {history.map((item) => (
                <div key={item.id} className="flex items-center gap-4 bg-white dark:bg-zinc-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-zinc-700/50">
                  <img src={item.imageUrl} alt={item.name} className="w-16 h-16 rounded-lg object-cover" />
                  <div className="flex-1">
                    <h5 className="font-bold text-gray-900 dark:text-white">{item.name}</h5>
                    <div className="flex gap-2 text-xs mt-1">
                      <span className="px-2 py-0.5 rounded bg-gray-100 dark:bg-zinc-700 text-gray-600 dark:text-gray-300">{item.category}</span>
                      {item.isSimulation && <span className="px-2 py-0.5 rounded bg-orange-100 text-orange-600">Simulated</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Scanner;