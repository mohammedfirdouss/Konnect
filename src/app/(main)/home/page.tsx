'use client';

import { HomeTab } from '@/components/tabs/HomeTab';
import { useUser } from '../../contexts/UserContext';

export default function HomePage() {
  const { user } = useUser();

  if (!user) return null;

  return <HomeTab user={user} />;
}
