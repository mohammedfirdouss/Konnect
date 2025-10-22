import { Home, ShoppingBag, ShoppingCart, CreditCard, FileText, Trophy, Package } from 'lucide-react';

type TabType = 'home' | 'marketplace' | 'cart' | 'wallet' | 'bills' | 'gamification';
type UserRole = 'buyer' | 'seller' | 'both' | null;

interface BottomNavProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  userRole: UserRole;
}

export function BottomNav({ activeTab, onTabChange, userRole }: BottomNavProps) {
  const isSeller = userRole === 'seller' || userRole === 'both';

  const tabs = [
    {
      id: 'home' as TabType,
      icon: Home,
      label: 'Home',
    },
    {
      id: 'marketplace' as TabType,
      icon: isSeller ? Package : ShoppingBag,
      label: isSeller ? 'My Listings' : 'Marketplace',
    },
    {
      id: 'cart' as TabType,
      icon: isSeller ? Package : ShoppingCart,
      label: isSeller ? 'My Orders' : 'Cart',
    },
    {
      id: 'wallet' as TabType,
      icon: CreditCard,
      label: 'Wallet',
    },
    {
      id: 'bills' as TabType,
      icon: FileText,
      label: 'Bills',
    },
    {
      id: 'gamification' as TabType,
      icon: Trophy,
      label: 'Rewards',
    },
  ];

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-50 px-2 py-2"
      style={{ backgroundColor: '#121212', borderTop: '1px solid #333333' }}
    >
      <div className="flex items-center justify-around">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className="flex flex-col items-center gap-1 py-2 px-3 rounded-lg transition-all"
              style={{
                color: isActive ? '#9945FF' : '#B3B3B3',
              }}
            >
              <Icon size={22} />
              <span className="text-xs">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
