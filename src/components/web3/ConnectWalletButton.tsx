'use client';

import {
  Wallet,
  ConnectWallet,
  WalletDropdown,
  WalletDropdownDisconnect,
} from '@coinbase/onchainkit/wallet';
import {
  Identity,
  Avatar,
  Name,
  Address,
} from '@coinbase/onchainkit/identity';
import { useWallet } from '@/context/WalletContext';
import { useEffect } from 'react';
import { useAccount } from 'wagmi';

export default function ConnectWalletButton() {
  const { setWalletState } = useWallet();
  const { address, isConnected } = useAccount();

  useEffect(() => {
    if (isConnected && address) {
      setWalletState(address);
    } else {
      setWalletState(undefined);
    }
  }, [isConnected, address, setWalletState]);

  return (
    <Wallet>
      <ConnectWallet>
        <Avatar className="h-6 w-6" />
        <Name />
      </ConnectWallet>
      <WalletDropdown>
        <Identity className="px-4 pt-3 pb-2" hasCopyAddressOnClick>
          <Avatar />
          <Name />
          <Address />
        </Identity>
        <WalletDropdownDisconnect />
      </WalletDropdown>
    </Wallet>
  );
} 