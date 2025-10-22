import { useState } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { ArrowLeft, User, Mail, Phone, CreditCard, Shield } from 'lucide-react';
import { useUser } from '../contexts/UserContext';
import { toast } from 'sonner@2.0.3';

export function PersonalInfo() {
  const navigate = useNavigate();
  const { user, setUser } = useUser();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    studentId: '',
    nin: '',
  });

  const [errors, setErrors] = useState({
    name: '',
    email: '',
    phone: '',
  });

  const validateForm = () => {
    const newErrors = {
      name: '',
      email: '',
      phone: '',
    };

    let isValid = true;

    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
      isValid = false;
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
      isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
      isValid = false;
    }

    // Phone validation
    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
      isValid = false;
    } else if (!/^[0-9]{10,11}$/.test(formData.phone.replace(/\s/g, ''))) {
      newErrors.phone = 'Please enter a valid phone number';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = () => {
    if (!validateForm()) {
      toast.error('Please fill in all required fields correctly');
      return;
    }

    if (!user?.role) {
      toast.error('Please select a role first');
      navigate('/role');
      return;
    }

    // Store basic user info, wallet will be created in next step
    setUser({
      ...user,
      name: formData.name,
      email: formData.email,
      phone: formData.phone,
      walletAddress: '', // Will be set in wallet creation
      balance: 0,
    });

    navigate('/wallet-creation');
  };

  const handleBack = () => {
    navigate('/role');
  };

  return (
    <div className="min-h-screen flex flex-col px-6 py-8" style={{ backgroundColor: '#121212' }}>
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={handleBack}
          className="mb-6 p-2 rounded-lg transition-all"
          style={{ color: '#B3B3B3' }}
        >
          <ArrowLeft size={24} />
        </button>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h2 className="mb-2" style={{ color: '#FFFFFF' }}>
            Personal Information
          </h2>
          <p style={{ color: '#B3B3B3' }}>
            Tell us about yourself to create your account
          </p>
        </motion.div>

        {/* Progress Indicator */}
        <div className="flex gap-2 mt-6">
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: '#9945FF' }} />
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: '#9945FF' }} />
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: '#333333' }} />
          <div className="h-1 flex-1 rounded-full" style={{ backgroundColor: '#333333' }} />
        </div>
      </div>

      {/* Form */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="flex-1 space-y-5"
      >
        {/* Name */}
        <div>
          <Label style={{ color: '#B3B3B3' }}>
            Full Name <span style={{ color: '#FF4D4D' }}>*</span>
          </Label>
          <div className="relative mt-2">
            <User
              size={20}
              className="absolute left-3 top-1/2 -translate-y-1/2"
              style={{ color: '#666666' }}
            />
            <Input
              type="text"
              placeholder="Enter your full name"
              value={formData.name}
              onChange={(e) => {
                setFormData({ ...formData, name: e.target.value });
                setErrors({ ...errors, name: '' });
              }}
              className="pl-10"
              style={{
                backgroundColor: '#1E1E1E',
                borderColor: errors.name ? '#FF4D4D' : '#333333',
                color: '#FFFFFF',
              }}
            />
          </div>
          {errors.name && (
            <p className="text-xs mt-1" style={{ color: '#FF4D4D' }}>
              {errors.name}
            </p>
          )}
        </div>

        {/* Email */}
        <div>
          <Label style={{ color: '#B3B3B3' }}>
            Email Address <span style={{ color: '#FF4D4D' }}>*</span>
          </Label>
          <div className="relative mt-2">
            <Mail
              size={20}
              className="absolute left-3 top-1/2 -translate-y-1/2"
              style={{ color: '#666666' }}
            />
            <Input
              type="email"
              placeholder="your.email@university.edu"
              value={formData.email}
              onChange={(e) => {
                setFormData({ ...formData, email: e.target.value });
                setErrors({ ...errors, email: '' });
              }}
              className="pl-10"
              style={{
                backgroundColor: '#1E1E1E',
                borderColor: errors.email ? '#FF4D4D' : '#333333',
                color: '#FFFFFF',
              }}
            />
          </div>
          {errors.email && (
            <p className="text-xs mt-1" style={{ color: '#FF4D4D' }}>
              {errors.email}
            </p>
          )}
        </div>

        {/* Phone */}
        <div>
          <Label style={{ color: '#B3B3B3' }}>
            Phone Number <span style={{ color: '#FF4D4D' }}>*</span>
          </Label>
          <div className="relative mt-2">
            <Phone
              size={20}
              className="absolute left-3 top-1/2 -translate-y-1/2"
              style={{ color: '#666666' }}
            />
            <Input
              type="tel"
              placeholder="08012345678"
              value={formData.phone}
              onChange={(e) => {
                setFormData({ ...formData, phone: e.target.value });
                setErrors({ ...errors, phone: '' });
              }}
              className="pl-10"
              style={{
                backgroundColor: '#1E1E1E',
                borderColor: errors.phone ? '#FF4D4D' : '#333333',
                color: '#FFFFFF',
              }}
            />
          </div>
          {errors.phone && (
            <p className="text-xs mt-1" style={{ color: '#FF4D4D' }}>
              {errors.phone}
            </p>
          )}
        </div>

        {/* Optional Fields */}
        <div className="pt-4" style={{ borderTop: '1px solid #333333' }}>
          <p className="text-sm mb-4" style={{ color: '#666666' }}>
            Optional Information
          </p>

          {/* Student ID */}
          <div className="mb-4">
            <Label style={{ color: '#B3B3B3' }}>Student ID (Optional)</Label>
            <div className="relative mt-2">
              <CreditCard
                size={20}
                className="absolute left-3 top-1/2 -translate-y-1/2"
                style={{ color: '#666666' }}
              />
              <Input
                type="text"
                placeholder="Enter your student ID"
                value={formData.studentId}
                onChange={(e) =>
                  setFormData({ ...formData, studentId: e.target.value })
                }
                className="pl-10"
                style={{
                  backgroundColor: '#1E1E1E',
                  borderColor: '#333333',
                  color: '#FFFFFF',
                }}
              />
            </div>
          </div>

          {/* NIN */}
          <div>
            <Label style={{ color: '#B3B3B3' }}>NIN (Optional)</Label>
            <div className="relative mt-2">
              <Shield
                size={20}
                className="absolute left-3 top-1/2 -translate-y-1/2"
                style={{ color: '#666666' }}
              />
              <Input
                type="text"
                placeholder="Enter your NIN"
                value={formData.nin}
                onChange={(e) =>
                  setFormData({ ...formData, nin: e.target.value })
                }
                className="pl-10"
                style={{
                  backgroundColor: '#1E1E1E',
                  borderColor: '#333333',
                  color: '#FFFFFF',
                }}
              />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Continue Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
        className="mt-8"
      >
        <Button
          onClick={handleSubmit}
          className="w-full"
          style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
        >
          Continue
        </Button>
      </motion.div>
    </div>
  );
}
