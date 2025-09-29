import { StyleSheet, View } from 'react-native';
import { Appbar, useTheme } from 'react-native-paper';
import { useNavigation } from '@react-navigation/core';
import { TopBarWalletMenu } from './TopBarUI';
import { router } from 'expo-router';
import { theme } from '@/constants/Colors';


export function TopBar() {

//   const theme = useTheme();

  return (
    <>
      <View style={styles.topBar}>
        <TopBarWalletMenu />

        <Appbar.Action
          icon="cog"
          mode="contained-tonal"
          onPress={() => {
            router.replace('/(tabs)/profile');
          }}
        />
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  topBar: {
    justifyContent: 'flex-end',
    alignItems: 'center',
    backgroundColor: theme.background,
    padding: 16,
    flexDirection: 'row',
  },
});
