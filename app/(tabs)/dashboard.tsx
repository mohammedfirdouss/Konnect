import React from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  ScrollView,
  TouchableOpacity 
} from 'react-native';
import { theme } from '@/constants/Colors';
import { mockSellerStats } from '@/constants/MockData';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { TrendingUp, Package, Eye, DollarSign, Star, Plus } from 'lucide-react-native';
import { router } from 'expo-router';

export default function DashboardScreen() {
  const stats = mockSellerStats;

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Seller Dashboard</Text>
          <Text style={styles.subtitle}>Welcome back, Alex! 👋</Text>
        </View>

        {/* Quick Stats */}
        <View style={styles.statsGrid}>
          <Card style={styles.statCard}>
            <DollarSign color={theme.accent} size={24} />
            <Text style={styles.statNumber}>${stats.totalRevenue}</Text>
            <Text style={styles.statLabel}>Total Revenue</Text>
          </Card>
          
          <Card style={styles.statCard}>
            <Package color={theme.primary} size={24} />
            <Text style={styles.statNumber}>{stats.totalSales}</Text>
            <Text style={styles.statLabel}>Total Sales</Text>
          </Card>
          
          <Card style={styles.statCard}>
            <Eye color={theme.warning} size={24} />
            <Text style={styles.statNumber}>{stats.activeListings}</Text>
            <Text style={styles.statLabel}>Active Listings</Text>
          </Card>
          
          <Card style={styles.statCard}>
            <Star color={theme.warning} size={24} fill={theme.warning} />
            <Text style={styles.statNumber}>{stats.rating}</Text>
            <Text style={styles.statLabel}>Rating</Text>
          </Card>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionsGrid}>
            <TouchableOpacity 
              style={styles.actionCard}
              onPress={() => router.push('/add-listing')}
            >
              <Plus color={theme.primary} size={32} />
              <Text style={styles.actionTitle}>Add Listing</Text>
              <Text style={styles.actionSubtitle}>Create new product or service</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.actionCard}
              onPress={() => router.push('/listings')}
            >
              <Package color={theme.accent} size={32} />
              <Text style={styles.actionTitle}>Manage Listings</Text>
              <Text style={styles.actionSubtitle}>Edit your products</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Recent Activity */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          <Card style={styles.activityCard}>
            <View style={styles.activityItem}>
              <View style={styles.activityIcon}>
                <TrendingUp color={theme.accent} size={16} />
              </View>
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>New order received</Text>
                <Text style={styles.activityTime}>2 hours ago</Text>
              </View>
            </View>
            
            <View style={styles.activityItem}>
              <View style={styles.activityIcon}>
                <Eye color={theme.primary} size={16} />
              </View>
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>Calculus Textbook viewed 5 times</Text>
                <Text style={styles.activityTime}>4 hours ago</Text>
              </View>
            </View>
            
            <View style={styles.activityItem}>
              <View style={styles.activityIcon}>
                <DollarSign color={theme.warning} size={16} />
              </View>
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>Payment received: $75</Text>
                <Text style={styles.activityTime}>1 day ago</Text>
              </View>
            </View>
          </Card>
        </View>

        {/* Performance Overview */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>This Month</Text>
          <Card style={styles.performanceCard}>
            <View style={styles.performanceRow}>
              <Text style={styles.performanceLabel}>Revenue</Text>
              <Text style={styles.performanceValue}>$324</Text>
            </View>
            <View style={styles.performanceRow}>
              <Text style={styles.performanceLabel}>Orders</Text>
              <Text style={styles.performanceValue}>12</Text>
            </View>
            <View style={styles.performanceRow}>
              <Text style={styles.performanceLabel}>Views</Text>
              <Text style={styles.performanceValue}>156</Text>
            </View>
          </Card>
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
  subtitle: {
    fontSize: 16,
    color: theme.textMuted,
    marginTop: 4,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    // gap: 12,
    marginBottom: 24,
  },
  statCard: {
    width: '48%', // Ensures 2 columns
    marginBottom: 12,
    alignItems: 'center',
    paddingVertical: 20,
    backgroundColor: theme.surface, // Optional: for better separation
    borderRadius: 12, // Optional: for rounded corners
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.text,
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: theme.textMuted,
    textAlign: 'center',
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.text,
    marginBottom: 16,
  },
  actionsGrid: {
    flexDirection: 'row',
    gap: 12,
  },
  actionCard: {
    flex: 1,
    backgroundColor: theme.surface,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.text,
    marginTop: 8,
    marginBottom: 4,
  },
  actionSubtitle: {
    fontSize: 12,
    color: theme.textMuted,
    textAlign: 'center',
  },
  activityCard: {
    paddingVertical: 8,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
  },
  activityIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.background,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  activityContent: {
    flex: 1,
  },
  activityTitle: {
    fontSize: 14,
    color: theme.text,
    marginBottom: 2,
  },
  activityTime: {
    fontSize: 12,
    color: theme.textMuted,
  },
  performanceCard: {
    paddingVertical: 8,
  },
  performanceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
  },
  performanceLabel: {
    fontSize: 14,
    color: theme.textMuted,
  },
  performanceValue: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
  },
});