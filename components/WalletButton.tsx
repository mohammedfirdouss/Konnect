import { Account, useAuthorization } from '../hooks/useAuthorization';
import { useMobileWallet } from '../hooks/useMobileWallet';
import { ellipsify } from '@/lib/helpers';
import { Button } from "./ui/Button";



 const  WalletButton =({
  selectedAccount,
  openMenu,
}: {
  selectedAccount: Account | null;  
  openMenu: () => void;
}) =>{
  const { connect } = useMobileWallet();
  return (
    <Button
    //   icon="wallet"
    //   mode="contained-tonal"
    //   style={{ alignSelf: 'center' }}
      onPress={() => selectedAccount ? openMenu() : connect()}
    >
      {selectedAccount
        ? ellipsify(selectedAccount.publicKey.toBase58())
        : 'Connect'}
    </Button>
  );
}

export default WalletButton
