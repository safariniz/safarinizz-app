import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Users, TrendingUp, LogIn, LogOut } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

const CATEGORIES = ['All', 'Focus', 'Chill', 'Overthinking', 'Students', 'Night Owls', 'Creators'];

export default function CommunityRoomsPageV3() {
  const [rooms, setRooms] = useState([]);
  const [trending, setTrending] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [joinedRooms, setJoinedRooms] = useState(new Set());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRooms();
    loadTrending();
  }, [selectedCategory]);

  const loadRooms = async () => {
    setLoading(true);
    try {
      const params = selectedCategory !== 'All' ? `?category=${selectedCategory}` : '';
      const response = await axios.get(`${API}/v3/rooms/list${params}`, getAuthHeader());
      setRooms(response.data.rooms || []);
    } catch (error) {
      toast.error('Failed to load rooms');
    } finally {
      setLoading(false);
    }
  };

  const loadTrending = async () => {
    try {
      const response = await axios.get(`${API}/v3/rooms/trending`, getAuthHeader());
      setTrending(response.data.rooms || []);
    } catch (error) {
      console.error('Failed to load trending');
    }
  };

  const joinRoom = async (roomId) => {
    try {
      await axios.post(`${API}/v3/rooms/${roomId}/join`, {}, getAuthHeader());
      setJoinedRooms(prev => new Set([...prev, roomId]));
      toast.success('Joined room');
      loadRooms();
    } catch (error) {
      toast.error('Failed to join room');
    }
  };

  const leaveRoom = async (roomId) => {
    try {
      await axios.post(`${API}/v3/rooms/${roomId}/leave`, {}, getAuthHeader());
      setJoinedRooms(prev => {
        const newSet = new Set(prev);
        newSet.delete(roomId);
        return newSet;
      });
      toast.success('Left room');
      loadRooms();
    } catch (error) {
      toast.error('Failed to leave room');
    }
  };

  return (
    <div className="px-4 py-4 space-y-4">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold mb-1">Community Rooms</h2>
        <p className="text-sm text-gray-600">Join vibe-based spaces</p>
      </div>

      {/* Trending */}
      {trending.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-orange-500" />
            <h3 className="font-semibold text-sm">Trending Now</h3>
          </div>
          <div className="flex gap-2 overflow-x-auto pb-2">
            {trending.map((room) => (
              <Card
                key={room.id}
                className="flex-shrink-0 w-48 glass border-none shadow-md"
              >
                <CardContent className="p-3">
                  <p className="font-semibold text-sm mb-1">{room.name}</p>
                  <p className="text-xs text-gray-600 mb-2">{room.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      <Users className="inline w-3 h-3 mr-1" />
                      {room.member_count}
                    </span>
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-6 text-xs px-2"
                      onClick={() => joinRoom(room.id)}
                    >
                      Join
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Category Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {CATEGORIES.map((cat) => (
          <Button
            key={cat}
            size="sm"
            variant={selectedCategory === cat ? 'default' : 'outline'}
            onClick={() => setSelectedCategory(cat)}
            className="flex-shrink-0"
          >
            {cat}
          </Button>
        ))}
      </div>

      {/* Room List */}
      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-600">Loading rooms...</p>
        </div>
      ) : rooms.length === 0 ? (
        <Card className="glass border-none shadow-lg">
          <CardContent className="p-8 text-center">
            <p className="text-gray-600">No rooms in this category</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {rooms.map((room) => (
            <Card key={room.id} className="glass border-none shadow-md">
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-semibold mb-1">{room.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">{room.description}</p>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded">
                        {room.category}
                      </span>
                      <span>
                        <Users className="inline w-3 h-3 mr-1" />
                        {room.member_count} members
                      </span>
                    </div>
                  </div>
                  {joinedRooms.has(room.id) ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => leaveRoom(room.id)}
                    >
                      <LogOut className="w-4 h-4 mr-1" />
                      Leave
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => joinRoom(room.id)}
                    >
                      <LogIn className="w-4 h-4 mr-1" />
                      Join
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