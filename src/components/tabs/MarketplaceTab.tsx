import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Plus, Heart, Star, ShoppingCart, Package, TrendingUp, DollarSign, Eye } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { useUser } from '../../contexts/UserContext';
import { useCart } from '../../contexts/CartContext';
import { ImageWithFallback } from '../figma/ImageWithFallback';
import { useIsMobile } from '../../hooks/useIsMobile';
import { toast } from 'sonner@2.0.3';

interface Product {
  id: number;
  name: string;
  price: number;
  seller: string;
  rating: number;
  category: string;
  image: string;
}

interface Listing {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  type: 'good' | 'service';
  deliveryFee?: number;
  status: 'active' | 'sold' | 'inactive';
  views: number;
  sales: number;
}

export function MarketplaceTab() {
  const { user } = useUser();
  const { isMobile } = useIsMobile();
  const { addToCart } = useCart();
  const navigate = useNavigate();
  
  if (!user) return null;

  const [activeCategory, setActiveCategory] = useState<'goods' | 'services'>('goods');
  const [selectedSubCategory, setSelectedSubCategory] = useState<string>('All');
  const [createListingOpen, setCreateListingOpen] = useState(false);
  const [listingType, setListingType] = useState<'good' | 'service'>('good');
  const [listingName, setListingName] = useState('');
  const [listingDescription, setListingDescription] = useState('');
  const [listingCategory, setListingCategory] = useState('');
  const [listingPrice, setListingPrice] = useState('');
  const [listingDeliveryFee, setListingDeliveryFee] = useState('');
  
  const isSeller = user.role === 'seller' || user.role === 'both';

  // Mock seller listings
  const myListings: Listing[] = [
    {
      id: 1,
      name: 'iPhone 13 Pro',
      description: 'Barely used, excellent condition',
      price: 450000,
      category: 'Electronics',
      type: 'good',
      deliveryFee: 2000,
      status: 'active',
      views: 245,
      sales: 12
    },
    {
      id: 2,
      name: 'Graphic Design Service',
      description: 'Logo and brand identity design',
      price: 25000,
      category: 'Design',
      type: 'service',
      status: 'active',
      views: 128,
      sales: 8
    },
    {
      id: 3,
      name: 'MacBook Air M2',
      description: 'Like new, 256GB SSD, 8GB RAM',
      price: 850000,
      category: 'Electronics',
      type: 'good',
      deliveryFee: 3000,
      status: 'active',
      views: 412,
      sales: 5
    },
    {
      id: 4,
      name: 'Campus Hoodie',
      description: 'Premium quality, various sizes',
      price: 12500,
      category: 'Fashion',
      type: 'good',
      deliveryFee: 1000,
      status: 'sold',
      views: 89,
      sales: 3
    },
  ];

  const handleAddToCart = (product: Product, type: 'good' | 'service') => {
    addToCart({
      id: product.id,
      name: product.name,
      price: product.price,
      seller: product.seller,
      category: product.category,
      image: product.image,
      type,
    });
    toast.success(`${product.name} added to cart!`, {
      duration: 2000,
    });
  };

  const handleCreateListing = () => {
    if (!listingName.trim() || !listingDescription.trim() || !listingCategory || !listingPrice) {
      toast.error('Please fill in all required fields');
      return;
    }

    const price = parseFloat(listingPrice);
    if (price <= 0) {
      toast.error('Please enter a valid price');
      return;
    }

    // Simulate creating listing
    toast.success(`${listingName} has been listed on the marketplace!`, {
      duration: 3000,
    });

    // Reset form
    setListingName('');
    setListingDescription('');
    setListingCategory('');
    setListingPrice('');
    setListingDeliveryFee('');
    setListingType('good');
    setCreateListingOpen(false);
  };

  const goodsCategories = ['All', 'Hot Deals', 'Fashion', 'Beauty and Personal Care', 'Electronics', 'Books', 'Home & Living'];
  const servicesCategories = ['All', 'Education', 'Design', 'Tech', 'Media', 'Transportation'];

  const goods: Product[] = [
    {
      id: 1,
      name: 'iPhone 13 Pro',
      price: 450000,
      seller: 'TechHub NG',
      rating: 4.8,
      category: 'Electronics',
      image: 'https://images.unsplash.com/photo-1564572234453-6b14f6e6fcfb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzbWFydHBob25lJTIwZWxlY3Ryb25pY3N8ZW58MXx8fHwxNzYxMDE2Mjg1fDA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 2,
      name: 'Premium Hoodie',
      price: 12500,
      seller: 'Campus Styles',
      rating: 4.9,
      category: 'Fashion',
      image: 'https://images.unsplash.com/photo-1732475530169-70c2cda1712f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxob29kaWUlMjBmYXNoaW9ufGVufDF8fHx8MTc2MTA1MTI5NXww&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 3,
      name: 'MacBook Air M2',
      price: 850000,
      seller: 'Apple Store NG',
      rating: 5.0,
      category: 'Electronics',
      image: 'https://images.unsplash.com/photo-1511385348-a52b4a160dc2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsYXB0b3AlMjBjb21wdXRlcnxlbnwxfHx8fDE3NjEwMjMxOTh8MA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 4,
      name: 'Engineering Textbooks',
      price: 25000,
      seller: 'BookMart',
      rating: 4.7,
      category: 'Books',
      image: 'https://images.unsplash.com/photo-1666281269793-da06484657e8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx0ZXh0Ym9va3MlMjBlZHVjYXRpb258ZW58MXx8fHwxNzYxMDA4OTEyfDA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 5,
      name: 'Sony WH-1000XM5',
      price: 180000,
      seller: 'Audio Pro',
      rating: 4.9,
      category: 'Electronics',
      image: 'https://images.unsplash.com/photo-1713618651165-a3cf7f85506c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWFkcGhvbmVzJTIwYXVkaW98ZW58MXx8fHwxNzYxMDQyOTQ1fDA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 6,
      name: 'Nike Air Max',
      price: 45000,
      seller: 'Sneaker World',
      rating: 4.8,
      category: 'Fashion',
      image: 'https://images.unsplash.com/photo-1656944227480-98180d2a5155?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzbmVha2VycyUyMHNob2VzfGVufDF8fHx8MTc2MDk3NTQ2M3ww&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 7,
      name: 'Skincare Bundle',
      price: 15000,
      seller: 'Beauty Haven',
      rating: 4.6,
      category: 'Beauty and Personal Care',
      image: 'https://images.unsplash.com/photo-1605204376600-72ed73f1f9ec?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxza2luY2FyZSUyMGJlYXV0eSUyMHByb2R1Y3RzfGVufDF8fHx8MTc2MTA0MTE1MXww&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 8,
      name: 'Travel Backpack',
      price: 18500,
      seller: 'Bag Store',
      rating: 4.7,
      category: 'Fashion',
      image: 'https://images.unsplash.com/photo-1535982330050-f1c2fb79ff78?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxiYWNrcGFjayUyMHNjaG9vbHxlbnwxfHx8fDE3NjEwNDM2NDl8MA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 9,
      name: 'Smart Watch Pro',
      price: 65000,
      seller: 'Gadget Zone',
      rating: 4.5,
      category: 'Electronics',
      image: 'https://images.unsplash.com/photo-1706892807280-f8648dda29ef?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx3YXRjaCUyMGFjY2Vzc29yaWVzfGVufDF8fHx8MTc2MTAzMjE0OHww&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 10,
      name: 'Canon EOS Camera',
      price: 320000,
      seller: 'Photo Pro',
      rating: 4.9,
      category: 'Electronics',
      image: 'https://images.unsplash.com/photo-1561139726-d0821060523f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjYW1lcmElMjBlbGVjdHJvbmljc3xlbnwxfHx8fDE3NjEwNTYxMzF8MA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 11,
      name: 'Designer Perfume',
      price: 28000,
      seller: 'Fragrance Hub',
      rating: 4.8,
      category: 'Beauty and Personal Care',
      image: 'https://images.unsplash.com/photo-1607506740211-ff3d6b933dda?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwZXJmdW1lJTIwZnJhZ3JhbmNlfGVufDF8fHx8MTc2MTA1NjEzMnww&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 12,
      name: 'Ray-Ban Sunglasses',
      price: 35000,
      seller: 'Fashion Optics',
      rating: 4.7,
      category: 'Fashion',
      image: 'https://images.unsplash.com/photo-1663585703603-9be01a72a62a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdW5nbGFzc2VzJTIwZmFzaGlvbnxlbnwxfHx8fDE3NjA5Njk1MDJ8MA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 13,
      name: 'PlayStation 5',
      price: 550000,
      seller: 'Gaming Central',
      rating: 5.0,
      category: 'Electronics',
      image: 'https://images.unsplash.com/photo-1580234797602-22c37b2a6230?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxnYW1pbmclMjBjb25zb2xlfGVufDF8fHx8MTc2MTAxNTcxMXww&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 14,
      name: 'Modern Desk Lamp',
      price: 8500,
      seller: 'Home Essentials',
      rating: 4.6,
      category: 'Home & Living',
      image: 'https://images.unsplash.com/photo-1621447980929-6638614633c8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkZXNrJTIwbGFtcHxlbnwxfHx8fDE3NjEwNDc1MDh8MA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 15,
      name: 'Leather Notebook Set',
      price: 5500,
      seller: 'Stationery Plus',
      rating: 4.5,
      category: 'Books',
      image: 'https://images.unsplash.com/photo-1621866271250-9dc9780cfc1f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxub3RlYm9vayUyMHN0YXRpb25lcnl8ZW58MXx8fHwxNzYxMDU2MTMzfDA&ixlib=rb-4.1.0&q=80&w=1080',
    },
    {
      id: 16,
      name: 'Mountain Bike',
      price: 125000,
      seller: 'Cycle Store',
      rating: 4.8,
      category: 'Electronics',
      image: 'https://images.unsplash.com/photo-1760040795488-1dd9e5a0d83a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxiaWN5Y2xlJTIwdHJhbnNwb3J0fGVufDF8fHx8MTc2MTA1NjEzM3ww&ixlib=rb-4.1.0&q=80&w=1080',
    },
  ];

  const services: Product[] = [
    { id: 101, name: 'Math Tutoring (Per Hour)', price: 3500, seller: 'Prof. Adams', rating: 4.9, category: 'Education', image: '' },
    { id: 102, name: 'Logo Design Package', price: 15000, seller: 'Creative Studio', rating: 4.8, category: 'Design', image: '' },
    { id: 103, name: 'Website Development', price: 80000, seller: 'Tech Solutions', rating: 5.0, category: 'Tech', image: '' },
    { id: 104, name: 'Photography Session', price: 25000, seller: 'Photo Masters', rating: 4.9, category: 'Media', image: '' },
    { id: 105, name: 'Campus Ride Share', price: 1000, seller: 'Safe Rides NG', rating: 4.7, category: 'Transportation', image: '' },
    { id: 106, name: 'Assignment Writing Help', price: 5000, seller: 'Study Buddy', rating: 4.6, category: 'Education', image: '' },
    { id: 107, name: 'Video Editing Service', price: 20000, seller: 'Edit Pro', rating: 4.8, category: 'Media', image: '' },
    { id: 108, name: 'Social Media Management', price: 35000, seller: 'Digital Kings', rating: 4.7, category: 'Design', image: '' },
  ];

  const filteredGoods =
    selectedSubCategory === 'All'
      ? goods
      : goods.filter((item) => item.category === selectedSubCategory || selectedSubCategory === 'Hot Deals');

  const filteredServices =
    selectedSubCategory === 'All'
      ? services
      : services.filter((item) => item.category === selectedSubCategory);

  const currentCategories = activeCategory === 'goods' ? goodsCategories : servicesCategories;

  // Seller View
  if (isSeller) {
    const totalRevenue = myListings.reduce((sum, listing) => sum + (listing.price * listing.sales), 0);
    const totalSales = myListings.reduce((sum, listing) => sum + listing.sales, 0);
    const activeListings = myListings.filter(l => l.status === 'active').length;

    return (
      <div className={`${isMobile ? 'px-4' : 'px-8 max-w-7xl mx-auto'} py-6 space-y-6`}>
        {/* Header with Stats */}
        <div className="flex items-center justify-between">
          <h2 style={{ color: '#FFFFFF' }}>My Listings</h2>
          <Dialog open={createListingOpen} onOpenChange={setCreateListingOpen}>
            <DialogTrigger asChild>
              <Button style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}>
                <Plus size={20} className="mr-2" />
                Create Listing
              </Button>
            </DialogTrigger>
            <DialogContent style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
              <DialogHeader>
                <DialogTitle style={{ color: '#FFFFFF' }}>Create New Listing</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                {/* Type Selection */}
                <div>
                  <Label style={{ color: '#B3B3B3' }}>Listing Type</Label>
                  <div className="grid grid-cols-2 gap-3 mt-2">
                    <button
                      onClick={() => setListingType('good')}
                      className="p-3 rounded-lg transition-all"
                      style={{
                        backgroundColor: listingType === 'good' ? 'rgba(153, 69, 255, 0.2)' : '#121212',
                        borderWidth: '2px',
                        borderColor: listingType === 'good' ? '#9945FF' : '#333333'
                      }}
                    >
                      <Package size={24} className="mx-auto mb-2" style={{ color: '#9945FF' }} />
                      <p style={{ color: '#FFFFFF' }}>Good</p>
                    </button>
                    <button
                      onClick={() => setListingType('service')}
                      className="p-3 rounded-lg transition-all"
                      style={{
                        backgroundColor: listingType === 'service' ? 'rgba(153, 69, 255, 0.2)' : '#121212',
                        borderWidth: '2px',
                        borderColor: listingType === 'service' ? '#9945FF' : '#333333'
                      }}
                    >
                      <Star size={24} className="mx-auto mb-2" style={{ color: '#9945FF' }} />
                      <p style={{ color: '#FFFFFF' }}>Service</p>
                    </button>
                  </div>
                </div>

                <div>
                  <Label style={{ color: '#B3B3B3' }}>Name *</Label>
                  <Input
                    placeholder={listingType === 'good' ? 'e.g., iPhone 13 Pro' : 'e.g., Logo Design Service'}
                    value={listingName}
                    onChange={(e) => setListingName(e.target.value)}
                    style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                  />
                </div>

                <div>
                  <Label style={{ color: '#B3B3B3' }}>Description *</Label>
                  <Textarea
                    placeholder="Describe your item or service..."
                    value={listingDescription}
                    onChange={(e) => setListingDescription(e.target.value)}
                    rows={3}
                    style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                  />
                </div>

                <div>
                  <Label style={{ color: '#B3B3B3' }}>Category *</Label>
                  <Select value={listingCategory} onValueChange={setListingCategory}>
                    <SelectTrigger style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
                      <SelectItem value="electronics" style={{ color: '#FFFFFF' }}>Electronics</SelectItem>
                      <SelectItem value="fashion" style={{ color: '#FFFFFF' }}>Fashion</SelectItem>
                      <SelectItem value="books" style={{ color: '#FFFFFF' }}>Books</SelectItem>
                      <SelectItem value="beauty" style={{ color: '#FFFFFF' }}>Beauty & Personal Care</SelectItem>
                      <SelectItem value="home" style={{ color: '#FFFFFF' }}>Home & Living</SelectItem>
                      <SelectItem value="education" style={{ color: '#FFFFFF' }}>Education</SelectItem>
                      <SelectItem value="design" style={{ color: '#FFFFFF' }}>Design</SelectItem>
                      <SelectItem value="tech" style={{ color: '#FFFFFF' }}>Tech</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label style={{ color: '#B3B3B3' }}>Price (NGN) *</Label>
                  <Input
                    type="number"
                    placeholder="0"
                    value={listingPrice}
                    onChange={(e) => setListingPrice(e.target.value)}
                    style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                  />
                </div>

                {listingType === 'good' && (
                  <div>
                    <Label style={{ color: '#B3B3B3' }}>Delivery Fee (Optional)</Label>
                    <Input
                      type="number"
                      placeholder="0"
                      value={listingDeliveryFee}
                      onChange={(e) => setListingDeliveryFee(e.target.value)}
                      style={{ backgroundColor: '#121212', borderColor: '#333333', color: '#FFFFFF' }}
                    />
                  </div>
                )}

                <Button 
                  className="w-full" 
                  style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
                  onClick={handleCreateListing}
                >
                  Publish Listing
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Analytics Cards */}
        <div className={`grid gap-4 ${isMobile ? 'grid-cols-2' : 'grid-cols-4'}`}>
          <Card className="p-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgba(153, 69, 255, 0.2)' }}>
                <Package size={20} style={{ color: '#9945FF' }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: '#B3B3B3' }}>Active</p>
                <p className="text-xl" style={{ color: '#FFFFFF' }}>{activeListings}</p>
              </div>
            </div>
          </Card>

          <Card className="p-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgba(74, 255, 153, 0.2)' }}>
                <TrendingUp size={20} style={{ color: '#4AFF99' }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: '#B3B3B3' }}>Total Sales</p>
                <p className="text-xl" style={{ color: '#FFFFFF' }}>{totalSales}</p>
              </div>
            </div>
          </Card>

          <Card className={`p-4 ${isMobile ? 'col-span-2' : ''}`} style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgba(255, 191, 0, 0.2)' }}>
                <DollarSign size={20} style={{ color: '#FFBF00' }} />
              </div>
              <div>
                <p className="text-sm" style={{ color: '#B3B3B3' }}>Revenue</p>
                <p className="text-xl" style={{ color: '#FFFFFF' }}>₦{totalRevenue.toLocaleString()}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Listings Grid */}
        <div className={`grid gap-4 ${isMobile ? 'grid-cols-2' : 'grid-cols-3 lg:grid-cols-4 xl:grid-cols-5'}`}>
          {myListings.map((listing) => (
            <Card 
              key={listing.id} 
              className="overflow-hidden" 
              style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}
            >
              <div className="aspect-square relative" style={{ backgroundColor: '#333333' }}>
                <div className="absolute inset-0 flex items-center justify-center">
                  <Package size={48} style={{ color: '#666666' }} />
                </div>
                <div 
                  className="absolute top-2 right-2 px-2 py-1 rounded text-xs"
                  style={{
                    backgroundColor: listing.status === 'active' ? '#4AFF99' : '#666666',
                    color: '#121212'
                  }}
                >
                  {listing.status}
                </div>
              </div>
              <div className="p-3">
                <h3 className="text-sm mb-1 truncate" style={{ color: '#FFFFFF' }}>
                  {listing.name}
                </h3>
                <p className="text-xs mb-2 truncate" style={{ color: '#666666' }}>
                  {listing.description}
                </p>
                <p className="mb-2" style={{ color: '#9945FF' }}>
                  ₦{listing.price.toLocaleString()}
                </p>
                <div className="flex items-center justify-between text-xs mb-3" style={{ color: '#B3B3B3' }}>
                  <div className="flex items-center gap-1">
                    <Eye size={12} />
                    <span>{listing.views}</span>
                  </div>
                  <span>{listing.sales} sales</span>
                </div>
                <div className="flex gap-2">
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="flex-1 text-xs" 
                    style={{ borderColor: '#9945FF', color: '#9945FF' }}
                  >
                    Edit
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="text-xs"
                    style={{ borderColor: '#FF4D4D', color: '#FF4D4D' }}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  // Buyer View
  return (
    <div className={`${isMobile ? 'px-4' : 'px-8 max-w-7xl mx-auto'} py-6 space-y-6`}>
      {/* Goods/Services Tabs */}
      <Tabs value={activeCategory} onValueChange={(v) => setActiveCategory(v as 'goods' | 'services')}>
        <div className="flex items-center justify-between mb-6">
          <TabsList className={`${isMobile ? 'grid grid-cols-2' : 'inline-flex'}`} style={{ backgroundColor: '#1E1E1E' }}>
            <TabsTrigger
              value="goods"
              className="px-8 py-2"
              style={{
                backgroundColor: activeCategory === 'goods' ? '#9945FF' : 'transparent',
                color: activeCategory === 'goods' ? '#FFFFFF' : '#B3B3B3',
              }}
            >
              Goods
            </TabsTrigger>
            <TabsTrigger
              value="services"
              className="px-8 py-2"
              style={{
                backgroundColor: activeCategory === 'services' ? '#9945FF' : 'transparent',
                color: activeCategory === 'services' ? '#FFFFFF' : '#B3B3B3',
              }}
            >
              Services
            </TabsTrigger>
          </TabsList>
        </div>

        {/* Category Filters */}
        <div className="flex gap-3 overflow-x-auto pb-4 mb-6 scrollbar-hide">
          {currentCategories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedSubCategory(cat)}
              className="px-5 py-2 rounded-full whitespace-nowrap transition-all text-sm"
              style={{
                backgroundColor: selectedSubCategory === cat ? '#9945FF' : '#1E1E1E',
                color: selectedSubCategory === cat ? '#FFFFFF' : '#B3B3B3',
                border: selectedSubCategory === cat ? 'none' : '1px solid #333333',
              }}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Goods Tab Content */}
        <TabsContent value="goods" className="mt-0">
          <div className={`grid gap-5 ${isMobile ? 'grid-cols-2' : 'grid-cols-3 lg:grid-cols-4 xl:grid-cols-5'}`}>
            {filteredGoods.map((item) => (
              <Card
                key={item.id}
                className="overflow-hidden group cursor-pointer transition-all hover:shadow-lg hover:scale-105"
                style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}
                onClick={() => navigate(`/product/${item.id}`)}
              >
                <div className="relative aspect-square overflow-hidden">
                  <ImageWithFallback
                    src={item.image}
                    alt={item.name}
                    className="w-full h-full object-cover transition-transform group-hover:scale-110"
                  />
                  <button
                    className="absolute top-3 right-3 p-2 rounded-full transition-all backdrop-blur-sm"
                    style={{ backgroundColor: 'rgba(0, 0, 0, 0.6)' }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Heart size={16} style={{ color: '#FFFFFF' }} />
                  </button>
                </div>
                <div className="p-3 space-y-2">
                  <h3 className="text-sm truncate" style={{ color: '#FFFFFF' }}>
                    {item.name}
                  </h3>
                  <div className="flex items-center gap-1">
                    <Star size={14} fill="#FFBF00" style={{ color: '#FFBF00' }} />
                    <span className="text-xs" style={{ color: '#FFBF00' }}>
                      {item.rating}
                    </span>
                    <span className="text-xs ml-1" style={{ color: '#666666' }}>
                      ({Math.floor(Math.random() * 500) + 100})
                    </span>
                  </div>
                  <p className="text-sm" style={{ color: '#9945FF' }}>
                    ₦{item.price.toLocaleString()}
                  </p>
                  <Button 
                    className="w-full" 
                    size="sm" 
                    style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAddToCart(item, 'good');
                    }}
                  >
                    <ShoppingCart size={16} className="mr-2" />
                    Add to Cart
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Services Tab Content */}
        <TabsContent value="services" className="mt-0">
          <div className={`grid gap-5 ${isMobile ? 'grid-cols-2' : 'grid-cols-3 lg:grid-cols-4 xl:grid-cols-5'}`}>
            {filteredServices.map((item) => (
              <Card
                key={item.id}
                className="overflow-hidden group cursor-pointer transition-all hover:shadow-lg hover:scale-105"
                style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}
                onClick={() => navigate(`/product/${item.id}`)}
              >
                <div className="aspect-square flex items-center justify-center" style={{ backgroundColor: '#333333' }}>
                  <div className="text-center">
                    <div
                      className="w-20 h-20 rounded-full flex items-center justify-center mx-auto"
                      style={{ backgroundColor: '#9945FF' }}
                    >
                      <span className="text-3xl">
                        {item.category === 'Education' && '📚'}
                        {item.category === 'Design' && '🎨'}
                        {item.category === 'Tech' && '💻'}
                        {item.category === 'Media' && '📸'}
                        {item.category === 'Transportation' && '🚗'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="p-3 space-y-2">
                  <h3 className="text-sm truncate" style={{ color: '#FFFFFF' }}>
                    {item.name}
                  </h3>
                  <div className="flex items-center gap-1">
                    <Star size={14} fill="#FFBF00" style={{ color: '#FFBF00' }} />
                    <span className="text-xs" style={{ color: '#FFBF00' }}>
                      {item.rating}
                    </span>
                    <span className="text-xs ml-1" style={{ color: '#666666' }}>
                      ({Math.floor(Math.random() * 300) + 50})
                    </span>
                  </div>
                  <p className="text-sm" style={{ color: '#9945FF' }}>
                    ₦{item.price.toLocaleString()}
                  </p>
                  <Button 
                    className="w-full" 
                    size="sm" 
                    style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAddToCart(item, 'service');
                    }}
                  >
                    <ShoppingCart size={16} className="mr-2" />
                    Book Service
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
