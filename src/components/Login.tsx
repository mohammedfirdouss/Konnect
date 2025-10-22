import { useState } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Eye, EyeOff } from 'lucide-react';
import { useUser } from '../contexts/UserContext';
import { toast } from 'sonner@2.0.3';
import { useIsMobile } from '../hooks/useIsMobile';

export function Login() {
  const navigate = useNavigate();
  const { setUser } = useUser();
  const { isMobile } = useIsMobile();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      toast.error('Please enter your email and password');
      return;
    }

    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      // Check if user exists in localStorage
      const savedCredentials = localStorage.getItem('konnect_credentials');
      
      if (savedCredentials) {
        try {
          const credentials = JSON.parse(savedCredentials);
          
          if (credentials.email === email && credentials.password === password) {
            // Load user data
            const savedUser = localStorage.getItem('konnect_user');
            if (savedUser) {
              setUser(JSON.parse(savedUser));
              toast.success('Welcome back!');
              navigate('/home');
            }
          } else {
            toast.error('Invalid email or password');
          }
        } catch (e) {
          toast.error('Login failed. Please try again.');
        }
      } else {
        toast.error('No account found. Please sign up first.');
      }
      
      setIsLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center px-6"
      style={{ backgroundColor: '#121212' }}
    >
      <div className={`w-full ${isMobile ? 'max-w-md' : 'max-w-6xl'}`}>
        <div className={isMobile ? '' : 'grid grid-cols-2 gap-12 items-center'}>
          {/* Left side - Branding (Desktop only) */}
          {!isMobile && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="mb-8">
                <div 
                  className="w-32 h-32 mb-6 rounded-3xl flex items-center justify-center"
                  style={{ backgroundColor: '#9945FF' }}
                >
                  <svg width="80" height="80" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M32 8L8 20L32 32L56 20L32 8Z" fill="white" />
                    <path d="M8 28V44L32 56L56 44V28L32 40L8 28Z" fill="white" />
                  </svg>
                </div>
                <h1 className="mb-4 text-5xl" style={{ color: '#FFFFFF' }}>
                  Welcome back to Konnect
                </h1>
                <p className="text-xl" style={{ color: '#B3B3B3' }}>
                  Your Campus Economy Hub powered by Solana
                </p>
              </div>
              
              <div className="space-y-4 mt-8">
                <div className="flex items-start gap-3">
                  <div 
                    className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: 'rgba(153, 69, 255, 0.2)' }}
                  >
                    🔒
                  </div>
                  <div>
                    <p style={{ color: '#FFFFFF' }}>Secure Escrow Payments</p>
                    <p className="text-sm" style={{ color: '#666666' }}>
                      Your funds are protected until delivery
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div 
                    className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: 'rgba(153, 69, 255, 0.2)' }}
                  >
                    ⚡
                  </div>
                  <div>
                    <p style={{ color: '#FFFFFF' }}>Instant Transactions</p>
                    <p className="text-sm" style={{ color: '#666666' }}>
                      Fast blockchain-powered payments
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div 
                    className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: 'rgba(153, 69, 255, 0.2)' }}
                  >
                    🎯
                  </div>
                  <div>
                    <p style={{ color: '#FFFFFF' }}>Gamified Experience</p>
                    <p className="text-sm" style={{ color: '#666666' }}>
                      Earn rewards and level up as you trade
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Right side - Login Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="w-full"
          >
            {/* Mobile logo */}
            {isMobile && (
              <div className="text-center mb-8">
                <div 
                  className="w-20 h-20 mx-auto mb-4 rounded-3xl flex items-center justify-center"
                  style={{ backgroundColor: '#9945FF' }}
                >
                  <svg width="48" height="48" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M32 8L8 20L32 32L56 20L32 8Z" fill="white" />
                    <path d="M8 28V44L32 56L56 44V28L32 40L8 28Z" fill="white" />
                  </svg>
                </div>
                <h2 style={{ color: '#FFFFFF' }}>Welcome back</h2>
                <p style={{ color: '#B3B3B3' }}>Sign in to your account</p>
              </div>
            )}

            {!isMobile && (
              <div className="mb-8">
                <h2 className="mb-2 text-3xl" style={{ color: '#FFFFFF' }}>Sign in</h2>
                <p style={{ color: '#B3B3B3' }}>Enter your credentials to continue</p>
              </div>
            )}

            <div className="space-y-5">
              <div>
                <Label style={{ color: '#B3B3B3' }}>Email</Label>
                <Input
                  type="email"
                  placeholder="your.email@university.edu"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onKeyPress={handleKeyPress}
                  style={{
                    backgroundColor: '#1E1E1E',
                    borderColor: '#333333',
                    color: '#FFFFFF',
                  }}
                />
              </div>

              <div>
                <Label style={{ color: '#B3B3B3' }}>Password</Label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onKeyPress={handleKeyPress}
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

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded"
                    style={{ accentColor: '#9945FF' }}
                  />
                  <span className="text-sm" style={{ color: '#B3B3B3' }}>
                    Remember me
                  </span>
                </label>
                <button
                  type="button"
                  className="text-sm"
                  style={{ color: '#9945FF' }}
                  onClick={() => toast.info('Password reset coming soon!')}
                >
                  Forgot password?
                </button>
              </div>

              <Button
                onClick={handleLogin}
                disabled={isLoading}
                className="w-full"
                style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </Button>

              <div className="text-center">
                <p style={{ color: '#B3B3B3' }}>
                  Don't have an account?{' '}
                  <button
                    type="button"
                    onClick={() => navigate('/register')}
                    style={{ color: '#9945FF' }}
                  >
                    Sign up
                  </button>
                </p>
              </div>
            </div>

            {/* Security notice */}
            <div 
              className="mt-6 p-4 rounded-lg"
              style={{ backgroundColor: 'rgba(90, 200, 250, 0.1)', borderLeft: '3px solid #5AC8FA' }}
            >
              <p className="text-sm" style={{ color: '#B3B3B3' }}>
                🔐 Your account is protected with Solana blockchain security
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
