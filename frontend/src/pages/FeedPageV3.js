import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Heart, Users, TrendingUp } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL || '';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function FeedPageV3() {
  const { t } = useTranslation();
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('global');

  useEffect(() => {
    loadFeed();
  }, [activeTab]);

  const loadFeed = async () => {
    setLoading(true);
    try {
      const endpoint = activeTab === 'global' ? '/v3/social/global-feed' : '/v3/social/feed';
      const response = await axios.get(`${API}${endpoint}`, getAuthHeader());
      setFeed(response.data.feed || []);
    } catch (error) {
      console.error('Feed yüklenemedi:', error);
      toast.error(t('feed.loadError'));
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async (userId) => {
    try {
      await axios.post(`${API}/v3/social/follow/${userId}`, {}, getAuthHeader());
      toast.success(t('feed.followSuccess'));
      loadFeed();
    } catch (error) {
      toast.error(t('feed.followError'));
    }
  };

  return (
    <div className="px-4 py-4 space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold gradient-text">{t('feed.title')}</h1>
        <TrendingUp className="w-6 h-6 text-purple-600" />
      </div>

      <div className="flex gap-2 mb-4">
        <Button
          variant={activeTab === 'global' ? 'default' : 'outline'}
          onClick={() => setActiveTab('global')}
          className="flex-1"
        >
          <Users className="w-4 h-4 mr-2" />
          {t('feed.global')}
        </Button>
        <Button
          variant={activeTab === 'personal' ? 'default' : 'outline'}
          onClick={() => setActiveTab('personal')}
          className="flex-1"
        >
          <Heart className="w-4 h-4 mr-2" />
          {t('feed.following')}
        </Button>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-500">{t('common.loading')}</p>
        </div>
      ) : feed.length === 0 ? (
        <Card className="glass border-none">
          <CardContent className="p-8 text-center">
            <p className="text-gray-500">
              {activeTab === 'global' ? t('feed.noPostsGlobal') : t('feed.noPostsFollowing')}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {feed.map((item) => (
            <Card key={item.id} className="glass border-none shadow-md hover-lift">
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-10 h-10 rounded-full"
                      style={{ backgroundColor: item.color || '#8B9DC3' }}
                    />
                    <div>
                      <p className="font-medium text-sm">{item.profile?.handle || '@anonim'}</p>
                      <p className="text-xs text-gray-500">{item.profile?.vibe_identity}</p>
                    </div>
                  </div>
                  {item.profile && !item.is_following && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleFollow(item.profile.user_id)}
                    >
                      {t('feed.followButton')}
                    </Button>
                  )}
                </div>

                <p className="text-lg font-semibold mb-1">{item.emotion_label}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{item.description}</p>

                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>{new Date(item.timestamp).toLocaleDateString('tr-TR')}</span>
                  <span>{t('feed.lightLevel')}: {(item.light_frequency * 100).toFixed(0)}%</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
