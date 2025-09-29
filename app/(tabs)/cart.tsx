import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  FlatList,
  Image,
  TouchableOpacity,
} from 'react-native';
import { theme } from '@/constants/Colors';
import { mockProducts } from '@/constants/MockData';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Trash2, Plus, Minus } from 'lucide-react-native';
import { router } from 'expo-router';
import { StorageService } from '@/services/StorageService';
import { STORAGE_KEYS } from '@/constants/storageKeys';
import { ProductInterface } from '@/interface/marketplace';
import { CartItem } from '@/interface/orders';

export default function CartScreen() {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);

  const updateQuantity = (id: string, change: number) => {
    setCartItems((items) =>
      items.map((item) =>
        item.id === id
          ? { ...item, quantity: Math.max(1, item.quantity + change) }
          : item
      )
    );
  };

  const removeItem = async (id: string) => {
    // setCartItems(items => items.filter(item => item.id !== id));

    try {
      // Get current cart items
      const existingCartItems = await StorageService.getItem<CartItem[]>(
        STORAGE_KEYS.CART
      );
      const cartItems: CartItem[] = existingCartItems ?? [];

      const updatedCart = cartItems.filter((item) => item.id !== id);

      await StorageService.setItem(STORAGE_KEYS.CART, updatedCart);

      setCartItems(updatedCart);

      console.log(`Item ${id} removed from cart`);
    } catch (error) {
      console.error('Error removing item from cart:', error);
    }
  };

  const total = cartItems.reduce(
    (sum, item) => sum + item.product.price * item.quantity,
    0
  );

  const fetchCartItems = async () => {
    const stored = await StorageService.getItem<CartItem[]>(STORAGE_KEYS.CART);
    // console.log('cartItems', stored);
    setCartItems(stored ?? []);
  };

  useEffect(() => {
    fetchCartItems();
  }, [fetchCartItems]);

  const renderCartItem = ({ item }: { item: CartItem }) => (
    <Card style={styles.cartItem}>
      <Image
        source={{
          uri: 'https://images.pexels.com/photos/18105/pexels-photo.jpg?auto=compress&cs=tinysrgb&w=400',
        }}
        style={styles.productImage}
      />
      <View style={styles.itemDetails}>
        <Text style={styles.productTitle}>{item.product?.title}</Text>
        <Text style={styles.productPrice}>{item.product?.price} SOL</Text>
        <Text style={styles.sellerName}>
          {item.product?.profiles?.full_name}
        </Text>
      </View>
      <View style={styles.itemControls}>
        <TouchableOpacity
          onPress={() => removeItem(item.id)}
          style={styles.removeButton}
        >
          <Trash2 color={theme.danger} size={16} />
        </TouchableOpacity>
        <View style={styles.quantityControls}>
          <TouchableOpacity
            onPress={() => updateQuantity(item.id, -1)}
            style={styles.quantityButton}
          >
            <Minus color={theme.text} size={16} />
          </TouchableOpacity>
          <Text style={styles.quantity}>{item.quantity}</Text>
          <TouchableOpacity
            onPress={() => updateQuantity(item.id, 1)}
            style={styles.quantityButton}
          >
            <Plus color={theme.text} size={16} />
          </TouchableOpacity>
        </View>
      </View>
    </Card>
  );

  if (cartItems.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Shopping Cart</Text>
        </View>
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>Your cart is empty</Text>
          <Text style={styles.emptySubtext}>
            Browse products to start shopping
          </Text>
          <Button
            title="Explore Marketplace"
            onPress={() => router.push('/search')}
            style={styles.exploreButton}
          />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Shopping Cart</Text>
        <Text style={styles.itemCount}>{cartItems.length} items</Text>
      </View>

      <FlatList
        data={cartItems}
        renderItem={renderCartItem}
        keyExtractor={(item, i) => item.id + i}
        contentContainerStyle={styles.cartList}
        showsVerticalScrollIndicator={false}
      />

      <View style={styles.footer}>
        <Card style={styles.totalCard}>
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Total:</Text>
            <Text style={styles.totalAmount}>{total.toFixed(2)} SOL</Text>
          </View>
          <Button
            title="Proceed to Checkout"
            onPress={() => router.push('/checkout')}
            style={styles.checkoutButton}
          />
        </Card>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.background,
    paddingTop: 50,
  },
  header: {
    padding: 20,
    paddingBottom: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.text,
  },
  itemCount: {
    fontSize: 14,
    color: theme.textMuted,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.text,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 16,
    color: theme.textMuted,
    textAlign: 'center',
    marginBottom: 24,
  },
  exploreButton: {
    minWidth: 200,
  },
  cartList: {
    padding: 20,
    paddingTop: 10,
  },
  cartItem: {
    flexDirection: 'row',
    marginBottom: 16,
    padding: 12,
  },
  productImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    marginRight: 12,
  },
  itemDetails: {
    flex: 1,
  },
  productTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.text,
    marginBottom: 4,
  },
  productPrice: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.accent,
    marginBottom: 2,
  },
  sellerName: {
    fontSize: 12,
    color: theme.textMuted,
  },
  itemControls: {
    alignItems: 'flex-end',
  },
  removeButton: {
    padding: 4,
    marginBottom: 8,
  },
  quantityControls: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.background,
    borderRadius: 8,
    paddingHorizontal: 4,
  },
  quantityButton: {
    padding: 8,
  },
  quantity: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.text,
    minWidth: 30,
    textAlign: 'center',
  },
  footer: {
    padding: 20,
    paddingTop: 10,
  },
  totalCard: {
    padding: 20,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.text,
  },
  totalAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.accent,
  },
  checkoutButton: {
    width: '100%',
  },
});
