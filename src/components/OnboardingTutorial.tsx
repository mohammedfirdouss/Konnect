import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import { Button } from './ui/button';
import { ShoppingBag, ShoppingCart, CreditCard, FileText, Trophy, ChevronRight, ChevronLeft } from 'lucide-react';

const slides = [
  {
    icon: ShoppingBag,
    title: 'Marketplace',
    description: 'Buy & sell goods and services with fellow students on campus',
  },
  {
    icon: ShoppingCart,
    title: 'Cart & Order Tracking',
    description: 'Track your orders in real-time with secure delivery codes',
  },
  {
    icon: FileText,
    title: 'Bills & Subscriptions',
    description: 'Pay for airtime, utilities, and digital subscriptions instantly',
  },
  {
    icon: CreditCard,
    title: 'Wallet & Escrow',
    description: 'Secure transactions with automatic escrow powered by Solana',
  },
  {
    icon: Trophy,
    title: 'Gamification & Levels',
    description: 'Earn points, badges, and climb the campus leaderboard',
  },
];

export function OnboardingTutorial() {
  const navigate = useNavigate();
  const [currentSlide, setCurrentSlide] = useState(0);

  const handleNext = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(prev => prev + 1);
    } else {
      navigate('/home');
    }
  };

  const handlePrev = () => {
    if (currentSlide > 0) {
      setCurrentSlide(prev => prev - 1);
    }
  };

  const handleSkip = () => {
    navigate('/home');
  };

  const slide = slides[currentSlide];
  const Icon = slide.icon;

  return (
    <div className="min-h-screen flex flex-col items-center justify-between px-6 py-12" style={{ backgroundColor: '#121212' }}>
      <div className="flex-1 flex flex-col items-center justify-center w-full max-w-md">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentSlide}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
            className="text-center"
          >
            <div className="w-24 h-24 mx-auto mb-8 rounded-3xl flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
              <Icon size={48} color="#FFFFFF" />
            </div>

            <h2 className="mb-4" style={{ color: '#FFFFFF' }}>
              {slide.title}
            </h2>
            <p style={{ color: '#B3B3B3' }}>
              {slide.description}
            </p>
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="w-full max-w-md space-y-6">
        <div className="flex justify-center gap-2">
          {slides.map((_, index) => (
            <div
              key={index}
              className="h-2 rounded-full transition-all"
              style={{
                width: index === currentSlide ? '32px' : '8px',
                backgroundColor: index === currentSlide ? '#9945FF' : '#333333',
              }}
            />
          ))}
        </div>

        <div className="flex gap-3">
          {currentSlide > 0 && (
            <Button
              onClick={handlePrev}
              variant="outline"
              className="flex-1"
              style={{ borderColor: '#9945FF', color: '#9945FF', backgroundColor: 'transparent' }}
            >
              <ChevronLeft size={20} />
              Previous
            </Button>
          )}
          <Button
            onClick={handleNext}
            className="flex-1"
            style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
          >
            {currentSlide < slides.length - 1 ? (
              <>
                Next
                <ChevronRight size={20} />
              </>
            ) : (
              'Start Using Konnect'
            )}
          </Button>
        </div>

        <button
          onClick={handleSkip}
          className="w-full text-center py-2"
          style={{ color: '#666666' }}
        >
          Skip Tutorial
        </button>
      </div>
    </div>
  );
}
