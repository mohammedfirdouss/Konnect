import { Stack } from 'expo-router';

export default function OnboardingLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="splash" />
      <Stack.Screen name="welcome" />
      <Stack.Screen name="role-selection" />
      <Stack.Screen name="university-selection" />
      <Stack.Screen name="auth" />
    </Stack>
  );
}