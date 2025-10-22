'use client';

import { useRouter } from 'next/navigation';
import { RoleSelection } from '@/components/RoleSelection';
import { useUser, UserRole } from '../contexts/UserContext';
import { useEffect } from 'react';

export default function RolePage() {
  const router = useRouter();
  const { user, setUser } = useUser();

  useEffect(() => {
    if (!user) {
      router.push('/auth');
    }
  }, [user, router]);

  const handleRoleSelect = (role: UserRole) => {
    if (user) {
      setUser({ ...user, role });
      router.push('/wallet-setup');
    }
  };

  if (!user) return null;

  return <RoleSelection onRoleSelect={handleRoleSelect} />;
}
