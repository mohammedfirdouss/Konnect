import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  FlatList,
  TouchableOpacity 
} from 'react-native';
import { theme } from '@/constants/Colors';
import { categories, mockProducts } from '@/constants/MockData';
import { ProductCard } from '@/components/ProductCard';
import { Input } from '@/components/ui/Input';
import { router } from 'expo-router';
import { Filter } from 'lucide-react-native';

export default function SearchScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const filteredProducts = mockProducts.filter(product => {
    const matchesSearch = product.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !selectedCategory || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const renderCategory = ({ item }: { item: typeof categories[0] }) => (
    <TouchableOpacity 
      style={[
        styles.filterChip,
        selectedCategory === item.name && styles.filterChipActive
      ]}
      onPress={() => setSelectedCategory(selectedCategory === item.name ? null : item.name)}
    >
      <Text style={styles.filterChipIcon}>{item.icon}</Text>
      <Text style={[
        styles.filterChipText,
        selectedCategory === item.name && styles.filterChipTextActive
      ]}>
        {item.name}
      </Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Search Marketplace</Text>
        <Input
          placeholder="Search products and services..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          style={styles.searchInput}
        />
      </View>

      <View style={styles.filtersContainer}>
        <View style={styles.filtersHeader}>
          <Text style={styles.filtersTitle}>Filters</Text>
          <TouchableOpacity style={styles.filterButton}>
            <Filter color={theme.textMuted} size={16} />
          </TouchableOpacity>
        </View>
        <FlatList
          data={categories}
          renderItem={renderCategory}
          keyExtractor={(item) => item.id}
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filtersScroll}
        />
      </View>

      <View style={styles.resultsContainer}>
        <Text style={styles.resultsCount}>
          {filteredProducts.length} results found
        </Text>
        <FlatList
          data={filteredProducts}
          renderItem={({ item }) => (
            <ProductCard
              product={item}
              onPress={() => router.push(`/product/${item.id}`)}
            />
          )}
          keyExtractor={(item) => item.id}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.productsList}
        />
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
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.text,
    marginBottom: 16,
  },
  searchInput: {
    marginBottom: 0,
  },
  filtersContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  filtersHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  filtersTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
  },
  filterButton: {
    padding: 8,
  },
  filtersScroll: {
    paddingRight: 20,
  },
  filterChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.surface,
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginRight: 8,
    borderWidth: 1,
    borderColor: theme.border,
  },
  filterChipActive: {
    backgroundColor: theme.primary,
    borderColor: theme.primary,
  },
  filterChipIcon: {
    fontSize: 14,
    marginRight: 4,
  },
  filterChipText: {
    fontSize: 12,
    color: theme.text,
    fontWeight: '500',
  },
  filterChipTextActive: {
    color: theme.text,
  },
  resultsContainer: {
    flex: 1,
    paddingHorizontal: 20,
  },
  resultsCount: {
    fontSize: 14,
    color: theme.textMuted,
    marginBottom: 16,
  },
  productsList: {
    paddingBottom: 20,
  },
});