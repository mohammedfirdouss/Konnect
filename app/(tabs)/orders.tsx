import React from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  FlatList,
  Image,
  TouchableOpacity 
} from 'react-native';
import { theme } from '@/constants/Colors';
import { mockOrders, Order } from '@/constants/MockData';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { MapPin, Clock, CircleCheck as CheckCircle } from 'lucide-react-native';
import { router } from 'expo-router';

export default function OrdersScreen() {
  const getStatusColor = (status: Order['status']) => {
    switch (status) {
      case 'pending': return theme.warning;
      case 'confirmed': return theme.primary;
      case 'delivering': return theme.accent;
      case 'delivered': return theme.success;
      case 'disputed': return theme.danger;
      default: return theme.textMuted;
    }
  };

  const getStatusText = (status: Order['status']) => {
    switch (status) {
      case 'pending': return 'Order Pending';
      case 'confirmed': return 'Confirmed';
      case 'delivering': return 'Out for Delivery';
      case 'delivered': return 'Delivered';
      case 'disputed': return 'Disputed';
      default: return status;
    }
  };

  const renderOrder = ({ item }: { item: Order }) => (
    <Card style={styles.orderCard}>
      <View style={styles.orderHeader}>
        <Image
          source={{ uri: item.product.images[0] }}
          style={styles.productImage}
        />
        <View style={styles.orderInfo}>
          <Text style={styles.productTitle}>{item.product.title}</Text>
          <Text style={styles.sellerName}>{item.product.seller.name}</Text>
          <Text style={styles.orderDate}>
            {item.createdAt.toLocaleDateString()}
          </Text>
        </View>
        <View style={styles.orderMeta}>
          <Text style={styles.orderAmount}>{item.totalAmount} SOL</Text>
          <Text
            style={{
              fontSize: 12,
              fontWeight: '600',
              color:
                item.escrowStatus === 'held' ? theme.warning : theme.success,
              marginBottom: 4,
            }}
          >
            {item.escrowStatus === 'held'
              ? `🔒 ${item.escrowAmount} SOL Secured`
              : `✅ ${item.escrowAmount} SOL Released`}
          </Text>
          <Text style={styles.statusText}>{getStatusText(item.status)}</Text>
        </View>
      </View>

      <View style={styles.escrowSection}>
        <View style={styles.escrowStatus}>
          <Text style={styles.escrowLabel}>Escrow Status:</Text>
          <Text
            style={[
              styles.escrowValue,
              {
                color:
                  item.escrowStatus === 'held' ? theme.warning : theme.success,
              },
            ]}
          >
            {item.escrowStatus === 'held' ? '🔒 Funds Secured' : '✅ Released'}
          </Text>
        </View>
      </View>

      <View style={styles.orderActions}>
        <Button
          title="Track Order"
          variant="outline"
          size="small"
          onPress={() => router.push(`/order-tracking/${item.id}`)}
          style={styles.trackButton}
        />
        {item.status === 'delivered' && item.escrowStatus === 'held' && (
          <Button
            title="Confirm Delivery"
            size="small"
            onPress={() => router.push(`/order-tracking/${item.id}`)}
            style={styles.confirmButton}
          />
        )}
      </View>
    </Card>
  );

  if (mockOrders.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>My Orders</Text>
        </View>
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No orders yet</Text>
          <Text style={styles.emptySubtext}>
            Start shopping to see your orders here
          </Text>
          <Button
            title="Browse Products"
            onPress={() => router.push('/search')}
            style={styles.browseButton}
          />
        </View>
      </SafeAreaView>
    );
  }

  if ([].length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>My Orders</Text>
        </View>
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No orders found</Text>
          <Text style={styles.emptySubtext}>
            Browse products to start shopping
          </Text>
          <Button
            title="Explore Marketplace"
            onPress={() => router.push('/search')}
            // style={styles.}
          />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>My Orders</Text>
        <Text style={styles.orderCount}>{mockOrders.length} orders</Text>
      </View>

      <FlatList
        data={mockOrders}
        renderItem={renderOrder}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.ordersList}
        showsVerticalScrollIndicator={false}
      />
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.text,
  },
  orderCount: {
    fontSize: 14,
    color: theme.textMuted,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.text,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 16,
    color: theme.textMuted,
    textAlign: 'center',
    marginBottom: 24,
  },
  browseButton: {
    minWidth: 200,
  },
  ordersList: {
    padding: 20,
    paddingTop: 10,
  },
  orderCard: {
    marginBottom: 16,
  },
  orderHeader: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  productImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    marginRight: 12,
  },
  orderInfo: {
    flex: 1,
  },
  productTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.text,
    marginBottom: 4,
  },
  sellerName: {
    fontSize: 12,
    color: theme.textMuted,
    marginBottom: 2,
  },
  orderDate: {
    fontSize: 12,
    color: theme.textMuted,
  },
  orderMeta: {
    alignItems: 'flex-end',
  },
  orderAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.accent,
    marginBottom: 8,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
    color: theme.text,
  },
  escrowSection: {
    borderTopWidth: 1,
    borderTopColor: theme.border,
    paddingTop: 12,
    marginBottom: 12,
  },
  escrowStatus: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  escrowLabel: {
    fontSize: 12,
    color: theme.textMuted,
  },
  escrowValue: {
    fontSize: 12,
    fontWeight: '600',
  },
  orderActions: {
    flexDirection: 'row',
    gap: 8,
  },
  trackButton: {
    flex: 1,
  },
  confirmButton: {
    flex: 1,
  },
});