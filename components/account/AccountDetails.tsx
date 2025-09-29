import { useAuthorization } from '@/hooks/useAuthorization';
import { View, StyleSheet } from 'react-native';
import { useTheme } from 'react-native-paper';
import { AccountBalance, AccountButtonGroup, AccountTokens } from './AccountUI';
import { theme } from '@/constants/Colors';



const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: theme.surface,
    borderRadius: 12,
    marginHorizontal: 20,
  },
  balanceSection: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  tokensSection: {
    marginTop: 24,
    backgroundColor: theme.surfaceSecondary,
    borderRadius: 12,
    padding: 16,
  },
});

export function AccountDetailFeature() {
  const { selectedAccount } = useAuthorization();
  const paperTheme = useTheme();

  // if (!selectedAccount) {
  //   return null;
  // }

  return (
    <View style={styles.container}>
      <View style={styles.balanceSection}>
        <AccountBalance address={selectedAccount?.publicKey} />
        <AccountButtonGroup address={selectedAccount?.publicKey} />
      </View>
      {/* <View style={styles.tokensSection}>
        <AccountTokens address={selectedAccount?.publicKey} />
      </View> */}
    </View>
  );

}
