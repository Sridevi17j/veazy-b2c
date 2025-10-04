'use client';

import { useState, useEffect, useCallback } from 'react';

interface VisaDetailsProps {
  country: string;
  countryCode: string;
  purpose: string;
  onChatOpen?: () => void;
}

interface VisaData {
  country_name: string;
  country_code: string;
  visa_type: string;
  visa_code: string;
  visa_details?: {
    stay_duration: string;
    validity_period: string;
    entry_type: string;
    processing_time: string;
    fee_range: string;
    description: string;
  };
  document_requirements?: Array<{
    name: string;
    description: string;
    required: boolean;
    category: string;
    notes?: string;
  }>;
  approval_process?: Array<{
    step_number: number;
    title: string;
    description: string;
    estimated_time: string;
  }>;
}

export default function VisaDetails({ country, countryCode, purpose, onChatOpen }: VisaDetailsProps) {
  const [visaData, setVisaData] = useState<VisaData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchVisaDetails = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/countries/${countryCode}/purposes/${purpose}/visa-details`);
      if (!response.ok) {
        throw new Error('Failed to fetch visa details');
      }
      const data = await response.json();
      setVisaData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch visa details');
      console.error('Error fetching visa details:', err);
    } finally {
      setLoading(false);
    }
  }, [countryCode, purpose]);

  useEffect(() => {
    if (country && purpose) {
      fetchVisaDetails();
    }
  }, [country, purpose, fetchVisaDetails]);

  if (loading) {
    return (
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-8">
          <div className="flex justify-center items-center h-64">
            <div className="text-lg text-gray-600">Loading visa details...</div>
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-8">
          <div className="text-center text-red-600">
            <p>Error: {error}</p>
            <button 
              onClick={fetchVisaDetails}
              className="mt-4 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
            >
              Retry
            </button>
          </div>
        </div>
      </section>
    );
  }

  if (!visaData) {
    return (
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-8">
          <div className="text-center text-gray-600">
            Select a country and purpose to see visa details
          </div>
        </div>
      </section>
    );
  }
  return (
    <section className="responsive-spacing bg-white">
      <div className="responsive-container">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-8">
          {/* Left side - Visa details */}
          <div className="lg:col-span-2 space-y-8">
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">{visaData.country_name} Visa at Glance</h2>
                <div className="w-32 h-1 bg-gradient-to-r from-purple-600 via-purple-400 to-transparent"></div>
              </div>
              
              <div className="bg-gray-50 rounded-lg responsive-card">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6">
                  <div>
                    <div className="text-sm text-gray-600 mb-1 font-medium">Visa Type:</div>
                    <div className="font-semibold text-gray-900">{visaData.visa_type}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-1 font-medium">Stay Duration</div>
                    <div className="font-semibold text-gray-900">{visaData.visa_details?.stay_duration || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-1 font-medium">Visa Valid For:</div>
                    <div className="font-semibold text-gray-900">{visaData.visa_details?.validity_period || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-1 font-medium">Entry Type:</div>
                    <div className="font-semibold text-gray-900">{visaData.visa_details?.entry_type || 'N/A'}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Documents Requirements */}
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">Documents Requirement for {visaData.country_name}</h2>
                <div className="w-32 h-1 bg-gradient-to-r from-purple-600 via-purple-400 to-transparent"></div>
              </div>
              
              <div className="space-y-4">
                {visaData.document_requirements?.map((doc, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-6">
                    <div className="flex items-start space-x-4">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                      </div>
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold mb-3 text-gray-900">{doc.name}</h3>
                        <p className="text-gray-600 text-sm leading-relaxed">
                          {doc.description}
                        </p>
                      </div>
                    </div>
                  </div>
                )) || (
                  <div className="bg-gray-50 rounded-lg p-6 text-center text-gray-500">
                    Document requirements not available
                  </div>
                )}
              </div>
            </div>

            {/* Visa Approval Process */}
            <div>
              <div className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">Visa approval process</h2>
                <div className="w-32 h-1 bg-gradient-to-r from-purple-600 via-purple-400 to-transparent"></div>
              </div>
              
              <div className="relative mb-12">
                <div className="absolute top-3 left-0 right-0 h-1 bg-gradient-to-r from-purple-600 via-purple-400 to-purple-200 mobile-hidden"></div>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-8 relative">
                  {visaData.approval_process?.map((step, index) => (
                    <div key={index} className="text-center">
                      <div className="w-6 h-6 bg-purple-600 rounded-full mx-auto mb-6 relative z-10"></div>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h3 className="text-sm text-gray-600 mb-1">Step {step.step_number}</h3>
                        <h4 className="font-medium text-gray-900">{step.title}</h4>
                        <p className="text-xs text-gray-500 mt-2">{step.estimated_time}</p>
                      </div>
                    </div>
                  )) || (
                    <>
                      <div className="text-center">
                        <div className="w-6 h-6 bg-purple-600 rounded-full mx-auto mb-6 relative z-10"></div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <h3 className="text-sm text-gray-600 mb-1">Step 1</h3>
                          <h4 className="font-medium text-gray-900">Application Processing</h4>
                        </div>
                      </div>
                      
                      <div className="text-center">
                        <div className="w-6 h-6 bg-purple-600 rounded-full mx-auto mb-6 relative z-10"></div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <h3 className="text-sm text-gray-600 mb-1">Step 2</h3>
                          <h4 className="font-medium text-gray-900">Approval Letter Issued</h4>
                        </div>
                      </div>
                      
                      <div className="text-center">
                        <div className="w-6 h-6 bg-purple-600 rounded-full mx-auto mb-6 relative z-10"></div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <h3 className="text-sm text-gray-600 mb-1">Step 3</h3>
                          <h4 className="font-medium text-gray-900">Visa Stamping & Entry</h4>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Why it Works?</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>🚫 No agents, no hidden fees</li>
                  <li>🤖 AI that knows embassy requirements inside-out.</li>
                  <li>🇮🇳 Designed for Indian travellers, optimised for Vietnam.</li>
                </ul>
              </div>
            </div>

            {/* DIY Your Visa with AI */}
            <div>
              <div className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">DIY Your Visa with AI</h2>
                <div className="w-32 h-1 bg-gradient-to-r from-purple-600 via-purple-400 to-transparent"></div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center space-x-4 p-4 rounded-lg border-l-4 border-purple-600">
                  <div className="w-6 h-6 bg-purple-600 rounded text-white flex items-center justify-center text-xs font-medium">
                    1
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base font-medium text-purple-600">Chat with Visa Genie</h3>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4 p-4 rounded-lg border-l-4 border-purple-600">
                  <div className="w-6 h-6 bg-purple-600 rounded text-white flex items-center justify-center text-xs font-medium">
                    2
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base font-medium text-purple-600">Watch AI Fill Your Application</h3>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4 p-4 rounded-lg border-l-4 border-purple-600">
                  <div className="w-6 h-6 bg-purple-600 rounded text-white flex items-center justify-center text-xs font-medium">
                    3
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base font-medium text-purple-600">Review Everything</h3>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4 p-4 rounded-lg border-l-4 border-purple-600">
                  <div className="w-6 h-6 bg-purple-600 rounded text-white flex items-center justify-center text-xs font-medium">
                    4
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base font-medium text-purple-600">Submit Your Visa Form</h3>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4 p-4 rounded-lg border-l-4 border-purple-600">
                  <div className="w-6 h-6 bg-purple-600 rounded text-white flex items-center justify-center text-xs font-medium">
                    5
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base font-medium text-purple-600">Get Notified When Approved</h3>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Right side - Call to action */}
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="text-center mb-6">
              <button 
                onClick={onChatOpen}
                className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors font-medium text-sm w-full"
              >
                Get your visa by 11 June 2025
              </button>
            </div>
            
            <div className="space-y-4 mb-6">
              <div className="text-sm text-gray-600 mb-4">
                Powered by Visa Genie, your details are auto-mapped into embassy-approved forms.
              </div>
              <div className="text-sm text-gray-600">
                Review, edit if needed, and submit with confidence.
              </div>
            </div>
            
            <div className="space-y-3 border-t pt-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Government fee</span>
                <div className="text-right">
                  <span className="text-lg font-semibold text-gray-900">2500</span>
                  <span className="text-xs text-gray-500 ml-2">Per adult</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Service fee*</span>
                <div className="text-right">
                  <span className="text-lg font-semibold text-gray-900">0</span>
                  <span className="text-xs text-gray-500 ml-2">Per adult</span>
                </div>
              </div>
              
              <div className="text-xs text-gray-500 mt-3">
                *Pay service fee only after visa is submitted and this fee is 100% refundable if visa is not approved on time.
              </div>
              
              <button 
                onClick={onChatOpen}
                className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 transition-colors font-medium text-sm mt-4"
              >
                Start Now
              </button>
            </div>
            
            <div className="mt-6 p-4 border border-purple-300 rounded-lg">
              <div className="text-lg font-semibold mb-2">No Agents, No Confusion</div>
              <div className="text-sm text-gray-600">
                Skip agents and confusing forms. Veazy lets you fill and submit your own visa with AI-powered guidance — simple, error-free, and made for Indian travelers.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}