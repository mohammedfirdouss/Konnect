import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { Button } from './ui/button';
import { Switch } from './ui/switch';
import { Bell, Sparkles } from 'lucide-react';
import { useIsMobile } from '../hooks/useIsMobile';

export function NotificationSetup() {
  const navigate = useNavigate();
  const { isMobile } = useIsMobile();
  const [pushNotifications, setPushNotifications] = useState(true);
  const [aiRecommendations, setAiRecommendations] = useState(true);

  const handleComplete = () => {
    // Skip tutorial and go directly to marketplace hub (home) for all screen sizes
    navigate('/home');
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6" style={{ backgroundColor: '#121212' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        <h2 className="mb-3 text-center" style={{ color: '#FFFFFF' }}>
          Notifications & Preferences
        </h2>
        <p className="mb-8 text-center" style={{ color: '#B3B3B3' }}>
          Customize your Konnect experience
        </p>

        <div className="space-y-4 mb-8">
          <div className="p-6 rounded-xl flex items-start justify-between" style={{ backgroundColor: '#1E1E1E' }}>
            <div className="flex items-start gap-4 flex-1">
              <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
                <Bell size={20} color="#FFFFFF" />
              </div>
              <div className="flex-1">
                <h3 className="mb-1" style={{ color: '#FFFFFF' }}>
                  Push Notifications
                </h3>
                <p className="text-sm" style={{ color: '#B3B3B3' }}>
                  Delivery updates, bills reminders, and milestones
                </p>
              </div>
            </div>
            <Switch
              checked={pushNotifications}
              onCheckedChange={setPushNotifications}
              className="ml-4"
            />
          </div>

          <div className="p-6 rounded-xl flex items-start justify-between" style={{ backgroundColor: '#1E1E1E' }}>
            <div className="flex items-start gap-4 flex-1">
              <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
                <Sparkles size={20} color="#FFFFFF" />
              </div>
              <div className="flex-1">
                <h3 className="mb-1" style={{ color: '#FFFFFF' }}>
                  AI Recommendations
                </h3>
                <p className="text-sm" style={{ color: '#B3B3B3' }}>
                  Personalized product suggestions and smart tips
                </p>
              </div>
            </div>
            <Switch
              checked={aiRecommendations}
              onCheckedChange={setAiRecommendations}
              className="ml-4"
            />
          </div>
        </div>

        <Button
          onClick={handleComplete}
          className="w-full"
          style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
        >
          Finish Setup
        </Button>
      </motion.div>
    </div>
  );
}
