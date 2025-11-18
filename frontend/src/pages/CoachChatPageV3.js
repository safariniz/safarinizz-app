import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function CoachChatPageV3() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    startSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startSession = async () => {
    try {
      const response = await axios.post(
        `${API}/v3/coach/start-session`,
        {},
        getAuthHeader()
      );
      setSessionId(response.data.session_id);
      // Welcome message
      setMessages([{
        role: 'assistant',
        content: "Hi! I'm your AI coach. I'm here to help you understand your emotional patterns. How are you feeling today?"
      }]);
    } catch (error) {
      toast.error('Failed to start coach session');
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return;

    const userMessage = input;
    setInput('');
    
    // Add user message immediately
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(
        `${API}/v3/coach/message`,
        {
          session_id: sessionId,
          message: userMessage
        },
        getAuthHeader()
      );
      
      // Add assistant reply
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.reply
      }]);
    } catch (error) {
      toast.error('Failed to send message');
      // Remove user message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full" style={{ height: 'calc(100vh - 8rem)' }}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600" />
          <h2 className="text-lg font-semibold">AI Coach</h2>
        </div>
        <p className="text-xs text-gray-600">Empathetic cognitive guidance</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-2xl ${
                msg.role === 'user'
                  ? 'bg-purple-600 text-white rounded-br-none'
                  : 'glass border border-gray-200 rounded-bl-none'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="glass border border-gray-200 p-3 rounded-2xl rounded-bl-none">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3 border-t border-gray-200 bg-white">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything..."
            className="flex-1"
            disabled={loading}
          />
          <Button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-purple-600"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}