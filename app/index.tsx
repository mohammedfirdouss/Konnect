// import '../polyfills';
// import 'react-native-get-random-values';
// import { Buffer } from 'buffer';
// global.Buffer = Buffer;

import { useCallback, useEffect } from 'react';
import {
  router,
  useFocusEffect,
  useRootNavigationState,
  useRouter,
} from 'expo-router';
import { Text, View } from 'react-native';

export default function Index() {
  const router = useRouter();

  useFocusEffect(
    useCallback(() => {
      // This runs when the screen is focused and navigation is ready
      router.replace('/(onboarding)/splash');
    }, [router])
  );

  return null;
}
