'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import dynamic from 'next/dynamic';

const ChatInterface = dynamic(() => import('@/components/ChatInterface'), {
  ssr: false,
  loading: () => <div className="animate-pulse">Loading chat...</div>
});

interface ChatContext {
  country: string;
  purpose: string;
  date: string;
}

export default function VisaAssistantChatPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const [chatContext, setChatContext] = useState<ChatContext | null>(null);

  // Parse URL parameters to get chat context
  useEffect(() => {
    if (params.params && Array.isArray(params.params)) {
      const [countrySlug, purposeSlug, dateSlug] = params.params;
      
      if (countrySlug && purposeSlug && dateSlug) {
        // Convert URL slugs back to readable format
        const country = countrySlug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const purpose = purposeSlug.replace(/-visa$/, '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const date = dateSlug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        setChatContext({ country, purpose, date });
      }
    }
  }, [params]);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen">
      <ChatInterface 
        isOpen={true} 
        onClose={() => router.push('/visa-assistant')}
        initialContext={chatContext}
      />
    </div>
  );
}