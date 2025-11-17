import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Copy, Plus, Users as UsersIcon } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

export default function RoomPage({ onLogout }) {
  const { roomId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [mode, setMode] = useState('select'); // 'select', 'create', 'join', 'view'
  const [roomCode, setRoomCode] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [cssId, setCssId] = useState(location.state?.cssId || '');
  const [currentRoomId, setCurrentRoomId] = useState(roomId || '');
  const [collectiveCSS, setCollectiveCSS] = useState(null);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (roomId) {
      setMode('view');
      loadRoomData(roomId);
    }
  }, [roomId]);

  const loadRoomData = async (rId) => {
    setLoading(true);
    try {
      const [cssResponse, membersResponse] = await Promise.all([
        axios.get(`${API}/room/${rId}/collective-css`, getAuthHeader()),
        axios.get(`${API}/room/${rId}/members`, getAuthHeader())
      ]);
      setCollectiveCSS(cssResponse.data);
      setMembers(membersResponse.data.members);
    } catch (error) {
      toast.error('Oda verisi yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRoom = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/room/create`, {}, getAuthHeader());
      setRoomCode(response.data.room_code);
      setCurrentRoomId(response.data.id);
      setMode('create');
      toast.success('Oda oluşturuldu');
    } catch (error) {
      toast.error('Oda oluşturulamadı');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = async () => {
    if (!joinCode.trim()) {
      toast.error('Oda kodu girin');
      return;
    }
    if (!cssId) {
      toast.error('Lütfen önce bir CSS oluşturun');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API}/room/join`,
        { room_code: joinCode, css_id: cssId },
        getAuthHeader()
      );
      toast.success('Odaya katıldınız');
      navigate(`/room/${response.data.room_id}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Odaya katılınamadı');
    } finally {
      setLoading(false);
    }
  };

  const copyRoomCode = () => {
    navigator.clipboard.writeText(roomCode);
    toast.success('Oda kodu kopyalandı');
  };

  return (
    <div className="min-h-screen p-6">
      <header className="max-w-6xl mx-auto mb-8 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/')}
            data-testid="back-button"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Geri
          </Button>
          <h1 className="text-3xl font-bold gradient-text" data-testid="room-title">Senkronizasyon Odası</h1>
        </div>
      </header>

      <div className="max-w-4xl mx-auto">
        {mode === 'select' && (
          <Card className="glass border-none shadow-xl" data-testid="room-select-card">
            <CardHeader>
              <CardTitle>Kolektif CSS Oluştur</CardTitle>
              <CardDescription>
                Arkadaşlarınızla duygusal senkronizasyon odası oluşturun veya katılın.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                onClick={handleCreateRoom}
                disabled={loading}
                className="w-full bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600"
                data-testid="create-room-button"
              >
                <Plus className="w-4 h-4 mr-2" />
                Yeni Oda Oluştur
              </Button>
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-gray-500">veya</span>
                </div>
              </div>
              <div className="space-y-2">
                <Input
                  placeholder="Oda Kodu (örn: A1B2C3D4)"
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                  className="bg-white/50"
                  data-testid="join-room-code-input"
                />
                <Button
                  onClick={handleJoinRoom}
                  disabled={loading}
                  variant="outline"
                  className="w-full"
                  data-testid="join-room-button"
                >
                  Odaya Katıl
                </Button>
              </div>
              {!cssId && (
                <p className="text-sm text-amber-600 text-center">
                  Not: Odaya katılmak için önce bir CSS oluşturmalısınız.
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {mode === 'create' && (
          <Card className="glass border-none shadow-xl" data-testid="room-created-card">
            <CardHeader>
              <CardTitle>Oda Oluşturuldu</CardTitle>
              <CardDescription>
                Arkadaşlarınızla bu kodu paylaşın.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2">
                <Input
                  value={roomCode}
                  readOnly
                  className="bg-white/50 text-2xl font-bold text-center"
                  data-testid="room-code-display"
                />
                <Button
                  onClick={copyRoomCode}
                  variant="outline"
                  data-testid="copy-room-code-button"
                >
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
              <Button
                onClick={() => navigate(`/room/${currentRoomId}`)}
                className="w-full"
                data-testid="view-room-button"
              >
                Odayı Görüntüle
              </Button>
            </CardContent>
          </Card>
        )}

        {mode === 'view' && (
          <div className="space-y-6">
            {/* Collective CSS */}
            {collectiveCSS && (
              <Card className="glass border-none shadow-xl" data-testid="collective-css-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <UsersIcon className="w-5 h-5" />
                    Kolektif CSS
                  </CardTitle>
                  <CardDescription>
                    {collectiveCSS.member_count} kişinin duygusal senkronizasyonu
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="flex justify-center items-center p-8">
                      <div
                        className="css-orb w-48 h-48 light-glow"
                        style={{
                          backgroundColor: collectiveCSS.color,
                          opacity: collectiveCSS.light_frequency
                        }}
                        data-testid="collective-css-orb"
                      ></div>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Duygusal Etiket</p>
                        <p className="text-xl font-semibold" data-testid="collective-emotion-label">{collectiveCSS.emotion_label}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Açıklama</p>
                        <p className="text-sm" data-testid="collective-description">{collectiveCSS.description}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                        <div>
                          <p className="text-xs text-gray-500">Renk</p>
                          <p className="text-sm font-mono" data-testid="collective-color">{collectiveCSS.color}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Işık Frekansı</p>
                          <p className="text-sm" data-testid="collective-light-frequency">{(collectiveCSS.light_frequency * 100).toFixed(0)}%</p>
                        </div>
                        <div className="col-span-2">
                          <p className="text-xs text-gray-500">Ses Dokusu</p>
                          <p className="text-sm capitalize" data-testid="collective-sound-texture">{collectiveCSS.sound_texture}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Members */}
            <Card className="glass border-none shadow-xl" data-testid="room-members-card">
              <CardHeader>
                <CardTitle>Oda Üyeleri</CardTitle>
                <CardDescription>{members.length} katılımcı</CardDescription>
              </CardHeader>
              <CardContent>
                {members.length === 0 ? (
                  <p className="text-gray-500 text-center py-4" data-testid="no-members-text">Henüz kimse katılmadı.</p>
                ) : (
                  <div className="space-y-2">
                    {members.map((member, index) => (
                      <div
                        key={member.id}
                        className="flex items-center justify-between p-3 bg-white/30 rounded-lg"
                        data-testid={`member-item-${index}`}
                      >
                        <span className="text-sm" data-testid={`member-id-${index}`}>Anonim Katılımcı #{index + 1}</span>
                        <span className="text-xs text-gray-500" data-testid={`member-join-time-${index}`}>
                          {new Date(member.joined_at).toLocaleTimeString('tr-TR')}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}