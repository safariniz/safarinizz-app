import React from 'react';
import { Heart } from 'lucide-react';
import EmpathyMatch from '@/components/EmpathyMatch';

export default function MatchPage() {
  return (
    <div className="px-4 py-4">
      <div className="flex items-center gap-2 mb-4">
        <Heart className="w-5 h-5 text-purple-600" />
        <h2 className="text-lg font-semibold">Empati Eşleşmesi</h2>
      </div>
      
      <EmpathyMatch />
    </div>
  );
}