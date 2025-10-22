import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { UserProvider, useUser } from './contexts/UserContext';
import { CartProvider } from './contexts/CartContext';
import { Toaster } from './components/ui/sonner';
import { WelcomeScreen } from './components/WelcomeScreen';
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
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
}

function OnboardingRoute({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

function RootRedirect() {
  const { isAuthenticated, user } = useUser();
  
  if (isAuthenticated && user?.walletAddress) {
    return <Navigate to="/home" replace />;
  }
  
  return <WelcomeScreen />;
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
          
          {/* Catch all - redirect to home or welcome */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </CartProvider>
      </UserProvider>
    </BrowserRouter>
  );
}
