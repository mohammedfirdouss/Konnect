import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  FlatList,
  Image,
  TouchableOpacity 
} from 'react-native';
import { theme } from '@/constants/Colors';
import { mockListings, Listing } from '@/constants/MockData';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Eye, CreditCard as Edit, Pause, Play, Trash2 } from 'lucide-react-native';
import { router } from 'expo-router';

export default function ListingsScreen() {
  const [listings, setListings] = useState(mockListings);

  const toggleListingStatus = (id: string) => {
    setListings(prev => prev.map(listing => 
      listing.id === id 
        ? { ...listing, status: listing.status === 'active' ? 'paused' : 'active' }
        : listing
    ));
  };

  const deleteListing = (id: string) => {
    setListings(prev => prev.filter(listing => listing.id !== id));
  };

  const getStatusColor = (status: Listing['status']) => {
    switch (status) {
      case 'active': return theme.accent;
      case 'paused': return theme.warning;
      case 'sold': return theme.textMuted;
      default: return theme.textMuted;
    }
  };

  const renderListing = ({ item }: { item: Listing }) => (
    <Card style={styles.listingCard}>
      <View style={styles.listingHeader}>
        <Image source={{ uri: item.images[0] }} style={styles.productImage} />
        <View style={styles.listingInfo}>
          <Text style={styles.listingTitle}>{item.title}</Text>
          <Text style={styles.listingCategory}>{item.category}</Text>
          <Text style={styles.listingPrice}>${item.price}</Text>
        </View>
        <View style={styles.listingMeta}>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
            <Text style={styles.statusText}>{item.status}</Text>
          </View>
          <View style={styles.viewsContainer}>
            <Eye color={theme.textMuted} size={12} />
            <Text style={styles.viewsText}>{item.views}</Text>
          </View>
        </View>
      </View>

      <View style={styles.listingActions}>
        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => router.push(`/edit-listing/${item.id}`)}
        >
          <Edit color={theme.primary} size={16} />
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => toggleListingStatus(item.id)}
        >
          {item.status === 'active' ? (
            <Pause color={theme.warning} size={16} />
          ) : (
            <Play color={theme.accent} size={16} />
          )}
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => deleteListing(item.id)}
        >
          <Trash2 color={theme.danger} size={16} />
        </TouchableOpacity>
      </View>
    </Card>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>My Listings</Text>
        <Button
          title="Add New"
          onPress={() => router.push('/add-listing')}
          size="small"
        />
      </View>

      {listings.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No listings yet</Text>
          <Text style={styles.emptySubtext}>Create your first listing to start selling</Text>
          <Button 
            title="Add Listing" 
            onPress={() => router.push('/add-listing')}
            style={styles.addButton}
          />
        </View>
      ) : (
        <FlatList
          data={listings}
          renderItem={renderListing}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listingsList}
          showsVerticalScrollIndicator={false}
        />
      )}
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.text,
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
  addButton: {
    minWidth: 200,
  },
  listingsList: {
    padding: 20,
    paddingTop: 10,
  },
  listingCard: {
    marginBottom: 16,
  },
  listingHeader: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  productImage: {
    width: 60,
    height: 60,
    borderRadius: 8,
    marginRight: 12,
  },
  listingInfo: {
    flex: 1,
  },
  listingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
    marginBottom: 4,
  },
  listingCategory: {
    fontSize: 12,
    color: theme.textMuted,
    marginBottom: 4,
  },
  listingPrice: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.accent,
  },
  listingMeta: {
    alignItems: 'flex-end',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginBottom: 8,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
    color: theme.text,
    textTransform: 'capitalize',
  },
  viewsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  viewsText: {
    fontSize: 12,
    color: theme.textMuted,
    marginLeft: 4,
  },
  listingActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 12,
    borderTopWidth: 1,
    borderTopColor: theme.border,
    paddingTop: 12,
  },
  actionButton: {
    padding: 8,
    borderRadius: 8,
    backgroundColor: theme.background,
  },
});