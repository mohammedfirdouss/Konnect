'use client';

import { GamificationTab } from '@/components/tabs/GamificationTab';
import { useUser } from '../../contexts/UserContext';

export default function GamificationPage() {
  const { user } = useUser();

  if (!user) return null;

  return <GamificationTab user={user} />;
}
