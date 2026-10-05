export interface User {
  name: string;
  email: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: number;
}

export interface FoodItem {
  id: string;
  name: string;
  category: string;
  image: string;
  color: string;
  benefits: string;
  taste: string;
  calories: string;
  storageTips: string;
}

export interface ScanResult {
  id: string;
  timestamp: number;
  imageUrl: string;
  name: string;
  category: string;
  condition: 'Fresh' | 'Eatable' | 'Expired' | 'Spoiled';
  shelfLife: string;
  calories: string;
  confidence?: number;
  isSimulation?: boolean;
  source?: string;
  details?: string;
}

export type Theme = 'light' | 'dark';

export enum AppView {
  SPLASH,
  LOGIN,
  DASHBOARD,
  CHAT,
  SCANNER
}