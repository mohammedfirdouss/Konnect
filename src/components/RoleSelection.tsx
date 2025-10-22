import { motion } from 'motion/react';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag, Store } from 'lucide-react';
import { useUser, UserRole } from '../contexts/UserContext';

export function RoleSelection() {
  const navigate = useNavigate();
  const { user, setUser } = useUser();

  const handleRoleSelect = (role: UserRole) => {
    // Create a temporary user object with the selected role
    setUser({
      name: '',
      email: '',
      phone: '',
      role,
      walletAddress: '',
      balance: 0,
    });
    navigate('/personal-info');
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6" style={{ backgroundColor: '#121212' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        <h2 className="mb-3 text-center" style={{ color: '#FFFFFF' }}>
          Choose Your Role
        </h2>
        <p className="mb-6 text-center" style={{ color: '#B3B3B3' }}>
          Select how you want to use Konnect
        </p>

        {/* Progress Indicator */}
        <div className="flex gap-2 mb-8">
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: '#9945FF' }} />
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: '#333333' }} />
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: '#333333' }} />
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: '#333333' }} />
        </div>

        <div className="space-y-4">
          <button
            onClick={() => handleRoleSelect('buyer')}
            className="w-full p-6 rounded-xl flex items-center gap-4 transition-all hover:scale-[1.02]"
            style={{ backgroundColor: '#1E1E1E', border: '1px solid #333333' }}
          >
            <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
              <ShoppingBag size={24} color="#FFFFFF" />
            </div>
            <div className="text-left flex-1">
              <h3 className="mb-1" style={{ color: '#FFFFFF' }}>
                Buyer
              </h3>
              <p className="text-sm" style={{ color: '#B3B3B3' }}>
                Browse and purchase goods & services
              </p>
            </div>
          </button>

          <button
            onClick={() => handleRoleSelect('seller')}
            className="w-full p-6 rounded-xl flex items-center gap-4 transition-all hover:scale-[1.02]"
            style={{ backgroundColor: '#1E1E1E', border: '1px solid #333333' }}
          >
            <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
              <Store size={24} color="#FFFFFF" />
            </div>
            <div className="text-left flex-1">
              <h3 className="mb-1" style={{ color: '#FFFFFF' }}>
                Seller
              </h3>
              <p className="text-sm" style={{ color: '#B3B3B3' }}>
                List and sell your goods & services
              </p>
            </div>
          </button>

          <button
            onClick={() => handleRoleSelect('both')}
            className="w-full p-6 rounded-xl flex items-center gap-4 transition-all hover:scale-[1.02]"
            style={{ backgroundColor: '#1E1E1E', border: '1px solid #333333' }}
          >
            <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
              <div className="flex">
                <ShoppingBag size={16} color="#FFFFFF" />
                <Store size={16} color="#FFFFFF" className="ml-0.5" />
              </div>
            </div>
            <div className="text-left flex-1">
              <h3 className="mb-1" style={{ color: '#FFFFFF' }}>
                Both
              </h3>
              <p className="text-sm" style={{ color: '#B3B3B3' }}>
                Buy and sell on the platform
              </p>
            </div>
          </button>
        </div>
      </motion.div>
    </div>
  );
}
