import React from 'react';
import { useTranslation } from 'react-i18next';
import { TrendingUp } from 'lucide-react';
import MoodTimeline from '@/components/MoodTimeline';
import AICoachPanel from '@/components/AICoachPanel';
import MoodForecast from '@/components/MoodForecast';

export default function InsightsPage({ isPremium }) {
  const { t } = useTranslation();
  
  return (
    <div className="px-4 py-4 space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <TrendingUp className="w-5 h-5 text-purple-600" />
        <h2 className="text-lg font-semibold">{t('insights.title')}</h2>
      </div>
      
      <MoodTimeline />
      <AICoachPanel isPremium={isPremium} />
      <MoodForecast isPremium={isPremium} />
    </div>
  );
}
