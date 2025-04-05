"use client";

import { useWallet } from "@/context/WalletContext";
import { Button } from "@/components/ui/button";
import MockApyChart from "@/components/investor/MockApyChart";
import PageBackground from '@/components/layout/PageBackground';

// Mock data for vault statistics
const vaultStats = {
  totalAmount: 1250000,
  lendedAmount: 750000,
  tradingAmount: 425000,
  apy: {
    past: {
      week: 9.8,
      month: 10.2,
      year: 11.5
    },
    estimated: {
      week: 10.5,
      month: 11.0,
      year: 11.8
    }
  }
};

export default function EarnPage() {
  const { isConnected } = useWallet();

  const handleDeposit = () => {
    console.log("Mock Deposit Triggered - Will integrate with USDC contract later");
  };

  const handleWithdraw = () => {
    console.log("Mock Withdraw Triggered - Will integrate with smart contract later");
  };

  // Helper function to format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  // Helper function to format percentage
  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  if (!isConnected) {
    return (
      <PageBackground>
        <div className="min-h-screen py-8">
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-3xl font-bold text-foreground mb-4">Please Connect Your Wallet</h1>
            <p className="text-muted-foreground">Connect your wallet to access the investor dashboard.</p>
          </div>
        </div>
      </PageBackground>
    );
  }

  const idleAmount = vaultStats.totalAmount - vaultStats.lendedAmount - vaultStats.tradingAmount;

  return (
    <PageBackground>
      <div className="min-h-screen py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            {/* Header Section */}
            <div className="mb-8 text-center">
              <h1 className="text-4xl font-bold text-foreground mb-2">Earn</h1>
              <p className="text-xl text-muted-foreground">
                Earn passively while helping your local business stay afloat
              </p>
            </div>

            {/* Vault Overview Section */}
            <div className="bg-card/30 backdrop-blur-md p-6 rounded-lg shadow-md mb-8 border border-white/10">
              <h2 className="text-xl font-semibold mb-6 text-foreground">Vault Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-card/20 backdrop-blur-sm p-4 rounded-lg border border-white/5">
                  <p className="text-sm text-muted-foreground mb-1">Total Vault Value</p>
                  <p className="text-2xl font-bold text-[#C3550B]">{formatCurrency(vaultStats.totalAmount)}</p>
                </div>
                <div className="bg-card/20 backdrop-blur-sm p-4 rounded-lg border border-white/5">
                  <p className="text-sm text-muted-foreground mb-1">Currently Lent</p>
                  <p className="text-2xl font-bold text-foreground">{formatCurrency(vaultStats.lendedAmount)}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatPercentage((vaultStats.lendedAmount / vaultStats.totalAmount) * 100)} of total
                  </p>
                </div>
                <div className="bg-card/20 backdrop-blur-sm p-4 rounded-lg border border-white/5">
                  <p className="text-sm text-muted-foreground mb-1">In Trading</p>
                  <p className="text-2xl font-bold text-foreground">{formatCurrency(vaultStats.tradingAmount)}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatPercentage((vaultStats.tradingAmount / vaultStats.totalAmount) * 100)} of total
                  </p>
                </div>
              </div>
            </div>

            {/* Fund Allocation Chart */}
            <div className="bg-card/30 backdrop-blur-md p-6 rounded-lg shadow-md mb-8 border border-white/10">
              <h2 className="text-xl font-semibold mb-4 text-foreground">Fund Allocation</h2>
              <div className="h-4 w-full rounded-full bg-card/20 overflow-hidden">
                <div className="h-full flex">
                  <div 
                    className="bg-[#C3550B]" 
                    style={{ width: `${(vaultStats.lendedAmount / vaultStats.totalAmount) * 100}%` }}
                    title="Lent Out"
                  />
                  <div 
                    className="bg-[#E67E22]" 
                    style={{ width: `${(vaultStats.tradingAmount / vaultStats.totalAmount) * 100}%` }}
                    title="In Trading"
                  />
                  <div 
                    className="bg-muted" 
                    style={{ width: `${(idleAmount / vaultStats.totalAmount) * 100}%` }}
                    title="Idle"
                  />
                </div>
              </div>
              <div className="flex justify-between mt-2 text-sm text-muted-foreground">
                <span>Lent Out ({formatPercentage((vaultStats.lendedAmount / vaultStats.totalAmount) * 100)})</span>
                <span>In Trading ({formatPercentage((vaultStats.tradingAmount / vaultStats.totalAmount) * 100)})</span>
                <span>Idle ({formatPercentage((idleAmount / vaultStats.totalAmount) * 100)})</span>
              </div>
            </div>

            {/* APY Chart */}
            <div className="mb-8">
              <MockApyChart />
            </div>

            {/* Performance Metrics */}
            <div className="bg-card/30 backdrop-blur-md p-6 rounded-lg shadow-md mb-8 border border-white/10">
              <h2 className="text-xl font-semibold mb-6 text-foreground">Performance Metrics</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Historical Performance */}
                <div>
                  <h3 className="text-lg font-medium mb-4 text-foreground">Historical APY</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Past Week</span>
                      <span className="font-semibold text-[#C3550B]">{formatPercentage(vaultStats.apy.past.week)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Past Month</span>
                      <span className="font-semibold text-[#C3550B]">{formatPercentage(vaultStats.apy.past.month)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Past Year</span>
                      <span className="font-semibold text-[#C3550B]">{formatPercentage(vaultStats.apy.past.year)}</span>
                    </div>
                  </div>
                </div>
                {/* Estimated Performance */}
                <div>
                  <h3 className="text-lg font-medium mb-4 text-foreground">Estimated APY</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Current Week</span>
                      <span className="font-semibold text-[#C3550B]">{formatPercentage(vaultStats.apy.estimated.week)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Current Month</span>
                      <span className="font-semibold text-[#C3550B]">{formatPercentage(vaultStats.apy.estimated.month)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground">Current Year</span>
                      <span className="font-semibold text-[#C3550B]">{formatPercentage(vaultStats.apy.estimated.year)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Strategy Section */}
              <div className="bg-card/30 backdrop-blur-md p-6 rounded-lg shadow-md border border-white/10">
                <h2 className="text-xl font-semibold mb-4 text-foreground">AI Strategy</h2>
                <div className="space-y-4">
                  <div className="bg-card/20 backdrop-blur-sm p-4 rounded-md border border-white/5">
                    <p className="text-lg font-medium text-[#C3550B]">
                      Current Strategy Focus:
                    </p>
                    <p className="text-foreground mt-2">
                      AI-Optimized Stable Yield
                    </p>
                  </div>
                  <div className="bg-card/20 backdrop-blur-sm p-4 rounded-md border border-white/5">
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
              <div className="bg-card/30 backdrop-blur-md p-6 rounded-lg shadow-md border border-white/10">
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
                    Our AI automatically allocates funds to verified invoices and manages trading strategies.
                  </p>
                </div>
                <div className="space-y-2">
                  <h3 className="font-medium text-foreground">3. Earn Returns</h3>
                  <p className="text-sm text-muted-foreground">
                    Earn returns from both invoice factoring and AI-driven trading.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageBackground>
  );
} 