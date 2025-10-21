'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Header from '@/components/Header'
import VisaDetails from '@/components/VisaDetails'

export default function VisaInformationPage() {
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedCountryCode, setSelectedCountryCode] = useState<string>('');
  const [selectedPurpose, setSelectedPurpose] = useState<string>('');
  const params = useParams();
  const router = useRouter();

  // Parse URL parameters to get country and purpose
  useEffect(() => {
    if (params.country && params.purpose) {
      const countrySlug = params.country as string;
      const purposeSlug = params.purpose as string;
      
      // Convert URL slugs back to readable format
      const country = countrySlug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      const purpose = purposeSlug.replace(/-visa$/, '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      
      setSelectedCountry(country);
      setSelectedPurpose(purpose);
      
      // Set country code based on country name (you might want to fetch this from API)
      const countryCodeMap: { [key: string]: string } = {
        'Vietnam': 'VNM',
        'Thailand': 'THA', 
        'Indonesia': 'IDN',
        'United Arab Emirates': 'ARE'
      };
      setSelectedCountryCode(countryCodeMap[country] || '');
    }
  }, [params]);

  const handleChatOpen = () => {
    if (selectedCountry && selectedPurpose) {
      // Create SEO-friendly URL for chat with current date
      const countrySlug = selectedCountry.toLowerCase().replace(/\s+/g, '-');
      const purposeSlug = selectedPurpose.toLowerCase().replace(/\s+/g, '-') + '-visa';
      const dateSlug = new Date().toLocaleDateString('en-US', { 
        month: 'long', 
        year: 'numeric' 
      }).toLowerCase().replace(/\s+/g, '-');
      
      router.push(`/visa-assistant/${countrySlug}/${purposeSlug}/${dateSlug}`);
    }
  };

  if (!selectedCountry || !selectedPurpose) {
    return (
      <div className="min-h-screen bg-white">
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading visa details...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <Header onChatOpen={handleChatOpen} />
      
      {/* Breadcrumb header */}
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
              onClick={() => router.push('/')}
              className="text-purple-600 hover:text-purple-700 font-medium"
            >
              ← Change Selection
            </button>
          </div>
        </div>
      </section>

      <VisaDetails 
        country={selectedCountry}
        countryCode={selectedCountryCode}
        purpose={selectedPurpose}
        onChatOpen={handleChatOpen}
      />
    </div>
  );
}