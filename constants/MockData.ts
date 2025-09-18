export interface Product {
  id: string;
  title: string;
  description: string;
  price: number;
  category: string;
  seller: {
    id: string;
    name: string;
    avatar: string;
    rating: number;
    campus: string;
  };
  images: string[];
  location: string;
  createdAt: Date;
}

export interface Order {
  id: string;
  productId: string;
  product: Product;
  status: 'pending' | 'confirmed' | 'delivering' | 'delivered' | 'disputed';
  escrowStatus: 'held' | 'released' | 'disputed';
  escrowAmount: number; // Amount in SOL
  escrowWallet: string; // Mock Solana wallet address
  totalAmount: number;
  createdAt: Date;
  deliveryDate?: Date;
  trackingId?: string;
}

export interface Listing {
  id: string;
  title: string;
  description: string;
  price: number;
  category: string;
  images: string[];
  status: 'active' | 'paused' | 'sold';
  views: number;
  createdAt: Date;
}

export interface SellerStats {
  totalSales: number;
  totalRevenue: number;
  activeListings: number;
  pendingOrders: number;
  rating: number;
  totalReviews: number;
}

export const categories = [
  { id: '1', name: 'Food', icon: '🍔' },
  { id: '2', name: 'Fashion', icon: '👕' },
  { id: '3', name: 'Books', icon: '📚' },
  { id: '4', name: 'Services', icon: '🛠️' },
  { id: '5', name: 'Tech', icon: '💻' },
  { id: '6', name: 'Sports', icon: '⚽' },
  { id: '7', name: 'Tutoring', icon: '🎓' },
  { id: '8', name: 'Laundry', icon: '🧺' },
];

// export const universities = [
//   { id: '1', name: 'Stanford University', location: 'Stanford, CA' },
//   { id: '2', name: 'MIT', location: 'Cambridge, MA' },
//   { id: '3', name: 'UC Berkeley', location: 'Berkeley, CA' },
//   { id: '4', name: 'Harvard University', location: 'Cambridge, MA' },
//   { id: '5', name: 'UCLA', location: 'Los Angeles, CA' },
// ];

export const universities = [
  { id: '1', name: 'University of Lagos (UNILAG)', location: 'Lagos, NG' },
  { id: '2', name: 'Covenant University', location: 'Ota, Ogun State, NG' },
  { id: '3', name: 'University of Ibadan (UI)', location: 'Ibadan, NG' },
  {
    id: '4',
    name: 'University of Nigeria, Nsukka (UNN)',
    location: 'Enugu, NG',
  },
  {
    id: '5',
    name: 'Obafemi Awolowo University (OAU)',
    location: 'Ile Ife, Osun, NG',
  },

  {
    id: '6',
    name: 'Lagos State University (LASU)',
    location: 'Ojo, Lagos, NG',
  },
  {
    id: '7',
    name: 'Federal University of Technology, Akure (FUTA)',
    location: 'Akure, NG',
  },
  { id: '8', name: 'Ahmadu Bello University (ABU)', location: 'Zaria, NG' },
  { id: '9', name: 'University of Benin (UNIBEN)', location: 'Benin City, NG' },
  {
    id: '10',
    name: 'Babcock University',
    location: 'Ilishan-Remo, Ogun State, NG',
  },
];


export const mockProducts: Product[] = [
  {
    id: '1',
    title: 'Calculus Textbook',
    description: 'Stewart Calculus 8th Edition. Great condition, no highlighting.',
    price: 75,
    category: 'Books',
    seller: {
      id: 's1',
      name: 'Alex Chen',
      avatar: 'https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=1',
      rating: 4.8,
      campus: 'Stanford University',
    },
    images: ['https://images.pexels.com/photos/256520/pexels-photo-256520.jpeg?auto=compress&cs=tinysrgb&w=400'],
    location: 'Tresidder Union',
    createdAt: new Date(),
  },
  {
    id: '2',
    title: 'MacBook Pro Repair',
    description: 'Professional MacBook repair service. Screen replacement, battery, keyboard fixes.',
    price: 120,
    category: 'Services',
    seller: {
      id: 's2',
      name: 'Tech Solutions Co',
      avatar: 'https://images.pexels.com/photos/2182970/pexels-photo-2182970.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=1',
      rating: 4.9,
      campus: 'Stanford University',
    },
    images: ['https://images.pexels.com/photos/18105/pexels-photo.jpg?auto=compress&cs=tinysrgb&w=400'],
    location: 'Engineering Quad',
    createdAt: new Date(),
  },
  {
    id: '3',
    title: 'Homemade Cookies',
    description: 'Fresh baked chocolate chip cookies. Made daily in dorm kitchen.',
    price: 8,
    category: 'Food',
    seller: {
      id: 's3',
      name: 'Sarah Kim',
      avatar: 'https://images.pexels.com/photos/1674752/pexels-photo-1674752.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=1',
      rating: 4.7,
      campus: 'Stanford University',
    },
    images: ['https://images.pexels.com/photos/230325/pexels-photo-230325.jpeg?auto=compress&cs=tinysrgb&w=400'],
    location: 'Wilbur Hall',
    createdAt: new Date(),
  },
];

export const mockOrders: Order[] = [
  {
    id: '1',
    productId: '1',
    product: mockProducts[0],
    status: 'delivering',
    escrowStatus: 'held',
    escrowAmount: 2.1, // SOL equivalent
    escrowWallet: '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU',
    totalAmount: 75,
    createdAt: new Date(Date.now() - 86400000),
    trackingId: 'TRK001',
  },
  {
    id: '2',
    productId: '2',
    product: mockProducts[1],
    status: 'delivered',
    escrowStatus: 'released',
    escrowAmount: 3.4, // SOL equivalent
    escrowWallet: '9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM',
    totalAmount: 120,
    createdAt: new Date(Date.now() - 172800000),
    deliveryDate: new Date(Date.now() - 86400000),
    trackingId: 'TRK002',
  },
];

export const mockListings: Listing[] = [
  {
    id: '1',
    title: 'Calculus Textbook',
    description: 'Stewart Calculus 8th Edition. Great condition, no highlighting.',
    price: 75,
    category: 'Books',
    images: ['https://images.pexels.com/photos/256520/pexels-photo-256520.jpeg?auto=compress&cs=tinysrgb&w=400'],
    status: 'active',
    views: 24,
    createdAt: new Date(Date.now() - 86400000),
  },
  {
    id: '2',
    title: 'MacBook Pro Repair',
    description: 'Professional MacBook repair service. Screen replacement, battery, keyboard fixes.',
    price: 120,
    category: 'Services',
    images: ['https://images.pexels.com/photos/18105/pexels-photo.jpg?auto=compress&cs=tinysrgb&w=400'],
    status: 'active',
    views: 18,
    createdAt: new Date(Date.now() - 172800000),
  },
];

export const mockSellerStats: SellerStats = {
  totalSales: 47,
  totalRevenue: 1250,
  activeListings: 8,
  pendingOrders: 3,
  rating: 4.8,
  totalReviews: 23,
};