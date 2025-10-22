# Konnect PWA - Next.js Routing Guide

## 🔀 Application Structure

The application uses **Next.js App Router** with file-based routing for a complete PWA experience.

## 📁 Route Structure

### Onboarding Flow
- `/` - Welcome screen (redirects to `/home` if authenticated)
- `/auth` - Sign up / Login
- `/role` - Role selection (Buyer / Seller / Both)
- `/wallet-setup` - Wallet creation & phone verification
- `/notifications` - Notification preferences
- `/tutorial` - Onboarding tutorial (can be skipped)

### Main Application (Protected Routes)
All routes under `/(main)` require authentication and redirect to `/` if not logged in.

- `/home` - Personalized dashboard with AI recommendations
- `/marketplace` - Browse goods/services (Buyer) OR manage listings (Seller)
- `/cart` - Cart management (Buyer) OR order fulfillment (Seller)
- `/wallet` - Balance, transactions, escrow summary
- `/bills` - Pay airtime, utilities, subscriptions
- `/gamification` - Levels, badges, leaderboard

## 🔐 Authentication Flow

### State Management
User state is managed via React Context (`UserContext`) with localStorage persistence:

```typescript
const { user, setUser, isAuthenticated } = useUser();
```

### Protected Routes
The `(main)` layout checks authentication and redirects unauthenticated users:

```typescript
if (!isAuthenticated || !user?.walletAddress) {
  router.push('/');
}
```

### Logout
Clears localStorage and redirects to welcome screen:

```typescript
localStorage.removeItem('konnect_user');
router.push('/');
```

## 🧭 Navigation Patterns

### Programmatic Navigation
```typescript
import { useRouter } from 'next/navigation';

const router = useRouter();
router.push('/home');
```

### Bottom Navigation
Clicking tabs in `BottomNav` triggers route changes:

```typescript
const handleTabChange = (tab: string) => {
  router.push(`/${tab}`);
};
```

### Search Functionality
Search query is passed via URL params:
```typescript
// In TopBar
router.push(`/marketplace?q=${searchQuery}`);

// In MarketplacePage
const searchParams = useSearchParams();
const searchQuery = searchParams.get('q') || '';
```

## 📱 PWA Features

### Manifest
Located at `/app/manifest.json` with:
- Standalone display mode
- Portrait orientation
- Custom theme colors (#9945FF - Solana Purple)
- Icon specifications

### Metadata
Defined in `/app/layout.tsx`:
```typescript
export const metadata: Metadata = {
  title: 'Konnect - Campus Economy Hub',
  manifest: '/manifest.json',
  themeColor: '#9945FF',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
  },
};
```

## 🔄 Route Guards

### Onboarding Progression
Each onboarding step checks for prerequisite completion:

- `/auth` - No prerequisites
- `/role` - Requires user data
- `/wallet-setup` - Requires role selection
- `/notifications` - Requires wallet address
- `/tutorial` - Requires notification setup
- `/home` - Requires complete onboarding

### Example Guard
```typescript
useEffect(() => {
  if (!user || !user.role) {
    router.push('/role');
  }
}, [user, router]);
```

## 🎯 Deep Linking

All routes support direct access via URL:
- `https://konnect.app/marketplace` - Direct to marketplace
- `https://konnect.app/wallet` - Direct to wallet
- `https://konnect.app/bills` - Direct to bills

Unauthenticated users will be redirected through onboarding flow.

## 📊 Route Groups

### (main) Group
Uses route grouping `(main)` to share layout without affecting URL:
- Shared: TopBar, BottomNav, HamburgerMenu
- All tabs inherit main layout
- URL stays clean: `/home` not `/(main)/home`

## 🔍 Current Route Detection

The layout detects active route for bottom nav highlighting:

```typescript
const getCurrentTab = () => {
  if (pathname.includes('/home')) return 'home';
  if (pathname.includes('/marketplace')) return 'marketplace';
  // ...
};
```

## 🚀 Future Enhancements

Potential routing improvements:
- Dynamic routes for product details: `/marketplace/[id]`
- User profiles: `/profile/[userId]`
- Transaction details: `/wallet/transaction/[id]`
- Category filtering: `/marketplace?category=electronics`
- Pagination: `/marketplace?page=2`
