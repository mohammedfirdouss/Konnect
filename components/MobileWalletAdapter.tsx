import { transact } from '@solana-mobile/mobile-wallet-adapter-protocol-web3js';
import { PublicKey, Transaction, VersionedTransaction } from '@solana/web3.js';

 class MobileWalletAdapter {
  publicKey: PublicKey | null;
  constructor() {
    this.publicKey = null;
  }

  async signTransaction(transaction: Transaction | VersionedTransaction) {
    return await transact(async (wallet) => {
      const signedTransactions = await wallet.signTransactions({
        transactions: [transaction],
      });
      return signedTransactions[0];
    });
  }

  async signAllTransactions(transactions: (Transaction | VersionedTransaction)[]) {
    return await transact(async (wallet) => {
      const signedTransactions = await wallet.signTransactions({
        transactions,
      });
      return signedTransactions;
    });
  }

  async signMessage(message: string) {
    return await transact(async (wallet) => {
      const signedMessages = await wallet.signMessages({
        messages: [message],
      });
      return signedMessages[0];
    });
  }
}


export default MobileWalletAdapter;