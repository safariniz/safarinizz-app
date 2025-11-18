import React from 'react';
import { Radar } from 'lucide-react';
import VibeRadar from '@/components/VibeRadar';

export default function RadarPage() {
  return (
    <div className="px-4 py-4">
      <div className="flex items-center gap-2 mb-4">
        <Radar className="w-5 h-5 text-purple-600" />
        <h2 className="text-lg font-semibold">Vibe Radar</h2>
      </div>
      
      <VibeRadar />
    </div>
  );
}