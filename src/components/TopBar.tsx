import { Menu, Search, Bell } from 'lucide-react';
import { Input } from './ui/input';

interface TopBarProps {
  onMenuClick: () => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  showMenuButton?: boolean;
}

export function TopBar({ onMenuClick, searchQuery, onSearchChange, showMenuButton = true }: TopBarProps) {
  return (
    <div
      className="fixed top-0 right-0 z-50 px-4 py-3 flex items-center gap-3"
      style={{
        backgroundColor: '#121212',
        borderBottom: '1px solid #333333',
        left: showMenuButton ? 0 : '16rem',
      }}
    >
      {showMenuButton && (
        <button
          onClick={onMenuClick}
          className="p-2 rounded-lg"
          style={{ color: '#FFFFFF' }}
        >
          <Menu size={24} />
        </button>
      )}

      <div className="flex-1 relative">
        <Input
          type="text"
          placeholder="Search products, services..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full pl-4 pr-10"
          style={{
            backgroundColor: '#1E1E1E',
            borderColor: '#333333',
            color: '#FFFFFF',
          }}
        />
        <Search
          size={20}
          className="absolute right-3 top-1/2 -translate-y-1/2"
          style={{ color: '#666666' }}
        />
      </div>

      <button className="p-2 rounded-lg relative" style={{ color: '#FFFFFF' }}>
        <Bell size={24} style={{ color: '#9945FF' }} />
        <div
          className="absolute top-1 right-1 w-2 h-2 rounded-full"
          style={{ backgroundColor: '#FF4D4D' }}
        />
      </button>
    </div>
  );
}
