import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';
import { Card } from './ui/Card';
import { MarketPlaceProductInterface } from '@/interface/marketplace';
import { theme } from '@/constants/Colors';
import { useQuery } from '@tanstack/react-query';
import { getListingImages } from '@/api/listings';

interface ProductCardProps {
  product: MarketPlaceProductInterface;
  onPress: () => void;
  style?: any;
}

export function ProductCard({ product, onPress, style }: ProductCardProps) {
  // const { data: productImages } = useQuery({
  //   queryKey: ['product-images', product.id],
  //   queryFn: () => getListingImages(product.id.toString()),
  // });

  // console.log('productImages', productImages);
  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.8}>
      <Card style={{ ...styles.container, ...style }}>
        <Image
          source={{
            uri: 'https://images.pexels.com/photos/18105/pexels-photo.jpg?auto=compress&cs=tinysrgb&w=400',
          }}
          style={styles.image}
        />
        <View style={styles.content}>
          <Text style={styles.title} numberOfLines={2}>
            {product.title}
          </Text>
          <Text style={styles.category}>{product.category}</Text>
          <View style={styles.footer}>
            <Text style={styles.price}>{product.price} SOL</Text>
            {/* <View style={styles.seller}>
              <Image
                source={{ uri: product.seller.avatar }}
                style={styles.avatar}
              />
              <Text style={styles.sellerName}>{product.seller.name}</Text>
            </View> */}
          </View>
        </View>
      </Card>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  image: {
    width: '100%',
    height: 160,
    borderRadius: 8,
    marginBottom: 12,
  },
  content: {
    flex: 1,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
    marginBottom: 4,
  },
  category: {
    fontSize: 12,
    color: theme.textMuted,
    marginBottom: 8,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  price: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.accent,
  },
  seller: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 20,
    height: 20,
    borderRadius: 10,
    marginRight: 4,
  },
  sellerName: {
    fontSize: 12,
    color: theme.textSecondary,
  },
});