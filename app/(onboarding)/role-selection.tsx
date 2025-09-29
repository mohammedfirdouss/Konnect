import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity } from 'react-native';
import { theme } from '@/constants/Colors';
import { Button } from '@/components/ui/Button';
import { ShoppingBag, Store } from 'lucide-react-native';
import { router } from 'expo-router';
import { StorageService } from '@/services/StorageService';
import { STORAGE_KEYS } from '@/constants/storageKeys';

export default function RoleSelectionScreen() {
  const [selectedRole, setSelectedRole] = useState<'buyer' | 'seller' | null>(
    null
  );

  const handleContinue = async () => {
    console.log('selectedRole', selectedRole);
    if (selectedRole) {
      await StorageService.setItem(STORAGE_KEYS.ROLE, selectedRole);
      router.push('/(onboarding)/university-selection');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>How do you want to use Konnect?</Text>
        <Text style={styles.subtitle}>You can always change this later</Text>

        <View style={styles.options}>
          <TouchableOpacity
            style={[
              styles.optionCard,
              selectedRole === 'buyer' && styles.optionCardSelected,
            ]}
            onPress={() => setSelectedRole('buyer')}
          >
            <ShoppingBag
              color={
                // selectedRole === 'buyer' ? theme.primary : theme.textMuted
                theme.textMuted
              }
              size={48}
            />
            <Text
              style={[
                styles.optionTitle,
                // selectedRole === 'buyer' && styles.optionTitleSelected,
              ]}
            >
              I want to buy
            </Text>
            <Text style={styles.optionDescription}>
              Browse and purchase goods and services from fellow students
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.optionCard,
              selectedRole === 'seller' && styles.optionCardSelected,
            ]}
            onPress={() => setSelectedRole('seller')}
          >
            <Store
              color={
                theme.textMuted
                // selectedRole === 'seller' ? theme.primary : theme.textMuted
              }
              size={48}
            />
            <Text
              style={[
                styles.optionTitle,
                // selectedRole === 'seller' && styles.optionTitleSelected,
              ]}
            >
              I want to sell
            </Text>
            <Text style={styles.optionDescription}>
              Start selling your products and services to your campus
            </Text>
          </TouchableOpacity>
        </View>

        <Button
          title="Continue"
          onPress={handleContinue}
          disabled={!selectedRole}
          style={styles.continueButton}
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
    marginBottom: 40,
  },
  options: {
    flex: 1,
    gap: 20,
  },
  optionCard: {
    backgroundColor: theme.surface,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  optionCardSelected: {
    borderColor: theme.primary,
    backgroundColor: theme.surfaceSecondary,
  },
  optionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.text,
    marginTop: 16,
    marginBottom: 8,
  },
  optionTitleSelected: {
    color: theme.primary,
  },
  optionDescription: {
    fontSize: 14,
    color: theme.textMuted,
    textAlign: 'center',
    lineHeight: 20,
  },
  continueButton: {
    marginBottom: 40,
  },
});