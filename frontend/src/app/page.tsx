'use client';

import { useState } from 'react';
import Header from '@/components/Header'
import HeroSection from '@/components/HeroSection'
import VisaDetails from '@/components/VisaDetails'
import ChatInterface from '@/components/ChatInterface'

export default function Home() {
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedCountryCode, setSelectedCountryCode] = useState<string>('');
  const [selectedPurpose, setSelectedPurpose] = useState<string>('');
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);

  const handleChatOpen = () => {
    setIsChatOpen(true);
  };

  const handleChatClose = () => {
    setIsChatOpen(false);
  };

  return (
    <div className="min-h-screen bg-white">
      <Header onChatOpen={handleChatOpen} />
      <HeroSection 
        onCountrySelect={(country: string, countryCode: string) => {
          setSelectedCountry(country);
          setSelectedCountryCode(countryCode);
        }}
        onPurposeSelect={(purpose: string) => {
          setSelectedPurpose(purpose);
        }}
        onChatOpen={handleChatOpen}
      />
      <VisaDetails 
        country={selectedCountry}
        countryCode={selectedCountryCode}
        purpose={selectedPurpose}
        onChatOpen={handleChatOpen}
      />
      <ChatInterface 
        isOpen={isChatOpen} 
        onClose={handleChatClose}
      />
    </div>
  );
}
