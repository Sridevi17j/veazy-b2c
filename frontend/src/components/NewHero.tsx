'use client';

import { useState, useEffect } from 'react'
import { MessageCircle, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import CustomDatePicker from './DatePicker'

interface Country {
  id: string;
  code: string;
  name: string;
  official_name?: string;
  purposes: string[];
}

interface NewHeroProps {
  onCountrySelect?: (country: string, countryCode: string) => void;
  onPurposeSelect?: (purpose: string) => void;
  onChatOpen?: () => void;
}

export default function NewHero({ onCountrySelect, onPurposeSelect, onChatOpen }: NewHeroProps) {
  const [departureDate, setDepartureDate] = useState<Date | undefined>(new Date('2025-10-05'));
  const [returnDate, setReturnDate] = useState<Date | undefined>(new Date('2025-10-15'));
  const [today, setToday] = useState<Date | null>(null);
  const [selectedCountry, setSelectedCountry] = useState<string>('Vietnam');
  const [selectedPurpose, setSelectedPurpose] = useState<string>('Tourism');
  const [countries, setCountries] = useState<Country[]>([]);
  const [availablePurposes, setAvailablePurposes] = useState<string[]>([]);
  const [countriesLoading, setCountriesLoading] = useState(false);
  const [isCountryDropdownOpen, setIsCountryDropdownOpen] = useState(false);
  const [isPurposeDropdownOpen, setIsPurposeDropdownOpen] = useState(false);
  const [hasFetchedCountries, setHasFetchedCountries] = useState(false);
  const [sessionCache, setSessionCache] = useState<{countries?: Country[]}>({});

  // Set today's date consistently on mount to avoid hydration mismatch
  useEffect(() => {
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    setToday(now);
  }, []);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('[data-dropdown="country"]') && !target.closest('[data-dropdown="purpose"]')) {
        setIsCountryDropdownOpen(false);
        setIsPurposeDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Don't render the date pickers until today is set to avoid hydration mismatch
  if (!today) {
    return (
      <section className="relative overflow-hidden py-20 lg:py-32">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-purple-600/5 to-green-600/10"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left side - Content */}
            <div className="text-center lg:text-left">
              <Badge variant="outline" className="inline-flex items-center space-x-1 bg-blue-100 text-blue-800 mb-6 border-transparent">
                ✨ AI-Powered Visa Magic
              </Badge>
              
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
                Get Your Visa{" "}
                <span className="bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">Automagically</span>
              </h1>
              
              <p className="text-xl text-gray-600 mb-8 max-w-2xl">
                Chat with our friendly AI visa expert who understands your unique situation. 
                Skip the government sites, avoid the paperwork hassle, and watch your visa 
                application happen in real-time like magic! ✨
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-4" onClick={onChatOpen}>
                  <MessageCircle className="mr-2 h-5 w-5" />
                  Start Chatting Now
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </div>

              <div className="flex items-center justify-center lg:justify-start space-x-8 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>No government sites</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Real-time tracking</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Human-like AI</span>
                </div>
              </div>
            </div>

            {/* Right side - Form with 4 dropdowns */}
            <div className="relative">
              <div className="relative bg-white rounded-2xl shadow-2xl p-8 mx-auto max-w-md">
                <div className="absolute -top-4 -left-4 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <MessageCircle className="w-4 h-4 text-white" />
                </div>
                <form className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-xs text-muted-foreground mb-1 font-medium">Destination</label>
                    <div className="w-full p-3 text-sm border border-input rounded-lg bg-background">
                      <div className="flex items-center justify-between">
                        <span className="text-foreground">Vietnam</span>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs text-muted-foreground mb-1 font-medium">Departure Date</label>
                    <div className="w-full p-3 text-sm border border-input rounded-lg bg-background">
                      <span className="text-foreground">10/18/2025</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs text-muted-foreground mb-1 font-medium">Return Date</label>
                    <div className="w-full p-3 text-sm border border-input rounded-lg bg-background">
                      <span className="text-foreground">10/18/2025</span>
                    </div>
                  </div>
                  <div className="col-span-2">
                    <label className="block text-xs text-muted-foreground mb-1 font-medium">Purpose of travel</label>
                    <div className="w-full p-3 text-sm border border-input rounded-lg bg-background">
                      <div className="flex items-center justify-between">
                        <span className="text-foreground">Tourism</span>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>
                  </div>
                </form>
                
                {/* Floating decorative elements */}
                <div className="absolute -top-8 -right-8 w-16 h-16 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full opacity-20 animate-bounce"></div>
                <div className="absolute -bottom-8 -left-8 w-12 h-12 bg-gradient-to-br from-green-400 to-blue-400 rounded-full opacity-20 animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>
      </section>
    );
  }

  const handleDepartureDateChange = (date: Date | undefined) => {
    setDepartureDate(date);
    // If return date is before new departure date, clear it
    if (date && returnDate && returnDate < date) {
      setReturnDate(undefined);
    }
  };

  const handleReturnDateChange = (date: Date | undefined) => {
    setReturnDate(date);
  };

  // Fetch countries from API with session caching
  const fetchCountries = async () => {
    if (hasFetchedCountries || countriesLoading) return;
    
    // Check session cache first
    if (sessionCache.countries) {
      setCountries(sessionCache.countries);
      setHasFetchedCountries(true);
      return;
    }
    
    setCountriesLoading(true);
    try {
      // const response = await fetch('http://localhost:8000/api/countries/supported'); // Local development
      const response = await fetch('https://veazy-backend.onrender.com/api/countries/supported');
      if (!response.ok) {
        throw new Error('Failed to fetch countries');
      }
      const data = await response.json();
      
      // Update both state and session cache
      setCountries(data);
      setSessionCache(prev => ({ ...prev, countries: data }));
      setHasFetchedCountries(true);
    } catch (error) {
      console.error('Error fetching countries:', error);
      // Fallback to hardcoded countries with purposes
      const fallbackCountries = [
        { id: '1', code: 'VNM', name: 'Vietnam', purposes: ['tourism', 'business', 'social', 'cultural'] },
        { id: '2', code: 'THA', name: 'Thailand', purposes: ['tourism', 'business', 'investment', 'family visit'] },
        { id: '3', code: 'IDN', name: 'Indonesia', purposes: ['tourism', 'business', 'social'] },
        { id: '4', code: 'ARE', name: 'United Arab Emirates', purposes: ['tourism', 'business', 'investment', 'medical'] }
      ];
      setCountries(fallbackCountries);
      setSessionCache(prev => ({ ...prev, countries: fallbackCountries }));
      setHasFetchedCountries(true);
    } finally {
      setCountriesLoading(false);
    }
  };

  // Handle country dropdown click
  const handleCountryDropdownClick = () => {
    setIsCountryDropdownOpen(!isCountryDropdownOpen);
    if (!isCountryDropdownOpen) {
      fetchCountries();
    }
  };

  // Handle country selection
  const handleCountrySelect = (country: Country) => {
    setSelectedCountry(country.name);
    setAvailablePurposes(country.purposes);
    setSelectedPurpose('');
    setIsCountryDropdownOpen(false);
    // Notify parent component
    onCountrySelect?.(country.name, country.code);
  };

  // Handle purpose dropdown click
  const handlePurposeDropdownClick = () => {
    setIsPurposeDropdownOpen(!isPurposeDropdownOpen);
  };

  // Handle purpose selection
  const handlePurposeSelect = (purpose: string) => {
    setSelectedPurpose(purpose);
    setIsPurposeDropdownOpen(false);
    // Notify parent component
    onPurposeSelect?.(purpose);
  };

  // Calculate minimum date for return date picker
  const getReturnMinDate = () => {
    // Return date cannot be before today AND cannot be before departure date
    if (departureDate && departureDate >= today) {
      return departureDate;
    }
    return today;
  };

  return (
    <section className="relative overflow-hidden py-20 lg:py-32">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-purple-600/5 to-green-600/10"></div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left side - Content */}
          <div className="text-center lg:text-left">
            <Badge variant="outline" className="inline-flex items-center space-x-1 bg-blue-100 text-blue-800 mb-6 border-transparent">
              ✨ AI-Powered Visa Magic
            </Badge>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
              Get Your Visa{" "}
              <span className="bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">Automagically</span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-2xl">
              Chat with our friendly AI visa expert who understands your unique situation. 
              Skip the government sites, avoid the paperwork hassle, and watch your visa 
              application happen in real-time like magic! ✨
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mb-8">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-4" onClick={onChatOpen}>
                <MessageCircle className="mr-2 h-5 w-5" />
                Start Chatting Now
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </div>

            <div className="flex items-center justify-center lg:justify-start space-x-8 text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>No government sites</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Real-time tracking</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Human-like AI</span>
              </div>
            </div>
          </div>

          {/* Right side - Form with 4 dropdowns */}
          <div className="relative">
            <div className="relative bg-white rounded-2xl shadow-2xl p-8 mx-auto max-w-md">
              <div className="absolute -top-4 -left-4 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <MessageCircle className="w-4 h-4 text-white" />
              </div>
              <form className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-xs text-muted-foreground mb-1 font-medium">Destination</label>
                  <div className="relative" data-dropdown="country">
                    <div
                      onClick={handleCountryDropdownClick}
                      className="w-full p-3 text-sm border border-input rounded-lg focus:ring-2 focus:ring-ring focus:border-transparent bg-background cursor-pointer hover:bg-accent/50 transition-colors duration-200"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-foreground">
                          {countriesLoading ? 'Loading...' : selectedCountry}
                        </span>
                        <svg 
                          className={`w-4 h-4 transition-transform duration-200 ${isCountryDropdownOpen ? 'rotate-180' : ''}`}
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>

                    {/* Dropdown menu */}
                    {isCountryDropdownOpen && (
                      <div className="absolute top-full left-0 right-0 mt-1 bg-popover border border-border rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
                        {countriesLoading ? (
                          <div className="p-3 text-center text-muted-foreground">
                            Loading countries...
                          </div>
                        ) : countries.length > 0 ? (
                          countries.map((country) => (
                            <div
                              key={country.id}
                              onClick={() => handleCountrySelect(country)}
                              className={`
                                p-3 cursor-pointer transition-colors duration-150
                                hover:bg-accent hover:text-accent-foreground
                                ${selectedCountry === country.name ? 'bg-accent text-accent-foreground' : 'text-popover-foreground'}
                              `}
                            >
                              <div className="flex items-center justify-between">
                                <span className="font-medium">{country.name}</span>
                                <span className="text-xs text-muted-foreground">{country.code}</span>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="p-3 text-center text-muted-foreground">
                            No countries available
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                <div>
                  <CustomDatePicker
                    label="Departure Date"
                    selected={departureDate}
                    onSelect={handleDepartureDateChange}
                    placeholder="Select departure date"
                    fromDate={today}
                  />
                </div>
                <div>
                  <CustomDatePicker
                    label="Return Date"
                    selected={returnDate}
                    onSelect={handleReturnDateChange}
                    placeholder="Select return date"
                    fromDate={getReturnMinDate()}
                    error={returnDate && departureDate && returnDate < departureDate}
                    errorMessage={returnDate && departureDate && returnDate < departureDate ? "Return date cannot be before departure date" : undefined}
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-xs text-muted-foreground mb-1 font-medium">Purpose of travel</label>
                  <div className="relative" data-dropdown="purpose">
                    <div
                      onClick={handlePurposeDropdownClick}
                      className="w-full p-3 text-sm border border-input rounded-lg focus:ring-2 focus:ring-ring focus:border-transparent bg-background cursor-pointer hover:bg-accent/50 transition-colors duration-200"
                    >
                      <div className="flex items-center justify-between">
                        <span className={`${selectedPurpose ? 'text-foreground' : 'text-muted-foreground'}`}>
                          {selectedPurpose || 'Select purpose'}
                        </span>
                        <svg 
                          className={`w-4 h-4 transition-transform duration-200 ${isPurposeDropdownOpen ? 'rotate-180' : ''}`}
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>

                    {/* Purpose dropdown menu */}
                    {isPurposeDropdownOpen && (
                      <div className="absolute top-full left-0 right-0 mt-1 bg-popover border border-border rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
                        {availablePurposes.length > 0 ? (
                          availablePurposes.map((purpose, index) => (
                            <div
                              key={index}
                              onClick={() => handlePurposeSelect(purpose)}
                              className={`
                                p-3 cursor-pointer transition-colors duration-150
                                hover:bg-accent hover:text-accent-foreground
                                ${selectedPurpose === purpose ? 'bg-accent text-accent-foreground' : 'text-popover-foreground'}
                              `}
                            >
                              <span className="font-medium capitalize">{purpose}</span>
                            </div>
                          ))
                        ) : (
                          <div className="p-3 text-center text-muted-foreground">
                            {selectedCountry ? 'No purposes available for this country' : 'Please select a country first'}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </form>
              
              {/* Floating decorative elements */}
              <div className="absolute -top-8 -right-8 w-16 h-16 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full opacity-20 animate-bounce"></div>
              <div className="absolute -bottom-8 -left-8 w-12 h-12 bg-gradient-to-br from-green-400 to-blue-400 rounded-full opacity-20 animate-pulse"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}