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
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  ArrowLeft,
  Star,
  MapPin,
  Shield,
  MessageCircle,
  ShoppingCart,
} from 'lucide-react-native';
import { useQuery } from '@tanstack/react-query';
import { getSingleListing } from '@/api/listings';
import { getSingleMarketplace } from '@/api/marketplace';
import { StorageService } from '@/services/StorageService';
import { STORAGE_KEYS } from '@/constants/storageKeys';
import Toast from 'react-native-toast-message';

const { width } = Dimensions.get('window');

export default function ProductDetailScreen() {
  const { id } = useLocalSearchParams();
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // Find product by id (in real app, this would be an API call)
  // const product = mockProducts.find((p) => p.id === id);

  const mockProductImages = [
    'https://images.pexels.com/photos/18105/pexels-photo.jpg?auto=compress&cs=tinysrgb&w=400',
  ];

  const { data: productData } = useQuery({
    queryKey: ['product-images', id],
    queryFn: () => getSingleListing(id.toString()),
  });

  const { data: marketplaceData } = useQuery({
    queryKey: ['marketplace', id, productData?.marketplace_id],
    queryFn: () => getSingleMarketplace(productData?.marketplace_id),
    enabled: !!productData?.marketplace_id,
  });

  if (!productData) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.errorText}>Product not found</Text>
      </SafeAreaView>
    );
  }

  const handleAddToCart = async () => {
    try {
      // Validate product data exists
      if (!productData || !productData.id) {
        return;
      }

      const productId = String(productData.id);

      // Get existing cart items with proper type
      const existingCartItems = await StorageService.getItem(STORAGE_KEYS.CART);
      const cartItems = existingCartItems ?? [];

      // Check if product already exists in cart
      const existingItemIndex = cartItems.findIndex(
        (item: any) => item.id === productId
      );

      let updatedCart;

      if (existingItemIndex !== -1) {
        updatedCart = cartItems.map((item: any, index: any) =>
          index === existingItemIndex
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );

        Toast.show({
          type: 'success',
          text1: `Increased quantity to ${updatedCart[existingItemIndex].quantity}`,
        });
      } else {
        const newCartItem = {
          id: productId,
          product: productData,
          quantity: 1,
        };

        updatedCart = [...cartItems, newCartItem];

        Toast.show({
          type: 'success',
          text1: 'Product added to cart',
        });
      }

      // Save updated cart
      await StorageService.setItem(STORAGE_KEYS.CART, updatedCart);
    } catch (error) {
      console.error('Error adding item to cart:', error);

      Toast.show({
        type: 'warn',
        text1: 'Failed to add item to cart. Please try again.',
      });
    }
  };

  const handleBuyNow = async() => {
    await handleAddToCart()
    // Mock buy now - go to checkout
    router.push('/checkout');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => router.back()}
          style={styles.backButton}
        >
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
              const index = Math.round(
                event.nativeEvent.contentOffset.x / width
              );
              setCurrentImageIndex(index);
            }}
          >
            {mockProductImages.map((image, index) => (
              <Image
                key={index}
                source={{ uri: image }}
                style={styles.productImage}
              />
            ))}
          </ScrollView>

          <View style={styles.imageIndicators}>
            {mockProductImages.map((_, index) => (
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
            <Text style={styles.productTitle}>{productData?.title}</Text>
            <Text style={styles.productCategory}>{productData?.category}</Text>
            <Text style={styles.productPrice}>{productData?.price} SOL</Text>
            <Text style={styles.productDescription}>
              {productData?.description}
            </Text>

            <View style={styles.locationRow}>
              <MapPin color={theme.textMuted} size={16} />
              <Text style={styles.locationText}>{productData?.location}</Text>
            </View>
          </Card>

          {/* Seller Info */}
          <Card style={styles.sellerCard}>
            <View style={styles.sellerHeader}>
              <Image
                source={{
                  uri: 'https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&dpr=1',
                }}
                style={styles.sellerAvatar}
              />
              <View style={styles.sellerInfo}>
                <Text style={styles.sellerName}>
                  {productData?.profiles?.full_name}
                </Text>
                <Text style={styles.sellerCampus}>{marketplaceData?.name}</Text>
                <View style={styles.ratingRow}>
                  <Star color={theme.warning} size={14} fill={theme.warning} />
                  <Text style={styles.ratingText}>4.5 rating</Text>
                </View>
              </View>
              {/* <TouchableOpacity style={styles.messageButton}>
                <MessageCircle color={theme.primary} size={20} />
              </TouchableOpacity> */}
            </View>
          </Card>

          {/* Escrow Info */}
          <Card style={styles.escrowCard}>
            <View style={styles.escrowHeader}>
              <Shield color={theme.accent} size={20} />
              <Text style={styles.escrowTitle}>
                Secure Payment with Solana Escrow
              </Text>
            </View>
            <Text style={styles.escrowDescription}>
              Your payment is held securely in a Solana smart contract until
              delivery is confirmed. Funds are automatically released when you
              confirm receipt.
            </Text>
            <View style={styles.escrowFeatures}>
              <Text style={styles.escrowFeature}>• Payment held in SOL</Text>
              <Text style={styles.escrowFeature}>
                • Automatic release on confirmation
              </Text>
              <Text style={styles.escrowFeature}>
                • Dispute resolution available
              </Text>
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