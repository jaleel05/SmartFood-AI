import React, { useState } from 'react';
import { User } from '../types';
import { Leaf, Lock, Mail, User as UserIcon, CheckCircle2 } from 'lucide-react';

interface LoginProps {
  onLogin: (user: User) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Strict Email Validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address.');
      return;
    }

    // Strict Password Validation (At least 4 chars)
    if (password.length < 4) {
      setError('Password must be at least 4 characters long.');
      return;
    }

    if (name.trim().length === 0) {
      setError('Please enter your full name.');
      return;
    }

    onLogin({ name, email });
  };

  return (
    <div className="flex items-center justify-center min-h-screen px-4 py-12" style={{ backgroundImage: 'url(https://san-j.com/wp-content/uploads/2024/02/01-healthiest-fruits-vegetables-REV02.jpg)', backgroundSize: 'cover', backgroundPosition: 'center', backgroundRepeat: 'no-repeat' }}>
      <div className="w-full max-w-md bg-white dark:bg-zinc-800 rounded-3xl shadow-2xl p-8 border border-white/20 dark:border-zinc-700 backdrop-blur-xl">
        <div className="flex flex-col items-center mb-10">
          <div className="w-20 h-20 bg-gradient-to-tr from-brand-100 to-green-100 dark:from-green-900/40 dark:to-emerald-900/40 rounded-full flex items-center justify-center mb-6 shadow-lg shadow-green-500/20 text-brand-600 dark:text-brand-400">
            <Leaf size={40} className="drop-shadow-sm" />
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Welcome Back</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-2">Sign in to SmartFood AI</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/50 text-red-600 dark:text-red-400 p-4 rounded-xl text-sm font-medium text-center animate-shake">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div className="relative group">
              <UserIcon className="absolute left-4 top-4 text-gray-400 group-focus-within:text-brand-500 transition-colors" size={20} />
              <input
                type="text"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full pl-12 pr-4 py-3.5 bg-gray-50 dark:bg-zinc-900 border border-gray-200 dark:border-zinc-700 rounded-xl focus:ring-4 focus:ring-brand-500/20 focus:border-brand-500 outline-none text-gray-900 dark:text-white transition-all font-medium placeholder-gray-400"
              />
            </div>

            <div className="relative group">
              <Mail className="absolute left-4 top-4 text-gray-400 group-focus-within:text-brand-500 transition-colors" size={20} />
              <input
                type="email"
                placeholder="Email Address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-12 pr-4 py-3.5 bg-gray-50 dark:bg-zinc-900 border border-gray-200 dark:border-zinc-700 rounded-xl focus:ring-4 focus:ring-brand-500/20 focus:border-brand-500 outline-none text-gray-900 dark:text-white transition-all font-medium placeholder-gray-400"
              />
            </div>

            <div className="relative group">
              <Lock className="absolute left-4 top-4 text-gray-400 group-focus-within:text-brand-500 transition-colors" size={20} />
              <input
                type="password"
                placeholder="Password (min. 4 chars)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-12 pr-4 py-3.5 bg-gray-50 dark:bg-zinc-900 border border-gray-200 dark:border-zinc-700 rounded-xl focus:ring-4 focus:ring-brand-500/20 focus:border-brand-500 outline-none text-gray-900 dark:text-white transition-all font-medium placeholder-gray-400"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-gradient-to-r from-brand-600 to-green-600 hover:from-brand-700 hover:to-green-700 text-white font-bold py-4 rounded-xl transition-all transform active:scale-[0.98] shadow-lg shadow-brand-500/30 flex items-center justify-center gap-2"
          >
            <span>Sign In Securely</span>
            <CheckCircle2 size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;