'use client';

import { useRouter } from 'next/navigation';
import { OnboardingTutorial } from '@/components/OnboardingTutorial';
import { useUser } from '../contexts/UserContext';
import { useEffect } from 'react';

export default function TutorialPage() {
  const router = useRouter();
  const { user } = useUser();

  useEffect(() => {
    if (!user || !user.walletAddress) {
      router.push('/notifications');
    }
  }, [user, router]);

  const handleComplete = () => {
    router.push('/home');
  };

  return <OnboardingTutorial onComplete={handleComplete} />;
}
