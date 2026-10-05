import React, { useEffect } from 'react';
import { Leaf } from 'lucide-react';

interface SplashScreenProps {
  onFinish: () => void;
}

const SplashScreen: React.FC<SplashScreenProps> = ({ onFinish }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onFinish();
    }, 2500);
    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white dark:bg-zinc-900 transition-colors duration-500">
      <div className="flex flex-col items-center animate-fade-in-up">
        <div className="w-24 h-24 bg-brand-100 dark:bg-green-900/30 rounded-3xl flex items-center justify-center mb-6 shadow-xl shadow-brand-500/10">
          <Leaf className="w-12 h-12 text-brand-600 dark:text-brand-500 animate-pulse" />
        </div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-lime-600 bg-clip-text text-transparent mb-2">
          SmartFood AI
        </h1>
        <p className="text-gray-500 dark:text-gray-400 text-sm tracking-widest uppercase">
          Eat Smart • Live Healthy
        </p>
      </div>
    </div>
  );
};

export default SplashScreen;