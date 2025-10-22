import { useNavigate, useLocation } from 'react-router-dom';
import { Home, ShoppingBag, ShoppingCart, CreditCard, FileText, Trophy, Package, User, LogOut } from 'lucide-react';
import { useUser } from '../contexts/UserContext';

export function DesktopSidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useUser();

  if (!user) return null;

  const isSeller = user.role === 'seller' || user.role === 'both';

  const navItems = [
    {
      id: 'home',
      icon: Home,
      label: 'Home',
      path: '/home',
    },
    {
      id: 'marketplace',
      icon: isSeller ? Package : ShoppingBag,
      label: isSeller ? 'My Listings' : 'Marketplace',
      path: '/marketplace',
    },
    {
      id: 'cart',
      icon: isSeller ? Package : ShoppingCart,
      label: isSeller ? 'My Orders' : 'Cart',
      path: '/cart',
    },
    {
      id: 'wallet',
      icon: CreditCard,
      label: 'Wallet',
      path: '/wallet',
    },
    {
      id: 'bills',
      icon: FileText,
      label: 'Bills',
      path: '/bills',
    },
    {
      id: 'gamification',
      icon: Trophy,
      label: 'Rewards',
      path: '/gamification',
    },
  ];

  const handleLogout = () => {
    localStorage.removeItem('konnect_user');
    navigate('/');
  };

  return (
    <div
      className="fixed left-0 top-0 bottom-0 w-64 flex flex-col"
      style={{ backgroundColor: '#1E1E1E', borderRight: '1px solid #333333' }}
    >
      {/* Logo/Brand */}
      <div className="p-6 border-b" style={{ borderColor: '#333333' }}>
        <h2 style={{ color: '#9945FF' }}>Konnect</h2>
        <p className="text-sm mt-1" style={{ color: '#B3B3B3' }}>
          Campus Marketplace
        </p>
      </div>

      {/* User Profile */}
      <div className="p-4 border-b" style={{ borderColor: '#333333' }}>
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ backgroundColor: '#9945FF' }}
          >
            <User size={20} style={{ color: '#FFFFFF' }} />
          </div>
          <div className="flex-1">
            <p className="text-sm" style={{ color: '#FFFFFF' }}>
              {user.name}
            </p>
            <p className="text-xs" style={{ color: '#B3B3B3' }}>
              {user.role === 'both' ? 'Buyer & Seller' : user.role === 'seller' ? 'Seller' : 'Buyer'}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <button
              key={item.id}
              onClick={() => navigate(item.path)}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all"
              style={{
                backgroundColor: isActive ? '#9945FF' : 'transparent',
                color: isActive ? '#FFFFFF' : '#B3B3B3',
              }}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t space-y-2" style={{ borderColor: '#333333' }}>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all"
          style={{ color: '#FF4D4D' }}
        >
          <LogOut size={20} />
          <span>Log Out</span>
        </button>
        <div className="px-4 py-2">
          <p className="text-xs" style={{ color: '#666666' }}>
            Konnect v1.0.0
          </p>
          <p className="text-xs" style={{ color: '#666666' }}>
            Powered by Solana
          </p>
        </div>
      </div>
    </div>
  );
}
