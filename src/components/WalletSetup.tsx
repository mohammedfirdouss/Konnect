import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Wallet, Check } from 'lucide-react';
import { useUser } from '../contexts/UserContext';

export function WalletSetup() {
  const navigate = useNavigate();
  const { user, setUser } = useUser();
  const [step, setStep] = useState<'verify' | 'wallet'>('verify');
  const [otp, setOtp] = useState('');
  const [verified, setVerified] = useState(false);

  const handleVerifyOTP = () => {
    if (otp.length === 6) {
      setVerified(true);
      setTimeout(() => setStep('wallet'), 500);
    }
  };

  const handleContinue = () => {
    const mockWalletAddress = `SOL${Math.random().toString(36).substring(2, 15)}`;
    if (user) {
      setUser({ ...user, walletAddress: mockWalletAddress });
      navigate('/notifications');
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6" style={{ backgroundColor: '#121212' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        <div className="w-16 h-16 mx-auto mb-6 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
          <Wallet size={32} color="#FFFFFF" />
        </div>

        <h2 className="mb-3 text-center" style={{ color: '#FFFFFF' }}>
          {step === 'verify' ? 'Verify Phone Number' : 'Wallet Setup'}
        </h2>
        <p className="mb-8 text-center" style={{ color: '#B3B3B3' }}>
          {step === 'verify' 
            ? `Enter the OTP sent to ${user.phone}`
            : 'Your wallet has been created successfully'
          }
        </p>

        {step === 'verify' ? (
          <div className="space-y-6">
            <div>
              <Label htmlFor="otp" style={{ color: '#B3B3B3' }}>
                Enter OTP
              </Label>
              <Input
                id="otp"
                type="text"
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="000000"
                style={{ backgroundColor: '#1E1E1E', borderColor: '#333333', color: '#FFFFFF' }}
                className="mt-1.5 text-center tracking-widest"
              />
            </div>

            {verified && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center justify-center gap-2 p-3 rounded-lg"
                style={{ backgroundColor: '#4AFF99', color: '#121212' }}
              >
                <Check size={20} />
                <span>Phone verified successfully!</span>
              </motion.div>
            )}

            <Button
              onClick={handleVerifyOTP}
              disabled={otp.length !== 6}
              className="w-full"
              style={{ 
                backgroundColor: otp.length === 6 ? '#9945FF' : '#2A2A2A',
                color: otp.length === 6 ? '#FFFFFF' : '#666666'
              }}
            >
              Verify OTP
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="p-4 rounded-lg" style={{ backgroundColor: '#1E1E1E', border: '1px solid #333333' }}>
              <p className="text-sm mb-2" style={{ color: '#B3B3B3' }}>
                Wallet Address
              </p>
              <p className="break-all" style={{ color: '#FFFFFF' }}>
                SOL...{Math.random().toString(36).substring(2, 10)}
              </p>
            </div>

            <div className="p-4 rounded-lg" style={{ backgroundColor: '#1E1E1E', border: '1px solid #333333' }}>
              <p className="text-sm mb-2" style={{ color: '#B3B3B3' }}>
                Balance (NGN)
              </p>
              <p style={{ color: '#FFFFFF' }}>
                ₦0.00
              </p>
            </div>

            <div className="p-4 rounded-lg" style={{ backgroundColor: '#5AC8FA', color: '#121212' }}>
              <p className="text-sm">
                💡 Your Solana transactions are managed automatically in the background
              </p>
            </div>

            <Button
              onClick={handleContinue}
              className="w-full"
              style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
            >
              Continue to Marketplace
            </Button>
          </div>
        )}
      </motion.div>
    </div>
  );
}
