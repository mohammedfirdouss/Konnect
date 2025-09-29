import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';
import { theme } from '@/constants/Colors';
import { router } from 'expo-router';
import { StorageService } from '@/services/StorageService';
import { STORAGE_KEYS } from '@/constants/storageKeys';

export default function SplashScreen() {
  useEffect(() => {
    StorageService.getItem(STORAGE_KEYS.MARKETPLACE);

    const timer = setTimeout(() => {

      StorageService.getItem(STORAGE_KEYS.MARKETPLACE);

      router.replace('/(onboarding)/welcome');
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <View style={styles.container}>
      <View style={styles.logoContainer}>
        <Image
          source={require('../../assets/images/logo.png')}
          style={{ width: 200, height: 150 }}
        />
        {/* <Text style={styles.logo}>Konnect</Text>
        <Text style={styles.tagline}>Campus Marketplace</Text> */}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.background,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoContainer: {
    alignItems: 'center',
  },
  logo: {
    fontSize: 48,
    fontWeight: 'bold',
    color: theme.primary,
    marginBottom: 8,
  },
  tagline: {
    fontSize: 16,
    color: theme.textMuted,
    fontWeight: '500',
  },
});