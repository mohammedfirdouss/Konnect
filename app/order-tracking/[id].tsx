import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  ScrollView,
  TouchableOpacity,
  Alert 
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { theme } from '@/constants/Colors';
import { mockOrders } from '@/constants/MockData';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ArrowLeft, Package, Truck, CircleCheck as CheckCircle, Shield, MapPin, Clock } from 'lucide-react-native';

export default function OrderTrackingScreen() {
  const { id } = useLocalSearchParams();
  const [order, setOrder] = useState(mockOrders.find(o => o.id === id));

  if (!order) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.errorText}>Order not found</Text>
      </SafeAreaView>
    );
  }

  const getStatusSteps = () => {
    const steps = [
      { id: 'pending', title: 'Order Placed', icon: Package, completed: true },
      { id: 'confirmed', title: 'Order Confirmed', icon: CheckCircle, completed: order.status !== 'pending' },
      { id: 'delivering', title: 'Out for Delivery', icon: Truck, completed: ['delivering', 'delivered'].includes(order.status) },
      { id: 'delivered', title: 'Delivered', icon: CheckCircle, completed: order.status === 'delivered' },
    ];
    return steps;
  };

  const handleConfirmDelivery = () => {
    Alert.alert(
      'Confirm Delivery',
      `Are you sure you want to confirm delivery? This will release ${order.escrowAmount} SOL from escrow to the seller.`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Confirm', 
          onPress: () => {
            setOrder(prev => prev ? { ...prev, status: 'delivered', escrowStatus: 'released' } : null);
            Alert.alert('Success', 'Delivery confirmed! Funds have been released to the seller.');
          }
        }
      ]
    );
  };

  const handleDispute = () => {
    Alert.alert(
      'Dispute Order',
      'This will start a dispute resolution process. Our team will review your case.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Start Dispute', 
          style: 'destructive',
          onPress: () => {
            setOrder(prev => prev ? { ...prev, status: 'disputed', escrowStatus: 'disputed' } : null);
            Alert.alert('Dispute Started', 'Your dispute has been submitted. We will contact you within 24 hours.');
          }
        }
      ]
    );
  };

  const steps = getStatusSteps();
  const currentStepIndex = steps.findIndex(step => step.id === order.status);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <ArrowLeft color={theme.text} size={24} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Track Order</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Order Info */}
        <Card style={styles.orderCard}>
          <Text style={styles.orderTitle}>{order.product.title}</Text>
          <Text style={styles.orderSeller}>from {order.product.seller.name}</Text>
          <View style={styles.orderMeta}>
            <Text style={styles.orderAmount}>${order.totalAmount}</Text>
            <Text style={styles.trackingId}>#{order.trackingId}</Text>
          </View>
        </Card>

        {/* Tracking Steps */}
        <Card style={styles.trackingCard}>
          <Text style={styles.sectionTitle}>Order Status</Text>
          <View style={styles.stepsContainer}>
            {steps.map((step, index) => {
              const StepIcon = step.icon;
              const isActive = index === currentStepIndex;
              const isCompleted = step.completed;
              
              return (
                <View key={step.id} style={styles.stepContainer}>
                  <View style={styles.stepLeft}>
                    <View style={[
                      styles.stepIcon,
                      isCompleted && styles.stepIconCompleted,
                      isActive && styles.stepIconActive,
                    ]}>
                      <StepIcon 
                        color={isCompleted ? theme.text : theme.textMuted} 
                        size={20} 
                      />
                    </View>
                    {index < steps.length - 1 && (
                      <View style={[
                        styles.stepLine,
                        isCompleted && styles.stepLineCompleted,
                      ]} />
                    )}
                  </View>
                  <View style={styles.stepContent}>
                    <Text style={[
                      styles.stepTitle,
                      isCompleted && styles.stepTitleCompleted,
                      isActive && styles.stepTitleActive,
                    ]}>
                      {step.title}
                    </Text>
                    {isActive && (
                      <Text style={styles.stepTime}>
                        {order.status === 'delivering' ? 'Estimated delivery: 2-3 hours' : 'In progress...'}
                      </Text>
                    )}
                  </View>
                </View>
              );
            })}
          </View>
        </Card>

        {/* Escrow Status */}
        <Card style={styles.escrowCard}>
          <View style={styles.escrowHeader}>
            <Shield color={theme.accent} size={20} />
            <Text style={styles.escrowTitle}>Escrow Status</Text>
          </View>
          <View style={styles.escrowInfo}>
            <Text style={styles.escrowAmount}>{order.escrowAmount} SOL</Text>
            <Text style={[
              styles.escrowStatus,
              { color: order.escrowStatus === 'held' ? theme.warning : theme.success }
            ]}>
              {order.escrowStatus === 'held' ? '🔒 Funds Secured' : '✅ Released to Seller'}
            </Text>
          </View>
          <Text style={styles.escrowDescription}>
            {order.escrowStatus === 'held' 
              ? 'Your payment is safely held in escrow until you confirm delivery.'
              : 'Funds have been released to the seller after delivery confirmation.'
            }
          </Text>
          <Text style={styles.walletAddress}>
            Escrow Wallet: {order.escrowWallet}
          </Text>
        </Card>

        {/* Delivery Location */}
        <Card style={styles.locationCard}>
          <View style={styles.locationHeader}>
            <MapPin color={theme.primary} size={20} />
            <Text style={styles.locationTitle}>Delivery Location</Text>
          </View>
          <Text style={styles.locationAddress}>{order.product.location}</Text>
          <Text style={styles.locationCampus}>{order.product.seller.campus}</Text>
        </Card>

        {/* Actions */}
        {order.status === 'delivered' && order.escrowStatus === 'held' && (
          <View style={styles.actionsContainer}>
            <Button
              title="Confirm Delivery"
              onPress={handleConfirmDelivery}
              style={styles.confirmButton}
            />
            <Button
              title="Report Issue"
              variant="outline"
              onPress={handleDispute}
              style={styles.disputeButton}
            />
          </View>
        )}

        {order.status === 'delivering' && (
          <View style={styles.actionsContainer}>
            <Button
              title="Contact Seller"
              variant="outline"
              onPress={() => Alert.alert('Feature Coming Soon', 'Direct messaging will be available soon!')}
              style={styles.contactButton}
            />
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.border,
  },
  backButton: {
    padding: 4,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.text,
  },
  placeholder: {
    width: 32,
  },
  errorText: {
    fontSize: 18,
    color: theme.text,
    textAlign: 'center',
    marginTop: 100,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  orderCard: {
    marginBottom: 20,
  },
  orderTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.text,
    marginBottom: 4,
  },
  orderSeller: {
    fontSize: 14,
    color: theme.textMuted,
    marginBottom: 12,
  },
  orderMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  orderAmount: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.accent,
  },
  trackingId: {
    fontSize: 14,
    color: theme.textMuted,
  },
  trackingCard: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
    marginBottom: 16,
  },
  stepsContainer: {
    paddingLeft: 8,
  },
  stepContainer: {
    flexDirection: 'row',
    marginBottom: 24,
  },
  stepLeft: {
    alignItems: 'center',
    marginRight: 16,
  },
  stepIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: theme.surface,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: theme.border,
  },
  stepIconCompleted: {
    backgroundColor: theme.accent,
    borderColor: theme.accent,
  },
  stepIconActive: {
    backgroundColor: theme.primary,
    borderColor: theme.primary,
  },
  stepLine: {
    width: 2,
    height: 24,
    backgroundColor: theme.border,
    marginTop: 8,
  },
  stepLineCompleted: {
    backgroundColor: theme.accent,
  },
  stepContent: {
    flex: 1,
    paddingTop: 8,
  },
  stepTitle: {
    fontSize: 16,
    color: theme.textMuted,
    marginBottom: 4,
  },
  stepTitleCompleted: {
    color: theme.text,
    fontWeight: '600',
  },
  stepTitleActive: {
    color: theme.primary,
    fontWeight: '600',
  },
  stepTime: {
    fontSize: 14,
    color: theme.textMuted,
  },
  escrowCard: {
    marginBottom: 20,
  },
  escrowHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  escrowTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
    marginLeft: 8,
  },
  escrowInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  escrowAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.accent,
  },
  escrowStatus: {
    fontSize: 14,
    fontWeight: '600',
  },
  escrowDescription: {
    fontSize: 14,
    color: theme.textSecondary,
    lineHeight: 20,
    marginBottom: 8,
  },
  walletAddress: {
    fontSize: 12,
    color: theme.textMuted,
    fontFamily: 'monospace',
  },
  locationCard: {
    marginBottom: 20,
  },
  locationHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  locationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
    marginLeft: 8,
  },
  locationAddress: {
    fontSize: 16,
    color: theme.text,
    marginBottom: 4,
  },
  locationCampus: {
    fontSize: 14,
    color: theme.textMuted,
  },
  actionsContainer: {
    gap: 12,
    marginBottom: 40,
  },
  confirmButton: {
    width: '100%',
  },
  disputeButton: {
    width: '100%',
  },
  contactButton: {
    width: '100%',
  },
});