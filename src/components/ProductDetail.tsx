import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'motion/react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { ArrowLeft, ShoppingCart, ChevronDown, ChevronUp, Store, MapPin, Star } from 'lucide-react';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { useCart } from '../contexts/CartContext';
import { useUser } from '../contexts/UserContext';
import { toast } from 'sonner@2.0.3';
import { useIsMobile } from '../hooks/useIsMobile';

interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  image?: string;
  category: string;
  seller: string;
  sellerRating?: number;
  location?: string;
  deliveryFee?: number;
  condition?: string;
}

// Mock product data - in a real app, this would come from an API
const mockProducts: Product[] = [
  {
    id: 1,
    name: 'MacBook Air M2',
    description: 'Barely used MacBook Air M2 with 8GB RAM and 256GB SSD. Comes with original charger and box. Perfect condition, only 3 months old. Great for students and professionals.',
    price: 450000,
    image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800',
    category: 'Electronics',
    seller: 'David K.',
    sellerRating: 4.8,
    location: 'Yaba Campus',
    deliveryFee: 2000,
    condition: 'Like New',
  },
  {
    id: 2,
    name: 'iPhone 13 Pro',
    description: 'iPhone 13 Pro 128GB in excellent condition. Battery health at 95%. No scratches, comes with case and screen protector.',
    price: 380000,
    image: 'https://images.unsplash.com/photo-1632661674596-df8be070a5c5?w=800',
    category: 'Electronics',
    seller: 'Sarah M.',
    sellerRating: 4.9,
    location: 'Surulere Campus',
    deliveryFee: 1500,
    condition: 'Excellent',
  },
  {
    id: 3,
    name: 'Study Desk',
    description: 'Sturdy wooden study desk with drawers. Perfect for dorm rooms or study spaces. Dimensions: 120cm x 60cm x 75cm.',
    price: 25000,
    category: 'Furniture',
    seller: 'John D.',
    sellerRating: 4.5,
    location: 'Ikeja Campus',
    deliveryFee: 3000,
    condition: 'Good',
  },
  {
    id: 4,
    name: 'Calculus Textbook',
    description: 'Stewart Calculus 8th Edition. Lightly used with minimal highlighting. All pages intact.',
    price: 8000,
    category: 'Books',
    seller: 'Emma L.',
    sellerRating: 5.0,
    location: 'Yaba Campus',
    deliveryFee: 500,
    condition: 'Good',
  },
];

export function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { user } = useUser();
  const { isMobile } = useIsMobile();
  
  const [product, setProduct] = useState<Product | null>(null);
  const [showFeeBreakdown, setShowFeeBreakdown] = useState(false);
  const [isAdding, setIsAdding] = useState(false);

  useEffect(() => {
    // Find the product by ID
    const foundProduct = mockProducts.find(p => p.id === Number(id));
    if (foundProduct) {
      setProduct(foundProduct);
    } else {
      toast.error('Product not found');
      navigate('/marketplace');
    }
  }, [id, navigate]);

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#121212' }}>
        <p style={{ color: '#B3B3B3' }}>Loading...</p>
      </div>
    );
  }

  const platformFee = Math.round(product.price * 0.02); // 2% platform fee
  const gasFee = 500; // Mock SOL gas fee in Naira
  const deliveryFee = product.deliveryFee || 0;
  const totalPrice = product.price + platformFee + gasFee + deliveryFee;

  const handleAddToCart = () => {
    setIsAdding(true);
    
    // Simulate a small delay for better UX
    setTimeout(() => {
      addToCart({
        id: product.id,
        name: product.name,
        price: product.price,
        image: product.image || '',
        seller: product.seller,
        category: product.category,
        type: 'good',
      });
      
      toast.success(`${product.name} added to cart`);
      setIsAdding(false);
    }, 300);
  };

  const handleBuyNow = () => {
    handleAddToCart();
    setTimeout(() => {
      navigate('/cart');
    }, 400);
  };

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
          onClick={() => navigate(-1)}
          className="p-2 rounded-lg transition-all"
          style={{ color: '#B3B3B3' }}
        >
          <ArrowLeft size={24} />
        </button>
        <h3 style={{ color: '#FFFFFF' }}>Product Details</h3>
      </div>

      {/* Content */}
      <div className={isMobile ? 'px-4 py-6' : 'max-w-7xl mx-auto px-8 py-8'}>
        <div className={isMobile ? 'space-y-6' : 'grid grid-cols-2 gap-8'}>
          {/* Left Column - Image */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <Card className="overflow-hidden" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
              {product.image ? (
                <ImageWithFallback
                  src={product.image}
                  alt={product.name}
                  className={isMobile ? 'w-full h-64 object-cover' : 'w-full h-96 object-cover'}
                />
              ) : (
                <div 
                  className={isMobile ? 'w-full h-64 flex items-center justify-center' : 'w-full h-96 flex items-center justify-center'}
                  style={{ backgroundColor: '#333333' }}
                >
                  <ShoppingCart size={48} style={{ color: '#666666' }} />
                </div>
              )}
            </Card>

            {/* Seller Info Card - Desktop only */}
            {!isMobile && (
              <Card className="p-4 mt-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
                <div className="flex items-center gap-3">
                  <div 
                    className="w-12 h-12 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#9945FF' }}
                  >
                    <Store size={24} style={{ color: '#FFFFFF' }} />
                  </div>
                  <div className="flex-1">
                    <h4 style={{ color: '#FFFFFF' }}>{product.seller}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      {product.sellerRating && (
                        <div className="flex items-center gap-1">
                          <Star size={14} style={{ color: '#FFBF00', fill: '#FFBF00' }} />
                          <span className="text-sm" style={{ color: '#B3B3B3' }}>
                            {product.sellerRating}
                          </span>
                        </div>
                      )}
                      {product.location && (
                        <>
                          <span style={{ color: '#666666' }}>•</span>
                          <div className="flex items-center gap-1">
                            <MapPin size={14} style={{ color: '#666666' }} />
                            <span className="text-sm" style={{ color: '#B3B3B3' }}>
                              {product.location}
                            </span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    style={{ borderColor: '#9945FF', color: '#9945FF' }}
                  >
                    View Profile
                  </Button>
                </div>
              </Card>
            )}
          </motion.div>

          {/* Right Column - Details */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="space-y-4"
          >
            {/* Product Info */}
            <Card className="p-6" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h2 className="mb-2" style={{ color: '#FFFFFF' }}>{product.name}</h2>
                  <div className="flex items-center gap-2 mb-3">
                    <span 
                      className="px-2 py-1 rounded text-xs"
                      style={{ backgroundColor: 'rgba(153, 69, 255, 0.1)', color: '#9945FF' }}
                    >
                      {product.category}
                    </span>
                    {product.condition && (
                      <span 
                        className="px-2 py-1 rounded text-xs"
                        style={{ backgroundColor: 'rgba(74, 255, 153, 0.1)', color: '#4AFF99' }}
                      >
                        {product.condition}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <p style={{ color: '#9945FF' }}>₦{product.price.toLocaleString()}</p>
              </div>

              <div className="mb-4 pb-4" style={{ borderBottom: '1px solid #333333' }}>
                <p style={{ color: '#B3B3B3' }}>{product.description}</p>
              </div>

              {/* Delivery Fee */}
              {deliveryFee > 0 && (
                <div className="flex items-center justify-between py-2">
                  <span style={{ color: '#B3B3B3' }}>Delivery Fee:</span>
                  <span style={{ color: '#FFFFFF' }}>₦{deliveryFee.toLocaleString()}</span>
                </div>
              )}

              {/* Fee Breakdown Toggle */}
              <button
                onClick={() => setShowFeeBreakdown(!showFeeBreakdown)}
                className="w-full flex items-center justify-between py-3 px-4 rounded-lg transition-all"
                style={{ backgroundColor: '#121212' }}
              >
                <span style={{ color: '#B3B3B3' }}>Fee Breakdown</span>
                {showFeeBreakdown ? (
                  <ChevronUp size={20} style={{ color: '#9945FF' }} />
                ) : (
                  <ChevronDown size={20} style={{ color: '#9945FF' }} />
                )}
              </button>

              {/* Expandable Fee Breakdown */}
              {showFeeBreakdown && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="mt-2 p-4 rounded-lg space-y-3"
                  style={{ backgroundColor: '#121212' }}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm" style={{ color: '#666666' }}>Item Price:</span>
                    <span className="text-sm" style={{ color: '#FFFFFF' }}>₦{product.price.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm" style={{ color: '#666666' }}>Platform Fee (2%):</span>
                    <span className="text-sm" style={{ color: '#FFFFFF' }}>₦{platformFee.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm" style={{ color: '#666666' }}>SOL Gas Fee:</span>
                    <span className="text-sm" style={{ color: '#FFFFFF' }}>₦{gasFee.toLocaleString()}</span>
                  </div>
                  {deliveryFee > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm" style={{ color: '#666666' }}>Delivery Fee:</span>
                      <span className="text-sm" style={{ color: '#FFFFFF' }}>₦{deliveryFee.toLocaleString()}</span>
                    </div>
                  )}
                  <div className="h-px" style={{ backgroundColor: '#333333' }} />
                  <div className="flex items-center justify-between">
                    <span style={{ color: '#FFFFFF' }}>Total:</span>
                    <span style={{ color: '#9945FF' }}>₦{totalPrice.toLocaleString()}</span>
                  </div>
                </motion.div>
              )}
            </Card>

            {/* Seller Info Card - Mobile only */}
            {isMobile && (
              <Card className="p-4" style={{ backgroundColor: '#1E1E1E', borderColor: '#333333' }}>
                <div className="flex items-center gap-3">
                  <div 
                    className="w-12 h-12 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: '#9945FF' }}
                  >
                    <Store size={24} style={{ color: '#FFFFFF' }} />
                  </div>
                  <div className="flex-1">
                    <h4 style={{ color: '#FFFFFF' }}>{product.seller}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      {product.sellerRating && (
                        <div className="flex items-center gap-1">
                          <Star size={14} style={{ color: '#FFBF00', fill: '#FFBF00' }} />
                          <span className="text-sm" style={{ color: '#B3B3B3' }}>
                            {product.sellerRating}
                          </span>
                        </div>
                      )}
                      {product.location && (
                        <>
                          <span style={{ color: '#666666' }}>•</span>
                          <div className="flex items-center gap-1">
                            <MapPin size={14} style={{ color: '#666666' }} />
                            <span className="text-sm" style={{ color: '#B3B3B3' }}>
                              {product.location}
                            </span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {/* Action Buttons - Desktop only */}
            {!isMobile && (
              <div className="flex gap-3 mt-6">
                <Button
                  onClick={handleAddToCart}
                  disabled={isAdding}
                  variant="outline"
                  className="flex-1"
                  style={{ borderColor: '#9945FF', color: '#9945FF' }}
                >
                  <ShoppingCart size={20} className="mr-2" />
                  Add to Cart
                </Button>
                <Button
                  onClick={handleBuyNow}
                  disabled={isAdding}
                  className="flex-1"
                  style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
                >
                  Buy Now
                </Button>
              </div>
            )}
          </motion.div>
        </div>
      </div>

      {/* Action Buttons - Mobile Fixed Bottom */}
      {isMobile && (
        <div 
          className="fixed left-0 right-0 p-4 flex gap-3" 
          style={{ 
            backgroundColor: '#121212', 
            borderTop: '1px solid #333333',
            bottom: '72px',
            zIndex: 60
          }}
        >
          <Button
            onClick={handleAddToCart}
            disabled={isAdding}
            variant="outline"
            className="flex-1"
            style={{ borderColor: '#9945FF', color: '#9945FF' }}
          >
            <ShoppingCart size={20} className="mr-2" />
            Add to Cart
          </Button>
          <Button
            onClick={handleBuyNow}
            disabled={isAdding}
            className="flex-1"
            style={{ backgroundColor: '#9945FF', color: '#FFFFFF' }}
          >
            Buy Now
          </Button>
        </div>
      )}
    </div>
  );
}
