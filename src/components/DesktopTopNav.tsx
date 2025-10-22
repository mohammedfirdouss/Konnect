import { useNavigate, useLocation } from 'react-router-dom';
import { Search, ShoppingCart, Bell, User, ChevronDown } from 'lucide-react';
import { Input } from './ui/input';
import { useUser } from '../contexts/UserContext';
import { useCart } from '../contexts/CartContext';
import { useState } from 'react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';

interface DesktopTopNavProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export function DesktopTopNav({ searchQuery, onSearchChange }: DesktopTopNavProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useUser();
  const { getCartCount } = useCart();

  if (!user) return null;

  const cartCount = getCartCount();

  const navItems = [
    { label: 'Home', path: '/home' },
    { label: 'Marketplace', path: '/marketplace' },
    { label: 'Wallet', path: '/wallet' },
    { label: 'Bills', path: '/bills' },
    { label: 'Rewards', path: '/gamification' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('konnect_user');
    navigate('/');
  };

  return (
    <div
      className="fixed top-0 left-0 right-0 z-50"
      style={{ backgroundColor: '#121212', borderBottom: '1px solid #333333' }}
    >
      <div className="px-6 py-3">
        {/* Top Row: Logo, Search, Cart, Notifications, Profile */}
        <div className="flex items-center gap-6 mb-3">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: '#9945FF' }}
            >
              <span className="text-lg">K</span>
            </div>
            <h3 style={{ color: '#9945FF' }}>Konnect</h3>
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-2xl relative">
            <Input
              type="text"
              placeholder="Search for products, services, and more..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full pl-4 pr-10"
              style={{
                backgroundColor: '#1E1E1E',
                borderColor: '#333333',
                color: '#FFFFFF',
              }}
            />
            <Search
              size={20}
              className="absolute right-3 top-1/2 -translate-y-1/2"
              style={{ color: '#666666' }}
            />
          </div>

          {/* Cart Icon */}
          <button
            onClick={() => navigate('/cart')}
            className="p-2 rounded-lg relative hover:bg-opacity-10 transition-all"
            style={{ color: '#FFFFFF' }}
          >
            <ShoppingCart size={24} />
            {cartCount > 0 && (
              <div
                className="absolute top-0 right-0 w-5 h-5 rounded-full flex items-center justify-center text-xs"
                style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
              >
                {cartCount}
              </div>
            )}
          </button>

          {/* Notifications */}
          <button className="p-2 rounded-lg relative" style={{ color: '#FFFFFF' }}>
            <Bell size={24} />
            <div
              className="absolute top-1 right-1 w-2 h-2 rounded-full"
              style={{ backgroundColor: '#FF4D4D' }}
            />
          </button>

          {/* User Profile Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="flex items-center gap-2 px-3 py-2 rounded-lg transition-all"
                style={{ color: '#FFFFFF', backgroundColor: '#1E1E1E' }}
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: '#9945FF' }}
                >
                  <User size={16} />
                </div>
                <span className="text-sm">{user.name}</span>
                <ChevronDown size={16} />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}
            >
              <DropdownMenuItem
                style={{ color: '#FFFFFF' }}
                onClick={() => navigate('/wallet')}
              >
                My Wallet
              </DropdownMenuItem>
              <DropdownMenuItem
                style={{ color: '#FFFFFF' }}
                onClick={() => navigate('/gamification')}
              >
                My Rewards
              </DropdownMenuItem>
              <DropdownMenuItem style={{ color: '#FFFFFF' }}>
                Account Settings
              </DropdownMenuItem>
              <DropdownMenuItem
                style={{ color: '#FF4D4D' }}
                onClick={handleLogout}
              >
                Log Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Bottom Row: Navigation Links */}
        <div className="flex items-center gap-6 border-t pt-3" style={{ borderColor: '#333333' }}>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className="px-3 py-1 rounded transition-all"
                style={{
                  color: isActive ? '#9945FF' : '#B3B3B3',
                  borderBottom: isActive ? '2px solid #9945FF' : '2px solid transparent',
                }}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
