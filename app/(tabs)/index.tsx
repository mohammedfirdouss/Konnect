import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  SafeAreaView,
} from 'react-native';
import { theme } from '@/constants/Colors';
import { categories } from '@/constants/MockData';
import { ProductCard } from '@/components/ProductCard';
import { router } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { getMarketplaceProducts } from '@/api/marketplace';
import { useAuthorization } from '@/hooks/useAuthorization';
import { MarketPlaceProductInterface } from '@/interface/marketplace';
import { TopBar } from '@/components/top-bar/TopBar';
import { fetchAIRecommendations } from '@/api/ai';

const HomeScreen = () => {
  const { selectedAccount } = useAuthorization();

  const { data: recommededProducts } = useQuery({
    queryKey: ['ai-recommedations'],
    queryFn: fetchAIRecommendations,
  });

  const { data: marketPlaceProducts, isLoading } = useQuery({
    queryKey: ['marketplace-products'],
    queryFn: getMarketplaceProducts,
  });

  console.log('marketPlaceProducts', marketPlaceProducts);

  const renderCategory = ({ item }: { item: (typeof categories)[0] }) => (
    <TouchableOpacity
      style={styles.categoryCard}
      onPress={() => router.push(`/search?category=${item.name}`)}
    >
      <Text style={styles.categoryIcon}>{item.icon}</Text>
      <Text style={styles.categoryName}>{item.name}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <TopBar />

        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Welcome back! 👋</Text>
            <Text style={styles.subtitle}>
              Find everything you need on campus
            </Text>
          </View>
        </View>

        {/* Categories */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Categories</Text>
          <FlatList
            data={categories}
            renderItem={renderCategory}
            keyExtractor={(item) => item.id}
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.categoriesContainer}
          />
        </View>

        {/* AI Recommendations */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>✨ Recommended for you</Text>
            <Text style={styles.aiLabel}>AI Powered</Text>
          </View>

          {/* {recommededProducts?.recommedations?.length > 0 ? ( */}
          {recommededProducts?.products?.length > 0 ? (
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.recommendationsGrid}
            >
              {recommededProducts?.products
                ?.slice(0, 4)
                .map((product: MarketPlaceProductInterface) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onPress={() => router.replace(`/product/${product.id}`)}
                    style={styles.recommendationCard}
                  />
                ))}
            </ScrollView>
          ) : (
            <View>
              <Text
                style={{
                  color: 'white',
                }}
              >
                No recommeded products. Keep browsing
              </Text>
            </View>
          )}
        </View>

        {/* Recent Listings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Listings</Text>
          <ScrollView showsVerticalScrollIndicator={false}>
            <View style={styles.listingsGrid}>
              {isLoading ? (
                <Text style={{ color: theme.text }}>Loading...</Text>
              ) : (
                marketPlaceProducts?.products?.map(
                  (product: MarketPlaceProductInterface) => (
                    <View style={styles.listingCard} key={product.id}>
                      <ProductCard
                        product={product}
                        onPress={() => router.push(`/product/${product.id}`)}
                      />
                    </View>
                  )
                )
              )}
            </View>
          </ScrollView>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

export default HomeScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.background,
    paddingTop: 50,
  },
  header: {
    padding: 20,
    paddingBottom: 10,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.text,
  },
  subtitle: {
    fontSize: 16,
    color: theme.textMuted,
    marginTop: 4,
  },
  section: {
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    // marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.text,
    marginBottom: 16,
  },
  aiLabel: {
    fontSize: 12,
    color: theme.accent,
    backgroundColor: theme.surface,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    fontWeight: '600',
  },
  categoriesContainer: {
    paddingRight: 20,
  },
  categoryCard: {
    backgroundColor: theme.surface,
    borderRadius: 12,
    padding: 16,
    marginRight: 12,
    alignItems: 'center',
    minWidth: 80,
  },
  categoryIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  categoryName: {
    fontSize: 12,
    color: theme.text,
    fontWeight: '500',
    textAlign: 'center',
  },

  recommendationsGrid: {
    flexDirection: 'row',
    alignItems: 'stretch',
    gap: 12,
    paddingRight: 20,
  },
  recommendationCard: {
    width: '100%',
    minWidth: 250,
    // marginRight: 12,
  },
  listingsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  listingCard: {
    width: '48%',
    marginBottom: 16,
  },
});
