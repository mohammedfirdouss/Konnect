// hooks/useAnchorProvider.ts
import { useMemo } from "react";
import { AnchorProvider, Wallet } from "@coral-xyz/anchor";
import { Transaction, VersionedTransaction } from "@solana/web3.js";
import { useMobileWallet } from "./useMobileWallet";
import { useAuthorization } from "./useAuthorization";
import { useConnection } from "../components/ConnectionProvider";

export function useAnchorProvider() {
  const { connection } = useConnection(); // 👈 use connection from provider
  const { selectedAccount } = useAuthorization();
  const wallet = useMobileWallet();

  const provider = useMemo(() => {
    if (!wallet || !selectedAccount?.publicKey) return null;

    const anchorWallet = {
      publicKey: selectedAccount.publicKey,
      signTransaction: async <T extends Transaction | VersionedTransaction>(tx: T): Promise<T> => {
        await wallet.signAndSendTransaction(tx, 0);
        return tx;
      },
      signAllTransactions: async <T extends Transaction | VersionedTransaction>(txs: T[]): Promise<T[]> => {
        for (const tx of txs) {
          await wallet.signAndSendTransaction(tx, 0);
        }
        return txs;
      },
    } as Wallet;

    return new AnchorProvider(connection, anchorWallet, {
      commitment: "confirmed",
    });
  }, [wallet, selectedAccount, connection]);

  return provider;
}
