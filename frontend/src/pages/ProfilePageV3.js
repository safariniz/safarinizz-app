import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { User, Edit, Save, Sparkles, Users, Heart } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL || '';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function ProfilePageV3() {
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [bio, setBio] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await axios.get(`${API}/v3/profile/me`, getAuthHeader());
      setProfile(response.data);
      setBio(response.data.bio || '');
    } catch (error) {
      console.error('Profil yüklenemedi:', error);
      toast.error('Profil yüklenemedi');
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/v3/profile/update`, { bio }, getAuthHeader());
      toast.success('Profil güncellendi');
      setEditing(false);
      loadProfile();
    } catch (error) {
      toast.error('Profil güncellenemedi');
    } finally {
      setLoading(false);
    }
  };

  if (!profile) {
    return (
      <div className="px-4 py-4">
        <div className="text-center py-8">
          <p className="text-gray-500">Yükleniyor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-4 space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold gradient-text">Profilim</h1>
        <User className="w-6 h-6 text-purple-600" />
      </div>

      {/* Profile Header Card */}
      <Card className="glass border-none shadow-xl">
        <CardContent className="p-6">
          <div className="flex flex-col items-center text-center mb-6">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center mb-4">
              <User className="w-12 h-12 text-white" />
            </div>
            <h2 className="text-2xl font-bold gradient-text">{profile.handle}</h2>
            <Badge className="mt-2 bg-gradient-to-r from-purple-500 to-pink-500">
              {profile.vibe_identity}
            </Badge>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 text-purple-600 mb-1">
                <Sparkles className="w-4 h-4" />
                <span className="text-2xl font-bold">{profile.css_count || 0}</span>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400">CSS</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 text-blue-600 mb-1">
                <Users className="w-4 h-4" />
                <span className="text-2xl font-bold">{profile.followers_count || 0}</span>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400">Takipçi</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 text-pink-600 mb-1">
                <Heart className="w-4 h-4" />
                <span className="text-2xl font-bold">{profile.following_count || 0}</span>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400">Takip</p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-sm text-gray-700 dark:text-gray-300">Hakkımda</h3>
              {!editing && (
                <Button size="sm" variant="ghost" onClick={() => setEditing(true)}>
                  <Edit className="w-4 h-4" />
                </Button>
              )}
            </div>

            {editing ? (
              <div className="space-y-2">
                <Textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Kendini kısaca anlat..."
                  className="glass-strong min-h-24"
                />
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    className="gradient-bg flex-1"
                    onClick={handleSave}
                    disabled={loading}
                  >
                    <Save className="w-4 h-4 mr-1" />
                    Kaydet
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setEditing(false);
                      setBio(profile.bio || '');
                    }}
                  >
                    İptal
                  </Button>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-600 dark:text-gray-400 glass-strong p-3 rounded-lg">
                {profile.bio || 'Henüz bir şey yazmışsın...'}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Stats Card */}
      <Card className="glass border-none shadow-lg">
        <CardContent className="p-4">
          <h3 className="font-semibold mb-3">Aktivite</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Üyelik:</span>
              <span className="font-medium">
                {new Date(profile.created_at).toLocaleDateString('tr-TR')}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Vibe Kimliği:</span>
              <Badge variant="outline">{profile.vibe_identity}</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
