import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Layout from "@/components/layout/Layout";
import OnchainKitProvider from "@/components/providers/OnchainKitProvider";
import { WalletProvider } from "@/context/WalletContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Pipe It !!",
  description: "Invoice Factoring Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <OnchainKitProvider>
          <WalletProvider>
            <Layout>{children}</Layout>
          </WalletProvider>
        </OnchainKitProvider>
      </body>
    </html>
  );
}
