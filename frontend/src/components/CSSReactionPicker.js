import React from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getAuthHeader() {
  const token = localStorage.getItem('cogito_token');
  return { headers: { Authorization: `Bearer ${token}` } };
}

const reactions = [
  { type: 'wave', label: '🌊 Dalga', color: '#4299E1' },
  { type: 'pulse', label: '💓 Nabız', color: '#ED64A6' },
  { type: 'spiral', label: '🌀 Spiral', color: '#9F7AEA' },
  { type: 'color-shift', label: '🌈 Renk Kayması', color: '#F6AD55' }
];

export default function CSSReactionPicker({ cssId, onReact }) {
  const handleReaction = async (reactionType) => {
    try {
      await axios.post(
        `${API}/css/${cssId}/react?reaction_type=${reactionType}`,
        {},
        getAuthHeader()
      );
      toast.success('Reaksiyon eklendi');
      if (onReact) onReact();
    } catch (error) {
      toast.error('Reaksiyon eklenemedi');
    }
  };

  return (
    <div className="flex gap-2 flex-wrap" data-testid="css-reaction-picker">
      {reactions.map((reaction) => (
        <Button
          key={reaction.type}
          size="sm"
          variant="outline"
          onClick={() => handleReaction(reaction.type)}
          style={{ borderColor: reaction.color }}
          data-testid={`reaction-${reaction.type}-button`}
        >
          {reaction.label}
        </Button>
      ))}
    </div>
  );
}