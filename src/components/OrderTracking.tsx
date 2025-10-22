import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'motion/react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { ArrowLeft, CheckCircle2, Clock, Package, Truck, MapPin, Phone, FileText } from 'lucide-react';
import { useIsMobile } from '../hooks/useIsMobile';
import exampleImage from 'figma:asset/5716b60d4cdf746e0f00e9adfc0e72110a615e3d.png';

interface OrderStatus {
  id: number;
  title: string;
  description: string;
  timestamp?: string;
  completed: boolean;
}

interface Order {
  id: number;
  name: string;
  seller: string;
  price: number;
  deliveryCode: string;
  deliveryAddress: string;
  phoneNumber: string;
  currentStatus: number;
  items: Array<{
    name: string;
    quantity: number;
    price: number;
  }>;
}

// Mock order data - in a real app, this would come from an API
const mockOrders: { [key: string]: Order } = {
  '1': {
    id: 1,
    name: 'MacBook Air M2',
    seller: 'David K.',
    price: 450000,
    deliveryCode: '8090',
    deliveryAddress: '34 Christy Oladunni St, Lagos 102214, Lagos, Nigeria',
    phoneNumber: '+234 801 234 5678',
    currentStatus: 2,
    items: [
      { name: 'MacBook Air M2 - 256GB SSD', quantity: 1, price: 450000 }
    ]
  }
};

export function OrderTracking() {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { isMobile } = useIsMobile();
  
  const order = orderId ? mockOrders[orderId] : null;

  if (!order) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#121212' }}>
        <div className="text-center">
          <p style={{ color: '#B3B3B3' }}>Order not found</p>
          <Button
            onClick={() => navigate('/cart')}
            className="mt-4"
            style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
          >
            Back to Cart
          </Button>
        </div>
      </div>
    );
  }

  const orderStatuses: OrderStatus[] = [
    {
      id: 1,
      title: 'Order Received',
      description: 'Waiting for vendor to confirm your order.',
      timestamp: '2:03pm',
      completed: order.currentStatus >= 1,
    },
    {
      id: 2,
      title: 'Preparing Your Order',
      description: 'Your order will be ready in 1 minute',
      timestamp: '2:14pm',
      completed: order.currentStatus >= 2,
    },
    {
      id: 3,
      title: 'Rider Accepted Order',
      description: 'Your order has been assigned to a rider.',
      timestamp: order.currentStatus >= 3 ? '2:14pm' : undefined,
      completed: order.currentStatus >= 3,
    },
    {
      id: 4,
      title: 'Rider At The Vendor',
      description: 'Rider is waiting to pick up your order',
      timestamp: order.currentStatus >= 4 ? '2:16pm' : undefined,
      completed: order.currentStatus >= 4,
    },
    {
      id: 5,
      title: 'Rider Picked Up Order',
      description: 'Your order is on its way.',
      timestamp: order.currentStatus >= 5 ? '2:18pm' : undefined,
      completed: order.currentStatus >= 5,
    },
    {
      id: 6,
      title: 'Order Arrived',
      description: 'Your driver is around to deliver your order.',
      timestamp: order.currentStatus >= 6 ? '2:25pm' : undefined,
      completed: order.currentStatus >= 6,
    },
    {
      id: 7,
      title: 'Order Delivered',
      description: 'Your order has been delivered',
      timestamp: order.currentStatus >= 7 ? '2:30pm' : undefined,
      completed: order.currentStatus >= 7,
    },
  ];

  return (
    <div 
      className={isMobile ? 'min-h-screen pb-20' : 'min-h-screen pb-8'} 
      style={{ backgroundColor: '#121212' }}
    >
      {/* Header */}
      <div 
        className={isMobile ? 'sticky top-0 z-40 px-4 py-3 flex items-center gap-3' : 'px-8 py-4 flex items-center gap-3'}
        style={{ backgroundColor: '#121212', borderBottom: '1px solid #333333' }}
      >
        <button
          onClick={() => navigate('/cart')}
          className="p-2 rounded-lg transition-all"
          style={{ color: '#B3B3B3' }}
        >
          <ArrowLeft size={24} />
        </button>
        <h3 style={{ color: '#FFFFFF' }}>Track Order</h3>
      </div>

      {/* Content */}
      <div className={isMobile ? 'px-4 py-6 space-y-6' : 'max-w-4xl mx-auto px-8 py-8 space-y-6'}>
        {/* Order Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Card className="p-6" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h2 style={{ color: '#FFFFFF' }}>{order.name}</h2>
                <p className="mt-1" style={{ color: '#B3B3B3' }}>
                  Your order will be picked up shortly
                </p>
              </div>
              <div className="w-16 h-16 flex items-center justify-center">
                <Package size={40} style={{ color: '#9945FF' }} />
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Delivery Code */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card className="p-6" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
            <p className="text-sm mb-3" style={{ color: '#B3B3B3' }}>Delivery confirmation code</p>
            <h4 className="mb-2" style={{ color: '#FFFFFF' }}>Share this code with your rider</h4>
            <div className="flex gap-3 justify-center mt-4">
              {order.deliveryCode.split('').map((digit, index) => (
                <div
                  key={index}
                  className="w-16 h-20 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: '#121212', border: '2px solid #9945FF' }}
                >
                  <span className="text-3xl" style={{ color: '#9945FF' }}>{digit}</span>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* Order Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <Card className="p-6" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
            <h3 className="mb-6" style={{ color: '#FFFFFF' }}>Order Timeline</h3>
            <div className="space-y-6">
              {orderStatuses.map((status, index) => (
                <div key={status.id} className="flex gap-4">
                  {/* Timeline Line and Icon */}
                  <div className="flex flex-col items-center">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        status.completed ? 'bg-opacity-100' : 'bg-opacity-30'
                      }`}
                      style={{
                        backgroundColor: status.completed ? '#4AFF99' : '#333333',
                      }}
                    >
                      {status.completed ? (
                        <CheckCircle2 size={18} style={{ color: '#121212' }} />
                      ) : (
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: '#666666' }}
                        />
                      )}
                    </div>
                    {index < orderStatuses.length - 1 && (
                      <div
                        className="w-0.5 h-full mt-2"
                        style={{
                          backgroundColor: status.completed ? '#4AFF99' : '#333333',
                          minHeight: '40px',
                        }}
                      />
                    )}
                  </div>

                  {/* Status Content */}
                  <div className="flex-1 pb-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4
                          style={{
                            color: status.completed ? '#4AFF99' : '#666666',
                          }}
                        >
                          {status.title}
                        </h4>
                        <p
                          className="text-sm mt-1"
                          style={{
                            color: status.completed ? '#B3B3B3' : '#666666',
                          }}
                        >
                          {status.description}
                        </p>
                      </div>
                      {status.timestamp && (
                        <span
                          className="text-sm ml-4"
                          style={{ color: '#B3B3B3' }}
                        >
                          {status.timestamp}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* Delivery Details */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
        >
          <Card className="p-6" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
            <div className="flex items-center justify-between mb-4">
              <h3 style={{ color: '#FFFFFF' }}>Delivery details</h3>
              <button className="text-sm" style={{ color: '#9945FF' }}>
                Share trip 📤
              </button>
            </div>

            <div className="space-y-4">
              {/* Address */}
              <div className="flex gap-3 p-4 rounded-lg" style={{ backgroundColor: '#121212' }}>
                <MapPin size={20} style={{ color: '#9945FF' }} className="flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <p className="text-sm" style={{ color: '#B3B3B3' }}>Delivery Address</p>
                  <p className="mt-1" style={{ color: '#FFFFFF' }}>
                    {order.deliveryAddress}
                  </p>
                  <button className="mt-2 text-sm" style={{ color: '#9945FF' }}>
                    UPDATE
                  </button>
                </div>
              </div>

              {/* Phone */}
              <div className="flex gap-3 p-4 rounded-lg" style={{ backgroundColor: '#121212' }}>
                <Phone size={20} style={{ color: '#9945FF' }} className="flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <p className="text-sm" style={{ color: '#B3B3B3' }}>Contact Number</p>
                  <p className="mt-1" style={{ color: '#FFFFFF' }}>
                    {order.phoneNumber}
                  </p>
                  <button className="mt-2 text-sm" style={{ color: '#9945FF' }}>
                    UPDATE
                  </button>
                </div>
              </div>

              {/* Delivery Instructions */}
              <div className="flex gap-3 p-4 rounded-lg" style={{ backgroundColor: '#121212' }}>
                <FileText size={20} style={{ color: '#9945FF' }} className="flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <p className="text-sm" style={{ color: '#B3B3B3' }}>Delivery instructions</p>
                  <button className="mt-2 text-sm" style={{ color: '#9945FF' }}>
                    UPDATE
                  </button>
                </div>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Your Order */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.4 }}
        >
          <Card className="p-6" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
            <div className="flex items-center justify-between mb-4">
              <h3 style={{ color: '#FFFFFF' }}>Your order</h3>
              <button className="text-sm" style={{ color: '#9945FF' }}>
                CALL RIDER
              </button>
            </div>

            <div className="space-y-3">
              <div className="p-4 rounded-lg" style={{ backgroundColor: '#121212' }}>
                <p style={{ color: '#FFFFFF' }}>{order.name}</p>
                <p className="text-sm mt-1" style={{ color: '#B3B3B3' }}>
                  Seller: {order.seller}
                </p>
              </div>

              {order.items.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 rounded-lg"
                  style={{ backgroundColor: '#121212' }}
                >
                  <div className="flex-1">
                    <p className="text-sm" style={{ color: '#FFFFFF' }}>
                      {item.name} x {item.quantity}
                    </p>
                  </div>
                  <p style={{ color: '#9945FF' }}>
                    ₦{item.price.toLocaleString()}
                  </p>
                </div>
              ))}

              <div className="h-px" style={{ backgroundColor: '#333333' }} />

              <div className="flex items-center justify-between pt-2">
                <span style={{ color: '#FFFFFF' }}>Total</span>
                <span style={{ color: '#9945FF' }}>
                  ₦{order.price.toLocaleString()}
                </span>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Action Buttons */}
        {isMobile && (
          <div className="fixed bottom-0 left-0 right-0 p-4 flex gap-3" style={{ backgroundColor: '#121212', borderTop: '1px solid #333333' }}>
            <Button
              onClick={() => navigate('/cart')}
              variant="outline"
              className="flex-1"
              style={{ borderColor: '#9945FF', color: '#9945FF' }}
            >
              Back to Orders
            </Button>
            <Button
              className="flex-1"
              style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
            >
              Contact Seller
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
