import { Sparkles, TrendingUp, Zap, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { useUser } from '../../contexts/UserContext';

export function HomeTab() {
  const { user } = useUser();
  const navigate = useNavigate();
  
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

  return (
    <div className="px-4 py-6 space-y-6">
      <div>
        <h1 style={{ color: '#FFFFFF' }}>
          Welcome back, {user.name.split(' ')[0]}!
        </h1>
        <p style={{ color: '#B3B3B3' }}>
          Here's what's happening on campus today
        </p>
      </div>

      <Card className="p-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
            <Sparkles size={20} color="#FFFFFF" />
          </div>
          <div>
            <h3 style={{ color: '#FFFFFF' }}>AI Recommendations</h3>
            <p className="text-sm" style={{ color: '#B3B3B3' }}>
              Picked just for you
            </p>
          </div>
        </div>
        <div className="space-y-3">
          {aiRecommendations.map((item) => (
            <div
              key={item.id}
              className="p-3 rounded-lg flex items-center justify-between cursor-pointer transition-all hover:bg-opacity-80"
              style={{ backgroundColor: '#121212' }}
              onClick={() => navigate(`/product/${item.id}`)}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-12 h-12 rounded-lg"
                  style={{ backgroundColor: '#333333' }}
                />
                <div>
                  <p style={{ color: '#FFFFFF' }}>{item.name}</p>
                  <p className="text-sm" style={{ color: '#B3B3B3' }}>
                    ₦{item.price.toLocaleString()}
                  </p>
                </div>
              </div>
              <ArrowRight size={20} style={{ color: '#9945FF' }} />
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
              <Zap size={20} color="#FFFFFF" />
            </div>
            <h3 style={{ color: '#FFFFFF' }}>Daily Missions</h3>
          </div>
          <span className="text-sm" style={{ color: '#9945FF' }}>View All</span>
        </div>
        <div className="space-y-3">
          {missions.map((mission) => (
            <div key={mission.id} className="space-y-2">
              <div className="flex items-center justify-between">
                <p style={{ color: '#FFFFFF' }}>{mission.title}</p>
                <span className="text-sm" style={{ color: '#4AFF99' }}>
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
      </Card>

      <Card className="p-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
            <TrendingUp size={20} color="#FFFFFF" />
          </div>
          <h3 style={{ color: '#FFFFFF' }}>Featured This Week</h3>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 rounded-lg text-center" style={{ backgroundColor: '#121212' }}>
            <div className="w-full h-24 rounded-lg mb-2" style={{ backgroundColor: '#333333' }} />
            <p className="text-sm" style={{ color: '#FFFFFF' }}>Gaming Laptop</p>
            <p className="text-sm" style={{ color: '#9945FF' }}>₦250,000</p>
          </div>
          <div className="p-3 rounded-lg text-center" style={{ backgroundColor: '#121212' }}>
            <div className="w-full h-24 rounded-lg mb-2" style={{ backgroundColor: '#333333' }} />
            <p className="text-sm" style={{ color: '#FFFFFF' }}>Coding Tutoring</p>
            <p className="text-sm" style={{ color: '#9945FF' }}>₦5,000/hr</p>
          </div>
        </div>
      </Card>

      <div className="p-4 rounded-lg" style={{ backgroundColor: '#5AC8FA', color: '#121212' }}>
        <p className="text-sm">
          💡 <strong>Tip:</strong> Complete your profile to get better AI recommendations!
        </p>
      </div>
    </div>
  );
}
