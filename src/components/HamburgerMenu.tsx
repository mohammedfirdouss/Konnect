import { motion, AnimatePresence } from 'motion/react';
import { useNavigate } from 'react-router-dom';
import { X, User, Shield, History, Bot, HelpCircle, Share2, FileText, LogOut } from 'lucide-react';

interface HamburgerMenuUser {
  name: string;
  email: string;
  phone: string;
  role: 'buyer' | 'seller' | 'both' | null;
}

interface HamburgerMenuProps {
  isOpen: boolean;
  onClose: () => void;
  user: HamburgerMenuUser;
}

export function HamburgerMenu({ isOpen, onClose, user }: HamburgerMenuProps) {
  const navigate = useNavigate();
  
  const menuItems = [
    { icon: User, label: 'Account Settings', color: '#9945FF' },
    { icon: Shield, label: 'Escrow Management', color: '#9945FF' },
    { icon: History, label: 'Transaction History', color: '#9945FF' },
    { icon: Bot, label: 'AI Assistant', color: '#9945FF' },
    { icon: HelpCircle, label: 'Help / FAQ', color: '#9945FF' },
    { icon: Share2, label: 'Referral Program', color: '#9945FF' },
    { icon: FileText, label: 'Terms & Privacy', color: '#B3B3B3' },
    { icon: LogOut, label: 'Log Out', color: '#FF4D4D' },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50"
            style={{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }}
          />
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'tween', duration: 0.3 }}
            className="fixed top-0 left-0 bottom-0 z-50 w-[85%] max-w-sm overflow-y-auto"
            style={{ backgroundColor: '#1E1E1E' }}
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h3 style={{ color: '#FFFFFF' }}>{user.name}</h3>
                  <p className="text-sm" style={{ color: '#B3B3B3' }}>
                    {user.email}
                  </p>
                  <div
                    className="inline-block mt-2 px-3 py-1 rounded-full text-xs"
                    style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
                  >
                    {user.role === 'both' ? 'Buyer & Seller' : user.role === 'seller' ? 'Seller' : 'Buyer'}
                  </div>
                </div>
                <button onClick={onClose} style={{ color: '#FFFFFF' }}>
                  <X size={24} />
                </button>
              </div>

              <nav className="space-y-2">
                {menuItems.map((item, index) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={index}
                      className="w-full flex items-center gap-4 p-4 rounded-lg transition-all hover:bg-opacity-50"
                      style={{ backgroundColor: 'transparent' }}
                      onClick={() => {
                        if (item.label === 'Log Out') {
                          localStorage.removeItem('konnect_user');
                          navigate('/');
                        }
                      }}
                    >
                      <Icon size={22} style={{ color: item.color }} />
                      <span style={{ color: '#FFFFFF' }}>{item.label}</span>
                    </button>
                  );
                })}
              </nav>

              <div
                className="mt-8 p-4 rounded-lg"
                style={{ backgroundColor: '#121212' }}
              >
                <p className="text-sm" style={{ color: '#B3B3B3' }}>
                  Konnect v1.0.0
                </p>
                <p className="text-xs mt-1" style={{ color: '#666666' }}>
                  Powered by Solana
                </p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
