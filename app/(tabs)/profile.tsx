import React from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  Image,
  TouchableOpacity,
  ScrollView 
} from 'react-native';
import { theme } from '@/constants/Colors';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { User, MapPin, Star, Package, Settings, Bell, CircleHelp as HelpCircle, LogOut, Shield, ChevronRight } from 'lucide-react-native';
import { router } from 'expo-router';

export default function ProfileScreen() {
  const menuItems = [
    { 
      id: '1', 
      title: 'Account Settings', 
      icon: Settings, 
      action: () => router.push('/settings') 
    },
    { 
      id: '2', 
      title: 'Notifications', 
      icon: Bell, 
      action: () => router.push('/notifications') 
    },
    { 
      id: '3', 
      title: 'Order History', 
      icon: Package, 
      action: () => router.push('/orders') 
    },
    { 
      id: '4', 
      title: 'Safety Center', 
      icon: Shield, 
      action: () => router.push('/safety') 
    },
    { 
      id: '5', 
      title: 'Help & Support', 
      icon: HelpCircle, 
      action: () => router.push('/help') 
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Profile</Text>
        </View>

        {/* User Info Card */}
        <View style={styles.content}>
          <Card style={styles.userCard}>
            <View style={styles.userInfo}>
              <Image 
                source={{ uri: 'https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=1' }} 
                style={styles.avatar} 
              />
              <View style={styles.userDetails}>
                <Text style={styles.userName}>Alex Johnson</Text>
                <View style={styles.locationRow}>
                  <MapPin color={theme.textMuted} size={14} />
                  <Text style={styles.userLocation}>Stanford University</Text>
                </View>
                <View style={styles.ratingRow}>
                  <Star color={theme.warning} size={14} fill={theme.warning} />
                  <Text style={styles.userRating}>4.9 (23 reviews)</Text>
                </View>
              </View>
              <TouchableOpacity style={styles.editButton}>
                <User color={theme.primary} size={20} />
              </TouchableOpacity>
            </View>
          </Card>

          {/* Stats Cards */}
          <View style={styles.statsContainer}>
            <Card style={styles.statCard}>
              <Text style={styles.statNumber}>12</Text>
              <Text style={styles.statLabel}>Orders</Text>
            </Card>
            <Card style={styles.statCard}>
              <Text style={styles.statNumber}>$324</Text>
              <Text style={styles.statLabel}>Spent</Text>
            </Card>
            <Card style={styles.statCard}>
              <Text style={styles.statNumber}>4.9</Text>
              <Text style={styles.statLabel}>Rating</Text>
            </Card>
          </View>

          {/* Role Switch */}
          <Card style={styles.roleSwitchCard}>
            <Text style={styles.roleSwitchTitle}>Switch to Seller</Text>
            <Text style={styles.roleSwitchSubtitle}>Start selling on campus today</Text>
            <Button 
              title="Become a Seller" 
              onPress={() => router.push('/seller-onboarding')}
              variant="secondary"
              style={styles.roleSwitchButton}
            />
          </Card>

          {/* Menu Items */}
          <Card style={styles.menuCard}>
            {menuItems.map((item, index) => (
              <TouchableOpacity 
                key={item.id} 
                style={[
                  styles.menuItem,
                  index < menuItems.length - 1 && styles.menuItemBorder
                ]}
                onPress={item.action}
              >
                <item.icon color={theme.textMuted} size={20} />
                <Text style={styles.menuItemText}>{item.title}</Text>
                <ChevronRight color={theme.textMuted} size={16} />
              </TouchableOpacity>
            ))}
          </Card>

          {/* Logout Button */}
          <TouchableOpacity style={styles.logoutButton}>
            <LogOut color={theme.danger} size={20} />
            <Text style={styles.logoutText}>Sign Out</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.background,
    paddingTop: 50,
  },
  header: {
    padding: 20,
    paddingBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.text,
  },
  content: {
    padding: 20,
    paddingTop: 10,
  },
  userCard: {
    marginBottom: 20,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    marginRight: 16,
  },
  userDetails: {
    flex: 1,
  },
  userName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.text,
    marginBottom: 4,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  userLocation: {
    fontSize: 14,
    color: theme.textMuted,
    marginLeft: 4,
  },
  ratingRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  userRating: {
    fontSize: 14,
    color: theme.textMuted,
    marginLeft: 4,
  },
  editButton: {
    padding: 8,
  },
  statsContainer: {
    flexDirection: 'row',
    marginBottom: 20,
    gap: 12,
  },
  statCard: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 20,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.primary,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: theme.textMuted,
  },
  roleSwitchCard: {
    marginBottom: 20,
    alignItems: 'center',
    paddingVertical: 24,
  },
  roleSwitchTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.text,
    marginBottom: 4,
  },
  roleSwitchSubtitle: {
    fontSize: 14,
    color: theme.textMuted,
    marginBottom: 16,
    textAlign: 'center',
  },
  roleSwitchButton: {
    minWidth: 150,
  },
  menuCard: {
    marginBottom: 20,
    paddingVertical: 8,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 8,
  },
  menuItemBorder: {
    borderBottomWidth: 1,
    borderBottomColor: theme.border,
  },
  menuItemText: {
    flex: 1,
    fontSize: 16,
    color: theme.text,
    marginLeft: 12,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 24,
    backgroundColor: 'transparent',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.danger,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.danger,
    marginLeft: 8,
  },
});