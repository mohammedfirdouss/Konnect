import { Tabs } from 'expo-router';
import { Chrome as Home, Search, ShoppingCart, Package, User, ChartBar as BarChart3, List, Plus } from 'lucide-react-native';
import { theme } from '@/constants/Colors';
import { useContext, useEffect, useState } from 'react';
import { StorageService } from '@/services/StorageService';
import { STORAGE_KEYS } from '@/constants/storageKeys';
// import { UserContext } from '@/contexts/UserContext';
export default function TabLayout() {
  const [role, setRole] = useState('buyer');
  const [roleLoaded, setRoleLoaded] = useState(false);

  const handleUserRole = async () => {
    try {
      const user = await StorageService.getItem(STORAGE_KEYS.ROLE);
      setRole(user || 'buyer');
    } catch (error) {
      console.error('Error loading user role:', error);
    } finally {
      setRoleLoaded(true);
    }
  };

  useEffect(() => {
    handleUserRole();
  }, []);

  if (!roleLoaded) {
    return null;
  }

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
          href: role === 'buyer' ? '/' : null,
        }}
      />
      <Tabs.Screen
        name="search"
        options={{
          title: 'Search',
          tabBarIcon: ({ color, size }) => <Search color={color} size={size} />,
          href: role === 'buyer' ? '/search' : null,
        }}
      />
      <Tabs.Screen
        name="cart"
        options={{
          title: 'Cart',
          tabBarIcon: ({ color, size }) => (
            <ShoppingCart color={color} size={size} />
          ),
          href: role === 'buyer' ? '/cart' : null,
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
          href: role === 'seller' ? '/dashboard' : null, // Hide for buyers
        }}
      />
      <Tabs.Screen
        name="listings"
        options={{
          title: 'Listings',
          tabBarIcon: ({ color, size }) => <List color={color} size={size} />,
          href: role === 'seller' ? '/listings' : null,
        }}
      />
      <Tabs.Screen
        name="add-listing"
        options={{
          title: 'Add',
          tabBarIcon: ({ color, size }) => <Plus color={color} size={size} />,
          href: role === 'seller' ? '/add-listing' : null,
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
    {/* <Tabs.Screen
        name="product"
        options={{
          href: null, // Hide from tab bar
        }}
    
      /> */}
    </Tabs>
  );
}