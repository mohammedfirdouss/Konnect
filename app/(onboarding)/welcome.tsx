import React, { useState, useRef } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  Dimensions,
  SafeAreaView 
} from 'react-native';
import { theme } from '@/constants/Colors';
import { Button } from '@/components/ui/Button';
import { router } from 'expo-router';

const { width } = Dimensions.get('window');

const onboardingData = [
  {
    id: '1',
    title: 'Discover Everything',
    subtitle: 'Find everything you need on campus in one place',
    emoji: '🔍',
  },
  {
    id: '2',
    title: 'Safe Payments',
    subtitle: 'Buy goods and services safely with escrow payments',
    emoji: '🔒',
  },
  {
    id: '3',
    title: 'Grow Your Hustle',
    subtitle: 'Sell to your entire campus and grow your business',
    emoji: '🚀',
  },
];

export default function WelcomeScreen() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const renderSlide = ({ item }: { item: typeof onboardingData[0] }) => (
    <View style={styles.slide}>
      <Text style={styles.emoji}>{item.emoji}</Text>
      <Text style={styles.title}>{item.title}</Text>
      <Text style={styles.subtitle}>{item.subtitle}</Text>
    </View>
  );

  const handleNext = () => {
    if (currentIndex < onboardingData.length - 1) {
      const nextIndex = currentIndex + 1;
      flatListRef.current?.scrollToIndex({ index: nextIndex });
      setCurrentIndex(nextIndex);
    } else {
      router.push('/(onboarding)/role-selection');
    }
  };

  const handleSkip = () => {
    router.push('/(onboarding)/role-selection');
  };

  return (
    <SafeAreaView style={styles.container}>
      <FlatList
        ref={flatListRef}
        data={onboardingData}
        renderItem={renderSlide}
        keyExtractor={(item) => item.id}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={(event) => {
          const index = Math.round(event.nativeEvent.contentOffset.x / width);
          setCurrentIndex(index);
        }}
      />

      <View style={styles.footer}>
        <View style={styles.pagination}>
          {onboardingData.map((_, index) => (
            <View
              key={index}
              style={[
                styles.paginationDot,
                index === currentIndex && styles.paginationDotActive,
              ]}
            />
          ))}
        </View>

        <View style={styles.buttons}>
          <Button 
            title="Skip" 
            variant="outline" 
            onPress={handleSkip}
            style={styles.skipButton}
          />
          <Button 
            title={currentIndex === onboardingData.length - 1 ? "Get Started" : "Next"} 
            onPress={handleNext}
            style={styles.nextButton}
          />
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.background,
  },
  slide: {
    width,
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emoji: {
    fontSize: 120,
    marginBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.text,
    textAlign: 'center',
    marginBottom: 16,
  },
  subtitle: {
    fontSize: 18,
    color: theme.textMuted,
    textAlign: 'center',
    lineHeight: 26,
  },
  footer: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  pagination: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 32,
  },
  paginationDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: theme.surfaceSecondary,
    marginHorizontal: 4,
  },
  paginationDotActive: {
    backgroundColor: theme.primary,
    width: 24,
  },
  buttons: {
    flexDirection: 'row',
    gap: 16,
  },
  skipButton: {
    flex: 1,
  },
  nextButton: {
    flex: 2,
  },
});