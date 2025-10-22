import { motion } from 'motion/react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';

export function WelcomeScreen() {
  const navigate = useNavigate();

  const handleContinue = () => {
    navigate('/role');
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6" style={{ backgroundColor: '#121212' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center"
      >
        <div className="mb-8">
          <div className="w-24 h-24 mx-auto mb-6 rounded-3xl flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M32 8L8 20L32 32L56 20L32 8Z" fill="white" />
              <path d="M8 28V44L32 56L56 44V28L32 40L8 28Z" fill="white" />
            </svg>
          </div>
          <h1 className="mb-3" style={{ color: '#FFFFFF' }}>
            Welcome to Konnect
          </h1>
          <p style={{ color: '#B3B3B3' }}>
            Your Campus Economy Hub
          </p>
        </div>
        
        <Button
          onClick={handleContinue}
          className="w-full max-w-sm"
          style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
        >
          Get Started
        </Button>
      </motion.div>
    </div>
  );
}
