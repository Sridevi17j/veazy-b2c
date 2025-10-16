'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Loader2, ArrowLeft } from "lucide-react";

interface OTPVerificationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onVerify: (otpCode: string) => void;
  onBack: () => void;
  onResend: () => void;
  phoneNumber: string;
  countryCode: string;
  localPhone: string;
  isLoading?: boolean;
  canResend?: boolean;
}

export default function OTPVerificationModal({
  isOpen,
  onClose,
  onVerify,
  onBack,
  onResend,
  phoneNumber,
  countryCode,
  localPhone,
  isLoading = false,
  canResend = false
}: OTPVerificationModalProps) {
  const [otpCode, setOtpCode] = useState<string>('');
  const [timeLeft, setTimeLeft] = useState<number>(30); // 30 seconds for resend
  const [error, setError] = useState<string>('');
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Countdown timer
  useEffect(() => {
    if (!isOpen) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isOpen]);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setOtpCode('');
      setError('');
      setTimeLeft(600);
      // Focus first input
      setTimeout(() => {
        inputRefs.current[0]?.focus();
      }, 100);
    }
  }, [isOpen]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleOtpChange = (value: string, index: number) => {
    // Only allow digits
    const digit = value.replace(/\D/g, '').slice(-1);
    
    const newOtp = otpCode.split('');
    newOtp[index] = digit;
    const updatedOtp = newOtp.join('');
    
    setOtpCode(updatedOtp);
    setError('');

    // Move to next input if digit entered
    if (digit && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === 'Backspace') {
      if (!otpCode[index] && index > 0) {
        // Move to previous input if current is empty
        inputRefs.current[index - 1]?.focus();
      } else {
        // Clear current input
        const newOtp = otpCode.split('');
        newOtp[index] = '';
        setOtpCode(newOtp.join(''));
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    setOtpCode(pastedData);
    setError('');
    
    // Focus the next empty input or the last one
    const nextIndex = Math.min(pastedData.length, 5);
    inputRefs.current[nextIndex]?.focus();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (otpCode.length !== 6) {
      setError('Please enter the complete 6-digit code');
      return;
    }

    if (timeLeft <= 0) {
      setError('OTP has expired. Please request a new code');
      return;
    }

    onVerify(otpCode);
  };

  const handleResend = () => {
    setOtpCode('');
    setError('');
    setTimeLeft(30);
    onResend();
  };

  const handleClose = () => {
    if (!isLoading) {
      setError('');
      setOtpCode('');
      onClose();
    }
  };

  const maskedPhone = `${countryCode} ${localPhone.slice(0, -4).replace(/\d/g, '•')}${localPhone.slice(-4)}`;

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
            Verify Mobile Number
          </DialogTitle>
          <DialogDescription className="text-gray-500 text-sm">
            Your journey starts here
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 pt-2">
          {/* Timer display */}
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-1">
              Resend OTP in <span className="font-medium text-purple-600">{String(Math.floor(timeLeft / 60)).padStart(2, '0')}:{String(timeLeft % 60).padStart(2, '0')}</span>
            </p>
          </div>

          <div className="space-y-4">
            <div className="flex gap-3 justify-center">
              {[0, 1, 2, 3, 4, 5].map((index) => (
                <Input
                  key={index}
                  ref={(el) => (inputRefs.current[index] = el)}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={otpCode[index] || ''}
                  onChange={(e) => handleOtpChange(e.target.value, index)}
                  onKeyDown={(e) => handleKeyDown(e, index)}
                  onPaste={handlePaste}
                  disabled={isLoading}
                  className="w-11 h-11 text-center text-lg font-mono bg-white border-gray-200 rounded-lg focus:border-purple-500 focus:ring-purple-500"
                />
              ))}
            </div>
          </div>

          <div className="text-center space-y-2">
            <div className="text-sm text-gray-600">
              {timeLeft > 0 ? (
                <>Time remaining: <span className="font-mono font-medium">{formatTime(timeLeft)}</span></>
              ) : (
                <span className="text-red-600">Code expired</span>
              )}
            </div>
            
            {canResend && timeLeft <= 540 && ( // Allow resend after 1 minute
              <Button
                type="button"
                variant="link"
                onClick={handleResend}
                disabled={isLoading}
                className="text-sm"
              >
                Resend Code
              </Button>
            )}
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md text-center">
              {error}
            </div>
          )}

          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={onBack}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            <Button
              type="submit"
              disabled={isLoading || otpCode.length !== 6 || timeLeft <= 0}
              className="flex-1"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Verifying...
                </>
              ) : (
                'Verify Code'
              )}
            </Button>
          </div>
        </form>

        <div className="text-xs text-gray-500 text-center">
          Didn't receive the code? Check your messages or try resending.
        </div>
      </DialogContent>
    </Dialog>
  );
}