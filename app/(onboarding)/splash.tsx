import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';
import { theme } from '@/constants/Colors';
import { router } from 'expo-router';
import { StorageService } from '@/services/StorageService';
import { STORAGE_KEYS } from '@/constants/storageKeys';

export default function SplashScreen() {
  const handleRedirect = async () => {
    // setTimeout(() => {
    //   router.replace('/(onboarding)/welcome');
    // }, 500);

    setTimeout(async () => {
      const hasOpened = await StorageService.getItem(STORAGE_KEYS.OPENED);
      if (hasOpened) {
        const role = await StorageService.getItem(STORAGE_KEYS.ROLE);

        if (role) {
          const marketplace = await StorageService.getItem(
            STORAGE_KEYS.MARKETPLACE
          );

          if (marketplace) {
            const token = await StorageService.getItem(
              STORAGE_KEYS.ACCESS_TOKEN
            );
            if (token) {
              router.replace('/(tabs)');
              return;
            }
            router.replace('/(onboarding)/auth');
            return;
          }

          router.replace('/(onboarding)/university-selection');
          return;
        }

        router.replace('/(onboarding)/role-selection');
        return;
      }
      await StorageService.setItem(STORAGE_KEYS.OPENED, 'true');
      router.replace('/(onboarding)/welcome');
    }, 500);
  };
  useEffect(() => {
    handleRedirect();
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