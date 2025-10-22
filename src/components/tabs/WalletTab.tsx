import { useState } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { ArrowUp, ArrowDown, Send, Eye, EyeOff, Shield, Clock, CheckCircle, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { useUser } from '../../contexts/UserContext';
import { useIsMobile } from '../../hooks/useIsMobile';
import { toast } from 'sonner@2.0.3';
import { motion, AnimatePresence } from 'motion/react';

interface Transaction {
  id: number;
  type: 'purchase' | 'deposit' | 'sale' | 'bill' | 'transfer';
  name: string;
  amount: number;
  date: string;
  status: 'completed' | 'pending' | 'failed';
  fees?: {
    platformFee?: number;
    gasFee?: number;
    deliveryFee?: number;
  };
}

export function WalletTab() {
  const { user, setUser } = useUser();
  const { isMobile } = useIsMobile();
  
  if (!user) return null;

  const [showBalance, setShowBalance] = useState(true);
  const [depositDialogOpen, setDepositDialogOpen] = useState(false);
  const [withdrawDialogOpen, setWithdrawDialogOpen] = useState(false);
  const [transferDialogOpen, setTransferDialogOpen] = useState(false);
  const [expandedTxId, setExpandedTxId] = useState<number | null>(null);
  const [copiedAddress, setCopiedAddress] = useState(false);

  // Deposit form state
  const [depositAmount, setDepositAmount] = useState('');
  const [depositMethod, setDepositMethod] = useState<'alchemy' | 'yellowcard'>('alchemy');

  // Withdraw form state
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [selectedBank, setSelectedBank] = useState('');
  const [accountNumber, setAccountNumber] = useState('');

  // Transfer form state
  const [transferRecipient, setTransferRecipient] = useState('');
  const [transferAmount, setTransferAmount] = useState('');

  // Calculate SOL equivalent (mock conversion rate: 1 SOL = ₦50,000)
  const solBalance = (user.balance / 50000).toFixed(4);

  const transactions: Transaction[] = [
    { 
      id: 1, 
      type: 'purchase', 
      name: 'iPhone 13 Pro', 
      amount: -85000, 
      date: '2025-10-14', 
      status: 'completed',
      fees: {
        platformFee: 1700,
        gasFee: 500,
        deliveryFee: 1500
      }
    },
    { 
      id: 2, 
      type: 'deposit', 
      name: 'Wallet Top-up via Alchemy Pay', 
      amount: 100000, 
      date: '2025-10-13', 
      status: 'completed',
      fees: {
        platformFee: 500,
        gasFee: 300
      }
    },
    { 
      id: 3, 
      type: 'sale', 
      name: 'Campus Hoodie', 
      amount: 8500, 
      date: '2025-10-12', 
      status: 'completed',
      fees: {
        platformFee: 170,
        gasFee: 500
      }
    },
    { 
      id: 4, 
      type: 'bill', 
      name: 'MTN Airtime', 
      amount: -1000, 
      date: '2025-10-11', 
      status: 'completed',
      fees: {
        platformFee: 20,
        gasFee: 300
      }
    },
    { 
      id: 5, 
      type: 'transfer', 
      name: 'Sent to Sarah M.', 
      amount: -5000, 
      date: '2025-10-10', 
      status: 'completed',
      fees: {
        gasFee: 300
      }
    },
  ];

  const escrowTransactions = [
    { id: 1, item: 'MacBook Air M2', amount: 450000, status: 'active', buyer: 'Alice W.' },
    { id: 2, item: 'Graphic Design Service', amount: 10000, status: 'pending', buyer: 'Bob S.' },
  ];

  const banks = [
    { value: 'gtb', label: 'GTBank' },
    { value: 'access', label: 'Access Bank' },
    { value: 'zenith', label: 'Zenith Bank' },
    { value: 'uba', label: 'UBA' },
    { value: 'firstbank', label: 'First Bank' },
    { value: 'fidelity', label: 'Fidelity Bank' },
  ];

  const handleCopyAddress = () => {
    if (user.walletAddress) {
      navigator.clipboard.writeText(user.walletAddress);
      setCopiedAddress(true);
      toast.success('Wallet address copied!');
      setTimeout(() => setCopiedAddress(false), 2000);
    }
  };

  const handleDeposit = () => {
    if (!depositAmount || parseFloat(depositAmount) <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    const amount = parseFloat(depositAmount);
    const methodName = depositMethod === 'alchemy' ? 'Alchemy Pay' : 'YellowCard';
    
    // Simulate deposit
    toast.success(`Deposit request submitted via ${methodName}!`);
    setDepositDialogOpen(false);
    setDepositAmount('');
  };

  const handleWithdraw = () => {
    if (!withdrawAmount || parseFloat(withdrawAmount) <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    if (!selectedBank) {
      toast.error('Please select a bank');
      return;
    }

    if (!accountNumber || accountNumber.length < 10) {
      toast.error('Please enter a valid account number');
      return;
    }

    const amount = parseFloat(withdrawAmount);
    
    if (amount > user.balance) {
      toast.error('Insufficient balance');
      return;
    }

    // Simulate withdrawal
    toast.success('Withdrawal request submitted!');
    setWithdrawDialogOpen(false);
    setWithdrawAmount('');
    setSelectedBank('');
    setAccountNumber('');
  };

  const handleTransfer = () => {
    if (!transferRecipient) {
      toast.error('Please enter recipient phone or email');
      return;
    }

    if (!transferAmount || parseFloat(transferAmount) <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    const amount = parseFloat(transferAmount);
    
    if (amount > user.balance) {
      toast.error('Insufficient balance');
      return;
    }

    // Simulate transfer
    toast.success(`₦${amount.toLocaleString()} sent to ${transferRecipient}!`);
    setTransferDialogOpen(false);
    setTransferRecipient('');
    setTransferAmount('');
  };

  const toggleTransaction = (id: number) => {
    setExpandedTxId(expandedTxId === id ? null : id);
  };

  return (
    <div className={isMobile ? 'px-4 py-6 space-y-6' : 'max-w-7xl mx-auto px-8 py-8 space-y-6'}>
      {/* Balance Card */}
      <Card className="p-6" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <span style={{ color: '#B3B3B3' }}>Available Balance</span>
            <p className="text-xs mt-1" style={{ color: '#666666' }}>
              ≈ {showBalance ? `${solBalance} SOL` : '****'}
            </p>
          </div>
          <button 
            onClick={() => setShowBalance(!showBalance)}
            className="p-2 rounded-lg transition-all hover:bg-opacity-10"
            style={{ backgroundColor: 'rgba(153, 69, 255, 0.1)' }}
          >
            {showBalance ? (
              <Eye size={20} style={{ color: '#9945FF' }} />
            ) : (
              <EyeOff size={20} style={{ color: '#9945FF' }} />
            )}
          </button>
        </div>
        <h1 className="mb-3" style={{ color: '#FFFFFF' }}>
          {showBalance ? `₦${user.balance.toLocaleString()}.00` : '₦****'}
        </h1>
        
        {/* Wallet Address */}
        <div 
          className="flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all"
          style={{ backgroundColor: '#121212' }}
          onClick={handleCopyAddress}
        >
          <div className="flex-1 overflow-hidden">
            <p className="text-xs mb-1" style={{ color: '#666666' }}>Solana Wallet Address</p>
            <p className="text-sm truncate" style={{ color: '#9945FF' }}>
              {user.walletAddress}
            </p>
          </div>
          <button className="ml-2 p-2">
            {copiedAddress ? (
              <Check size={16} style={{ color: '#4AFF99' }} />
            ) : (
              <Copy size={16} style={{ color: '#B3B3B3' }} />
            )}
          </button>
        </div>
      </Card>

      {/* Action Buttons */}
      <div className={isMobile ? 'grid grid-cols-4 gap-3' : 'grid grid-cols-4 gap-4'}>
        {/* Deposit */}
        <Dialog open={depositDialogOpen} onOpenChange={setDepositDialogOpen}>
          <DialogTrigger asChild>
            <button className="flex flex-col items-center gap-2 p-4 rounded-xl transition-all hover:scale-105" style={{ backgroundColor: '#1E1E1E' }}>
              <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
                <ArrowDown size={24} color="#FFFFFF" />
              </div>
              <span className="text-xs" style={{ color: '#FFFFFF' }}>Deposit</span>
            </button>
          </DialogTrigger>
          <DialogContent style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
            <DialogHeader>
              <DialogTitle style={{ color: '#FFFFFF' }}>Deposit Funds</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label style={{ color: '#B3B3B3' }}>Payment Method</Label>
                <div className="grid grid-cols-2 gap-3 mt-2">
                  <button
                    onClick={() => setDepositMethod('alchemy')}
                    className="p-3 rounded-lg transition-all"
                    style={{
                      backgroundColor: depositMethod === 'alchemy' ? 'rgba(153, 69, 255, 0.2)' : '#121212',
                      borderWidth: '2px',
                      borderColor: depositMethod === 'alchemy' ? '#9945FF' : '#333333'
                    }}
                  >
                    <p style={{ color: '#FFFFFF' }}>Alchemy Pay</p>
                    <p className="text-xs mt-1" style={{ color: '#B3B3B3' }}>Card, Bank Transfer</p>
                  </button>
                  <button
                    onClick={() => setDepositMethod('yellowcard')}
                    className="p-3 rounded-lg transition-all"
                    style={{
                      backgroundColor: depositMethod === 'yellowcard' ? 'rgba(153, 69, 255, 0.2)' : '#121212',
                      borderWidth: '2px',
                      borderColor: depositMethod === 'yellowcard' ? '#9945FF' : '#333333'
                    }}
                  >
                    <p style={{ color: '#FFFFFF' }}>YellowCard</p>
                    <p className="text-xs mt-1" style={{ color: '#B3B3B3' }}>Mobile Money</p>
                  </button>
                </div>
              </div>
              <div>
                <Label style={{ color: '#B3B3B3' }}>Amount (NGN)</Label>
                <Input
                  type="number"
                  placeholder="0"
                  value={depositAmount}
                  onChange={(e) => setDepositAmount(e.target.value)}
                  style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                />
                {depositAmount && (
                  <p className="text-xs mt-1" style={{ color: '#666666' }}>
                    ≈ {(parseFloat(depositAmount) / 50000).toFixed(4)} SOL
                  </p>
                )}
              </div>
              <div className="p-3 rounded-lg" style={{ backgroundColor: 'rgba(90, 200, 250, 0.1)', borderLeft: '3px solid #5AC8FA' }}>
                <p className="text-sm" style={{ color: '#B3B3B3' }}>
                  Funds will be converted to SOL and credited to your wallet automatically
                </p>
              </div>
              <Button 
                className="w-full" 
                style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
                onClick={handleDeposit}
              >
                Continue to {depositMethod === 'alchemy' ? 'Alchemy Pay' : 'YellowCard'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* Withdraw */}
        <Dialog open={withdrawDialogOpen} onOpenChange={setWithdrawDialogOpen}>
          <DialogTrigger asChild>
            <button className="flex flex-col items-center gap-2 p-4 rounded-xl transition-all hover:scale-105" style={{ backgroundColor: '#1E1E1E' }}>
              <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
                <ArrowUp size={24} color="#FFFFFF" />
              </div>
              <span className="text-xs" style={{ color: '#FFFFFF' }}>Withdraw</span>
            </button>
          </DialogTrigger>
          <DialogContent style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
            <DialogHeader>
              <DialogTitle style={{ color: '#FFFFFF' }}>Withdraw to Bank</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label style={{ color: '#B3B3B3' }}>Amount (NGN)</Label>
                <Input
                  type="number"
                  placeholder="0"
                  value={withdrawAmount}
                  onChange={(e) => setWithdrawAmount(e.target.value)}
                  style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                />
                <div className="flex items-center justify-between mt-2">
                  <p className="text-xs" style={{ color: '#666666' }}>
                    Available: ₦{user.balance.toLocaleString()}
                  </p>
                  <button
                    onClick={() => setWithdrawAmount(user.balance.toString())}
                    className="text-xs px-2 py-1 rounded"
                    style={{ color: '#9945FF', backgroundColor: 'rgba(153, 69, 255, 0.1)' }}
                  >
                    Max
                  </button>
                </div>
              </div>
              <div>
                <Label style={{ color: '#B3B3B3' }}>Bank</Label>
                <Select value={selectedBank} onValueChange={setSelectedBank}>
                  <SelectTrigger style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}>
                    <SelectValue placeholder="Select bank" />
                  </SelectTrigger>
                  <SelectContent style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
                    {banks.map((bank) => (
                      <SelectItem 
                        key={bank.value} 
                        value={bank.value}
                        style={{ color: '#FFFFFF' }}
                      >
                        {bank.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label style={{ color: '#B3B3B3' }}>Account Number</Label>
                <Input
                  type="text"
                  placeholder="0000000000"
                  value={accountNumber}
                  onChange={(e) => setAccountNumber(e.target.value)}
                  maxLength={10}
                  style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                />
              </div>
              <div className="p-3 rounded-lg" style={{ backgroundColor: 'rgba(255, 191, 0, 0.1)', borderLeft: '3px solid #FFBF00' }}>
                <p className="text-sm" style={{ color: '#B3B3B3' }}>
                  Processing time: 1-3 business days. Fee: ₦100 + SOL gas
                </p>
              </div>
              <Button 
                className="w-full" 
                style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
                onClick={handleWithdraw}
              >
                Confirm Withdrawal
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* P2P Transfer */}
        <Dialog open={transferDialogOpen} onOpenChange={setTransferDialogOpen}>
          <DialogTrigger asChild>
            <button className="flex flex-col items-center gap-2 p-4 rounded-xl transition-all hover:scale-105" style={{ backgroundColor: '#1E1E1E' }}>
              <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
                <Send size={24} color="#FFFFFF" />
              </div>
              <span className="text-xs" style={{ color: '#FFFFFF' }}>Transfer</span>
            </button>
          </DialogTrigger>
          <DialogContent style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
            <DialogHeader>
              <DialogTitle style={{ color: '#FFFFFF' }}>Peer-to-Peer Transfer</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label style={{ color: '#B3B3B3' }}>Recipient</Label>
                <Input
                  placeholder="Phone number or email"
                  value={transferRecipient}
                  onChange={(e) => setTransferRecipient(e.target.value)}
                  style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                />
                <p className="text-xs mt-1" style={{ color: '#666666' }}>
                  Enter registered phone or email
                </p>
              </div>
              <div>
                <Label style={{ color: '#B3B3B3' }}>Amount (NGN)</Label>
                <Input
                  type="number"
                  placeholder="0"
                  value={transferAmount}
                  onChange={(e) => setTransferAmount(e.target.value)}
                  style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                />
                <div className="flex items-center justify-between mt-2">
                  <p className="text-xs" style={{ color: '#666666' }}>
                    Available: ₦{user.balance.toLocaleString()}
                  </p>
                  {transferAmount && (
                    <p className="text-xs" style={{ color: '#666666' }}>
                      Fee: ₦300 (gas)
                    </p>
                  )}
                </div>
              </div>
              <div className="p-3 rounded-lg" style={{ backgroundColor: 'rgba(74, 255, 153, 0.1)', borderLeft: '3px solid #4AFF99' }}>
                <p className="text-sm" style={{ color: '#B3B3B3' }}>
                  Instant transfer between Konnect users. No platform fee!
                </p>
              </div>
              <Button 
                className="w-full" 
                style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
                onClick={handleTransfer}
              >
                Send Money
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* Escrow */}
        <button className="flex flex-col items-center gap-2 p-4 rounded-xl transition-all hover:scale-105" style={{ backgroundColor: '#1E1E1E' }}>
          <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
            <Shield size={24} color="#FFFFFF" />
          </div>
          <span className="text-xs" style={{ color: '#FFFFFF' }}>Escrow</span>
        </button>
      </div>

      {/* Escrow Summary */}
      <div>
        <h3 className="mb-3" style={{ color: '#FFFFFF' }}>Escrow Summary</h3>
        <div className="space-y-2">
          {escrowTransactions.map((escrow) => (
            <Card key={escrow.id} className="p-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: escrow.status === 'active' ? '#FFBF00' : '#9945FF' }}>
                  {escrow.status === 'active' ? (
                    <Clock size={20} color="#121212" />
                  ) : (
                    <Shield size={20} color="#FFFFFF" />
                  )}
                </div>
                <div className="flex-1">
                  <p style={{ color: '#FFFFFF' }}>{escrow.item}</p>
                  <p className="text-sm" style={{ color: '#B3B3B3' }}>{escrow.buyer}</p>
                </div>
                <div className="text-right">
                  <p style={{ color: '#9945FF' }}>₦{escrow.amount.toLocaleString()}</p>
                  <p className="text-xs" style={{ color: escrow.status === 'active' ? '#FFBF00' : '#B3B3B3' }}>
                    {escrow.status === 'active' ? 'Active' : 'Pending'}
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Transaction History */}
      <div>
        <h3 className="mb-3" style={{ color: '#FFFFFF' }}>Transaction History</h3>
        <div className="space-y-2">
          {transactions.map((tx) => {
            const isExpanded = expandedTxId === tx.id;
            const totalFees = (tx.fees?.platformFee || 0) + (tx.fees?.gasFee || 0) + (tx.fees?.deliveryFee || 0);
            
            return (
              <Card 
                key={tx.id} 
                className="overflow-hidden transition-all" 
                style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}
              >
                <button
                  onClick={() => toggleTransaction(tx.id)}
                  className="w-full p-4"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div
                        className="w-10 h-10 rounded-full flex items-center justify-center"
                        style={{
                          backgroundColor: tx.amount > 0 ? '#4AFF99' : '#FF4D4D',
                        }}
                      >
                        {tx.amount > 0 ? (
                          <ArrowDown size={20} color="#121212" />
                        ) : (
                          <ArrowUp size={20} color="#FFFFFF" />
                        )}
                      </div>
                      <div className="text-left">
                        <p style={{ color: '#FFFFFF' }}>{tx.name}</p>
                        <p className="text-sm" style={{ color: '#B3B3B3' }}>{tx.date}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-right">
                        <p style={{ color: tx.amount > 0 ? '#4AFF99' : '#FFFFFF' }}>
                          {tx.amount > 0 ? '+' : ''}₦{Math.abs(tx.amount).toLocaleString()}
                        </p>
                        <div className="flex items-center justify-end gap-1">
                          <CheckCircle size={12} style={{ color: '#4AFF99' }} />
                          <span className="text-xs" style={{ color: '#B3B3B3' }}>Completed</span>
                        </div>
                      </div>
                      {isExpanded ? (
                        <ChevronUp size={20} style={{ color: '#9945FF' }} />
                      ) : (
                        <ChevronDown size={20} style={{ color: '#9945FF' }} />
                      )}
                    </div>
                  </div>
                </button>

                {/* Expandable Fee Breakdown */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="px-4 pb-4 pt-2" style={{ borderTop: '1px solid #333333' }}>
                        <p className="text-sm mb-2" style={{ color: '#B3B3B3' }}>Fee Breakdown</p>
                        <div className="space-y-2">
                          {tx.fees?.platformFee && (
                            <div className="flex items-center justify-between">
                              <span className="text-sm" style={{ color: '#666666' }}>Platform Fee (2%):</span>
                              <span className="text-sm" style={{ color: '#FFFFFF' }}>₦{tx.fees.platformFee.toLocaleString()}</span>
                            </div>
                          )}
                          {tx.fees?.gasFee && (
                            <div className="flex items-center justify-between">
                              <span className="text-sm" style={{ color: '#666666' }}>SOL Gas Fee:</span>
                              <span className="text-sm" style={{ color: '#FFFFFF' }}>₦{tx.fees.gasFee.toLocaleString()}</span>
                            </div>
                          )}
                          {tx.fees?.deliveryFee && (
                            <div className="flex items-center justify-between">
                              <span className="text-sm" style={{ color: '#666666' }}>Delivery Fee:</span>
                              <span className="text-sm" style={{ color: '#FFFFFF' }}>₦{tx.fees.deliveryFee.toLocaleString()}</span>
                            </div>
                          )}
                          <div className="h-px" style={{ backgroundColor: '#333333' }} />
                          <div className="flex items-center justify-between">
                            <span className="text-sm" style={{ color: '#FFFFFF' }}>Total Fees:</span>
                            <span className="text-sm" style={{ color: '#9945FF' }}>₦{totalFees.toLocaleString()}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm" style={{ color: '#FFFFFF' }}>Net Amount:</span>
                            <span className="text-sm" style={{ color: tx.amount > 0 ? '#4AFF99' : '#FFFFFF' }}>
                              {tx.amount > 0 ? '+' : ''}₦{(Math.abs(tx.amount) - (tx.amount < 0 ? totalFees : 0)).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
