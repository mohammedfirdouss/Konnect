import { useState } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Smartphone, Zap, Tv, Bell, CheckCircle } from 'lucide-react';

export function BillsTab() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const categories = [
    { id: 'airtime', name: 'Airtime', icon: Smartphone, color: '#9945FF' },
    { id: 'utilities', name: 'Utilities', icon: Zap, color: '#FFBF00' },
    { id: 'subscriptions', name: 'Subscriptions', icon: Tv, color: '#5AC8FA' },
  ];

  const savedBills = [
    { id: 1, name: 'MTN Airtime', amount: 1000, type: 'airtime', number: '0801234567' },
    { id: 2, name: 'NEPA/PHCN', amount: 5000, type: 'utilities', meter: '12345678' },
    { id: 3, name: 'Netflix', amount: 5500, type: 'subscriptions', email: 'user@email.com' },
  ];

  const recentPayments = [
    { id: 1, name: 'MTN Airtime - ₦1,000', date: '2025-10-14', status: 'completed' },
    { id: 2, name: 'DSTV Subscription - ₦8,000', date: '2025-10-12', status: 'completed' },
    { id: 3, name: 'Glo Data - ₦2,000', date: '2025-10-10', status: 'completed' },
  ];

  return (
    <div className="px-4 py-6 space-y-6">
      <div>
        <h2 style={{ color: '#FFFFFF' }}>Bills & Subscriptions</h2>
        <p style={{ color: '#B3B3B3' }}>Pay your bills instantly</p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {categories.map((category) => {
          const Icon = category.icon;
          return (
            <Dialog key={category.id}>
              <DialogTrigger asChild>
                <button
                  className="flex flex-col items-center gap-3 p-4 rounded-xl"
                  style={{ backgroundColor: '#1E1E1E' }}
                  onClick={() => setSelectedCategory(category.id)}
                >
                  <div
                    className="w-12 h-12 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: category.color }}
                  >
                    <Icon size={24} color="#FFFFFF" />
                  </div>
                  <span className="text-sm text-center" style={{ color: '#FFFFFF' }}>
                    {category.name}
                  </span>
                </button>
              </DialogTrigger>
              <DialogContent style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
                <DialogHeader>
                  <DialogTitle style={{ color: '#FFFFFF' }}>Pay {category.name}</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  {category.id === 'airtime' && (
                    <>
                      <div>
                        <Label style={{ color: '#B3B3B3' }}>Network</Label>
                        <Select>
                          <SelectTrigger style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}>
                            <SelectValue placeholder="Select network" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="mtn">MTN</SelectItem>
                            <SelectItem value="glo">Glo</SelectItem>
                            <SelectItem value="airtel">Airtel</SelectItem>
                            <SelectItem value="9mobile">9mobile</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label style={{ color: '#B3B3B3' }}>Phone Number</Label>
                        <Input
                          type="tel"
                          placeholder="080..."
                          style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                        />
                      </div>
                      <div>
                        <Label style={{ color: '#B3B3B3' }}>Amount (NGN)</Label>
                        <Input
                          type="number"
                          placeholder="0"
                          style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                        />
                      </div>
                    </>
                  )}
                  {category.id === 'utilities' && (
                    <>
                      <div>
                        <Label style={{ color: '#B3B3B3' }}>Provider</Label>
                        <Select>
                          <SelectTrigger style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}>
                            <SelectValue placeholder="Select provider" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="nepa">NEPA/PHCN</SelectItem>
                            <SelectItem value="aedc">AEDC</SelectItem>
                            <SelectItem value="ekedc">EKEDC</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label style={{ color: '#B3B3B3' }}>Meter Number</Label>
                        <Input
                          placeholder="Enter meter number"
                          style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                        />
                      </div>
                      <div>
                        <Label style={{ color: '#B3B3B3' }}>Amount (NGN)</Label>
                        <Input
                          type="number"
                          placeholder="0"
                          style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                        />
                      </div>
                    </>
                  )}
                  {category.id === 'subscriptions' && (
                    <>
                      <div>
                        <Label style={{ color: '#B3B3B3' }}>Service</Label>
                        <Select>
                          <SelectTrigger style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}>
                            <SelectValue placeholder="Select service" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="netflix">Netflix</SelectItem>
                            <SelectItem value="spotify">Spotify</SelectItem>
                            <SelectItem value="dstv">DSTV</SelectItem>
                            <SelectItem value="gotv">GOtv</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label style={{ color: '#B3B3B3' }}>Account Number/Email</Label>
                        <Input
                          placeholder="Enter account details"
                          style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                        />
                      </div>
                      <div>
                        <Label style={{ color: '#B3B3B3' }}>Plan</Label>
                        <Select>
                          <SelectTrigger style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}>
                            <SelectValue placeholder="Select plan" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="basic">Basic - ₦5,500</SelectItem>
                            <SelectItem value="standard">Standard - ₦8,000</SelectItem>
                            <SelectItem value="premium">Premium - ₦10,500</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </>
                  )}
                  <div className="flex items-center gap-2 p-3 rounded-lg" style={{ backgroundColor: '#121212' }}>
                    <input type="checkbox" id="save-bill" />
                    <label htmlFor="save-bill" className="text-sm" style={{ color: '#B3B3B3' }}>
                      Save for quick payment next time
                    </label>
                  </div>
                  <Button className="w-full" style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}>
                    Pay Now
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          );
        })}
      </div>

      <Card className="p-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#9945FF' }}>
            <Bell size={20} color="#FFFFFF" />
          </div>
          <div>
            <h3 style={{ color: '#FFFFFF' }}>AI Reminders</h3>
            <p className="text-sm" style={{ color: '#B3B3B3' }}>
              Enabled for recurring bills
            </p>
          </div>
        </div>
        <p className="text-sm" style={{ color: '#B3B3B3' }}>
          We'll remind you when your bills are due based on your payment history
        </p>
      </Card>

      <div>
        <h3 className="mb-3" style={{ color: '#FFFFFF' }}>Saved Bills</h3>
        <div className="space-y-2">
          {savedBills.map((bill) => {
            const category = categories.find(c => c.id === bill.type);
            const Icon = category?.icon || Smartphone;
            return (
              <Card key={bill.id} className="p-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center"
                      style={{ backgroundColor: category?.color || '#9945FF' }}
                    >
                      <Icon size={20} color="#FFFFFF" />
                    </div>
                    <div>
                      <p style={{ color: '#FFFFFF' }}>{bill.name}</p>
                      <p className="text-sm" style={{ color: '#B3B3B3' }}>
                        {'number' in bill ? bill.number : 'meter' in bill ? bill.meter : bill.email}
                      </p>
                    </div>
                  </div>
                  <Button size="sm" style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}>
                    Pay ₦{bill.amount.toLocaleString()}
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="mb-3" style={{ color: '#FFFFFF' }}>Recent Payments</h3>
        <div className="space-y-2">
          {recentPayments.map((payment) => (
            <Card key={payment.id} className="p-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#4AFF99' }}
                  >
                    <CheckCircle size={20} color="#121212" />
                  </div>
                  <div>
                    <p style={{ color: '#FFFFFF' }}>{payment.name}</p>
                    <p className="text-sm" style={{ color: '#B3B3B3' }}>{payment.date}</p>
                  </div>
                </div>
                <span className="text-xs" style={{ color: '#4AFF99' }}>Completed</span>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
