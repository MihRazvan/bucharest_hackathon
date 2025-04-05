"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import React from "react";

declare global {
  interface Window {
    ethereum?: {
      selectedAddress: string;
    };
  }
}

const formSchema = z.object({
  firstName: z.string().min(2, "First name must be at least 2 characters"),
  lastName: z.string().min(2, "Last name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  companyName: z.string().min(2, "Company name must be at least 2 characters"),
  country: z.string().min(2, "Please select your country of residence"),
  registrationNumber: z.string().min(1, "Company registration number is required"),
  website: z.string().url("Please enter a valid URL").optional().or(z.literal('')),
});

type FormValues = z.infer<typeof formSchema>;

interface CompanyRegistrationFormProps {
  onSubmit?: (data: FormValues) => void;
}

export function CompanyRegistrationForm({ onSubmit }: CompanyRegistrationFormProps) {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: React.useMemo(() => {
      // Try to get saved form data from sessionStorage
      if (typeof window !== 'undefined') {
        const savedData = sessionStorage.getItem('companyRegistrationForm');
        return savedData ? JSON.parse(savedData) : {
          firstName: "",
          lastName: "",
          email: "",
          companyName: "",
          country: "",
          registrationNumber: "",
          website: "",
        };
      }
      return {
        firstName: "",
        lastName: "",
        email: "",
        companyName: "",
        country: "",
        registrationNumber: "",
        website: "",
      };
    }, []),
  });

  // Save form data to sessionStorage whenever it changes
  React.useEffect(() => {
    const subscription = form.watch((value) => {
      sessionStorage.setItem('companyRegistrationForm', JSON.stringify(value));
    });
    return () => subscription.unsubscribe();
  }, [form.watch]);

  const handleSubmit = (data: FormValues) => {
    // Create company object
    const companyData = {
      name: data.companyName,
      walletAddress: window.ethereum?.selectedAddress || '',
      ...data
    };
    
    // Store in session storage and call onSubmit
    sessionStorage.setItem('companyData', JSON.stringify(companyData));
    onSubmit?.(data);
    
    // Clear form data from session storage after successful submission
    sessionStorage.removeItem('companyRegistrationForm');
  };

  return (
    <div className="w-full mx-auto p-4 max-h-[80vh] overflow-y-auto">
      <div className="mb-4 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Company Registration</h1>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)} className="w-full space-y-4">
          <FormField
            control={form.control}
            name="firstName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>First name</FormLabel>
                <FormControl>
                  <Input placeholder="John" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          
          <FormField
            control={form.control}
            name="lastName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Last name</FormLabel>
                <FormControl>
                  <Input placeholder="Doe" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="companyName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Company name</FormLabel>
                <FormControl>
                  <Input placeholder="Acme Inc." {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input type="email" placeholder="john@company.com" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="country"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Country of Residence</FormLabel>
                <FormControl>
                  <Input placeholder="United States" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="registrationNumber"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Company Registration Number</FormLabel>
                <FormControl>
                  <Input placeholder="123456789" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="website"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Website (Optional)</FormLabel>
                <FormControl>
                  <Input type="url" placeholder="https://www.example.com" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button type="submit" className="w-full mt-6">
            Complete Registration
          </Button>
        </form>
      </Form>
    </div>
  );
} 