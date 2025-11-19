import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { MessageCircle, Send } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL || '';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function CoachChatPageV3() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    startSession();
  }, []);

  const startSession = async () => {
    try {
      const response = await axios.post(`${API}/v3/coach/start-session`, {}, getAuthHeader());
      setSessionId(response.data.session_id);
      setMessages([{
        role: 'assistant',
        content: 'Merhaba, ben senin bilişsel koçunum. Bugün sana nasıl destek olabilirim?'
      }]);
    } catch (error) {
      toast.error('Koç oturumu başlatılamadı');
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(
        `${API}/v3/coach/message`,
        { session_id: sessionId, message: input },
        getAuthHeader()
      );
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.reply
      }]);
    } catch (error) {
      toast.error('Mesaj gönderilemedi');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-128px)] px-4 py-4">
      <div className="flex items-center gap-2 mb-4">
        <MessageCircle className="w-6 h-6 text-purple-600" />
        <h1 className="text-2xl font-bold gradient-text">Bilişsel Koç</h1>
      </div>

      <Card className="flex-1 glass border-none shadow-lg mb-4 overflow-hidden">
        <CardContent className="p-4 h-full overflow-y-auto space-y-3">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] p-3 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
                    : 'glass-strong text-gray-800 dark:text-gray-200'
                }`}
              >
                <p className="text-sm">{msg.content}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="glass-strong p-3 rounded-lg">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Mesajını yaz..."
          className="glass-strong"
          disabled={loading}
        />
        <Button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="gradient-bg"
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
