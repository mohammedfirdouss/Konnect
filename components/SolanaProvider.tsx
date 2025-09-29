import React, { createContext, useContext, useState } from 'react';
import { transact } from '@solana-mobile/mobile-wallet-adapter-protocol';
import { Connection, clusterApiUrl, PublicKey } from '@solana/web3.js';
import MobileWalletAdapter from './MobileWalletAdapter';
import * as anchor from '@coral-xyz/anchor';
import { AuthToken } from '@solana-mobile/mobile-wallet-adapter-protocol';
import idl from '../idl.json';

interface SolanaContextType {
  publicKey: PublicKey | null;
  isConnected: boolean;
  connectWallet: () => Promise<void>;
  disconnectWallet: () => Promise<void>;
  connection: Connection;
  program: anchor.Program | null;
  walletAdapter: MobileWalletAdapter | null;
}

const SolanaContext = createContext<SolanaContextType | null>(null);

export const SolanaProvider = ({ children }: { children: React.ReactNode }) => {
  const [publicKey, setPublicKey] = useState<PublicKey | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [authToken, setAuthToken] = useState<AuthToken | null>(null);
  const connection = new Connection(clusterApiUrl('devnet'));



  const [program, setProgram] = useState<anchor.Program | null>(null);
  const [walletAdapter, setWalletAdapter] = useState<MobileWalletAdapter | null>(null);
  const PROGRAM_ID = new PublicKey(
    'B5nTWLtcbWiMpG26vTMBdVMZw3DL2ewsXZid1SDGBZNa'
  );

  const connectWallet = async () => {
    try {
      const result = await transact(async (wallet) => {
        const authorization = await wallet.authorize({
          cluster: 'devnet',
          identity: {
            name: 'Konnect',
            uri: 'https://konnect.xyz',
            icon: '../assets/images/favicon.png',
          },
        });
        return authorization;
      });

      if (result.accounts && result.accounts.length > 0) {
        const userPublicKey = new PublicKey(result.accounts[0].address);
        setPublicKey(userPublicKey);
        setIsConnected(true);

        // Create mobile wallet adapter
        const mobileWallet = new MobileWalletAdapter();
        mobileWallet.publicKey = userPublicKey;
        setWalletAdapter(mobileWallet);

        // Create Anchor provider with mobile wallet
        const provider = new anchor.AnchorProvider(connection, mobileWallet, {
          preflightCommitment: 'processed',
        });

        // Create program instance
        const anchorProgram = new anchor.Program(idl as anchor.Idl, PROGRAM_ID, provider);
        setProgram(anchorProgram);
        setAuthToken(result.auth_token);
      }
    } catch (error) {
      console.error('Wallet connection failed:', error);
    }
  };

  const disconnectWallet = async () => {
    try {
      await transact(async (wallet) => {
        await wallet.deauthorize({ auth_token: authToken! });
      });
    } catch (error) {
      console.error('Disconnect failed:', error);
    } finally {
      setPublicKey(null);
      setIsConnected(false);
      setProgram(null);
      setWalletAdapter(null);
      setAuthToken(null);
    }
  };



  return (
    <SolanaContext.Provider
      value={{
        publicKey,
        isConnected,
        connectWallet,
        disconnectWallet,
        connection,
        program,
        walletAdapter,
      }}
    >
      {children}
    </SolanaContext.Provider>
  );
};

export const useSolana = () => {
  const context = useContext(SolanaContext);
  if (!context) {
    throw new Error('useSolana must be used within SolanaProvider');
  }
  return context;
};
