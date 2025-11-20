import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import tr from './tr.json';
import en from './en.json';

const resources = {
  tr: { translation: tr },
  en: { translation: en }
};

// Get saved language or default to Turkish
const savedLanguage = localStorage.getItem('cogitoLanguage') || 'tr';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: savedLanguage,
    fallbackLng: 'tr',
    interpolation: {
      escapeValue: false
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'cogitoLanguage'
    }
  });

export default i18n;
