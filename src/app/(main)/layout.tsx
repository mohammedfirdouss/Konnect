'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { TopBar } from '@/components/TopBar';
import { BottomNav } from '@/components/BottomNav';
import { HamburgerMenu } from '@/components/HamburgerMenu';
import { useUser } from '../contexts/UserContext';

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated } = useUser();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Redirect to auth if not authenticated
    if (!isAuthenticated || !user?.walletAddress) {
      router.push('/');
    }
  }, [isAuthenticated, user, router]);

  if (!isAuthenticated || !user) {
    return null;
  }

  // Map pathname to tab
  const getCurrentTab = () => {
    if (pathname.includes('/home')) return 'home';
    if (pathname.includes('/marketplace')) return 'marketplace';
    if (pathname.includes('/cart')) return 'cart';
    if (pathname.includes('/wallet')) return 'wallet';
    if (pathname.includes('/bills')) return 'bills';
    if (pathname.includes('/gamification')) return 'gamification';
    return 'home';
  };

  const handleTabChange = (tab: string) => {
    router.push(`/${tab}`);
  };

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: '#121212' }}>
      <TopBar
        onMenuClick={() => setIsMenuOpen(true)}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      <HamburgerMenu
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
        user={user}
      />

      <div className="pt-16">{children}</div>

      <BottomNav
        activeTab={getCurrentTab()}
        onTabChange={handleTabChange}
        userRole={user.role}
      />
    </div>
  );
}
