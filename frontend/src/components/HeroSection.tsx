'use client';

import Image from 'next/image'
import { useState, useEffect } from 'react'
import CustomDatePicker from './DatePicker'

interface Country {
  id: string;
  code: string;
  name: string;
  official_name?: string;
  purposes: string[];
}

interface HeroSectionProps {
  onCountrySelect?: (country: string, countryCode: string) => void;
  onPurposeSelect?: (purpose: string) => void;
  onChatOpen?: () => void;
}

export default function HeroSection({ onCountrySelect, onPurposeSelect, onChatOpen: _onChatOpen }: HeroSectionProps) {
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
      <section className="relative bg-gray-50">
        {/* Hero image grid */}
        <div className="grid grid-cols-4 gap-0 h-[403px]">
          <div className="bg-gradient-to-br from-orange-200 to-yellow-300 overflow-hidden relative">
            <Image 
              src="https://images.unsplash.com/photo-1528127269322-539801943592?w=600&h=400&fit=crop&auto=format" 
              alt="Vietnam Temple"
              fill
              className="object-cover"
              priority
            />
          </div>
          <div className="bg-gradient-to-br from-green-200 to-emerald-300 overflow-hidden relative">
            <Image 
              src="https://images.unsplash.com/photo-1596414086775-3e321ab08f36?w=400&h=400&fit=crop" 
              alt="Ha Long Bay"
              fill
              className="object-cover"
            />
          </div>
          <div className="bg-gradient-to-br from-blue-200 to-cyan-300 overflow-hidden relative">
            <Image 
              src="https://images.unsplash.com/photo-1528181304800-259b08848526?w=400&h=400&fit=crop" 
              alt="Vietnam Boats"
              fill
              className="object-cover"
            />
          </div>
          <div className="bg-gradient-to-br from-red-200 to-pink-300 overflow-hidden relative">
            <Image 
              src="https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=400&h=400&fit=crop" 
              alt="Vietnam Street"
              fill
              className="object-cover"
            />
          </div>
        </div>

        {/* Travel form overlay with loading skeleton */}
        <div className="absolute top-8 left-1/2 transform -translate-x-1/2 z-10">
          <div className="bg-white rounded-xl shadow-lg p-6 max-w-4xl w-full">
            <form className="grid grid-cols-4 gap-4">
              <div>
                <label className="block text-xs text-gray-600 mb-1 font-medium">Destination</label>
                <select className="w-full p-3 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white">
                  <option>Vietnam</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1 font-medium">Departure Date</label>
                <div className="w-full p-3 text-sm border border-gray-300 rounded-lg bg-gray-100 animate-pulse">
                  Loading...
                </div>
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1 font-medium">Return Date</label>
                <div className="w-full p-3 text-sm border border-gray-300 rounded-lg bg-gray-100 animate-pulse">
                  Loading...
                </div>
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1 font-medium">Purpose of travel</label>
                <select className="w-full p-3 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white">
                  <option>Tourist</option>
                </select>
              </div>
            </form>
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
      const response = await fetch('http://localhost:8000/api/countries/supported');
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
    <section className="relative bg-gray-50">
      {/* Hero image grid */}
      <div className="grid grid-cols-4 gap-0 h-[403px]">
        <div className="bg-gradient-to-br from-orange-200 to-yellow-300 overflow-hidden relative">
          <Image 
            src="https://images.unsplash.com/photo-1528127269322-539801943592?w=600&h=400&fit=crop&auto=format" 
            alt="Vietnam Temple"
            fill
            className="object-cover"
            priority
          />
        </div>
        <div className="bg-gradient-to-br from-green-200 to-emerald-300 overflow-hidden relative">
          <Image 
            src="https://images.unsplash.com/photo-1596414086775-3e321ab08f36?w=400&h=400&fit=crop" 
            alt="Ha Long Bay"
            fill
            className="object-cover"
          />
        </div>
        <div className="bg-gradient-to-br from-blue-200 to-cyan-300 overflow-hidden relative">
          <Image 
            src="https://images.unsplash.com/photo-1528181304800-259b08848526?w=400&h=400&fit=crop" 
            alt="Vietnam Boats"
            fill
            className="object-cover"
          />
        </div>
        <div className="bg-gradient-to-br from-red-200 to-pink-300 overflow-hidden relative">
          <Image 
            src="https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=400&h=400&fit=crop" 
            alt="Vietnam Street"
            fill
            className="object-cover"
          />
        </div>
      </div>

      {/* Travel form overlay */}
      <div className="responsive-overlay z-10">
        <div className="bg-white rounded-xl shadow-lg responsive-card max-w-4xl mobile-full">
          <form className="responsive-form">
            <div>
              <label className="block text-xs text-gray-600 mb-1 font-medium">Destination</label>
              <div className="relative" data-dropdown="country">
                <div
                  onClick={handleCountryDropdownClick}
                  className="w-full p-3 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white cursor-pointer hover:bg-gray-50 transition-colors duration-200"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-gray-900">
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
                  <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
                    {countriesLoading ? (
                      <div className="p-3 text-center text-gray-500">
                        Loading countries...
                      </div>
                    ) : countries.length > 0 ? (
                      countries.map((country) => (
                        <div
                          key={country.id}
                          onClick={() => handleCountrySelect(country)}
                          className={`
                            p-3 cursor-pointer transition-colors duration-150
                            hover:bg-purple-50 hover:text-purple-700
                            ${selectedCountry === country.name ? 'bg-purple-100 text-purple-700' : 'text-gray-900'}
                          `}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{country.name}</span>
                            <span className="text-xs text-gray-500">{country.code}</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="p-3 text-center text-gray-500">
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
            <div>
              <label className="block text-xs text-gray-600 mb-1 font-medium">Purpose of travel</label>
              <div className="relative" data-dropdown="purpose">
                <div
                  onClick={handlePurposeDropdownClick}
                  className="w-full p-3 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white cursor-pointer hover:bg-gray-50 transition-colors duration-200"
                >
                  <div className="flex items-center justify-between">
                    <span className={`${selectedPurpose ? 'text-gray-900' : 'text-gray-500'}`}>
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
                  <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
                    {availablePurposes.length > 0 ? (
                      availablePurposes.map((purpose, index) => (
                        <div
                          key={index}
                          onClick={() => handlePurposeSelect(purpose)}
                          className={`
                            p-3 cursor-pointer transition-colors duration-150
                            hover:bg-purple-50 hover:text-purple-700
                            ${selectedPurpose === purpose ? 'bg-purple-100 text-purple-700' : 'text-gray-900'}
                          `}
                        >
                          <span className="font-medium capitalize">{purpose}</span>
                        </div>
                      ))
                    ) : (
                      <div className="p-3 text-center text-gray-500">
                        {selectedCountry ? 'No purposes available for this country' : 'Please select a country first'}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </form>
        </div>
      </div>
    </section>
  )
}