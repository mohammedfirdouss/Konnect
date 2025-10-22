import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { TopBar } from './TopBar';
import { BottomNav } from './BottomNav';
import { HamburgerMenu } from './HamburgerMenu';
import { DesktopTopNav } from './DesktopTopNav';
import { Footer } from './Footer';
import { useUser } from '../contexts/UserContext';
import { useIsMobile } from '../hooks/useIsMobile';

export function MainLayout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useUser();
  const { isMobile } = useIsMobile();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  if (!user) {
    return null;
  }

  // Map pathname to tab
  const getCurrentTab = () => {
    if (location.pathname.includes('/home')) return 'home';
    if (location.pathname.includes('/marketplace')) return 'marketplace';
    if (location.pathname.includes('/cart')) return 'cart';
    if (location.pathname.includes('/wallet')) return 'wallet';
    if (location.pathname.includes('/bills')) return 'bills';
    if (location.pathname.includes('/gamification')) return 'gamification';
    return 'home';
  };

  const handleTabChange = (tab: string) => {
    navigate(`/${tab}`);
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#121212' }}>
      {/* Mobile Top Bar */}
      {isMobile && (
        <TopBar
          onMenuClick={() => setIsMenuOpen(true)}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          showMenuButton={isMobile}
        />
      )}

      {/* Desktop Top Navigation */}
      {!isMobile && (
        <DesktopTopNav
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
        />
      )}

      {/* Mobile Hamburger Menu */}
      {isMobile && (
        <HamburgerMenu
          isOpen={isMenuOpen}
          onClose={() => setIsMenuOpen(false)}
          user={user}
        />
      )}

      {/* Main Content */}
      <div className={isMobile ? 'pt-16 pb-20' : 'pt-32'}>
        {children}
      </div>

      {/* Desktop Footer - Only shows on desktop */}
      {!isMobile && <Footer />}

      {/* Mobile Bottom Navigation */}
      {isMobile && (
        <BottomNav
          activeTab={getCurrentTab()}
          onTabChange={handleTabChange}
          userRole={user.role}
        />
      )}
    </div>
  );
}
