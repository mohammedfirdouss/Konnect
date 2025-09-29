import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  FlatList,
} from 'react-native';
import { theme } from '@/constants/Colors';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { universities } from '@/constants/MockData';
import { Search, ChevronRight } from 'lucide-react-native';
import { router, useFocusEffect } from 'expo-router';
import { StorageService } from '@/services/StorageService';
import { STORAGE_KEYS } from '@/constants/storageKeys';
import { useQuery } from '@tanstack/react-query';
import { getAllMarketplaces } from '@/api/marketplace';
import { MarketPlaceInterface } from '@/interface/marketplace';

export default function UniversitySelectionScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUniversity, setSelectedUniversity] = useState<
    string | number | null
  >(null);
  const [showCustomInput, setShowCustomInput] = useState<boolean>(false);

  const filteredUniversities = universities.filter((uni) =>
    uni.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleContinue = () => {
    if (selectedUniversity) {
      StorageService.setItem(STORAGE_KEYS.MARKETPLACE, selectedUniversity);
      router.push('/(onboarding)/auth');
    }
  };

  const handleRequestNewCampus = () => {
    // Mock functionality - would normally send a request
    // setShowCustomInput(!showCustomInput);
    // alert("Request submitted! We'll notify you when your campus is available.");

    router.push('/(onboarding)/request-marketplace');

    // router.push('/(onboarding)/auth');
  };

  const { data, isLoading } = useQuery({
    queryKey: ['marketplaces'],
    queryFn: getAllMarketplaces,
  });

  console.log('marketplace data', data);

  const renderUniversity = ({ item }: { item: MarketPlaceInterface }) => (
    <TouchableOpacity
      style={[
        styles.universityCard,
        selectedUniversity === item.id && styles.universityCardSelected,
      ]}
      onPress={() => {
        setShowCustomInput(false);
        setSelectedUniversity(item.id);
      }}
    >
      <View style={styles.universityInfo}>
        <Text style={styles.universityName}>{item.name}</Text>
        <Text style={styles.universityLocation}>{item.description}</Text>
      </View>
      <ChevronRight
        color={selectedUniversity === item.id ? theme.primary : theme.textMuted}
        size={20}
      />
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Select Your University</Text>
        <Text style={styles.subtitle}>
          Choose your campus to connect with your community
        </Text>

        <View style={styles.searchContainer}>
          <Input
            placeholder="Search universities..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            style={styles.searchInput}
          />
        </View>

        {isLoading ? (
          <Text style={{ color: theme.text }}>Loading...</Text>
        ) : (
          <FlatList
            data={data}
            renderItem={renderUniversity}
            keyExtractor={(item) => item?.id?.toString()}
            style={styles.universitiesList}
            showsVerticalScrollIndicator={false}
          />
        )}
        <View style={styles.footer}>
          <TouchableOpacity
            style={styles.requestButton}
            onPress={handleRequestNewCampus}
          >
            <Text style={styles.requestText}>
              Don't see your university? Request it here
            </Text>
          </TouchableOpacity>

          {showCustomInput && (
            <View style={{ marginBottom: 40 }}>
              <Input
                style={styles.searchInput}
                placeholder="Enter your university name"
                placeholderTextColor={theme.textSecondary}
                value={selectedUniversity?.toString()}
                onChangeText={setSelectedUniversity}
                autoFocus
              />

              <Button
                title="Request Marketplace"
                onPress={handleContinue}
                disabled={selectedUniversity == ''}
                style={styles.continueButton}
              />
            </View>
          )}

          {!showCustomInput && (
            <Button
              title="Continue"
              onPress={handleContinue}
              disabled={!selectedUniversity}
              style={styles.continueButton}
            />
          )}
        </View>
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
  content: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: theme.text,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: theme.textMuted,
    textAlign: 'center',
    marginBottom: 30,
  },
  searchContainer: {
    marginBottom: 20,
  },
  searchInput: {
    marginBottom: 0,
  },
  universitiesList: {
    flex: 1,
  },
  universityCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  universityCardSelected: {
    borderColor: theme.primary,
    backgroundColor: theme.surfaceSecondary,
  },
  universityInfo: {
    flex: 1,
  },
  universityName: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.text,
    marginBottom: 4,
  },
  universityLocation: {
    fontSize: 14,
    color: theme.textMuted,
  },
  footer: {
    paddingBottom: 40,
  },
  requestButton: {
    alignItems: 'center',
    paddingVertical: 16,
    marginBottom: 16,
  },
  requestText: {
    fontSize: 14,
    color: theme.primary,
    textDecorationLine: 'underline',
  },
  continueButton: {
    width: '100%',
  },
});
