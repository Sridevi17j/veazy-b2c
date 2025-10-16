'use client';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Loader2 } from "lucide-react";

interface PhoneNumberModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (countryCode: string, localPhone: string) => void;
  isLoading?: boolean;
}

export default function PhoneNumberModal({ 
  isOpen, 
  onClose, 
  onSubmit, 
  isLoading = false 
}: PhoneNumberModalProps) {
  const [localPhone, setLocalPhone] = useState<string>('');
  const [error, setError] = useState<string>('');


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate inputs
    if (!localPhone.trim()) {
      setError('Please enter your phone number');
      return;
    }

    // Basic phone number validation (only digits, spaces, hyphens allowed)
    const cleanPhone = localPhone.replace(/[\s-]/g, '');
    if (!/^\d{10}$/.test(cleanPhone)) {
      setError('Please enter a valid 10-digit phone number');
      return;
    }

    // Fixed country code for India
    onSubmit('+91', cleanPhone);
  };

  const handlePhoneChange = (value: string) => {
    // Allow only digits, spaces, and hyphens
    const formatted = value.replace(/[^\d\s-]/g, '');
    setLocalPhone(formatted);
    setError('');
  };

  const handleClose = () => {
    if (!isLoading) {
      setError('');
      setLocalPhone('');
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md bg-gray-50 border-none shadow-lg">
        <DialogHeader className="text-center space-y-3 pb-2">
          {/* Veazy Logo */}
          <div className="flex justify-center mb-2">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">V</span>
            </div>
          </div>
          
          <DialogTitle className="text-xl font-semibold text-gray-900">
            Welcome Onboard!
          </DialogTitle>
          <DialogDescription className="text-gray-500 text-sm">
            Your journey starts here
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 pt-2">
          <div className="space-y-2">
            <div className="flex gap-2">
              <div className="w-16 h-12 px-3 bg-gray-100 border border-gray-200 rounded-lg flex items-center justify-center text-gray-600 font-mono text-sm">
                +91
              </div>
              <Input
                id="phone-number"
                type="tel"
                placeholder="Mobile Number"
                value={localPhone}
                onChange={(e) => handlePhoneChange(e.target.value)}
                disabled={isLoading}
                className="flex-1 h-12 bg-white border-gray-200 rounded-lg text-gray-700 placeholder:text-gray-400"
                maxLength={15}
              />
            </div>
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">
              {error}
            </div>
          )}

          <Button
            type="submit"
            disabled={isLoading || !localPhone.trim()}
            className="w-full h-12 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-medium rounded-lg mt-6"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Sending...
              </>
            ) : (
              'Continue'
            )}
          </Button>
        </form>
        
        {/* Already have an account section */}
        <div className="text-center mt-6 pb-2">
          <p className="text-sm text-gray-500">
            Already have an account?{' '}
            <button 
              className="text-purple-600 hover:text-purple-700 font-medium"
              onClick={() => {/* Handle sign in */}}
            >
              Sign in
            </button>
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}