import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Wallet, CheckCircle, Loader2, Eye, EyeOff } from 'lucide-react';
import { useUser } from '../contexts/UserContext';
import { toast } from 'sonner@2.0.3';

export function WalletCreation() {
  const navigate = useNavigate();
  const { user, setUser, setHasCompletedOnboarding } = useUser();
  const [isCreating, setIsCreating] = useState(true);
  const [walletAddress, setWalletAddress] = useState('');
  const [step, setStep] = useState<'creating' | 'created' | 'password'>('creating');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

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
            balance: 50000, // Starting balance
            gamificationPoints: 0,
            level: 1,
          });
        }
      }, 2500);
    };

    createWallet();
  }, []);

  const handleContinueToPassword = () => {
    setStep('password');
  };

  const handleCreateAccount = () => {
    if (!password || !confirmPassword) {
      toast.error('Please enter and confirm your password');
      return;
    }

    if (password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    // Save credentials to localStorage
    if (user) {
      const credentials = {
        email: user.email,
        password: password, // In production, this should be hashed
      };
      localStorage.setItem('konnect_credentials', JSON.stringify(credentials));
      
      // Mark onboarding as completed
      setHasCompletedOnboarding(true);
      
      toast.success('Account created successfully!');
      navigate('/home');
    }
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
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: step === 'password' || step === 'created' ? '#9945FF' : '#333333' }} />
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
        ) : step === 'created' ? (
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
                    Starting Balance
                  </p>
                  <p className="text-sm" style={{ color: '#FFFFFF' }}>
                    ₦50,000
                  </p>
                </div>
                <div>
                  <p className="text-xs mb-1" style={{ color: '#666666' }}>
                    SOL Balance
                  </p>
                  <p className="text-sm" style={{ color: '#FFFFFF' }}>
                    1.00 SOL
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
              onClick={handleContinueToPassword}
              className="w-full"
              style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
            >
              Continue
            </Button>
          </>
        ) : (
          <>
            <div className="w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
              <Wallet size={40} style={{ color: '#FFFFFF' }} />
            </div>

            <h2 className="mb-3" style={{ color: '#FFFFFF' }}>
              Secure Your Account
            </h2>
            <p className="mb-6" style={{ color: '#B3B3B3' }}>
              Create a password to protect your account
            </p>

            <div className="space-y-4 text-left mb-6">
              <div>
                <Label style={{ color: '#B3B3B3' }}>Create Password</Label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter password (min. 6 characters)"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={{
                      backgroundColor: '#1E1E1E',
                      borderColor: '#333333',
                      color: '#FFFFFF',
                      paddingRight: '48px',
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2"
                  >
                    {showPassword ? (
                      <EyeOff size={20} style={{ color: '#666666' }} />
                    ) : (
                      <Eye size={20} style={{ color: '#666666' }} />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <Label style={{ color: '#B3B3B3' }}>Confirm Password</Label>
                <div className="relative">
                  <Input
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="Re-enter password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    style={{
                      backgroundColor: '#1E1E1E',
                      borderColor: '#333333',
                      color: '#FFFFFF',
                      paddingRight: '48px',
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2"
                  >
                    {showConfirmPassword ? (
                      <EyeOff size={20} style={{ color: '#666666' }} />
                    ) : (
                      <Eye size={20} style={{ color: '#666666' }} />
                    )}
                  </button>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-lg mb-6" style={{ backgroundColor: 'rgba(90, 200, 250, 0.1)', borderLeft: '3px solid #5AC8FA' }}>
              <p className="text-xs text-left" style={{ color: '#B3B3B3' }}>
                🔐 Use this password to sign in to your account. Make sure to remember it!
              </p>
            </div>

            <Button
              onClick={handleCreateAccount}
              className="w-full"
              style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
            >
              Create Account
            </Button>
          </>
        )}
      </motion.div>
    </div>
  );
}
