import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Users, TrendingUp, LogIn, LogOut } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL || '';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function CommunityRoomsPageV3() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [joinedRooms, setJoinedRooms] = useState(new Set());

  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/v3/rooms/list`, getAuthHeader());
      setRooms(response.data.rooms || []);
    } catch (error) {
      console.error('Odalar yüklenemedi:', error);
      toast.error('Odalar yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const handleJoin = async (roomId) => {
    try {
      await axios.post(`${API}/v3/rooms/${roomId}/join`, {}, getAuthHeader());
      setJoinedRooms(prev => new Set(prev).add(roomId));
      toast.success('Odaya katıldın');
      loadRooms();
    } catch (error) {
      toast.error('Odaya katılamadın');
    }
  };

  const handleLeave = async (roomId) => {
    try {
      await axios.post(`${API}/v3/rooms/${roomId}/leave`, {}, getAuthHeader());
      setJoinedRooms(prev => {
        const newSet = new Set(prev);
        newSet.delete(roomId);
        return newSet;
      });
      toast.success('Odadan çıktın');
      loadRooms();
    } catch (error) {
      toast.error('Odadan çıkılamadı');
    }
  };

  return (
    <div className="px-4 py-4 space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold gradient-text">Topluluk Odaları</h1>
        <Users className="w-6 h-6 text-purple-600" />
      </div>

      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Yükleniyor...</p>
        </div>
      ) : (
        <div className="space-y-3">
          {rooms.map((room) => (
            <Card key={room.id} className="glass border-none shadow-md hover-lift">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <CardTitle className="text-lg">{room.name}</CardTitle>
                      {room.is_trending && (
                        <Badge variant="default" className="bg-gradient-to-r from-orange-500 to-pink-500">
                          <TrendingUp className="w-3 h-3 mr-1" />
                          Popüler
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{room.description}</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <span className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      {room.member_count} üye
                    </span>
                    <Badge variant="outline">{room.category}</Badge>
                  </div>
                  
                  {joinedRooms.has(room.id) ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleLeave(room.id)}
                    >
                      <LogOut className="w-4 h-4 mr-1" />
                      Çık
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      className="gradient-bg"
                      onClick={() => handleJoin(room.id)}
                    >
                      <LogIn className="w-4 h-4 mr-1" />
                      Katıl
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
