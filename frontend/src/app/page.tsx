'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import { Navbar } from '@/components/Navbar';
import NewHero from '@/components/NewHero';
import { Features } from '@/components/Features';
import { HowItWorks } from '@/components/HowItWorks';
import { Benefits } from '@/components/Benefits';
import { Testimonials } from '@/components/Testimonials';
import { CTA } from '@/components/CTA';
import { Footer } from '@/components/Footer';
import { useAuth } from '@/contexts/AuthContext';

const ChatInterface = dynamic(() => import('@/components/ChatInterface'), {
  ssr: false,
  loading: () => <div className="animate-pulse">Loading chat...</div>
});

const AuthModal = dynamic(() => import('@/components/AuthModal'), {
  ssr: false,
  loading: () => <div className="animate-pulse">Loading...</div>
});

export default function LandingPage() {
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedCountryCode, setSelectedCountryCode] = useState<string>('');
  const [selectedPurpose, setSelectedPurpose] = useState<string>('');
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
  const [isAuthOpen, setIsAuthOpen] = useState<boolean>(false);
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  const handleChatOpen = () => {
    if (isAuthenticated) {
      setIsChatOpen(true);
    } else {
      setIsAuthOpen(true);
    }
  };

  const handleChatClose = () => {
    setIsChatOpen(false);
  };

  const handleAuthSuccess = () => {
    setIsAuthOpen(false);
    setIsChatOpen(true);
  };

  const handleAuthClose = () => {
    setIsAuthOpen(false);
  };

  // Redirect to application page when both country and purpose are selected
  useEffect(() => {
    if (selectedCountry && selectedPurpose && selectedCountryCode) {
      // Add a small delay for better UX (user can see their selection)
      setTimeout(() => {
        // Pass the selected data via URL params to the application page
        const params = new URLSearchParams({
          country: selectedCountry,
          countryCode: selectedCountryCode,
          purpose: selectedPurpose
        });
        router.push(`/veazy?${params.toString()}`);
      }, 800); // 800ms delay for better user experience
    }
  }, [selectedCountry, selectedCountryCode, selectedPurpose, router]);

  return (
    <div className="min-h-screen">
      <Navbar onChatOpen={handleChatOpen} />
      
      {/* Hero Section with 4 dropdowns */}
      <NewHero 
        onCountrySelect={(country: string, countryCode: string) => {
          setSelectedCountry(country);
          setSelectedCountryCode(countryCode);
        }}
        onPurposeSelect={(purpose: string) => {
          setSelectedPurpose(purpose);
        }}
        onChatOpen={handleChatOpen}
      />
      
      <Features />
      <HowItWorks />
      <Benefits />
      <Testimonials />
      <CTA onChatOpen={handleChatOpen} />
      <Footer />

      <ChatInterface 
        isOpen={isChatOpen} 
        onClose={handleChatClose}
      />

      <AuthModal
        isOpen={isAuthOpen}
        onClose={handleAuthClose}
        onSuccess={handleAuthSuccess}
      />
    </div>
  );
}