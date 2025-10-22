'use client';

import { CartTab } from '@/components/tabs/CartTab';
import { useUser } from '../../contexts/UserContext';

export default function CartPage() {
  const { user } = useUser();

  if (!user) return null;

  return <CartTab user={user} />;
}
