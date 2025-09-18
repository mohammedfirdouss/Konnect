import React from 'react';
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
import { ArrowLeft, Shield, ExternalLink, Copy, Clock, CircleCheck as CheckCircle } from 'lucide-react-native';

export default function EscrowStatusScreen() {
  const { id } = useLocalSearchParams();
  const order = mockOrders.find(o => o.id === id);

  if (!order) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.errorText}>Order not found</Text>
      </SafeAreaView>
    );
  }

  const copyToClipboard = (text: string) => {
    Alert.alert('Copied', 'Wallet address copied to clipboard');
  };

  const viewOnExplorer = () => {
    Alert.alert('Solana Explorer', 'This would open the transaction in Solana Explorer');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <ArrowLeft color={theme.text} size={24} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Escrow Status</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Escrow Overview */}
        <Card style={styles.overviewCard}>
          <View style={styles.escrowHeader}>
            <Shield color={theme.accent} size={32} />
            <View style={styles.escrowInfo}>
              <Text style={styles.escrowAmount}>{order.escrowAmount} SOL</Text>
              <Text style={[
                styles.escrowStatus,
                { color: order.escrowStatus === 'held' ? theme.warning : theme.success }
              ]}>
                {order.escrowStatus === 'held' ? 'Funds Secured in Escrow' : 'Funds Released'}
              </Text>
            </View>
          </View>
          
          <Text style={styles.escrowDescription}>
            {order.escrowStatus === 'held' 
              ? 'Your payment is safely locked in a Solana smart contract until delivery is confirmed.'
              : 'Funds have been successfully released to the seller after delivery confirmation.'
            }
          </Text>
        </Card>

        {/* Transaction Details */}
        <Card style={styles.detailsCard}>
          <Text style={styles.sectionTitle}>Transaction Details</Text>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Order ID</Text>
            <Text style={styles.detailValue}>#{order.id}</Text>
          </View>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Amount</Text>
            <Text style={styles.detailValue}>{order.escrowAmount} SOL</Text>
          </View>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>USD Value</Text>
            <Text style={styles.detailValue}>${order.totalAmount}</Text>
          </View>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Created</Text>
            <Text style={styles.detailValue}>{order.createdAt.toLocaleDateString()}</Text>
          </View>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Status</Text>
            <View style={styles.statusContainer}>
              {order.escrowStatus === 'held' ? (
                <Clock color={theme.warning} size={16} />
              ) : (
                <CheckCircle color={theme.success} size={16} />
              )}
              <Text style={[
                styles.statusText,
                { color: order.escrowStatus === 'held' ? theme.warning : theme.success }
              ]}>
                {order.escrowStatus === 'held' ? 'In Escrow' : 'Released'}
              </Text>
            </View>
          </View>
        </Card>

        {/* Wallet Information */}
        <Card style={styles.walletCard}>
          <Text style={styles.sectionTitle}>Escrow Wallet</Text>
          
          <View style={styles.walletRow}>
            <Text style={styles.walletLabel}>Smart Contract Address</Text>
            <View style={styles.walletAddressContainer}>
              <Text style={styles.walletAddress}>{order.escrowWallet}</Text>
              <TouchableOpacity 
                onPress={() => copyToClipboard(order.escrowWallet)}
                style={styles.copyButton}
              >
                <Copy color={theme.primary} size={16} />
              </TouchableOpacity>
            </View>
          </View>
          
          <Button
            title="View on Solana Explorer"
            variant="outline"
            onPress={viewOnExplorer}
            style={styles.explorerButton}
          />
        </Card>

        {/* How It Works */}
        <Card style={styles.howItWorksCard}>
          <Text style={styles.sectionTitle}>How Escrow Works</Text>
          
          <View style={styles.stepsList}>
            <View style={styles.step}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>1</Text>
              </View>
              <Text style={styles.stepText}>
                Your payment is locked in a Solana smart contract
              </Text>
            </View>
            
            <View style={styles.step}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>2</Text>
              </View>
              <Text style={styles.stepText}>
                Seller ships your item and provides tracking
              </Text>
            </View>
            
            <View style={styles.step}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>3</Text>
              </View>
              <Text style={styles.stepText}>
                You confirm delivery through the app
              </Text>
            </View>
            
            <View style={styles.step}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>4</Text>
              </View>
              <Text style={styles.stepText}>
                Funds are automatically released to the seller
              </Text>
            </View>
          </View>
        </Card>

        {/* Actions */}
        {order.escrowStatus === 'held' && order.status === 'delivered' && (
          <View style={styles.actionsContainer}>
            <Button
              title="Confirm Delivery & Release Funds"
              onPress={() => router.push(`/order-tracking/${order.id}`)}
              style={styles.releaseButton}
            />
            <Button
              title="Report Issue"
              variant="outline"
              onPress={() => Alert.alert('Dispute', 'This would start a dispute process')}
              style={styles.disputeButton}
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
  overviewCard: {
    marginBottom: 20,
  },
  escrowHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  escrowInfo: {
    marginLeft: 16,
  },
  escrowAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.accent,
    marginBottom: 4,
  },
  escrowStatus: {
    fontSize: 16,
    fontWeight: '600',
  },
  escrowDescription: {
    fontSize: 14,
    color: theme.textSecondary,
    lineHeight: 20,
  },
  detailsCard: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
    marginBottom: 16,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.border,
  },
  detailLabel: {
    fontSize: 14,
    color: theme.textMuted,
  },
  detailValue: {
    fontSize: 14,
    color: theme.text,
    fontWeight: '500',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusText: {
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 6,
  },
  walletCard: {
    marginBottom: 20,
  },
  walletRow: {
    marginBottom: 16,
  },
  walletLabel: {
    fontSize: 14,
    color: theme.textMuted,
    marginBottom: 8,
  },
  walletAddressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.background,
    borderRadius: 8,
    padding: 12,
  },
  walletAddress: {
    flex: 1,
    fontSize: 12,
    color: theme.text,
    fontFamily: 'monospace',
  },
  copyButton: {
    padding: 4,
    marginLeft: 8,
  },
  explorerButton: {
    width: '100%',
  },
  howItWorksCard: {
    marginBottom: 20,
  },
  stepsList: {
    gap: 16,
  },
  step: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  stepNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: theme.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  stepNumberText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: theme.text,
  },
  stepText: {
    flex: 1,
    fontSize: 14,
    color: theme.textSecondary,
    lineHeight: 20,
    paddingTop: 2,
  },
  actionsContainer: {
    gap: 12,
    marginBottom: 40,
  },
  releaseButton: {
    width: '100%',
  },
  disputeButton: {
    width: '100%',
  },
});