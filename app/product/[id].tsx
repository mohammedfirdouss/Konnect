import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  ScrollView,
  Image,
  TouchableOpacity,
  Dimensions 
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { theme } from '@/constants/Colors';
import { mockProducts } from '@/constants/MockData';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { ArrowLeft, Star, MapPin, Shield, MessageCircle, ShoppingCart } from 'lucide-react-native';

const { width } = Dimensions.get('window');

export default function ProductDetailScreen() {
  const { id } = useLocalSearchParams();
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  // Find product by id (in real app, this would be an API call)
  const product = mockProducts.find(p => p.id === id);
  
  if (!product) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.errorText}>Product not found</Text>
      </SafeAreaView>
    );
  }

  const handleAddToCart = () => {
    // Mock add to cart
    router.push('/cart');
  };

  const handleBuyNow = () => {
    // Mock buy now - go to checkout
    router.push('/checkout');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <ArrowLeft color={theme.text} size={24} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Product Details</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Product Images */}
        <View style={styles.imageContainer}>
          <ScrollView 
            horizontal 
            pagingEnabled 
            showsHorizontalScrollIndicator={false}
            onMomentumScrollEnd={(event) => {
              const index = Math.round(event.nativeEvent.contentOffset.x / width);
              setCurrentImageIndex(index);
            }}
          >
            {product.images.map((image, index) => (
              <Image key={index} source={{ uri: image }} style={styles.productImage} />
            ))}
          </ScrollView>
          
          <View style={styles.imageIndicators}>
            {product.images.map((_, index) => (
              <View
                key={index}
                style={[
                  styles.indicator,
                  index === currentImageIndex && styles.activeIndicator,
                ]}
              />
            ))}
          </View>
        </View>

        <View style={styles.content}>
          {/* Product Info */}
          <Card style={styles.productInfo}>
            <Text style={styles.productTitle}>{product.title}</Text>
            <Text style={styles.productCategory}>{product.category}</Text>
            <Text style={styles.productPrice}>${product.price}</Text>
            <Text style={styles.productDescription}>{product.description}</Text>
            
            <View style={styles.locationRow}>
              <MapPin color={theme.textMuted} size={16} />
              <Text style={styles.locationText}>{product.location}</Text>
            </View>
          </Card>

          {/* Seller Info */}
          <Card style={styles.sellerCard}>
            <View style={styles.sellerHeader}>
              <Image source={{ uri: product.seller.avatar }} style={styles.sellerAvatar} />
              <View style={styles.sellerInfo}>
                <Text style={styles.sellerName}>{product.seller.name}</Text>
                <Text style={styles.sellerCampus}>{product.seller.campus}</Text>
                <View style={styles.ratingRow}>
                  <Star color={theme.warning} size={14} fill={theme.warning} />
                  <Text style={styles.ratingText}>{product.seller.rating} rating</Text>
                </View>
              </View>
              <TouchableOpacity style={styles.messageButton}>
                <MessageCircle color={theme.primary} size={20} />
              </TouchableOpacity>
            </View>
          </Card>

          {/* Escrow Info */}
          <Card style={styles.escrowCard}>
            <View style={styles.escrowHeader}>
              <Shield color={theme.accent} size={20} />
              <Text style={styles.escrowTitle}>Secure Payment with Solana Escrow</Text>
            </View>
            <Text style={styles.escrowDescription}>
              Your payment is held securely in a Solana smart contract until delivery is confirmed. 
              Funds are automatically released when you confirm receipt.
            </Text>
            <View style={styles.escrowFeatures}>
              <Text style={styles.escrowFeature}>• Payment held in SOL</Text>
              <Text style={styles.escrowFeature}>• Automatic release on confirmation</Text>
              <Text style={styles.escrowFeature}>• Dispute resolution available</Text>
            </View>
          </Card>
        </View>
      </ScrollView>

      {/* Bottom Actions */}
      <View style={styles.bottomActions}>
        <Button
          title="Add to Cart"
          variant="outline"
          onPress={handleAddToCart}
          style={styles.addToCartButton}
        />
        <Button
          title="Buy Now"
          onPress={handleBuyNow}
          style={styles.buyNowButton}
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
  errorText: {
    fontSize: 18,
    color: theme.text,
    textAlign: 'center',
    marginTop: 100,
  },
  imageContainer: {
    position: 'relative',
  },
  productImage: {
    width,
    height: 300,
    resizeMode: 'cover',
  },
  imageIndicators: {
    position: 'absolute',
    bottom: 16,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
  },
  indicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.5)',
  },
  activeIndicator: {
    backgroundColor: theme.primary,
  },
  content: {
    padding: 20,
  },
  productInfo: {
    marginBottom: 16,
  },
  productTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.text,
    marginBottom: 8,
  },
  productCategory: {
    fontSize: 14,
    color: theme.textMuted,
    marginBottom: 8,
  },
  productPrice: {
    fontSize: 28,
    fontWeight: 'bold',
    color: theme.accent,
    marginBottom: 16,
  },
  productDescription: {
    fontSize: 16,
    color: theme.textSecondary,
    lineHeight: 24,
    marginBottom: 16,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  locationText: {
    fontSize: 14,
    color: theme.textMuted,
    marginLeft: 6,
  },
  sellerCard: {
    marginBottom: 16,
  },
  sellerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sellerAvatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginRight: 12,
  },
  sellerInfo: {
    flex: 1,
  },
  sellerName: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
    marginBottom: 4,
  },
  sellerCampus: {
    fontSize: 14,
    color: theme.textMuted,
    marginBottom: 4,
  },
  ratingRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ratingText: {
    fontSize: 14,
    color: theme.textMuted,
    marginLeft: 4,
  },
  messageButton: {
    padding: 8,
  },
  escrowCard: {
    marginBottom: 16,
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
    marginBottom: 12,
  },
  escrowFeatures: {
    gap: 4,
  },
  escrowFeature: {
    fontSize: 14,
    color: theme.textMuted,
  },
  bottomActions: {
    flexDirection: 'row',
    padding: 20,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: theme.border,
    gap: 12,
  },
  addToCartButton: {
    flex: 1,
  },
  buyNowButton: {
    flex: 2,
  },
});