import React, { useState, useEffect } from 'react';
import { User, AppView, Theme } from './types';
import Login from './components/Login';
import SplashScreen from './components/SplashScreen';
import Dashboard from './components/Dashboard';
import Chatbot from './components/Chatbot';
import Scanner from './components/Scanner';
import Layout from './components/Layout';

const App: React.FC = () => {
  // App State
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  
  const [view, setView] = useState<AppView>(() => {
    return localStorage.getItem('user') ? AppView.DASHBOARD : AppView.LOGIN;
  });

  const [theme, setTheme] = useState<Theme>('light');

  // Handle splash screen logic on initial login
  useEffect(() => {
    if (user && view === AppView.LOGIN) {
      setView(AppView.SPLASH);
    }
  }, [user]);

  // Handle Login
  const handleLogin = (newUser: User) => {
    localStorage.setItem('user', JSON.stringify(newUser));
    setUser(newUser);
    setView(AppView.SPLASH);
  };

  // Handle Logout
  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    setView(AppView.LOGIN);
    localStorage.removeItem('chatHistory');
    localStorage.removeItem('scanHistory');
  };

  // Theme Toggle
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const renderView = () => {
    switch (view) {
      case AppView.LOGIN:
        return <Login onLogin={handleLogin} />;
      case AppView.SPLASH:
        return <SplashScreen onFinish={() => setView(AppView.DASHBOARD)} />;
      case AppView.DASHBOARD:
        return <Dashboard onNavigate={setView} />;
      case AppView.CHAT:
        return <Chatbot />;
      case AppView.SCANNER:
        return <Scanner />;
      default:
        return <Dashboard onNavigate={setView} />;
    }
  };

  return (
    <Layout 
      user={user} 
      currentView={view} 
      onNavigate={setView} 
      onLogout={handleLogout}
      theme={theme}
      toggleTheme={toggleTheme}
    >
      {renderView()}
    </Layout>
  );
};

export default App;