'use client';

import { useRouter } from 'next/navigation';
import { NotificationSetup } from '@/components/NotificationSetup';
import { useUser } from '../contexts/UserContext';
import { useEffect } from 'react';

export default function NotificationsPage() {
  const router = useRouter();
  const { user } = useUser();

  useEffect(() => {
    if (!user || !user.walletAddress) {
      router.push('/wallet-setup');
    }
  }, [user, router]);

  const handleComplete = () => {
    router.push('/tutorial');
  };

  return <NotificationSetup onComplete={handleComplete} />;
}
