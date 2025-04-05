'use client';

import { OnchainKitProvider as BaseOnchainKitProvider } from '@coinbase/onchainkit';
import { base } from 'viem/chains';

export default function OnchainKitProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <BaseOnchainKitProvider
      chain={base}
      config={{
        appearance: {
          theme: 'base',
          mode: 'dark',
        },
        wallet: {
          display: 'modal',
          termsUrl: 'https://example.com/terms',
          privacyUrl: 'https://example.com/privacy',
        },
      }}
    >
      {children}
    </BaseOnchainKitProvider>
  );
} 