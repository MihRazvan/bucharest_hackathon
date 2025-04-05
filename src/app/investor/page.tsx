"use client";

import { useWallet } from "@/context/WalletContext";
import { Button } from "@/components/ui/button";

export default function InvestorPage() {
  const { isConnected, address } = useWallet();

  const handleDeposit = () => {
    console.log("Mock Deposit Triggered - Will integrate with USDC contract later");
  };

  const handleWithdraw = () => {
    console.log("Mock Withdraw Triggered - Will integrate with smart contract later");
  };

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-background py-8">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-3xl font-bold text-foreground mb-4">Please Connect Your Wallet</h1>
          <p className="text-muted-foreground">Connect your wallet to access the investor dashboard.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* Header Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">Investor Dashboard</h1>
            <p className="text-muted-foreground">
              Connected Wallet: {address?.slice(0, 6)}...{address?.slice(-4)}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Strategy Section */}
            <div className="bg-card p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4 text-foreground">AI Strategy</h2>
              <div className="space-y-4">
                <div className="p-4 bg-card/50 rounded-md">
                  <p className="text-lg font-medium text-[#C3550B]">
                    Current Strategy Focus:
                  </p>
                  <p className="text-foreground mt-2">
                    AI-Optimized Stable Yield
                  </p>
                </div>
                <div className="bg-card/50 p-4 rounded-md">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Target APY</p>
                      <p className="text-lg font-semibold text-foreground">8-12%</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Risk Level</p>
                      <p className="text-lg font-semibold text-foreground">Low-Medium</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Actions Section */}
            <div className="bg-card p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4 text-foreground">Actions</h2>
              <div className="space-y-6">
                {/* Deposit Section */}
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">Deposit Funds</h3>
                  <Button
                    onClick={handleDeposit}
                    className="w-full bg-[#C3550B] hover:bg-[#A34709] text-white"
                  >
                    Deposit test USDC
                  </Button>
                </div>

                {/* Withdraw Section */}
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground mb-2">Withdraw Funds</h3>
                  <Button
                    onClick={handleWithdraw}
                    variant="outline"
                    className="w-full border-[#C3550B] text-[#C3550B] hover:bg-[#C3550B] hover:text-white"
                  >
                    Withdraw Funds
                  </Button>
                </div>

                {/* Mock Portfolio Stats */}
                <div className="pt-4 border-t border-border">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Your Balance</p>
                      <p className="text-lg font-semibold text-foreground">0.00 USDC</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Total Earned</p>
                      <p className="text-lg font-semibold text-[#C3550B]">+0.00 USDC</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Additional Info Section */}
          <div className="mt-8 bg-card p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-foreground">How It Works</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <h3 className="font-medium text-foreground">1. Deposit USDC</h3>
                <p className="text-sm text-muted-foreground">
                  Start by depositing USDC into the platform&apos;s smart contract.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium text-foreground">2. AI Allocation</h3>
                <p className="text-sm text-muted-foreground">
                  Our AI automatically allocates funds to verified invoices.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium text-foreground">3. Earn Returns</h3>
                <p className="text-sm text-muted-foreground">
                  Earn stable returns from invoice factoring payments.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 