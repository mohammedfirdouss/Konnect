import { useState } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { RegistrationForm, RegistrationData } from './RegistrationForm';
import { useUser } from '../contexts/UserContext';
import { toast } from 'sonner@2.0.3';
import { useIsMobile } from '../hooks/useIsMobile';

export function Registration() {
  const navigate = useNavigate();
  const { setUser } = useUser();
  const { isMobile } = useIsMobile();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (data: RegistrationData) => {
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      // Check if user already exists
      const savedCredentials = localStorage.getItem('konnect_credentials');
      
      if (savedCredentials) {
        try {
          const credentials = JSON.parse(savedCredentials);
          if (credentials.email === data.email) {
            toast.error('An account with this email already exists. Please sign in.');
            setIsLoading(false);
            return;
          }
        } catch (e) {
          // Continue if parsing fails
        }
      }

      // Save credentials
      localStorage.setItem('konnect_credentials', JSON.stringify({
        email: data.email,
        password: data.password,
      }));

      // Create initial user object
      setUser({
        name: data.name,
        email: data.email,
        phone: data.phone,
        role: null, // Will be set in role selection
        walletAddress: '',
        balance: 0,
      });

      toast.success('Account created successfully!');
      
      // Navigate to role selection
      navigate('/role');
    }, 1000);
  };

  const handleBack = () => {
    navigate('/login');
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center px-6 py-8"
      style={{ backgroundColor: '#121212' }}
    >
      <div className={`w-full ${isMobile ? 'max-w-md' : 'max-w-2xl'}`}>
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={handleBack}
            className="mb-6 p-2 rounded-lg transition-all hover:bg-opacity-10"
            style={{ color: '#B3B3B3', backgroundColor: 'rgba(153, 69, 255, 0.1)' }}
          >
            <ArrowLeft size={24} />
          </button>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <h2 
              className={`mb-2 ${isMobile ? '' : 'text-4xl'}`}
              style={{ color: '#FFFFFF' }}
            >
              Create Your Account
            </h2>
            <p 
              className={isMobile ? '' : 'text-lg'}
              style={{ color: '#B3B3B3' }}
            >
              Join Konnect and start trading on campus
            </p>
          </motion.div>
        </div>

        {/* Registration Form */}
        <RegistrationForm onSubmit={handleSubmit} isLoading={isLoading} />

        {/* Sign In Link */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.3 }}
          className="mt-6 text-center"
        >
          <p style={{ color: '#B3B3B3' }}>
            Already have an account?{' '}
            <button
              onClick={() => navigate('/login')}
              className="underline"
              style={{ color: '#9945FF' }}
            >
              Sign in
            </button>
          </p>
        </motion.div>

        {/* Info Banner */}
        {!isMobile && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.4 }}
            className="mt-8 p-4 rounded-lg"
            style={{ backgroundColor: 'rgba(90, 200, 250, 0.1)', borderLeft: '3px solid #5AC8FA' }}
          >
            <p className="text-sm" style={{ color: '#B3B3B3' }}>
              📧 Your information is secure. We'll use your email for account verification and important updates only.
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
