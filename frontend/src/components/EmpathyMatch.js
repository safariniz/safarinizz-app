import React, { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Heart } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function EmpathyMatch() {
  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(false);

  const findMatch = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/empathy/find-match`, getAuthHeader());
      setMatch(response.data.match);
      toast.success(response.data.message);
    } catch (error) {
      if (error.response?.status === 400) {
        toast.error('En az 5 CSS snapshotı gerekli');
      } else {
        toast.error('Eşleşme bulunamadı');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="glass border-none shadow-xl" data-testid="empathy-match-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Heart className="w-5 h-5" />
          Empati Eşleşmesi
        </CardTitle>
      </CardHeader>
      <CardContent>
        {!match ? (
          <div className="text-center py-8">
            <Heart className="w-12 h-12 mx-auto mb-4 text-pink-400" />
            <p className="text-sm text-gray-600 mb-4">
              Benzer vibe'a sahip biriyle anonim eşleş
            </p>
            <Button
              onClick={findMatch}
              disabled={loading}
              data-testid="find-match-button"
            >
              {loading ? 'Aranıyor...' : 'Eşleşme Bul'}
            </Button>
          </div>
        ) : (
          <div className="text-center py-8">
            <div
              className="w-24 h-24 mx-auto mb-4 rounded-full flex items-center justify-center"
              style={{
                background: `conic-gradient(#667eea ${match.compatibility_score * 100}%, #e0e0e0 0)`
              }}
              data-testid="compatibility-circle"
            >
              <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-purple-600">
                  {(match.compatibility_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>
            <p className="text-lg font-semibold mb-2">Vibe Eşleşmesi!</p>
            <p className="text-xs text-gray-500">
              {new Date(match.matched_at).toLocaleString('tr-TR')}
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={findMatch}
              className="mt-4"
            >
              Yeni Eşleşme Bul
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}