import React from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function LanguageSwitcher({ variant = 'default' }) {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'tr' ? 'en' : 'tr';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
  };

  return (
    <Button
      onClick={toggleLanguage}
      variant={variant}
      size="sm"
      className="flex items-center gap-2"
    >
      <Globe className="w-4 h-4" />
      <span className="text-xs font-medium">
        {i18n.language === 'tr' ? 'EN' : 'TR'}
      </span>
    </Button>
  );
}
