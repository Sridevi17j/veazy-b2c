'use client';

import { User, Bot } from 'lucide-react';

interface Message {
  id: string;
  type: 'human' | 'ai';
  content: string;
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.type === 'human';
  
  return (
    <div className={`flex gap-4 mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-purple-600 to-purple-800 rounded-full flex items-center justify-center shadow-lg">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}
      
      <div className={`max-w-[75%] px-6 py-4 rounded-2xl shadow-sm ${
        isUser 
          ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white' 
          : 'bg-white border border-gray-200 text-gray-900'
      }`}>
        <div className="text-base leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>
        {message.timestamp && (
          <div className={`text-xs mt-3 font-medium ${
            isUser ? 'text-purple-100' : 'text-gray-400'
          }`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        )}
      </div>
      
      {isUser && (
        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-gray-600 to-gray-700 rounded-full flex items-center justify-center shadow-lg">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
}