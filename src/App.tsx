import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { UserProvider, useUser } from './contexts/UserContext';
import { CartProvider } from './contexts/CartContext';
import { Toaster } from './components/ui/sonner';
import { WelcomeScreen } from './components/WelcomeScreen';
import { Login } from './components/Login';
import { Registration } from './components/Registration';
import { RoleSelection } from './components/RoleSelection';
import { PersonalInfo } from './components/PersonalInfo';
import { WalletCreation } from './components/WalletCreation';
import { MainLayout } from './components/MainLayout';
import { ProductDetail } from './components/ProductDetail';
import { OrderTracking } from './components/OrderTracking';
import { HomeTab } from './components/tabs/HomeTab';
import { MarketplaceTab } from './components/tabs/MarketplaceTab';
import { CartTab } from './components/tabs/CartTab';
import { WalletTab } from './components/tabs/WalletTab';
import { BillsTab } from './components/tabs/BillsTab';
import { GamificationTab } from './components/tabs/GamificationTab';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useUser();
  
  if (!isAuthenticated || !user?.walletAddress) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function OnboardingRoute({ children }: { children: React.ReactNode }) {
  const { hasCompletedOnboarding } = useUser();
  
  // If user has already completed onboarding, redirect to login
  if (hasCompletedOnboarding) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function RootRedirect() {
  const { isAuthenticated, user, hasCompletedOnboarding } = useUser();
  
  // If authenticated with wallet, go to home
  if (isAuthenticated && user?.walletAddress) {
    return <Navigate to="/home" replace />;
  }
  
  // If onboarding is complete but not authenticated, go to login
  if (hasCompletedOnboarding) {
    return <Navigate to="/login" replace />;
  }
  
  // Otherwise show welcome screen
  return <WelcomeScreen />;
}

function LoginRedirect() {
  const { isAuthenticated, user } = useUser();
  
  // If authenticated, go to home
  if (isAuthenticated && user?.walletAddress) {
    return <Navigate to="/home" replace />;
  }
  
  // Otherwise show login page (it will handle invalid credentials)
  return <Login />;
}

export default function App() {
  return (
    <BrowserRouter>
      <UserProvider>
        <CartProvider>
          <Toaster 
            position="top-center" 
            toastOptions={{
              style: {
                background: '#1E1E1E',
                color: '#FFFFFF',
                border: '1px solid #333333',
              },
            }}
          />
          <Routes>
            {/* Welcome/Root */}
            <Route path="/" element={<RootRedirect />} />
            
            {/* Auth Routes */}
            <Route path="/login" element={<LoginRedirect />} />
            <Route path="/register" element={<Registration />} />
            
            {/* Onboarding Routes */}
            <Route 
              path="/role" 
              element={
                <OnboardingRoute>
                  <RoleSelection />
                </OnboardingRoute>
              } 
            />
            <Route 
              path="/personal-info" 
              element={
                <OnboardingRoute>
                  <PersonalInfo />
                </OnboardingRoute>
              } 
            />
            <Route 
              path="/wallet-creation" 
              element={
                <OnboardingRoute>
                  <WalletCreation />
                </OnboardingRoute>
              } 
            />
            
            {/* Protected Main App Routes */}
            <Route
              path="/home"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <HomeTab />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/marketplace"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <MarketplaceTab />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/product/:id"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <ProductDetail />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/order/:orderId"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <OrderTracking />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/cart"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <CartTab />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/wallet"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <WalletTab />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/bills"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <BillsTab />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/gamification"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <GamificationTab />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            
            {/* Catch all - redirect to root */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </CartProvider>
      </UserProvider>
    </BrowserRouter>
  );
}
