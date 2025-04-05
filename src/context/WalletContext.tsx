'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

interface WalletContextType {
  address: string | undefined;
  isConnected: boolean;
  setWalletState: (address: string | undefined) => void;
}

const WalletContext = createContext<WalletContextType | undefined>(undefined);

export function WalletProvider({ children }: { children: ReactNode }) {
  const [address, setAddress] = useState<string | undefined>();

  const setWalletState = (newAddress: string | undefined) => {
    setAddress(newAddress);
  };

  return (
    <WalletContext.Provider 
      value={{
        address,
        isConnected: !!address,
        setWalletState,
      }}
    >
      {children}
    </WalletContext.Provider>
  );
}

export function useWallet() {
  const context = useContext(WalletContext);
  if (context === undefined) {
    throw new Error('useWallet must be used within a WalletProvider');
  }
  return context;
} 