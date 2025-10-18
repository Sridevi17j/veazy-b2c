'use client';

import { useState } from 'react';
import PhoneNumberModal from './PhoneNumberModal';
import OTPVerificationModal from './OTPVerificationModal';
import AccountSetupModal from './AccountSetupModal';
import PreferenceModal from './PreferenceModal';
import { useAuth } from '@/contexts/AuthContext';

type AuthStep = 'phone' | 'otp' | 'account' | 'preference' | 'closed';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface UserData {
  countryCode: string;
  localPhone: string;
  otpCode: string;
  firstName: string;
  lastName: string;
  email: string;
  preferredName?: string;
}

export default function AuthModal({ isOpen, onClose, onSuccess }: AuthModalProps) {
  const [step, setStep] = useState<AuthStep>('phone');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [userData, setUserData] = useState<Partial<UserData>>({});

  const { login } = useAuth();

  // Step 1: Send OTP
  const handleSendOTP = async (countryCode: string, localPhone: string) => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/send-otp', {
      // const response = await fetch('https://veazy-backend.onrender.com/api/auth/send-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          country_code: countryCode,
          local_phone: localPhone,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setUserData({ countryCode, localPhone });
        setStep('otp');
      } else {
        setError(data.detail || 'Failed to send OTP. Please try again.');
      }
    } catch (error) {
      console.error('Send OTP error:', error);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: Verify OTP with Twilio
  const handleVerifyOTP = async (otpCode: string) => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/verify-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          country_code: userData.countryCode,
          local_phone: userData.localPhone,
          otp_code: otpCode
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // OTP verified successfully, proceed to account setup
          setUserData(prev => ({ ...prev, otpCode }));
          setStep('account');
        } else {
          setError(data.message || 'OTP verification failed');
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Invalid OTP code. Please try again.');
      }
    } catch (error) {
      console.error('OTP verification error:', error);
      setError('Verification failed. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 3: Collect account info
  const handleAccountSetup = (firstName: string, lastName: string, email: string) => {
    setUserData(prev => ({ ...prev, firstName, lastName, email }));
    setStep('preference');
  };

  // Step 4: Complete registration with all data
  const handleCompleteRegistration = async (preferredName?: string) => {
    setIsLoading(true);
    setError('');

    try {
      const completeUserData = { ...userData, preferredName };
      
      const response = await fetch('http://localhost:8000/api/auth/complete-registration', {
      // const response = await fetch('https://veazy-backend.onrender.com/api/auth/complete-registration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          country_code: completeUserData.countryCode,
          local_phone: completeUserData.localPhone,
          otp_code: completeUserData.otpCode,
          first_name: completeUserData.firstName,
          last_name: completeUserData.lastName,
          email: completeUserData.email,
          preferred_name: completeUserData.preferredName,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Update auth context
        login({
          id: data.user_id,
          phone_number: data.phone_number,
        });
        
        // Close modal and trigger success callback
        handleClose();
        onSuccess();
      } else {
        setError(data.detail || 'Registration failed. Please try again.');
      }
    } catch (error) {
      console.error('Complete registration error:', error);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOTP = async () => {
    if (userData.countryCode && userData.localPhone) {
      await handleSendOTP(userData.countryCode, userData.localPhone);
    }
  };

  const handleClose = () => {
    setStep('phone');
    setError('');
    setUserData({});
    onClose();
  };

  return (
    <>
      {/* Step 1: Phone Number */}
      <PhoneNumberModal
        isOpen={isOpen && step === 'phone'}
        onClose={handleClose}
        onSubmit={handleSendOTP}
        isLoading={isLoading}
      />
      
      {/* Step 2: OTP Verification */}
      <OTPVerificationModal
        isOpen={isOpen && step === 'otp'}
        onClose={handleClose}
        onVerify={handleVerifyOTP}
        onBack={() => setStep('phone')}
        onResend={handleResendOTP}
        phoneNumber={`${userData.countryCode} ${userData.localPhone}`}
        countryCode={userData.countryCode || ''}
        localPhone={userData.localPhone || ''}
        isLoading={isLoading}
        canResend={true}
      />

      {/* Step 3: Account Setup */}
      <AccountSetupModal
        isOpen={isOpen && step === 'account'}
        onClose={handleClose}
        onSubmit={handleAccountSetup}
        isLoading={isLoading}
      />

      {/* Step 4: Preference (Optional) */}
      <PreferenceModal
        isOpen={isOpen && step === 'preference'}
        onClose={handleClose}
        onSubmit={handleCompleteRegistration}
        onSkip={() => handleCompleteRegistration()}
        isLoading={isLoading}
        userFirstName={userData.firstName}
      />
    </>
  );
}