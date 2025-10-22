import { Card } from '../ui/card';
import { Progress } from '../ui/progress';
import { Trophy, Award, Star, TrendingUp, Crown, Zap } from 'lucide-react';
import { useUser } from '../../contexts/UserContext';

export function GamificationTab() {
  const { user } = useUser();
  
  if (!user) return null;
  const userStats = {
    level: 8,
    currentXP: 3500,
    nextLevelXP: 5000,
    totalPoints: 12450,
    rank: 23,
    totalUsers: 1247,
  };

  const badges = [
    { id: 1, name: 'First Purchase', icon: '🎉', unlocked: true, date: '2025-09-15' },
    { id: 2, name: 'Power Seller', icon: '⚡', unlocked: true, date: '2025-09-20' },
    { id: 3, name: 'Bill Master', icon: '💳', unlocked: true, date: '2025-09-25' },
    { id: 4, name: '5 Star Rating', icon: '⭐', unlocked: true, date: '2025-10-01' },
    { id: 5, name: 'Early Adopter', icon: '🚀', unlocked: true, date: '2025-09-10' },
    { id: 6, name: 'Social Butterfly', icon: '🦋', unlocked: false },
    { id: 7, name: 'Speed Demon', icon: '💨', unlocked: false },
    { id: 8, name: 'Campus Legend', icon: '👑', unlocked: false },
  ];

  const leaderboard = [
    { rank: 1, name: 'Sarah M.', points: 25840, level: 15 },
    { rank: 2, name: 'John D.', points: 23150, level: 14 },
    { rank: 3, name: 'Emma L.', points: 21300, level: 13 },
    { rank: 4, name: 'David K.', points: 18920, level: 12 },
    { rank: 5, name: 'Alice W.', points: 16750, level: 11 },
  ];

  const missions = [
    { id: 1, title: 'Complete 5 transactions', progress: 60, reward: 150, category: 'daily' },
    { id: 2, title: 'Maintain 5-star rating', progress: 100, reward: 300, category: 'weekly' },
    { id: 3, title: 'Refer 3 friends', progress: 33, reward: 500, category: 'special' },
    { id: 4, title: 'Pay 10 bills', progress: 70, reward: 200, category: 'monthly' },
  ];

  return (
    <div className="px-4 py-6 space-y-6">
      <Card className="p-6" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
              <Trophy size={32} color="#FFFFFF" />
            </div>
            <div>
              <h2 style={{ color: '#FFFFFF' }}>Level {userStats.level}</h2>
              <p className="text-sm" style={{ color: '#B3B3B3' }}>
                {userStats.totalPoints.toLocaleString()} total points
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="px-3 py-1 rounded-full inline-block" style={{ backgroundColor: '#9945FF' }}>
              <span className="text-sm" style={{ color: '#FFFFFF' }}>Rank #{userStats.rank}</span>
            </div>
            <p className="text-xs mt-1" style={{ color: '#B3B3B3' }}>
              of {userStats.totalUsers.toLocaleString()}
            </p>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span style={{ color: '#B3B3B3' }}>Progress to Level {userStats.level + 1}</span>
            <span style={{ color: '#9945FF' }}>
              {userStats.currentXP} / {userStats.nextLevelXP} XP
            </span>
          </div>
          <Progress
            value={(userStats.currentXP / userStats.nextLevelXP) * 100}
            className="h-3"
          />
        </div>
      </Card>

      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 style={{ color: '#FFFFFF' }}>Active Missions</h3>
          <span className="text-sm" style={{ color: '#9945FF' }}>View All</span>
        </div>
        <div className="space-y-3">
          {missions.map((mission) => (
            <Card key={mission.id} className="p-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: mission.progress === 100 ? '#4AFF99' : '#9945FF' }}>
                  {mission.progress === 100 ? (
                    <Star size={20} color="#121212" />
                  ) : (
                    <Zap size={20} color="#FFFFFF" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <p style={{ color: '#FFFFFF' }}>{mission.title}</p>
                    <span className="text-sm" style={{ color: '#4AFF99' }}>
                      +{mission.reward} pts
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ backgroundColor: '#121212' }}>
                      <div
                        className="h-full transition-all"
                        style={{
                          width: `${mission.progress}%`,
                          backgroundColor: mission.progress === 100 ? '#4AFF99' : '#9945FF',
                        }}
                      />
                    </div>
                    <span className="text-xs" style={{ color: '#B3B3B3' }}>
                      {mission.progress}%
                    </span>
                  </div>
                </div>
              </div>
              <div className="inline-block px-2 py-1 rounded text-xs" style={{ backgroundColor: '#121212', color: '#9945FF' }}>
                {mission.category}
              </div>
            </Card>
          ))}
        </div>
      </div>

      <div>
        <div className="flex items-center gap-3 mb-3">
          <Award size={24} style={{ color: '#9945FF' }} />
          <h3 style={{ color: '#FFFFFF' }}>Badges</h3>
        </div>
        <div className="grid grid-cols-4 gap-3">
          {badges.map((badge) => (
            <button
              key={badge.id}
              className="flex flex-col items-center gap-2 p-3 rounded-xl transition-all"
              style={{
                backgroundColor: badge.unlocked ? '#1E1E1E' : '#121212',
                opacity: badge.unlocked ? 1 : 0.5,
              }}
            >
              <div className="text-3xl">{badge.icon}</div>
              <span className="text-xs text-center" style={{ color: '#FFFFFF' }}>
                {badge.name}
              </span>
              {badge.unlocked && (
                <div className="w-4 h-4 rounded-full flex items-center justify-center" style={{ backgroundColor: '#4AFF99' }}>
                  <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                    <path d="M1 4L3.5 6.5L9 1" stroke="#121212" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className="flex items-center gap-3 mb-3">
          <TrendingUp size={24} style={{ color: '#9945FF' }} />
          <h3 style={{ color: '#FFFFFF' }}>Campus Leaderboard</h3>
        </div>
        <Card className="p-4 space-y-3" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
          {leaderboard.map((entry) => (
            <div
              key={entry.rank}
              className="flex items-center justify-between p-3 rounded-lg"
              style={{ backgroundColor: entry.rank <= 3 ? '#9945FF' : '#121212' }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center"
                  style={{
                    backgroundColor: entry.rank === 1 ? '#FFD700' : entry.rank === 2 ? '#C0C0C0' : entry.rank === 3 ? '#CD7F32' : '#333333',
                    color: entry.rank <= 3 ? '#121212' : '#FFFFFF',
                  }}
                >
                  {entry.rank === 1 ? <Crown size={16} /> : entry.rank}
                </div>
                <div>
                  <p style={{ color: entry.rank <= 3 ? '#FFFFFF' : '#FFFFFF' }}>
                    {entry.name}
                  </p>
                  <p className="text-xs" style={{ color: entry.rank <= 3 ? '#E0E0E0' : '#B3B3B3' }}>
                    Level {entry.level}
                  </p>
                </div>
              </div>
              <span style={{ color: entry.rank <= 3 ? '#FFFFFF' : '#9945FF' }}>
                {entry.points.toLocaleString()} pts
              </span>
            </div>
          ))}
          
          <div
            className="flex items-center justify-between p-3 rounded-lg border-2"
            style={{ backgroundColor: '#121212', borderColor: '#9945FF' }}
          >
            <div className="flex items-center gap-3">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center"
                style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
              >
                {userStats.rank}
              </div>
              <div>
                <p style={{ color: '#FFFFFF' }}>You</p>
                <p className="text-xs" style={{ color: '#B3B3B3' }}>
                  Level {userStats.level}
                </p>
              </div>
            </div>
            <span style={{ color: '#9945FF' }}>{userStats.totalPoints.toLocaleString()} pts</span>
          </div>
        </Card>
      </div>

      <div className="p-4 rounded-lg" style={{ backgroundColor: '#5AC8FA', color: '#121212' }}>
        <p className="text-sm">
          💡 <strong>Tip:</strong> Complete daily missions to climb the leaderboard faster!
        </p>
      </div>
    </div>
  );
}
