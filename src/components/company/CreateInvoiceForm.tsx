"use client";

import * as React from "react";
import { Input } from "@/components/layout/Layout";

interface CreateInvoiceFormProps {
  onInvoiceSubmit: (invoice: {
    id: string;
    amount: number;
    dueDate: string;
    status: 'Pending' | 'Approved' | 'Denied';
    termDays: number;
  }) => void;
}

export function CreateInvoiceForm({ onInvoiceSubmit }: CreateInvoiceFormProps) {
  const [amount, setAmount] = React.useState("");
  const [dueDate, setDueDate] = React.useState("");

  // Calculate tomorrow's date for the minimum selectable date
  const tomorrow = React.useMemo(() => {
    const date = new Date();
    date.setDate(date.getDate() + 1);
    return date.toISOString().split('T')[0];
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Calculate the number of days between today and the due date
    const today = new Date();
    const dueDateObj = new Date(dueDate);
    const diffTime = dueDateObj.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    const newInvoice = {
      id: Math.random().toString(36).substr(2, 9), // Generate a random ID
      amount: parseFloat(amount),
      dueDate,
      status: 'Pending' as const,
      termDays: diffDays
    };

    onInvoiceSubmit(newInvoice);
    
    // Reset form
    setAmount("");
    setDueDate("");
  };

  return (
    <div className="w-full bg-card/30 backdrop-blur-md p-6 rounded-lg shadow-md border border-white/10">
      <h2 className="text-2xl font-semibold mb-6 text-foreground">Create New Invoice</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="amount" className="block text-sm font-medium text-muted-foreground mb-1">
            Invoice Amount
          </label>
          <Input
            id="amount"
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Enter amount"
            required
            min="0"
            step="0.01"
            className="bg-card/20 backdrop-blur-sm border-white/5"
          />
        </div>
        
        <div>
          <label htmlFor="dueDate" className="block text-sm font-medium text-muted-foreground mb-1">
            Due Date
          </label>
          <Input
            id="dueDate"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            required
            min={tomorrow}
            className="bg-card/20 backdrop-blur-sm border-white/5"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-[#C3550B] text-white py-2 px-4 rounded-md hover:bg-[#A34709] transition-colors"
        >
          Submit Invoice
        </button>
      </form>
    </div>
  );
} 