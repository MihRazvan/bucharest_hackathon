'use client';

import { useWallet } from "@/context/WalletContext";

export default function Register() {
  const { isConnected } = useWallet();

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Register</h1>
        {isConnected ? (
          <p className="text-xl text-neutral-600">Create your account to get started</p>
        ) : (
          <div className="space-y-4">
            <p className="text-xl text-neutral-600">Please connect your wallet to register</p>
            <p className="text-sm text-neutral-500">
              Click the &quot;Connect Wallet&quot; button in the top right corner
            </p>
          </div>
        )}
      </div>
    </div>
  );
} 