'use client';

import * as React from 'react';
import { useState } from 'react';
import { useWallet } from '@/context/WalletContext';
import { Button } from '@/components/ui/button';
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogTrigger,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Filter } from "lucide-react";
import { CompanyRegistrationForm } from '@/components/forms/CompanyRegistrationForm';
import { CreateInvoiceForm } from "@/components/company/CreateInvoiceForm";
import { Slider } from "@/components/ui/slider";
import { useAccount } from "wagmi";
import PageBackground from '@/components/layout/PageBackground';

interface MockCompany {
  name: string;
  walletAddress: string;
}

interface MockInvoice {
  id: string;
  amount: number;
  dueDate: string;
  status: 'Pending' | 'Approved' | 'Denied';
  // Additional fields for approved invoices
  advanceRate?: number;
  advanceAmount?: number;
  feePercentage?: number;
  feeAmount?: number;
  totalToRepay?: number;
  termDays: number;
  repaidAmount?: number;
  paymentStatus?: 'Open' | 'Closed';
}

export default function CompanyPage() {
  const { isConnected, address } = useWallet();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [company, setCompany] = useState<MockCompany | null>(() => {
    if (typeof window !== 'undefined') {
      const savedCompany = sessionStorage.getItem('companyData');
      return savedCompany ? JSON.parse(savedCompany) : null;
    }
    return null;
  });
  const [mockInvoices, setMockInvoices] = useState<MockInvoice[]>(() => {
    if (typeof window !== 'undefined') {
      const savedInvoices = sessionStorage.getItem('invoicesData');
      return savedInvoices ? JSON.parse(savedInvoices) : [];
    }
    return [];
  });
  const [selectedInvoice, setSelectedInvoice] = useState<MockInvoice | null>(null);
  const [selectedAdvanceAmount, setSelectedAdvanceAmount] = useState<number>(0);
  const [inputValue, setInputValue] = useState<string>("");
  const [repaymentAmount, setRepaymentAmount] = useState<string>("");
  const [repayingInvoiceId, setRepayingInvoiceId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<'All' | 'Approved' | 'Denied'>('All');
  const [paymentStatusFilter, setPaymentStatusFilter] = useState<'All' | 'Open' | 'Closed'>('All');

  // Save company data when it changes
  React.useEffect(() => {
    if (company) {
      sessionStorage.setItem('companyData', JSON.stringify(company));
    }
  }, [company]);

  // Save invoices data when it changes
  React.useEffect(() => {
    sessionStorage.setItem('invoicesData', JSON.stringify(mockInvoices));
  }, [mockInvoices]);

  const handleInvoiceSubmit = (newInvoice: MockInvoice) => {
    // Calculate the number of days between today and the due date
    const today = new Date();
    const dueDate = new Date(newInvoice.dueDate);
    const diffTime = dueDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    const invoice = {
      ...newInvoice,
      status: 'Pending' as const,
      termDays: diffDays
    };
    setMockInvoices(prevInvoices => [invoice, ...prevInvoices]);
    setSelectedInvoice(invoice);
    // Set initial advance amount to maximum (70% of invoice amount)
    setSelectedAdvanceAmount(invoice.amount * 0.7);
  };

  const handleAcceptQuote = () => {
    if (!selectedInvoice) return;
    
    const advanceRate = Number(((selectedAdvanceAmount / selectedInvoice.amount) * 100).toFixed(2));
    const feePercentage = 0.03;
    const feeAmount = Number((selectedInvoice.amount * feePercentage).toFixed(2));
    const totalToRepay = Number((selectedAdvanceAmount + feeAmount).toFixed(2));

    setMockInvoices(prevInvoices => 
      prevInvoices.map(invoice => 
        invoice.id === selectedInvoice.id 
          ? {
              ...invoice,
              status: 'Approved',
              advanceRate: advanceRate,
              advanceAmount: Number(selectedAdvanceAmount.toFixed(2)),
              feePercentage: Number((feePercentage * 100).toFixed(2)),
              feeAmount,
              totalToRepay,
              termDays: invoice.termDays,
              repaidAmount: 0,
              paymentStatus: 'Open'
            }
          : invoice
      )
    );
    setSelectedInvoice(null);
    setSelectedAdvanceAmount(0);
  };

  const handleDenyQuote = () => {
    if (!selectedInvoice) return;
    
    setMockInvoices(prevInvoices => 
      prevInvoices.map(invoice => 
        invoice.id === selectedInvoice.id 
          ? { ...invoice, status: 'Denied' }
          : invoice
      )
    );
    setSelectedInvoice(null);
  };

  const handleAdvanceAmountChange = (value: number) => {
    setSelectedAdvanceAmount(value);
  };

  const handleAdvanceAmountInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleInputBlur = () => {
    const value = parseFloat(inputValue);
    if (!isNaN(value) && selectedInvoice) {
      const maxAdvance = selectedInvoice.amount * 0.7;
      const clampedValue = Math.min(Math.max(value, 1), maxAdvance);
      setSelectedAdvanceAmount(clampedValue);
      setInputValue(clampedValue.toFixed(2));
    } else {
      setInputValue(selectedAdvanceAmount.toFixed(2));
    }
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    }
  };

  // Update inputValue when selectedAdvanceAmount changes (for slider updates)
  React.useEffect(() => {
    setInputValue(selectedAdvanceAmount.toFixed(2));
  }, [selectedAdvanceAmount]);

  // Sort invoices based on status and due date
  const sortedInvoices = React.useMemo(() => {
    return [...mockInvoices].sort((a, b) => {
      // First, separate by main status groups
      if (a.status !== b.status) {
        // Approved invoices come first
        if (a.status === 'Approved' && b.status !== 'Approved') return -1;
        if (b.status === 'Approved' && a.status !== 'Approved') return 1;
        // Pending invoices come second
        if (a.status === 'Pending' && b.status !== 'Pending') return -1;
        if (b.status === 'Pending' && a.status !== 'Pending') return 1;
        // Denied invoices go last
        return 0;
      }

      // For Approved invoices, sort by payment status and due date
      if (a.status === 'Approved' && b.status === 'Approved') {
        // Open invoices come before Closed ones
        if (a.paymentStatus !== b.paymentStatus) {
          return a.paymentStatus === 'Open' ? -1 : 1;
        }
        // For Open invoices, sort by due date (earliest first)
        if (a.paymentStatus === 'Open') {
          return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
        }
      }

      // For other statuses or same payment status, sort by due date
      return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
    });
  }, [mockInvoices]);

  // Filter invoices based on selected filters
  const filteredInvoices = React.useMemo(() => {
    return sortedInvoices.filter(invoice => {
      // Apply status filter
      if (statusFilter !== 'All' && invoice.status !== statusFilter) {
        return false;
      }
      
      // Apply payment status filter only for Approved invoices
      if (statusFilter === 'Approved' && paymentStatusFilter !== 'All') {
        return invoice.paymentStatus === paymentStatusFilter;
      }

      return true;
    });
  }, [sortedInvoices, statusFilter, paymentStatusFilter]);

  const handleStartRepayment = (invoiceId: string) => {
    setRepayingInvoiceId(invoiceId);
    setRepaymentAmount("");
  };

  const handleCancelRepayment = () => {
    setRepayingInvoiceId(null);
    setRepaymentAmount("");
  };

  const handleRepaymentAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRepaymentAmount(e.target.value);
  };

  const handleRepayment = (invoice: MockInvoice) => {
    const amount = parseFloat(repaymentAmount);
    if (isNaN(amount) || amount <= 0) return;

    const remainingToRepay = (invoice.totalToRepay || 0) - (invoice.repaidAmount || 0);
    const validAmount = Math.min(amount, remainingToRepay);
    const newRepaidAmount = (invoice.repaidAmount || 0) + validAmount;
    const isFullyRepaid = newRepaidAmount >= (invoice.totalToRepay || 0);

    setMockInvoices(prevInvoices =>
      prevInvoices.map(inv =>
        inv.id === invoice.id
          ? {
              ...inv,
              repaidAmount: Number(newRepaidAmount.toFixed(2)),
              paymentStatus: isFullyRepaid ? 'Closed' : 'Open'
            }
          : inv
      )
    );

    setRepayingInvoiceId(null);
    setRepaymentAmount("");
  };

  // Calculate total amount due from open loans
  const totalAmountDue = React.useMemo(() => {
    return mockInvoices
      .filter(invoice => invoice.status === 'Approved' && invoice.paymentStatus === 'Open')
      .reduce((total, invoice) => {
        const remainingAmount = (invoice.totalToRepay || 0) - (invoice.repaidAmount || 0);
        return total + remainingAmount;
      }, 0);
  }, [mockInvoices]);

  // Clear all session data on disconnect or when needed
  const clearSessionData = () => {
    sessionStorage.removeItem('companyData');
    sessionStorage.removeItem('invoicesData');
    sessionStorage.removeItem('companyRegistrationForm');
    setCompany(null);
    setMockInvoices([]);
  };

  if (!isConnected) {
    return (
      <PageBackground>
        <div className="min-h-screen py-8">
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-3xl font-bold text-foreground mb-4">Please Connect Your Wallet</h1>
            <p className="text-muted-foreground">Connect your wallet to access the company dashboard.</p>
          </div>
        </div>
      </PageBackground>
    );
  }

  return (
    <PageBackground>
      <div className="min-h-screen py-8">
        {company ? (
          <div className="container mx-auto px-4">
            <h1 className="text-3xl font-bold text-foreground mb-8">
              Hello, {company.name}
            </h1>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="space-y-8">
                <CreateInvoiceForm onInvoiceSubmit={handleInvoiceSubmit} />
                
                {/* Factoring Quote Section */}
                {selectedInvoice && selectedInvoice.status === 'Pending' && (
                  <div className="bg-card/30 backdrop-blur-md p-6 rounded-lg shadow-md w-full border border-white/10">
                    <h2 className="text-xl font-semibold mb-4 text-foreground">Factoring Offer</h2>
                    <div className="space-y-4">
                      <p className="text-muted-foreground">
                        For invoice #{selectedInvoice.id.slice(0, 6)} of ${selectedInvoice.amount.toFixed(2)}, we can advance up to <span className="font-semibold">70%</span> at a <span className="font-semibold">3%</span> fee.
                      </p>
                      <div className="bg-card/20 backdrop-blur-sm p-4 rounded-md border border-white/5">
                        <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                          <div>
                            <p className="text-muted-foreground">Invoice Amount:</p>
                            <p className="font-medium">${selectedInvoice.amount.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Maximum Advance (70%):</p>
                            <p className="font-medium">${(selectedInvoice.amount * 0.7).toFixed(2)}</p>
                          </div>

                          <div className="col-span-2">
                            <p className="text-muted-foreground mb-2">Select Advance Amount:</p>
                            <div className="space-y-4">
                              <Slider
                                value={[selectedAdvanceAmount]}
                                onValueChange={(values: number[]) => handleAdvanceAmountChange(values[0])}
                                min={1}
                                max={selectedInvoice.amount * 0.7}
                                step={0.01}
                                className="[&_.slider-thumb]:bg-[#C3550B] [&_.slider-track]:bg-[#C3550B]"
                              />
                              <Input
                                type="number"
                                value={inputValue}
                                onChange={handleAdvanceAmountInput}
                                onBlur={handleInputBlur}
                                onKeyDown={handleInputKeyDown}
                                min={1}
                                max={selectedInvoice.amount * 0.7}
                                step={0.01}
                                className="w-full"
                              />
                            </div>
                          </div>

                          <div>
                            <p className="text-muted-foreground">Fee (3% of invoice):</p>
                            <p className="font-medium">${(selectedInvoice.amount * 0.03).toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Total to Repay:</p>
                            <p className="font-medium">${(selectedAdvanceAmount + selectedInvoice.amount * 0.03).toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Term:</p>
                            <p className="font-medium">{selectedInvoice.termDays} days</p>
                          </div>
                        </div>
                        <div className="flex gap-4 justify-end">
                          <Button 
                            onClick={handleDenyQuote}
                            variant="outline"
                            className="border-[#C3550B] text-[#C3550B] hover:bg-[#C3550B] hover:text-white"
                          >
                            Deny
                          </Button>
                          <Button 
                            onClick={handleAcceptQuote}
                            className="bg-[#C3550B] hover:bg-[#A34709] text-white"
                          >
                            Accept Quote
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Loan History Section */}
              <div className="bg-card/30 backdrop-blur-md p-6 rounded-lg shadow-md border border-white/10">
                <div className="mb-6">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold text-foreground">Loan History</h2>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className={`hover:bg-white/10 ${
                            (statusFilter !== 'All' || (statusFilter as string === 'Approved' && paymentStatusFilter !== 'All'))
                              ? 'text-[#C3550B]'
                              : 'text-muted-foreground'
                          }`}
                        >
                          <Filter className="h-5 w-5" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-[200px] bg-card/30 backdrop-blur-md border-white/10">
                        <div className="p-3">
                          <div className="space-y-4">
                            <div>
                              <label className="text-sm font-medium text-muted-foreground mb-2 block">Status</label>
                              <div className="flex flex-col gap-2">
                                <Button
                                  variant={statusFilter === 'All' ? "default" : "outline"}
                                  onClick={() => setStatusFilter('All')}
                                  className={statusFilter === 'All' 
                                    ? "bg-[#C3550B] hover:bg-[#A34709] w-full justify-start" 
                                    : "border-[#C3550B] text-[#C3550B] hover:bg-[#C3550B] hover:text-white w-full justify-start"
                                  }
                                  size="sm"
                                >
                                  All
                                </Button>
                                <Button
                                  variant={statusFilter === 'Approved' ? "default" : "outline"}
                                  onClick={() => setStatusFilter('Approved')}
                                  className={statusFilter === 'Approved'
                                    ? "bg-[#C3550B] hover:bg-[#A34709] w-full justify-start"
                                    : "border-[#C3550B] text-[#C3550B] hover:bg-[#C3550B] hover:text-white w-full justify-start"
                                  }
                                  size="sm"
                                >
                                  Approved
                                </Button>
                                <Button
                                  variant={statusFilter === 'Denied' ? "default" : "outline"}
                                  onClick={() => setStatusFilter('Denied')}
                                  className={statusFilter === 'Denied'
                                    ? "bg-[#C3550B] hover:bg-[#A34709] w-full justify-start"
                                    : "border-[#C3550B] text-[#C3550B] hover:bg-[#C3550B] hover:text-white w-full justify-start"
                                  }
                                  size="sm"
                                >
                                  Denied
                                </Button>
                              </div>
                            </div>

                            {statusFilter === 'Approved' && (
                              <>
                                <DropdownMenuSeparator />
                                <div>
                                  <label className="text-sm font-medium text-muted-foreground mb-2 block">Payment Status</label>
                                  <div className="flex flex-col gap-2">
                                    <Button
                                      variant={paymentStatusFilter === 'All' ? "default" : "outline"}
                                      onClick={() => setPaymentStatusFilter('All')}
                                      className={paymentStatusFilter === 'All'
                                        ? "bg-[#C3550B] hover:bg-[#A34709] w-full justify-start"
                                        : "border-[#C3550B] text-[#C3550B] hover:bg-[#C3550B] hover:text-white w-full justify-start"
                                      }
                                      size="sm"
                                    >
                                      All
                                    </Button>
                                    <Button
                                      variant={paymentStatusFilter === 'Open' ? "default" : "outline"}
                                      onClick={() => setPaymentStatusFilter('Open')}
                                      className={paymentStatusFilter === 'Open'
                                        ? "bg-[#C3550B] hover:bg-[#A34709] w-full justify-start"
                                        : "border-[#C3550B] text-[#C3550B] hover:bg-[#C3550B] hover:text-white w-full justify-start"
                                      }
                                      size="sm"
                                    >
                                      Open
                                    </Button>
                                    <Button
                                      variant={paymentStatusFilter === 'Closed' ? "default" : "outline"}
                                      onClick={() => setPaymentStatusFilter('Closed')}
                                      className={paymentStatusFilter === 'Closed'
                                        ? "bg-[#C3550B] hover:bg-[#A34709] w-full justify-start"
                                        : "border-[#C3550B] text-[#C3550B] hover:bg-[#C3550B] hover:text-white w-full justify-start"
                                      }
                                      size="sm"
                                    >
                                      Closed
                                    </Button>
                                  </div>
                                </div>
                              </>
                            )}
                          </div>
                        </div>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                  <div className="bg-card/20 backdrop-blur-sm p-4 rounded-md border border-white/5">
                    <div className="flex justify-between items-center">
                      <span className="text-muted-foreground font-medium">Amount due:</span>
                      <span className="text-lg font-semibold text-[#C3550B]">
                        ${totalAmountDue.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>

                {mockInvoices.length === 0 ? (
                  <p className="text-muted-foreground">No loans in history</p>
                ) : (
                  <div className="space-y-6">
                    {filteredInvoices.map((invoice) => (
                      <div key={invoice.id} className="border-b pb-6 last:border-b-0">
                        <div className="flex justify-between items-center mb-3">
                          <span className="font-medium">Invoice #{invoice.id.slice(0, 6)}</span>
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-1 rounded text-sm ${
                              invoice.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' : 
                              invoice.status === 'Approved' ? 'bg-green-100 text-green-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {invoice.status}
                            </span>
                            {invoice.status === 'Approved' && (
                              <span className={`px-2 py-1 rounded text-sm ${
                                invoice.paymentStatus === 'Open' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                              }`}>
                                {invoice.paymentStatus}
                              </span>
                            )}
                          </div>
                        </div>

                        {invoice.status === 'Pending' && (
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-muted-foreground">Amount:</span>
                              <span className="ml-2 font-medium">${invoice.amount.toFixed(2)}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Due Date:</span>
                              <span className="ml-2 font-medium">{new Date(invoice.dueDate).toLocaleDateString()}</span>
                            </div>
                          </div>
                        )}

                        {invoice.status === 'Approved' && (
                          <div className="space-y-3">
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <span className="text-muted-foreground">Invoice Amount:</span>
                                <span className="ml-2 font-medium">${invoice.amount.toFixed(2)}</span>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Advance Rate:</span>
                                <span className="ml-2 font-medium">{invoice.advanceRate?.toFixed(2)}%</span>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Advanced Amount:</span>
                                <span className="ml-2 font-medium">${invoice.advanceAmount?.toFixed(2)}</span>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Fee ({invoice.feePercentage}%):</span>
                                <span className="ml-2 font-medium">${invoice.feeAmount?.toFixed(2)}</span>
                              </div>
                              {invoice.paymentStatus === 'Open' && (
                                <>
                                  <div className="col-span-2 border-t pt-2">
                                    <div className="flex justify-between items-center text-sm">
                                      <span className="text-muted-foreground">Total Repaid So Far:</span>
                                      <span className="font-medium">${invoice.repaidAmount?.toFixed(2)}</span>
                                    </div>
                                  </div>
                                  {repayingInvoiceId === invoice.id ? (
                                    <div className="col-span-2 bg-card p-3 rounded-md">
                                      <div className="space-y-3">
                                        <div>
                                          <label className="block text-sm text-muted-foreground mb-1">
                                            Enter Repayment Amount:
                                          </label>
                                          <div className="flex gap-2">
                                            <Input
                                              type="number"
                                              value={repaymentAmount}
                                              onChange={handleRepaymentAmountChange}
                                              min={1}
                                              max={(invoice.totalToRepay || 0) - (invoice.repaidAmount || 0)}
                                              step={0.01}
                                              className="w-full"
                                              placeholder="Enter amount"
                                            />
                                          </div>
                                        </div>
                                        <div className="flex justify-end gap-2">
                                          <Button
                                            variant="outline"
                                            onClick={handleCancelRepayment}
                                            className="border-[#C3550B] text-[#C3550B] hover:bg-[#C3550B] hover:text-white"
                                          >
                                            Cancel
                                          </Button>
                                          <Button
                                            onClick={() => handleRepayment(invoice)}
                                            className="bg-[#C3550B] hover:bg-[#A34709] text-white"
                                          >
                                            Confirm Payment
                                          </Button>
                                        </div>
                                      </div>
                                    </div>
                                  ) : (
                                    <div className="col-span-2">
                                      <Button
                                        onClick={() => handleStartRepayment(invoice.id)}
                                        className="w-full bg-[#C3550B] hover:bg-[#A34709] text-white"
                                      >
                                        Repay
                                      </Button>
                                    </div>
                                  )}
                                </>
                              )}
                            </div>
                            <div className="mt-3 p-3 bg-card rounded-md">
                              <div className="flex justify-between items-center">
                                <span className="font-medium text-foreground">
                                  {invoice.paymentStatus === 'Open' ? 'Remaining to Repay:' : 'Total Repaid:'}
                                </span>
                                <span className="text-lg font-semibold text-[#C3550B]">
                                  ${invoice.paymentStatus === 'Open' 
                                    ? ((invoice.totalToRepay || 0) - (invoice.repaidAmount || 0)).toFixed(2)
                                    : invoice.totalToRepay?.toFixed(2)
                                  }
                                </span>
                              </div>
                              <div className="text-sm text-muted-foreground mt-1">
                                Due by: {new Date(invoice.dueDate).toLocaleDateString()}
                              </div>
                            </div>
                          </div>
                        )}

                        {invoice.status === 'Denied' && (
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-muted-foreground">Amount Requested:</span>
                              <span className="ml-2 font-medium">${invoice.amount.toFixed(2)}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Due Date:</span>
                              <span className="ml-2 font-medium">{new Date(invoice.dueDate).toLocaleDateString()}</span>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="container mx-auto px-4">
            <h1 className="text-3xl font-bold text-foreground mb-8">Company Registration</h1>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-[#C3550B] hover:bg-[#A34709] text-white">
                  Register Your Company
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-card/30 backdrop-blur-md border-white/10">
                <DialogTitle className="text-foreground">Company Registration</DialogTitle>
                <CompanyRegistrationForm onSubmit={(data) => {
                  setCompany({
                    name: data.companyName,
                    walletAddress: address || ''
                  });
                  setIsDialogOpen(false);
                }} />
              </DialogContent>
            </Dialog>
          </div>
        )}
      </div>
    </PageBackground>
  );
} 