import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type UserRole = 'buyer' | 'seller' | 'both' | null;

export interface User {
  name: string;
  email: string;
  phone: string;
  role: UserRole;
  walletAddress: string;
  balance: number;
  gamificationPoints?: number;
  level?: number;
}

interface UserContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  isAuthenticated: boolean;
  hasCompletedOnboarding: boolean;
  setHasCompletedOnboarding: (completed: boolean) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(false);

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('konnect_user');
    const onboardingStatus = localStorage.getItem('konnect_onboarding_completed');
    
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        console.error('Failed to parse saved user', e);
        localStorage.removeItem('konnect_user');
      }
    }

    if (onboardingStatus === 'true') {
      setHasCompletedOnboarding(true);
    }
  }, []);

  // Save user to localStorage when it changes
  useEffect(() => {
    if (user) {
      localStorage.setItem('konnect_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('konnect_user');
    }
  }, [user]);

  // Save onboarding status
  useEffect(() => {
    localStorage.setItem('konnect_onboarding_completed', hasCompletedOnboarding.toString());
  }, [hasCompletedOnboarding]);

  return (
    <UserContext.Provider
      value={{
        user,
        setUser,
        isAuthenticated: !!user,
        hasCompletedOnboarding,
        setHasCompletedOnboarding,
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}
