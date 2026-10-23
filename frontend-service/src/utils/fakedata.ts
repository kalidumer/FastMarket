import {Product,Category} from '../types/productType';

export const MOCK_CATEGORIES: Category[] = [
  { id: 'cat-1', name: 'Electronics', image: 'https://images.unsplash.com/photo-1498049794561-7780e7231661?auto=format&fit=crop&q=80&w=400', itemCount: 120 },
  { id: 'cat-2', name: 'Fashion', image: 'https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&q=80&w=400', itemCount: 350 },
  { id: 'cat-3', name: 'Home & Kitchen', image: 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&q=80&w=400', itemCount: 85 },
  { id: 'cat-4', name: 'Sports & Fitness', image: 'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&q=80&w=400', itemCount: 210 },
];

export const MOCK_PRODUCTS: Product[] = [
  { id: 'p-1', title: 'Wireless Noise-Canceling Headphones', desc: 'Experience crystal-clear sound with our wireless noise-canceling headphones.', price: 299.99, rating: 4.8, reviewCount: 128, image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=600', category: 'Electronics', isNew: true },
  { id: 'p-2', title: 'Minimalist Mechanical Keyboard', desc:'Experience the perfect blend of style and functionality with our minimalist mechanical keyboard.',price: 149.50, rating: 4.7, reviewCount: 89, image: 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&q=80&w=600', category: 'Electronics',isNew: false },
  { id: 'p-3', title: 'Ergonomic Office Desk Chair', desc: 'Enhance your workspace with our ergonomically designed office desk chair.', price: 220.00, rating: 4.5, reviewCount: 64, image: 'https://images.unsplash.com/photo-1580481072645-022f9a6d1270?auto=format&fit=crop&q=80&w=600', category: 'Home & Kitchen', isNew: false },
  { id: 'p-4', title: 'Smart Fitness Companion Watch', desc: 'Stay connected and track your fitness goals with our smart fitness companion watch.', price: 199.00, rating: 4.9, reviewCount: 210, image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=600', category: 'Sports & Fitness', isNew: true },
];