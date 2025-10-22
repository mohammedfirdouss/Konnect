import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Wallet, CheckCircle, Loader2 } from 'lucide-react';
import { useUser } from '../contexts/UserContext';
import { toast } from 'sonner@2.0.3';

export function WalletCreation() {
  const navigate = useNavigate();
  const { user, setUser } = useUser();
  const [isCreating, setIsCreating] = useState(true);
  const [walletAddress, setWalletAddress] = useState('');
  const [step, setStep] = useState<'creating' | 'created'>('creating');

  useEffect(() => {
    if (!user?.name || !user?.email) {
      toast.error('Please complete your personal information first');
      navigate('/personal-info');
      return;
    }

    // Simulate wallet creation
    const createWallet = async () => {
      // Generate a mock Solana wallet address
      const chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
      let address = '';
      for (let i = 0; i < 44; i++) {
        address += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      
      // Simulate network delay
      setTimeout(() => {
        setWalletAddress(address);
        setStep('created');
        setIsCreating(false);

        // Update user with wallet address
        if (user) {
          setUser({
            ...user,
            walletAddress: address,
            balance: 0,
          });
        }
      }, 2500);
    };

    createWallet();
  }, []);

  const handleContinue = () => {
    toast.success('Account created successfully!');
    navigate('/home');
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6" style={{ backgroundColor: '#121212' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md text-center"
      >
        {/* Progress Indicator */}
        <div className="flex gap-2 mb-8">
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: '#9945FF' }} />
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: '#9945FF' }} />
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: '#9945FF' }} />
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: step === 'created' ? '#9945FF' : '#333333' }} />
        </div>

        {step === 'creating' ? (
          <>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              className="w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#1E1E1E', border: '2px solid #9945FF' }}
            >
              <Wallet size={40} style={{ color: '#9945FF' }} />
            </motion.div>

            <h2 className="mb-3" style={{ color: '#FFFFFF' }}>
              Creating Your Wallet
            </h2>
            <p className="mb-6" style={{ color: '#B3B3B3' }}>
              Generating your Solana wallet securely...
            </p>

            <div className="flex items-center justify-center gap-2">
              <Loader2 size={20} className="animate-spin" style={{ color: '#9945FF' }} />
              <span className="text-sm" style={{ color: '#9945FF' }}>
                Please wait
              </span>
            </div>
          </>
        ) : (
          <>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, type: 'spring' }}
              className="w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center"
              style={{ backgroundColor: '#4AFF99' }}
            >
              <CheckCircle size={48} style={{ color: '#121212' }} />
            </motion.div>

            <h2 className="mb-3" style={{ color: '#FFFFFF' }}>
              Wallet Created!
            </h2>
            <p className="mb-6" style={{ color: '#B3B3B3' }}>
              Your Solana wallet has been successfully created
            </p>

            {/* Wallet Info */}
            <div className="p-4 rounded-xl mb-8" style={{ backgroundColor: '#1E1E1E', border: '1px solid #333333' }}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
                  <Wallet size={24} style={{ color: '#FFFFFF' }} />
                </div>
                <div className="flex-1 text-left">
                  <p className="text-sm mb-1" style={{ color: '#B3B3B3' }}>
                    Wallet Address
                  </p>
                  <p className="text-xs break-all" style={{ color: '#FFFFFF' }}>
                    {walletAddress.substring(0, 8)}...{walletAddress.substring(walletAddress.length - 8)}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4" style={{ borderTop: '1px solid #333333' }}>
                <div>
                  <p className="text-xs mb-1" style={{ color: '#666666' }}>
                    SOL Balance
                  </p>
                  <p className="text-sm" style={{ color: '#FFFFFF' }}>
                    0.00 SOL
                  </p>
                </div>
                <div>
                  <p className="text-xs mb-1" style={{ color: '#666666' }}>
                    USDT Balance
                  </p>
                  <p className="text-sm" style={{ color: '#FFFFFF' }}>
                    ₦0.00
                  </p>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-lg mb-6" style={{ backgroundColor: 'rgba(255, 191, 0, 0.1)', border: '1px solid #FFBF00' }}>
              <p className="text-xs" style={{ color: '#FFBF00' }}>
                💡 Your wallet is secured on the Solana blockchain. Keep your credentials safe!
              </p>
            </div>

            <Button
              onClick={handleContinue}
              className="w-full"
              style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
            >
              Get Started
            </Button>
          </>
        )}
      </motion.div>
    </div>
  );
}
