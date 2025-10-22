'use client';

import { useRouter } from 'next/navigation';
import { AuthScreen } from '@/components/AuthScreen';
import { useUser } from '../contexts/UserContext';

export default function AuthPage() {
  const router = useRouter();
  const { setUser } = useUser();

  const handleAuthComplete = (userData: { name: string; email: string; phone: string }) => {
    setUser({
      name: userData.name,
      email: userData.email,
      phone: userData.phone,
      role: null,
      walletAddress: '',
      balance: 0,
    });
    router.push('/role');
  };

  return <AuthScreen onComplete={handleAuthComplete} />;
}
