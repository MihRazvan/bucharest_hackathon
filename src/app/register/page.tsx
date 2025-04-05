'use client';

import { useWallet } from "@/context/WalletContext";

export default function Register() {
  const { isConnected } = useWallet();

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 text-foreground">Register</h1>
        {isConnected ? (
          <p className="text-xl text-muted-foreground">Create your account to get started</p>
        ) : (
          <div className="space-y-4">
            <p className="text-xl text-muted-foreground">Please connect your wallet to register</p>
            <p className="text-sm text-muted-foreground">
              Click the &quot;Connect Wallet&quot; button in the top right corner
            </p>
          </div>
        )}
      </div>
    </div>
  );
} 