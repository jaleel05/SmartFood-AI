import React from 'react';
import { AppView } from '../types';
import { MessageSquare, Scan, ArrowRight } from 'lucide-react';

interface DashboardProps {
  onNavigate: (view: AppView) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  return (
    <div className="h-full flex flex-col justify-center items-center py-6 md:py-10 animate-fade-in">
      <div className="text-center mb-10 max-w-2xl">
        <h2 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-4 tracking-tight">
          Eat Smart, <span className="bg-gradient-to-r from-brand-600 to-green-400 bg-clip-text text-transparent">Live Better</span>
        </h2>
        <p className="text-lg text-gray-500 dark:text-gray-400 leading-relaxed">
          Powered by MobileNetV2, EfficientNet & YOLOv8 to bring you the most advanced food analysis AI.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl px-4">
        <DashboardCard 
          title="AI Chatbot" 
          description="Interactive expert on fruits & vegetables." 
          icon={<MessageSquare size={32} />} 
          colorClass="from-blue-500 to-indigo-600"
          shadowClass="shadow-blue-500/20"
          onClick={() => onNavigate(AppView.CHAT)}
        />
        <DashboardCard 
          title="Smart Scan" 
          description="Real-time freshness & calorie detection." 
          icon={<Scan size={32} />} 
          colorClass="from-orange-500 to-amber-600"
          shadowClass="shadow-orange-500/20"
          onClick={() => onNavigate(AppView.SCANNER)}
        />
      </div>
    </div>
  );
};

const DashboardCard: React.FC<{ 
  title: string; 
  description: string; 
  icon: React.ReactNode; 
  colorClass: string;
  shadowClass: string;
  onClick: () => void;
}> = ({ title, description, icon, colorClass, shadowClass, onClick }) => (
  <button 
    onClick={onClick}
    className="group relative bg-white dark:bg-zinc-800 rounded-[2rem] p-8 shadow-xl hover:shadow-2xl transition-all duration-500 border border-gray-100 dark:border-zinc-700 text-left overflow-hidden h-72 flex flex-col justify-between transform hover:-translate-y-2"
  >
    <div className={`absolute top-0 right-0 w-40 h-40 bg-gradient-to-br ${colorClass} opacity-10 rounded-bl-full group-hover:scale-150 transition-transform duration-700 ease-out`} />
    
    <div>
      <div className={`w-14 h-14 bg-gradient-to-br ${colorClass} rounded-2xl flex items-center justify-center text-white ${shadowClass} shadow-lg mb-6 group-hover:rotate-6 transition-transform duration-300`}>
        {icon}
      </div>
      
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{title}</h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 font-medium leading-relaxed">{description}</p>
    </div>
    
    <div className="flex items-center text-sm font-bold text-gray-900 dark:text-white group-hover:gap-3 transition-all">
      Open <ArrowRight size={18} className="ml-2" />
    </div>
  </button>
);

export default Dashboard;