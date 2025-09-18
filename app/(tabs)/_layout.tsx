import { Tabs } from 'expo-router';
import { Chrome as Home, Search, ShoppingCart, Package, User, ChartBar as BarChart3, List, Plus } from 'lucide-react-native';
import { theme } from '@/constants/Colors';
import { useContext } from 'react';
// import { UserContext } from '@/contexts/UserContext';

export default function TabLayout() {
  // This would normally come from context, but we'll mock it for now
  const userRole = 'buyer' as 'buyer' | 'seller'; // or 'seller'

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: theme.surface,
          // borderTopColor: theme.border,
          // borderTopWidth: 1,
          paddingVertical: 5,

          height: 70,
        },
        tabBarActiveTintColor: theme.primary,
        tabBarInactiveTintColor: theme.textMuted,
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
      }}
    >
      {/* Buyer tabs */}
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, size }) => <Home color={color} size={size} />,
          href: userRole === 'buyer' ? '/' : null,
        }}
      />
      <Tabs.Screen
        name="search"
        options={{
          title: 'Search',
          tabBarIcon: ({ color, size }) => <Search color={color} size={size} />,
          href: userRole === 'buyer' ? '/search' : null,
        }}
      />
      <Tabs.Screen
        name="cart"
        options={{
          title: 'Cart',
          tabBarIcon: ({ color, size }) => (
            <ShoppingCart color={color} size={size} />
          ),
          href: userRole === 'buyer' ? '/cart' : null,
        }}
      />

      {/* Seller tabs */}
      <Tabs.Screen
        name="dashboard"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color, size }) => (
            <BarChart3 color={color} size={size} />
          ),
          href: userRole === 'seller' ? '/dashboard' : null, // Hide for buyers
        }}
      />
      <Tabs.Screen
        name="listings"
        options={{
          title: 'Listings',
          tabBarIcon: ({ color, size }) => <List color={color} size={size} />,
          href: userRole === 'seller' ? '/listings' : null,
        }}
      />
      <Tabs.Screen
        name="add-listing"
        options={{
          title: 'Add',
          tabBarIcon: ({ color, size }) => <Plus color={color} size={size} />,
          href: userRole === 'seller' ? '/add-listing' : null,
        }}
      />

      {/* Shared tabs */}
      <Tabs.Screen
        name="orders"
        options={{
          title: 'Orders',
          tabBarIcon: ({ color, size }) => (
            <Package color={color} size={size} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => <User color={color} size={size} />,
        }}
      />
    </Tabs>
  );
}