import React from 'react';
import { User, AppView, Theme } from '../types';
import { Moon, Sun, LogOut, ArrowLeft, User as UserIcon } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  user: User | null;
  currentView: AppView;
  onNavigate: (view: AppView) => void;
  onLogout: () => void;
  theme: Theme;
  toggleTheme: () => void;
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  user, 
  currentView, 
  onNavigate, 
  onLogout,
  theme,
  toggleTheme
}) => {
  const isDashboard = currentView === AppView.DASHBOARD;
  const isAuth = currentView === AppView.LOGIN || currentView === AppView.SPLASH;

  // Ensure "dark" class is applied to a wrapper if theme is dark, so child "dark:" modifiers work.
  // Explicitly set text colors: text-gray-900 (Black) for light, text-white for dark.

  if (isAuth) {
    return (
      <div className={theme === 'dark' ? 'dark' : ''}>
        <main className="min-h-screen bg-gradient-to-br from-brand-50 to-white dark:from-zinc-900 dark:to-zinc-800 text-gray-900 dark:text-white transition-colors duration-300">
          {children}
        </main>
      </div>
    );
  }

  return (
    <div className={`min-h-screen flex flex-col transition-colors duration-300 ${theme === 'dark' ? 'dark bg-zinc-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-zinc-800/80 backdrop-blur-xl shadow-sm border-b border-gray-200 dark:border-zinc-700 px-4 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            {!isDashboard && (
              <button 
                onClick={() => onNavigate(AppView.DASHBOARD)}
                className="p-2 -ml-2 rounded-full hover:bg-gray-100 dark:hover:bg-zinc-700 transition text-gray-600 dark:text-gray-300"
                aria-label="Back to Dashboard"
              >
                <ArrowLeft size={22} />
              </button>
            )}
            <h1 
              onClick={() => onNavigate(AppView.DASHBOARD)}
              className="text-2xl font-extrabold bg-gradient-to-r from-green-600 to-lime-500 bg-clip-text text-transparent cursor-pointer tracking-tight"
            >
              SmartFood AI
            </h1>
          </div>

          <div className="flex items-center gap-3 sm:gap-4">
            {user && (
              <div className="flex items-center gap-2 mr-2">
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  {user.name}
                </span>
              </div>
            )}
            
            <button 
              onClick={toggleTheme}
              className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-zinc-700 transition text-gray-600 dark:text-gray-300"
              aria-label="Toggle Theme"
            >
              {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
            </button>

            <button 
              onClick={onLogout}
              className="p-2 sm:px-4 sm:py-2 flex items-center gap-2 text-sm font-semibold text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition"
              title="Sign Out"
            >
              <LogOut size={20} />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 w-full max-w-7xl mx-auto p-4 md:p-8 animate-fade-in text-gray-900 dark:text-white">
        {children}
      </main>
    </div>
  );
};

export default Layout;