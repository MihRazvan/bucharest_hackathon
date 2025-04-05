"use client";

import Link from 'next/link';
import ConnectWalletButton from '@/components/web3/ConnectWalletButton';
import Image from 'next/image';
import * as React from "react";
import { cn } from "@/lib/utils";
import { useMotionTemplate, useMotionValue, motion } from "motion/react";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-black">
      <header className="bg-black border-b border-[#1a1a1a]">
        <nav className="container mx-auto flex items-center justify-between relative h-16">
          {/* Left side navigation */}
          <div className="flex items-center gap-12">
            <Link href="/company" className="text-foreground hover:text-muted-foreground transition-colors px-4">
              Register
            </Link>
            <Link href="/earn" className="text-foreground hover:text-muted-foreground transition-colors px-4">
              Earn
            </Link>
          </div>
          
          {/* Centered logo */}
          <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center">
            <Link href="/" className="flex items-center">
              <Image
                src="/logo.svg"
                alt="Pipe It !!"
                width={60}
                height={60}
                className="object-contain"
                priority
              />
            </Link>
          </div>

          {/* Right side wallet button */}
          <ConnectWalletButton />
        </nav>
      </header>
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
} 

// Input component extends from shadcnui - https://ui.shadcn.com/docs/components/input
type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    const radius = 100; // change this to increase the radius of the hover effect
    const [visible, setVisible] = React.useState(false);

    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    interface MouseEventData {
      currentTarget: HTMLElement;
      clientX: number;
      clientY: number;
    }

    function handleMouseMove({ currentTarget, clientX, clientY }: MouseEventData) {
      const { left, top } = currentTarget.getBoundingClientRect();

      mouseX.set(clientX - left);
      mouseY.set(clientY - top);
    }

    return (
      <motion.div
        style={{
          background: useMotionTemplate`
        radial-gradient(
          ${visible ? radius + "px" : "0px"} circle at ${mouseX}px ${mouseY}px,
          #C3550B,
          transparent 80%
        )
      `,
        }}
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        className="group/input rounded-lg p-[2px] transition duration-300"
      >
        <input
          type={type}
          className={cn(
            `shadow-input dark:placeholder-text-neutral-600 flex h-10 w-full rounded-md border-none bg-gray-50 px-3 py-2 text-sm text-black transition duration-400 group-hover/input:shadow-none file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-neutral-400 focus-visible:ring-[2px] focus-visible:ring-[#C3550B] focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:bg-zinc-800 dark:text-white dark:shadow-[0px_0px_1px_1px_#404040] dark:focus-visible:ring-[#C3550B]`,
            className,
          )}
          ref={ref}
          {...props}
        />
      </motion.div>
    );
  },
);
Input.displayName = "Input";

export { Input };