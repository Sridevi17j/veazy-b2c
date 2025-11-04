'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import ChatMessage from './ChatMessage';
import TypingIndicator from './TypingIndicator';
import { BACKEND_URL } from '@/config/api';

interface Message {
  id: string;
  content: string;
  type: 'human' | 'ai';
  timestamp: Date;
}

interface ChatContext {
  country: string;
  purpose: string;
  date: string;
}

interface ChatInterfaceProps {
  isOpen: boolean;
  onClose: () => void;
  initialContext?: ChatContext | null;
}

export default function ChatInterface({ isOpen, onClose, initialContext }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [isUserDropdownOpen, setIsUserDropdownOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const { user, logout, getAuthHeaders } = useAuth();
  const router = useRouter();

  // Create thread when chat opens
  useEffect(() => {
    if (isOpen && !threadId) {
      createThread();
    }
  }, [isOpen, threadId]);

  const createThread = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/threads`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Failed to create thread');
      }

      const data = await response.json();
      setThreadId(data.thread_id);
      setConnectionError(null);
    } catch (error) {
      console.error('Error creating thread:', error);
      setConnectionError('Failed to connect to Visa Genie. Please try again.');
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !threadId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      type: 'human',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await fetch(`${BACKEND_URL}/threads/${threadId}/runs/stream`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          input: {
            messages: [{ content: messageToSend }]
          }
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      // Generate unique ID for this conversation turn
      const conversationTurnId = `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

      if (reader) {
        let currentAiMessage: Message | null = null;
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'ai' && data.content) {
                  if (!currentAiMessage) {
                    // Start new AI message with unique conversation turn ID
                    currentAiMessage = {
                      id: conversationTurnId,
                      type: 'ai',
                      content: data.content,
                      timestamp: new Date()
                    };
                    setMessages(prev => [...prev, currentAiMessage!]);
                  } else {
                    // Update existing AI message - concatenate new content like working version
                    currentAiMessage.content += data.content;
                    setMessages(prev => prev.map(msg => 
                      msg.id === currentAiMessage!.id 
                        ? { ...msg, content: currentAiMessage!.content }
                        : msg
                    ));
                  }
                }
              } catch (parseError) {
                console.warn('Failed to parse streaming data:', line);
              }
            }
          }
        }
      }

      setIsTyping(false);

    } catch (error) {
      console.error('Error sending message:', error);
      setIsTyping(false);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I'm having trouble connecting right now. Please try again in a moment.",
        type: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // File upload functionality
  const handleAttachmentClick = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/jpeg,image/png,image/jpg,application/pdf';
    input.multiple = false;
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        handleFileUpload(file);
      }
    };
    input.click();
  };

  const handleFileUpload = async (file: File) => {
    if (!threadId) {
      alert('Please wait for the chat to initialize before uploading files.');
      return;
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      alert('Please upload only JPEG, PNG, or PDF files.');
      return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      alert('File size must be less than 10MB.');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Determine document type based on file name or prompt user
      const documentType = await determineDocumentType(file.name);
      
      // Create FormData for upload
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);
      formData.append('thread_id', threadId);

      // Upload file
      const uploadResponse = await fetch(`${BACKEND_URL}/api/upload-document`, {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('File upload failed');
      }

      const uploadResult = await uploadResponse.json();
      setUploadProgress(100);

      // Add upload confirmation message to chat
      const uploadMessage: Message = {
        id: Date.now().toString(),
        content: `📎 Uploaded: ${file.name} (${documentType})`,
        type: 'human',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, uploadMessage]);

      // Notify agent about successful upload
      setTimeout(async () => {
        setIsUploading(false);
        setUploadProgress(0);
        
        // Send message to agent about document upload
        const notificationMessage = `I have uploaded my passport bio page`;
        
        // Create the user message for the notification
        const userMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: notificationMessage,
          type: 'human',
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, userMessage]);
        setIsTyping(true);

        try {
          const response = await fetch(`${BACKEND_URL}/threads/${threadId}/runs/stream`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
              input: {
                messages: [{ content: notificationMessage }]
              }
            }),
          });

          if (!response.ok) {
            throw new Error('Failed to send message');
          }

          const reader = response.body?.getReader();
          const decoder = new TextDecoder();
          
          // Generate unique ID for this conversation turn
          const conversationTurnId = `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

          if (reader) {
            let currentAiMessage: Message | null = null;
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              const chunk = decoder.decode(value);
              const lines = chunk.split('\n');

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  try {
                    const data = JSON.parse(line.slice(6));
                    
                    if (data.type === 'ai' && data.content) {
                      if (!currentAiMessage) {
                        // Start new AI message with unique conversation turn ID
                        currentAiMessage = {
                          id: conversationTurnId,
                          type: 'ai',
                          content: data.content,
                          timestamp: new Date()
                        };
                        setMessages(prev => [...prev, currentAiMessage!]);
                      } else {
                        // Update existing AI message - concatenate new content
                        currentAiMessage.content += data.content;
                        setMessages(prev => prev.map(msg => 
                          msg.id === currentAiMessage!.id 
                            ? { ...msg, content: currentAiMessage!.content }
                            : msg
                        ));
                      }
                    }
                  } catch (parseError) {
                    console.warn('Failed to parse streaming data:', line);
                  }
                }
              }
            }
          }

          setIsTyping(false);

        } catch (error) {
          console.error('Error sending notification:', error);
          setIsTyping(false);
          
          const errorMessage: Message = {
            id: (Date.now() + 2).toString(),
            content: "I received your document but had trouble processing it. Let me try again.",
            type: 'ai',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, errorMessage]);
        }
      }, 500);

    } catch (error) {
      console.error('File upload error:', error);
      setIsUploading(false);
      setUploadProgress(0);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: "❌ File upload failed. Please try again.",
        type: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const determineDocumentType = async (filename: string): Promise<string> => {
    const lowerName = filename.toLowerCase();
    
    // Auto-detect based on filename
    if (lowerName.includes('passport') && lowerName.includes('bio')) {
      return 'passport_bio_page';
    }
    if (lowerName.includes('passport') && lowerName.includes('photo')) {
      return 'passport_photo';
    }
    if (lowerName.includes('passport')) {
      return 'passport_bio_page'; // Default to bio page
    }
    if (lowerName.includes('photo') || lowerName.includes('pic')) {
      return 'passport_photo';
    }
    
    // Default to passport bio page for happy path (no popup)
    return 'passport_bio_page';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50">
      <div className="bg-white w-full h-full flex shadow-2xl">
        {/* Sidebar */}
        <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col mobile-hidden">
          {/* Logo */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-purple-600 rounded flex items-center justify-center">
                <span className="text-white font-bold text-sm">V</span>
              </div>
              <span className="font-semibold text-gray-900">Veazy Logo</span>
            </div>
          </div>

          {/* Navigation */}
          <div className="p-4 space-y-2">
            <button className="w-full flex items-center space-x-3 p-3 rounded-lg bg-white border border-gray-200 hover:bg-gray-50 transition-colors">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="text-sm font-medium text-gray-700">New Trip</span>
            </button>
            
            <button className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-100 transition-colors">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span className="text-sm font-medium text-gray-700">Search</span>
            </button>

            <button className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-100 transition-colors">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="text-sm font-medium text-gray-700">Doc Library</span>
            </button>
          </div>

          {/* Trip History */}
          <div className="flex-1 p-4">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">Trips</h3>
            <div className="space-y-2">
              <button className="w-full text-left p-3 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="text-sm font-medium text-gray-900">Fastest visa</div>
              </button>
              <button className="w-full text-left p-3 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="text-sm font-medium text-gray-900">Thailand Visa</div>
              </button>
            </div>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button 
                onClick={onClose}
                className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              <div className="bg-purple-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                Visa Genie
              </div>
            </div>
            <div className="flex items-center space-x-4 mobile-hidden">
              {/* User Profile Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setIsUserDropdownOpen(!isUserDropdownOpen)}
                  className="flex items-center space-x-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <svg className={`w-4 h-4 transition-transform ${isUserDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Dropdown Menu */}
                {isUserDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                    <div className="py-1">
                      <button
                        onClick={() => {
                          router.push('/account/profile');
                          setIsUserDropdownOpen(false);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        <span>My Account</span>
                      </button>
                      <button
                        onClick={async () => {
                          await logout();
                          router.push('/');
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        <span>Logout</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {connectionError ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Connection Error</h3>
                <p className="text-gray-600 max-w-md mb-4">{connectionError}</p>
                <button 
                  onClick={createThread}
                  className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            ) : !threadId ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Connecting to Visa Genie...</h3>
                <p className="text-gray-600 max-w-md">
                  Setting up your personalized visa assistance session.
                </p>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Welcome to Visa Genie!</h3>
                <p className="text-gray-600 max-w-md">
                  I&apos;m here to help you with all your visa requirements. Ask me about destinations, 
                  document requirements, processing times, or anything else related to travel visas.
                </p>
                <div className="mt-4 flex items-center text-sm text-green-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  Connected and ready to help!
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))
            )}
            
            {isTyping && <TypingIndicator />}
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center space-x-3">
              <button 
                onClick={handleAttachmentClick}
                disabled={isUploading}
                className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Upload passport or document"
              >
                {isUploading ? (
                  <div className="w-5 h-5 border-2 border-gray-400 border-t-purple-600 rounded-full animate-spin"></div>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                )}
              </button>
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask Visa Genie anything about your next travel"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim()}
                className="p-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}