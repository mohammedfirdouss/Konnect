import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  ScrollView,
  TouchableOpacity,
  Alert 
} from 'react-native';
import { theme } from '@/constants/Colors';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ArrowLeft, Shield, Wallet, CreditCard } from 'lucide-react-native';
import { router } from 'expo-router';

export default function CheckoutScreen() {
  const [paymentMethod, setPaymentMethod] = useState<'solana' | 'card'>('solana');
  const [walletAddress, setWalletAddress] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [notes, setNotes] = useState('');

  // Mock order data
  const orderTotal = 75;
  const solPrice = 35.50; // Mock SOL price in USD
  const solAmount = (orderTotal / solPrice).toFixed(4);

  const handlePlaceOrder = () => {
    Alert.alert(
      'Order Placed!',
      `Your order has been placed successfully. Payment of ${solAmount} SOL is now held in escrow.`,
      [
        { text: 'Track Order', onPress: () => router.push('/order-tracking/1') },
        { text: 'OK', onPress: () => router.push('/(tabs)') }
      ]
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <ArrowLeft color={theme.text} size={24} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Checkout</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Order Summary */}
        <Card style={styles.summaryCard}>
          <Text style={styles.sectionTitle}>Order Summary</Text>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Calculus Textbook</Text>
            <Text style={styles.summaryValue}>$75.00</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Platform Fee</Text>
            <Text style={styles.summaryValue}>$0.00</Text>
          </View>
          <View style={[styles.summaryRow, styles.totalRow]}>
            <Text style={styles.totalLabel}>Total</Text>
            <Text style={styles.totalValue}>${orderTotal}</Text>
          </View>
        </Card>

        {/* Payment Method */}
        <Card style={styles.paymentCard}>
          <Text style={styles.sectionTitle}>Payment Method</Text>
          
          <TouchableOpacity
            style={[
              styles.paymentOption,
              paymentMethod === 'solana' && styles.paymentOptionSelected,
            ]}
            onPress={() => setPaymentMethod('solana')}
          >
            <Wallet color={paymentMethod === 'solana' ? theme.primary : theme.textMuted} size={24} />
            <View style={styles.paymentInfo}>
              <Text style={[
                styles.paymentTitle,
                paymentMethod === 'solana' && styles.paymentTitleSelected,
              ]}>
                Solana Wallet
              </Text>
              <Text style={styles.paymentSubtitle}>
                Pay with SOL ({solAmount} SOL ≈ ${orderTotal})
              </Text>
            </View>
            <View style={[
              styles.radioButton,
              paymentMethod === 'solana' && styles.radioButtonSelected,
            ]} />
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.paymentOption,
              paymentMethod === 'card' && styles.paymentOptionSelected,
            ]}
            onPress={() => setPaymentMethod('card')}
          >
            <CreditCard color={paymentMethod === 'card' ? theme.primary : theme.textMuted} size={24} />
            <View style={styles.paymentInfo}>
              <Text style={[
                styles.paymentTitle,
                paymentMethod === 'card' && styles.paymentTitleSelected,
              ]}>
                Credit Card
              </Text>
              <Text style={styles.paymentSubtitle}>
                Traditional payment (converted to SOL)
              </Text>
            </View>
            <View style={[
              styles.radioButton,
              paymentMethod === 'card' && styles.radioButtonSelected,
            ]} />
          </TouchableOpacity>
        </Card>

        {/* Wallet Connection */}
        {paymentMethod === 'solana' && (
          <Card style={styles.walletCard}>
            <Text style={styles.sectionTitle}>Connect Wallet</Text>
            <Input
              placeholder="Enter your Solana wallet address"
              value={walletAddress}
              onChangeText={setWalletAddress}
            />
            <Button
              title="Connect Phantom Wallet"
              variant="outline"
              onPress={() => setWalletAddress('7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU')}
              style={styles.connectButton}
            />
          </Card>
        )}

        {/* Delivery Info */}
        <Card style={styles.deliveryCard}>
          <Text style={styles.sectionTitle}>Delivery Information</Text>
          <Input
            label="Campus Location"
            placeholder="e.g., Tresidder Union, Room 201"
            value={deliveryAddress}
            onChangeText={setDeliveryAddress}
          />
          <Input
            label="Special Instructions (Optional)"
            placeholder="Any special delivery notes..."
            value={notes}
            onChangeText={setNotes}
            multiline
            numberOfLines={3}
          />
        </Card>

        {/* Escrow Information */}
        <Card style={styles.escrowCard}>
          <View style={styles.escrowHeader}>
            <Shield color={theme.accent} size={24} />
            <Text style={styles.escrowTitle}>Escrow Protection</Text>
          </View>
          <Text style={styles.escrowDescription}>
            Your payment of {solAmount} SOL will be held securely in a Solana smart contract. 
            Funds are only released to the seller after you confirm delivery.
          </Text>
          <View style={styles.escrowSteps}>
            <Text style={styles.escrowStep}>1. Payment locked in escrow</Text>
            <Text style={styles.escrowStep}>2. Seller ships your item</Text>
            <Text style={styles.escrowStep}>3. You confirm delivery</Text>
            <Text style={styles.escrowStep}>4. Funds released to seller</Text>
          </View>
        </Card>
      </ScrollView>

      {/* Place Order Button */}
      <View style={styles.footer}>
        <Button
          title={`Place Order (${solAmount} SOL)`}
          onPress={handlePlaceOrder}
          style={styles.placeOrderButton}
        />
      </View>
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
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 20,
  },
  summaryCard: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.text,
    marginBottom: 16,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  summaryLabel: {
    fontSize: 14,
    color: theme.textSecondary,
  },
  summaryValue: {
    fontSize: 14,
    color: theme.text,
  },
  totalRow: {
    borderTopWidth: 1,
    borderTopColor: theme.border,
    marginTop: 8,
    paddingTop: 16,
  },
  totalLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
  },
  totalValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.accent,
  },
  paymentCard: {
    marginBottom: 20,
  },
  paymentOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.border,
    marginBottom: 12,
  },
  paymentOptionSelected: {
    borderColor: theme.primary,
    backgroundColor: theme.surfaceSecondary,
  },
  paymentInfo: {
    flex: 1,
    marginLeft: 12,
  },
  paymentTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
    marginBottom: 4,
  },
  paymentTitleSelected: {
    color: theme.primary,
  },
  paymentSubtitle: {
    fontSize: 14,
    color: theme.textMuted,
  },
  radioButton: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: theme.border,
  },
  radioButtonSelected: {
    borderColor: theme.primary,
    backgroundColor: theme.primary,
  },
  walletCard: {
    marginBottom: 20,
  },
  connectButton: {
    marginTop: 12,
  },
  deliveryCard: {
    marginBottom: 20,
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
  escrowDescription: {
    fontSize: 14,
    color: theme.textSecondary,
    lineHeight: 20,
    marginBottom: 16,
  },
  escrowSteps: {
    gap: 8,
  },
  escrowStep: {
    fontSize: 14,
    color: theme.textMuted,
  },
  footer: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: theme.border,
  },
  placeOrderButton: {
    width: '100%',
  },
});