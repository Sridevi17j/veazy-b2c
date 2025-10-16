'use client';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Loader2 } from "lucide-react";

interface PreferenceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (preferredName?: string) => void;
  onSkip: () => void;
  isLoading?: boolean;
  userFirstName?: string;
}

export default function PreferenceModal({
  isOpen,
  onClose,
  onSubmit,
  onSkip,
  isLoading = false,
  userFirstName = ''
}: PreferenceModalProps) {
  const [preferredName, setPreferredName] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(preferredName.trim() || undefined);
  };

  const handleSkip = () => {
    onSkip();
  };

  const handleClose = () => {
    if (!isLoading) {
      setPreferredName('');
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
            Hey there!
          </DialogTitle>
          <DialogDescription className="text-gray-500 text-sm">
            Your preferred name or nickname
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 pt-2">
          <div className="space-y-2">
            <Input
              type="text"
              placeholder="Preferred name"
              value={preferredName}
              onChange={(e) => setPreferredName(e.target.value)}
              disabled={isLoading}
              className="h-12 bg-white border-gray-200 rounded-lg text-gray-700 placeholder:text-gray-400"
              maxLength={50}
            />
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full h-12 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-medium rounded-lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Completing...
              </>
            ) : (
              'Get Started'
            )}
          </Button>
        </form>
        
        {/* Skip section */}
        <div className="text-center mt-4 pb-2">
          <button 
            className="text-purple-600 hover:text-purple-700 font-medium text-sm"
            onClick={handleSkip}
            disabled={isLoading}
          >
            Skip
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}