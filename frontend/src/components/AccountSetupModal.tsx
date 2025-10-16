'use client';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Loader2 } from "lucide-react";

interface AccountSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (firstName: string, lastName: string, email: string) => void;
  isLoading?: boolean;
}

export default function AccountSetupModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false
}: AccountSetupModalProps) {
  const [firstName, setFirstName] = useState<string>('');
  const [lastName, setLastName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [error, setError] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!firstName.trim()) {
      setError('First name is required');
      return;
    }

    if (!lastName.trim()) {
      setError('Last name is required');
      return;
    }

    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError('Please enter a valid email address');
      return;
    }

    onSubmit(firstName.trim(), lastName.trim(), email.trim());
  };

  const handleClose = () => {
    if (!isLoading) {
      setError('');
      setFirstName('');
      setLastName('');
      setEmail('');
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
            Set up Account
          </DialogTitle>
          <DialogDescription className="text-gray-500 text-sm">
            Let's get started
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 pt-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Input
                type="text"
                placeholder="First Name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                disabled={isLoading}
                className="h-12 bg-white border-gray-200 rounded-lg text-gray-700 placeholder:text-gray-400"
                maxLength={50}
              />
            </div>
            <div className="space-y-1">
              <Input
                type="text"
                placeholder="Last Name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                disabled={isLoading}
                className="h-12 bg-white border-gray-200 rounded-lg text-gray-700 placeholder:text-gray-400"
                maxLength={50}
              />
            </div>
          </div>

          <div className="space-y-1">
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              className="h-12 bg-white border-gray-200 rounded-lg text-gray-700 placeholder:text-gray-400"
              maxLength={100}
            />
          </div>

          {error && (
            <div className="text-center">
              <p className="text-sm text-red-600 font-medium">{error}</p>
            </div>
          )}

          <Button
            type="submit"
            disabled={isLoading || !firstName.trim() || !lastName.trim() || !email.trim()}
            className="w-full h-12 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-medium rounded-lg mt-6"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Setting up...
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