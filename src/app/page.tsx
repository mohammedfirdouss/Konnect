'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { WelcomeScreen } from '@/components/WelcomeScreen';
import { useUser } from './contexts/UserContext';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, user } = useUser();

  useEffect(() => {
    // If user is authenticated and has completed onboarding, redirect to home
    if (isAuthenticated && user?.walletAddress) {
      router.push('/home');
    }
  }, [isAuthenticated, user, router]);

  const handleContinue = () => {
    router.push('/auth');
  };

  return <WelcomeScreen onContinue={handleContinue} />;
}
