import '../polyfills';

import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useFrameworkReady } from '@/hooks/useFrameworkReady';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Toast from 'react-native-toast-message';
// import '@solana/wallet-adapter-react-ui/styles.css';
// import { SolanaProvider } from '@/components/SolanaProvider';
import { ClusterProvider } from '@/components/cluster/cluster-data-access';
import { ConnectionProvider } from '@/components/ConnectionProvider';
import {
  adaptNavigationTheme,
  PaperProvider,
  useTheme,
} from 'react-native-paper';
import { SafeAreaView, useColorScheme } from 'react-native';
import {
  DarkTheme as NavigationDarkTheme,
  DefaultTheme as NavigationDefaultTheme,
} from '@react-navigation/native';
import { MD3DarkTheme, MD3LightTheme } from 'react-native-paper';
import { theme } from '@/constants/Colors';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import '../polyfills';


const queryClient = new QueryClient();

export default function RootLayout() {
  useFrameworkReady();

  //   const CombinedDefaultTheme = {
  //   ...MD3LightTheme,
  //   ...LightTheme,
  //   colors: {
  //     ...MD3LightTheme.colors,
  //     ...LightTheme.colors,
  //   },
  // };
  // const CombinedDarkTheme = {
  //   ...MD3DarkTheme,
  //   ...DarkTheme,
  //   colors: {
  //     ...MD3DarkTheme.colors,
  //     ...DarkTheme.colors,
  //   },

  const colorScheme = useColorScheme();
  const { LightTheme, DarkTheme } = adaptNavigationTheme({
    reactNavigationLight: NavigationDefaultTheme,
    reactNavigationDark: NavigationDarkTheme,
  });

  const CombinedDefaultTheme = {
    ...MD3LightTheme,
    ...LightTheme,
    colors: {
      ...MD3LightTheme.colors,
      ...LightTheme.colors,
    },
  };
  const CombinedDarkTheme = {
    ...MD3DarkTheme,
    ...DarkTheme,
    colors: {
      ...MD3DarkTheme.colors,
      ...DarkTheme.colors,
    },
  };

  const appTheme = useTheme(theme);

  return (
    <>
      <QueryClientProvider client={queryClient}>
        <ClusterProvider>
          <ConnectionProvider config={{ commitment: 'processed' }}>
            {/* <SafeAreaProvider>
              <SafeAreaView
                style={[
                  {
                    backgroundColor: theme.background,
                  },
                ]}
              > */}
            <PaperProvider theme={{}}>
              <Stack screenOptions={{ headerShown: false }}>
                <Stack.Screen name="(onboarding)" />
                <Stack.Screen name="(tabs)" />
                <Stack.Screen name="+not-found" />
              </Stack>
              <Toast position="bottom" />

              <StatusBar style="light" backgroundColor="#111827" />
            </PaperProvider>
            {/* </SafeAreaView>
            </SafeAreaProvider> */}
          </ConnectionProvider>
        </ClusterProvider>
      </QueryClientProvider>
    </>
  );
}
