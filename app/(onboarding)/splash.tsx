import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '@/constants/Colors';
import { router } from 'expo-router';

export default function SplashScreen() {
  useEffect(() => {
    const timer = setTimeout(() => {
      router.replace('/(onboarding)/welcome');
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <View style={styles.container}>
      <View style={styles.logoContainer}>
        <Text style={styles.logo}>Konnect</Text>
        <Text style={styles.tagline}>Campus Marketplace</Text>
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