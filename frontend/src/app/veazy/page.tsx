'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import dynamic from 'next/dynamic';
import Header from '@/components/Header'
import VisaDetails from '@/components/VisaDetails'

const ChatInterface = dynamic(() => import('@/components/ChatInterface'), {
  ssr: false,
  loading: () => <div className="animate-pulse">Loading chat...</div>
})

function VisaApplicationContent() {
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedCountryCode, setSelectedCountryCode] = useState<string>('');
  const [selectedPurpose, setSelectedPurpose] = useState<string>('');
  const [isChatOpen, setIsChatOpen] = useState<boolean>(false);
  const searchParams = useSearchParams();

  // Pre-populate selections from URL parameters (when coming from marketing page)
  useEffect(() => {
    const country = searchParams.get('country');
    const countryCode = searchParams.get('countryCode');
    const purpose = searchParams.get('purpose');

    if (country && countryCode && purpose) {
      setSelectedCountry(country);
      setSelectedCountryCode(countryCode);
      setSelectedPurpose(purpose);
    }
  }, [searchParams]);

  const handleChatOpen = () => {
    setIsChatOpen(true);
  };

  const handleChatClose = () => {
    setIsChatOpen(false);
  };

  return (
    <div className="min-h-screen bg-white">
      <Header onChatOpen={handleChatOpen} />
      
      {/* Show a breadcrumb or header to indicate user's selection */}
      {selectedCountry && selectedPurpose && (
        <section className="bg-gray-50 py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {selectedCountry} Visa Application
                </h1>
                <p className="text-gray-600">
                  Purpose: <span className="capitalize font-medium">{selectedPurpose}</span>
                </p>
              </div>
              <button 
                onClick={() => window.history.back()}
                className="text-purple-600 hover:text-purple-700 font-medium"
              >
                ← Change Selection
              </button>
            </div>
          </div>
        </section>
      )}

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

export default function VisaApplicationPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-white">
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading visa details...</p>
          </div>
        </div>
      </div>
    }>
      <VisaApplicationContent />
    </Suspense>
  );
}
