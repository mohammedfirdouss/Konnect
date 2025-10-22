'use client';

import { useSearchParams } from 'next/navigation';
import { MarketplaceTab } from '@/components/tabs/MarketplaceTab';
import { useUser } from '../../contexts/UserContext';

export default function MarketplacePage() {
  const { user } = useUser();
  const searchParams = useSearchParams();
  const searchQuery = searchParams.get('q') || '';

  if (!user) return null;

  return <MarketplaceTab user={user} searchQuery={searchQuery} />;
}
