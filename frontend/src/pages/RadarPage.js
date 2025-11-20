import React from 'react';
import { useTranslation } from 'react-i18next';
import { Radar } from 'lucide-react';
import VibeRadar from '@/components/VibeRadar';

export default function RadarPage() {
  const { t } = useTranslation();
  
  return (
    <div className="px-4 py-4">
      <div className="flex items-center gap-2 mb-4">
        <Radar className="w-5 h-5 text-purple-600" />
        <h2 className="text-lg font-semibold">{t('radar.title')}</h2>
      </div>
      
      <VibeRadar />
    </div>
  );
}
