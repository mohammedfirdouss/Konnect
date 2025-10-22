'use client';

import { useRouter } from 'next/navigation';
import { WalletSetup } from '@/components/WalletSetup';
import { useUser } from '../contexts/UserContext';
import { useEffect } from 'react';

export default function WalletSetupPage() {
  const router = useRouter();
  const { user, setUser } = useUser();

  useEffect(() => {
    if (!user || !user.role) {
      router.push('/role');
    }
  }, [user, router]);

  const handleWalletSetup = (walletAddress: string) => {
    if (user) {
      setUser({ ...user, walletAddress });
      router.push('/notifications');
    }
  };

  if (!user) return null;

  return <WalletSetup user={user} onComplete={handleWalletSetup} />;
}
