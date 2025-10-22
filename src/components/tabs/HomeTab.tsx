import { Sparkles, TrendingUp, Zap, ArrowRight, Trophy, DollarSign, Package } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { useUser } from '../../contexts/UserContext';
import { useIsMobile } from '../../hooks/useIsMobile';

export function HomeTab() {
  const { user } = useUser();
  const navigate = useNavigate();
  const { isMobile } = useIsMobile();
  
  if (!user) return null;

  const aiRecommendations = [
    { id: 2, name: 'iPhone 13 Pro', price: 380000, image: 'electronics', category: 'Electronics' },
    { id: 4, name: 'Calculus Textbook', price: 8000, image: 'education', category: 'Books' },
    { id: 1, name: 'MacBook Air M2', price: 450000, image: 'fashion', category: 'Electronics' },
  ];

  const missions = [
    { id: 1, title: 'Complete your first purchase', points: 50, progress: 0 },
    { id: 2, title: 'Pay 3 bills this week', points: 30, progress: 66 },
    { id: 3, title: 'Refer a friend', points: 100, progress: 0 },
  ];

  const quickStats = [
    { 
      label: 'Current Level', 
      value: user.level || '1',
      icon: <Trophy size={20} />,
      color: '#FFBF00'
    },
    { 
      label: 'Wallet Balance', 
      value: `₦${user.balance.toLocaleString()}`,
      icon: <DollarSign size={20} />,
      color: '#4AFF99'
    },
    { 
      label: 'Active Orders', 
      value: '2',
      icon: <Package size={20} />,
      color: '#9945FF'
    },
  ];

  const featuredItems = [
    { name: 'Gaming Laptop', price: 250000 },
    { name: 'Coding Tutoring', price: 5000 },
    { name: 'Campus Hoodie', price: 12500 },
    { name: 'Study Desk', price: 18000 },
  ];

  return (
    <div className={isMobile ? 'px-4 py-6 space-y-6' : 'max-w-7xl mx-auto px-8 py-8 space-y-8'}>
      {/* Header */}
      <div>
        <h1 className={isMobile ? '' : 'text-4xl'} style={{ color: '#FFFFFF' }}>
          Welcome back, {user.name.split(' ')[0]}!
        </h1>
        <p className={isMobile ? '' : 'text-lg mt-2'} style={{ color: '#B3B3B3' }}>
          Here's what's happening on campus today
        </p>
      </div>

      {/* Quick Stats - Desktop only */}
      {!isMobile && (
        <div className="grid grid-cols-3 gap-6">
          {quickStats.map((stat, index) => (
            <Card 
              key={index}
              className="p-6 transition-all hover:scale-105"
              style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm mb-2" style={{ color: '#B3B3B3' }}>
                    {stat.label}
                  </p>
                  <p className="text-3xl" style={{ color: '#FFFFFF' }}>
                    {stat.value}
                  </p>
                </div>
                <div 
                  className="w-14 h-14 rounded-xl flex items-center justify-center"
                  style={{ backgroundColor: `${stat.color}20` }}
                >
                  <div style={{ color: stat.color }}>
                    {stat.icon}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <div className={isMobile ? 'space-y-6' : 'grid grid-cols-3 gap-6'}>
        {/* AI Recommendations - Takes 2 columns on desktop */}
        <Card 
          className={`p-6 ${!isMobile ? 'col-span-2' : ''}`}
          style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div 
                className="w-12 h-12 rounded-xl flex items-center justify-center"
                style={{ backgroundColor: '#9945FF' }}
              >
                <Sparkles size={24} color="#FFFFFF" />
              </div>
              <div>
                <h3 className={isMobile ? '' : 'text-xl'} style={{ color: '#FFFFFF' }}>
                  AI Recommendations
                </h3>
                <p className="text-sm" style={{ color: '#B3B3B3' }}>
                  Picked just for you
                </p>
              </div>
            </div>
            {!isMobile && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/marketplace')}
                style={{ borderColor: '#9945FF', color: '#9945FF' }}
              >
                View All
              </Button>
            )}
          </div>
          
          <div className={isMobile ? 'space-y-3' : 'grid grid-cols-2 gap-4'}>
            {aiRecommendations.map((item) => (
              <div
                key={item.id}
                className="p-4 rounded-xl flex items-center justify-between cursor-pointer transition-all hover:bg-opacity-80"
                style={{ backgroundColor: '#121212' }}
                onClick={() => navigate(`/product/${item.id}`)}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`${isMobile ? 'w-12 h-12' : 'w-16 h-16'} rounded-lg`}
                    style={{ backgroundColor: '#333333' }}
                  />
                  <div>
                    <p style={{ color: '#FFFFFF' }}>{item.name}</p>
                    <p className="text-sm" style={{ color: '#9945FF' }}>
                      ₦{item.price.toLocaleString()}
                    </p>
                    <p className="text-xs mt-1" style={{ color: '#666666' }}>
                      {item.category}
                    </p>
                  </div>
                </div>
                <ArrowRight size={20} style={{ color: '#9945FF' }} />
              </div>
            ))}
          </div>
        </Card>

        {/* Daily Missions */}
        <Card 
          className="p-6"
          style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div 
                className="w-12 h-12 rounded-xl flex items-center justify-center"
                style={{ backgroundColor: '#9945FF' }}
              >
                <Zap size={24} color="#FFFFFF" />
              </div>
              <div>
                <h3 style={{ color: '#FFFFFF' }}>Daily Missions</h3>
                <p className="text-xs" style={{ color: '#B3B3B3' }}>
                  Earn rewards
                </p>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            {missions.map((mission) => (
              <div key={mission.id} className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm flex-1" style={{ color: '#FFFFFF' }}>
                    {mission.title}
                  </p>
                  <span 
                    className="text-xs px-2 py-1 rounded"
                    style={{ backgroundColor: '#4AFF99', color: '#121212' }}
                  >
                    +{mission.points} pts
                  </span>
                </div>
                <div className="w-full h-2 rounded-full overflow-hidden" style={{ backgroundColor: '#121212' }}>
                  <div
                    className="h-full transition-all"
                    style={{
                      width: `${mission.progress}%`,
                      backgroundColor: '#9945FF',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          {!isMobile && (
            <Button
              className="w-full mt-6"
              variant="outline"
              onClick={() => navigate('/gamification')}
              style={{ borderColor: '#9945FF', color: '#9945FF' }}
            >
              View All Missions
            </Button>
          )}
        </Card>
      </div>

      {/* Featured This Week */}
      <Card className="p-6" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div 
              className="w-12 h-12 rounded-xl flex items-center justify-center"
              style={{ backgroundColor: '#9945FF' }}
            >
              <TrendingUp size={24} color="#FFFFFF" />
            </div>
            <div>
              <h3 className={isMobile ? '' : 'text-xl'} style={{ color: '#FFFFFF' }}>
                Featured This Week
              </h3>
              <p className="text-sm" style={{ color: '#B3B3B3' }}>
                Hot deals on campus
              </p>
            </div>
          </div>
          {!isMobile && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/marketplace')}
              style={{ borderColor: '#9945FF', color: '#9945FF' }}
            >
              Browse All
            </Button>
          )}
        </div>

        <div className={`grid gap-4 ${isMobile ? 'grid-cols-2' : 'grid-cols-4'}`}>
          {featuredItems.map((item, index) => (
            <div 
              key={index}
              className="p-4 rounded-xl text-center cursor-pointer transition-all hover:scale-105"
              style={{ backgroundColor: '#121212' }}
              onClick={() => navigate('/marketplace')}
            >
              <div 
                className={`w-full ${isMobile ? 'h-24' : 'h-32'} rounded-lg mb-3`}
                style={{ backgroundColor: '#333333' }}
              />
              <p className="text-sm mb-2" style={{ color: '#FFFFFF' }}>
                {item.name}
              </p>
              <p className="text-sm" style={{ color: '#9945FF' }}>
                ₦{item.price.toLocaleString()}
                {item.name.includes('Tutoring') && '/hr'}
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* Tip Banner */}
      <div 
        className={`p-6 rounded-xl ${isMobile ? '' : 'flex items-center justify-between'}`}
        style={{ backgroundColor: '#5AC8FA', color: '#121212' }}
      >
        <div className={isMobile ? 'mb-4' : ''}>
          <p className={isMobile ? 'text-sm' : 'text-lg'}>
            💡 <strong>Tip:</strong> Complete your profile to get better AI recommendations!
          </p>
        </div>
        {!isMobile && (
          <Button
            onClick={() => navigate('/wallet')}
            style={{ backgroundColor: '#121212', color: '#FFFFFF' }}
          >
            Complete Profile
          </Button>
        )}
      </div>
    </div>
  );
}
