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


const AuthModal = dynamic(() => import('@/components/AuthModal'), {
  ssr: false,
  loading: () => <div className="animate-pulse">Loading...</div>
});

export default function LandingPage() {
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedCountryCode, setSelectedCountryCode] = useState<string>('');
  const [selectedPurpose, setSelectedPurpose] = useState<string>('');
  const [isAuthOpen, setIsAuthOpen] = useState<boolean>(false);
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  const handleChatOpen = () => {
    if (isAuthenticated) {
      router.push('/visa-assistant');
    } else {
      setIsAuthOpen(true);
    }
  };

  const handleAuthSuccess = () => {
    setIsAuthOpen(false);
    router.push('/visa-assistant');
  };

  const handleAuthClose = () => {
    setIsAuthOpen(false);
  };

  // Redirect to visa information page with SEO-friendly URL when form is completed
  useEffect(() => {
    if (selectedCountry && selectedPurpose && selectedCountryCode) {
      // Add a small delay for better UX (user can see their selection)
      setTimeout(() => {
        // Create SEO-friendly URL slugs for information page
        const countrySlug = selectedCountry.toLowerCase().replace(/\s+/g, '-');
        const purposeSlug = selectedPurpose.toLowerCase().replace(/\s+/g, '-') + '-visa';
        
        router.push(`/${countrySlug}/${purposeSlug}`);
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


      <AuthModal
        isOpen={isAuthOpen}
        onClose={handleAuthClose}
        onSuccess={handleAuthSuccess}
      />
    </div>
  );
}