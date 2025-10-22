import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { useUser } from '../contexts/UserContext';

export function AuthScreen() {
  const navigate = useNavigate();
  const { setUser } = useUser();
  const [activeTab, setActiveTab] = useState<'signup' | 'login'>('signup');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    if (activeTab === 'signup') {
      if (formData.name && formData.email && formData.phone && formData.password) {
        setUser({
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          role: null,
          walletAddress: '',
          balance: 0,
        });
        navigate('/role');
      }
    } else {
      if (formData.email && formData.password) {
        setUser({
          name: 'John Doe',
          email: formData.email,
          phone: '+234 800 000 0000',
          role: null,
          walletAddress: '',
          balance: 0,
        });
        navigate('/role');
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 py-8" style={{ backgroundColor: '#121212' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        <h2 className="mb-8 text-center" style={{ color: '#FFFFFF' }}>
          Welcome Back
        </h2>

        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'signup' | 'login')}>
          <TabsList className="grid w-full grid-cols-2 mb-6" style={{ backgroundColor: '#1E1E1E' }}>
            <TabsTrigger value="signup" style={{ color: activeTab === 'signup' ? '#9945FF' : '#B3B3B3' }}>
              Sign Up
            </TabsTrigger>
            <TabsTrigger value="login" style={{ color: activeTab === 'login' ? '#9945FF' : '#B3B3B3' }}>
              Login
            </TabsTrigger>
          </TabsList>

          <TabsContent value="signup" className="space-y-4">
            <div>
              <Label htmlFor="name" style={{ color: '#B3B3B3' }}>Full Name</Label>
              <Input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                style={{ backgroundColor: '#1E1E1E', borderColor: '#333333', color: '#FFFFFF' }}
                className="mt-1.5"
              />
            </div>
            <div>
              <Label htmlFor="email" style={{ color: '#B3B3B3' }}>Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                style={{ backgroundColor: '#1E1E1E', borderColor: '#333333', color: '#FFFFFF' }}
                className="mt-1.5"
              />
            </div>
            <div>
              <Label htmlFor="phone" style={{ color: '#B3B3B3' }}>Phone Number</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                style={{ backgroundColor: '#1E1E1E', borderColor: '#333333', color: '#FFFFFF' }}
                className="mt-1.5"
              />
            </div>
            <div>
              <Label htmlFor="password-signup" style={{ color: '#B3B3B3' }}>Password</Label>
              <Input
                id="password-signup"
                type="password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                style={{ backgroundColor: '#1E1E1E', borderColor: '#333333', color: '#FFFFFF' }}
                className="mt-1.5"
              />
            </div>
            <p className="text-sm" style={{ color: '#666666' }}>
              Optional: Upload student ID for verification
            </p>
          </TabsContent>

          <TabsContent value="login" className="space-y-4">
            <div>
              <Label htmlFor="email-login" style={{ color: '#B3B3B3' }}>Email / Phone</Label>
              <Input
                id="email-login"
                type="text"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                style={{ backgroundColor: '#1E1E1E', borderColor: '#333333', color: '#FFFFFF' }}
                className="mt-1.5"
              />
            </div>
            <div>
              <Label htmlFor="password-login" style={{ color: '#B3B3B3' }}>Password</Label>
              <Input
                id="password-login"
                type="password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                style={{ backgroundColor: '#1E1E1E', borderColor: '#333333', color: '#FFFFFF' }}
                className="mt-1.5"
              />
            </div>
            <button className="text-sm" style={{ color: '#9945FF' }}>
              Forgot Password?
            </button>
          </TabsContent>
        </Tabs>

        <Button
          onClick={handleSubmit}
          className="w-full mt-6"
          style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
        >
          {activeTab === 'signup' ? 'Continue' : 'Login'}
        </Button>
      </motion.div>
    </div>
  );
}
