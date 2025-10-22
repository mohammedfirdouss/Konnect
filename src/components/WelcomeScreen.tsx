import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { useIsMobile } from '../hooks/useIsMobile';
import { ShoppingBag, Wallet, Zap, Shield } from 'lucide-react';

export function WelcomeScreen() {
  const navigate = useNavigate();
  const { isMobile } = useIsMobile();
  const [hasAccount, setHasAccount] = useState(false);

  useEffect(() => {
    // Check if user has saved credentials (completed onboarding before)
    const savedCredentials = localStorage.getItem('konnect_credentials');
    setHasAccount(!!savedCredentials);
  }, []);

  const handleGetStarted = () => {
    navigate('/role');
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const features = [
    {
      icon: <ShoppingBag size={24} />,
      title: 'Buy & Sell',
      description: 'Trade goods and services securely with fellow students',
    },
    {
      icon: <Wallet size={24} />,
      title: 'Solana Wallet',
      description: 'Fast, secure blockchain payments with low fees',
    },
    {
      icon: <Shield size={24} />,
      title: 'Escrow Protection',
      description: 'Your funds are safe until delivery is confirmed',
    },
    {
      icon: <Zap size={24} />,
      title: 'Earn Rewards',
      description: 'Level up and earn points with every transaction',
    },
  ];

  return (
    <div 
      className="min-h-screen flex items-center justify-center px-6"
      style={{ backgroundColor: '#121212' }}
    >
      <div className={`w-full ${isMobile ? 'max-w-md' : 'max-w-7xl'}`}>
        <div className={isMobile ? 'text-center' : 'grid grid-cols-2 gap-16 items-center'}>
          {/* Left side - Hero Content */}
          <motion.div
            initial={{ opacity: 0, x: isMobile ? 0 : -20, y: isMobile ? 20 : 0 }}
            animate={{ opacity: 1, x: 0, y: 0 }}
            transition={{ duration: 0.6 }}
            className={isMobile ? '' : 'pr-8'}
          >
            <div className={isMobile ? 'mb-8' : 'mb-12'}>
              <div 
                className={`${isMobile ? 'w-24 h-24' : 'w-32 h-32'} mx-auto mb-6 rounded-3xl flex items-center justify-center`}
                style={{ backgroundColor: '#9945FF' }}
              >
                <svg 
                  width={isMobile ? '64' : '80'} 
                  height={isMobile ? '64' : '80'} 
                  viewBox="0 0 64 64" 
                  fill="none" 
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M32 8L8 20L32 32L56 20L32 8Z" fill="white" />
                  <path d="M8 28V44L32 56L56 44V28L32 40L8 28Z" fill="white" />
                </svg>
              </div>
              <h1 
                className={`mb-4 ${isMobile ? '' : 'text-6xl'}`}
                style={{ color: '#FFFFFF' }}
              >
                Welcome to Konnect
              </h1>
              <p 
                className={isMobile ? '' : 'text-xl'}
                style={{ color: '#B3B3B3' }}
              >
                Your Campus Economy Hub powered by Solana blockchain
              </p>
            </div>

            {!isMobile && (
              <div className="grid grid-cols-2 gap-6 mb-12">
                {features.map((feature, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 * index }}
                    className="flex items-start gap-3"
                  >
                    <div 
                      className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                      style={{ backgroundColor: 'rgba(153, 69, 255, 0.2)' }}
                    >
                      <div style={{ color: '#9945FF' }}>
                        {feature.icon}
                      </div>
                    </div>
                    <div>
                      <p className="mb-1" style={{ color: '#FFFFFF' }}>
                        {feature.title}
                      </p>
                      <p className="text-sm" style={{ color: '#666666' }}>
                        {feature.description}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
            
            <div className={`flex gap-3 ${isMobile ? 'flex-col' : 'flex-row'}`}>
              <Button
                onClick={handleGetStarted}
                className={`${isMobile ? 'w-full' : hasAccount ? 'flex-1' : ''}`}
                style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
              >
                Get Started
              </Button>
              {hasAccount && (
                <Button
                  onClick={handleLogin}
                  variant="outline"
                  className={`${isMobile ? 'w-full' : 'flex-1'}`}
                  style={{ borderColor: '#9945FF', color: '#9945FF' }}
                >
                  Sign In
                </Button>
              )}
            </div>

            {!isMobile && (
              <div className="mt-8">
                <p className="text-sm" style={{ color: '#666666' }}>
                  Trusted by students across campuses • Powered by Solana
                </p>
              </div>
            )}

            {!hasAccount && (
              <div className="mt-6 text-center">
                <p style={{ color: '#B3B3B3' }}>
                  Already have an account?{' '}
                  <button
                    onClick={handleLogin}
                    className="underline"
                    style={{ color: '#9945FF' }}
                  >
                    Sign in
                  </button>
                </p>
              </div>
            )}
          </motion.div>

          {/* Right side - Visual showcase (Desktop only) */}
          {!isMobile && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative"
            >
              <div className="relative">
                {/* Main phone mockup */}
                <div 
                  className="rounded-3xl p-6 mx-auto max-w-sm"
                  style={{ backgroundColor: '#1E1E1E', border: '2px solid #333333' }}
                >
                  <div className="space-y-4">
                    {/* Top bar */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-8 h-8 rounded-full"
                          style={{ backgroundColor: '#9945FF' }}
                        />
                        <span className="text-sm" style={{ color: '#FFFFFF' }}>Konnect</span>
                      </div>
                      <div 
                        className="px-3 py-1 rounded-full text-xs"
                        style={{ backgroundColor: 'rgba(74, 255, 153, 0.2)', color: '#4AFF99' }}
                      >
                        Active
                      </div>
                    </div>

                    {/* Balance card */}
                    <div 
                      className="p-4 rounded-xl"
                      style={{ background: 'linear-gradient(135deg, #9945FF 0%, #7F3DFF 100%)' }}
                    >
                      <p className="text-sm mb-2" style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                        Wallet Balance
                      </p>
                      <p className="text-3xl mb-3" style={{ color: '#FFFFFF' }}>
                        ₦45,000
                      </p>
                      <div className="flex gap-2">
                        <div 
                          className="px-3 py-1 rounded-lg text-xs flex-1 text-center"
                          style={{ backgroundColor: 'rgba(255, 255, 255, 0.2)', color: '#FFFFFF' }}
                        >
                          Deposit
                        </div>
                        <div 
                          className="px-3 py-1 rounded-lg text-xs flex-1 text-center"
                          style={{ backgroundColor: 'rgba(255, 255, 255, 0.2)', color: '#FFFFFF' }}
                        >
                          Send
                        </div>
                      </div>
                    </div>

                    {/* Recent activity */}
                    <div className="space-y-2">
                      <p className="text-xs" style={{ color: '#666666' }}>Recent Activity</p>
                      {[1, 2, 3].map((i) => (
                        <div 
                          key={i}
                          className="flex items-center justify-between p-3 rounded-lg"
                          style={{ backgroundColor: '#121212' }}
                        >
                          <div className="flex items-center gap-3">
                            <div 
                              className="w-10 h-10 rounded-lg"
                              style={{ backgroundColor: '#333333' }}
                            />
                            <div>
                              <p className="text-sm" style={{ color: '#FFFFFF' }}>
                                {i === 1 ? 'Textbook' : i === 2 ? 'Hoodie' : 'Airtime'}
                              </p>
                              <p className="text-xs" style={{ color: '#666666' }}>
                                Oct {22 - i}
                              </p>
                            </div>
                          </div>
                          <p className="text-sm" style={{ color: i === 1 ? '#4AFF99' : '#FFFFFF' }}>
                            {i === 1 ? '+' : '-'}₦{i === 1 ? '8,500' : i === 2 ? '12,000' : '1,000'}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Floating elements */}
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ duration: 3, repeat: Infinity }}
                  className="absolute -top-4 -right-4 px-4 py-3 rounded-xl"
                  style={{ backgroundColor: '#4AFF99', color: '#121212' }}
                >
                  <p className="text-xs">+50 pts</p>
                </motion.div>

                <motion.div
                  animate={{ y: [0, 10, 0] }}
                  transition={{ duration: 3, repeat: Infinity, delay: 1 }}
                  className="absolute -bottom-4 -left-4 px-4 py-3 rounded-xl"
                  style={{ backgroundColor: '#FFBF00', color: '#121212' }}
                >
                  <p className="text-xs">🔒 Escrow</p>
                </motion.div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
