'use client';

import { WalletTab } from '@/components/tabs/WalletTab';
import { useUser } from '../../contexts/UserContext';

export default function WalletPage() {
  const { user, setUser } = useUser();

  if (!user) return null;

  return <WalletTab user={user} setUser={setUser} />;
}
