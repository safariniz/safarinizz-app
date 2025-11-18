import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { User, Edit, Crown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

const VIBE_IDENTITIES = [
  { id: 'Ember', label: '🔥 Ember', desc: 'Energetic' },
  { id: 'Mist', label: '🌫️ Mist', desc: 'Calm' },
  { id: 'Flux', label: '⚡ Flux', desc: 'Chaotic' },
  { id: 'Nova', label: '✨ Nova', desc: 'Inspired' },
  { id: 'Echo', label: '💫 Echo', desc: 'Empathic' },
  { id: 'Drift', label: '🌊 Drift', desc: 'Tired' },
  { id: 'Prism', label: '🌈 Prism', desc: 'Curious' }
];

export default function ProfilePageV3() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSetup, setShowSetup] = useState(false);
  const [selectedVibe, setSelectedVibe] = useState('Ember');
  const navigate = useNavigate();

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/v3/profile/me`, getAuthHeader());
      setProfile(response.data);
    } catch (error) {
      if (error.response?.status === 404) {
        setShowSetup(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const createProfile = async () => {
    try {
      await axios.post(
        `${API}/v3/profile/create`,
        { vibe_identity: selectedVibe },
        getAuthHeader()
      );
      toast.success('Profile created!');
      await loadProfile();
      setShowSetup(false);
    } catch (error) {
      toast.error('Failed to create profile');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Loading...</p>
      </div>
    );
  }

  if (showSetup) {
    return (
      <div className="px-4 py-8">
        <Card className="glass border-none shadow-xl max-w-md mx-auto">
          <CardContent className="p-6 space-y-6">
            <div className="text-center">
              <User className="w-16 h-16 mx-auto mb-4 text-purple-600" />
              <h2 className="text-2xl font-bold mb-2">Choose Your Vibe</h2>
              <p className="text-sm text-gray-600">Select your emotional identity</p>
            </div>
            
            <div className="space-y-2">
              {VIBE_IDENTITIES.map((vibe) => (
                <button
                  key={vibe.id}
                  onClick={() => setSelectedVibe(vibe.id)}
                  className={`w-full p-4 rounded-lg border-2 transition text-left ${
                    selectedVibe === vibe.id
                      ? 'border-purple-600 bg-purple-50'
                      : 'border-gray-200 hover:border-purple-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-lg font-semibold">{vibe.label}</span>
                      <p className="text-sm text-gray-600">{vibe.desc}</p>
                    </div>
                    {selectedVibe === vibe.id && (
                      <div className="w-6 h-6 rounded-full bg-purple-600 flex items-center justify-center">
                        <span className="text-white text-xs">✓</span>
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>

            <Button
              onClick={createProfile}
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600"
            >
              Create Profile
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="px-4 py-4 space-y-4">
      <Card className="glass border-none shadow-xl">
        <CardContent className="p-6">
          {/* Avatar */}
          <div className="flex justify-center mb-6">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-3xl font-bold">
              {profile?.handle?.substring(0, 2).toUpperCase()}
            </div>
          </div>

          {/* Handle */}
          <div className="text-center mb-4">
            <h2 className="text-2xl font-bold mb-1">@{profile?.handle}</h2>
            <p className="text-sm text-gray-600">
              {VIBE_IDENTITIES.find(v => v.id === profile?.vibe_identity)?.label || profile?.vibe_identity}
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <p className="text-2xl font-bold">{profile?.css_count || 0}</p>
              <p className="text-xs text-gray-600">CSS</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{profile?.followers_count || 0}</p>
              <p className="text-xs text-gray-600">Followers</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{profile?.following_count || 0}</p>
              <p className="text-xs text-gray-600">Following</p>
            </div>
          </div>

          {/* Bio */}
          {profile?.bio && (
            <div className="mb-4 p-3 bg-white/30 rounded-lg">
              <p className="text-sm">{profile.bio}</p>
            </div>
          )}

          {/* Actions */}
          <div className="space-y-2">
            <Button
              variant="outline"
              className="w-full"
              onClick={() => navigate('/edit-profile')}
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit Profile
            </Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => navigate('/avatar-evolution')}
            >
              Avatar Evolution
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}