import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, Globe } from 'lucide-react';
import { toast } from 'sonner';
import CSSReactionPicker from '@/components/CSSReactionPicker';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function FeedPageV3() {
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(false);
  const [feedType, setFeedType] = useState('personalized'); // or 'global'

  useEffect(() => {
    loadFeed();
  }, [feedType]);

  const loadFeed = async () => {
    setLoading(true);
    try {
      const endpoint = feedType === 'personalized'
        ? `${API}/v3/social/feed`
        : `${API}/v3/social/global-feed`;
      
      const response = await axios.get(endpoint, getAuthHeader());
      setFeed(response.data.feed || []);
    } catch (error) {
      toast.error('Failed to load feed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-4">
      {/* Feed Type Toggle */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex gap-2">
          <Button
            size="sm"
            variant={feedType === 'personalized' ? 'default' : 'outline'}
            onClick={() => setFeedType('personalized')}
          >
            Following
          </Button>
          <Button
            size="sm"
            variant={feedType === 'global' ? 'default' : 'outline'}
            onClick={() => setFeedType('global')}
          >
            <Globe className="w-4 h-4 mr-1" />
            Global
          </Button>
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={loadFeed}
          disabled={loading}
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      {/* Feed Items */}
      {loading && feed.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading feed...</p>
        </div>
      ) : feed.length === 0 ? (
        <Card className="glass border-none shadow-lg">
          <CardContent className="p-8 text-center">
            <p className="text-gray-600 mb-4">
              {feedType === 'personalized'
                ? 'Follow some users to see their CSS updates here'
                : 'No activity yet'}
            </p>
            {feedType === 'personalized' && (
              <Button onClick={() => setFeedType('global')}>
                Explore Global Feed
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {feed.map((item, i) => (
            <Card
              key={i}
              className="glass border-none shadow-md"
              style={{ backgroundColor: item.color + '15' }}
            >
              <CardContent className="p-4">
                {/* Profile Header */}
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm"
                    style={{ backgroundColor: item.color }}
                  >
                    {item.profile?.handle?.substring(0, 2).toUpperCase() || '??'}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-sm">
                      @{item.profile?.handle || 'anonymous'}
                    </p>
                    <p className="text-xs text-gray-600">
                      {item.profile?.vibe_identity || 'Unknown'}
                    </p>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(item.timestamp).toLocaleDateString('tr-TR')}
                  </span>
                </div>

                {/* CSS Content */}
                <div className="mb-3">
                  <div
                    className="w-16 h-16 rounded-lg mb-2 light-glow mx-auto"
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <p className="font-semibold text-center mb-1">
                    {item.emotion_label}
                  </p>
                  <p className="text-sm text-gray-700 text-center">
                    {item.description}
                  </p>
                </div>

                {/* Reactions */}
                <div className="pt-3 border-t">
                  <CSSReactionPicker cssId={item.id} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}