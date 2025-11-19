import React from 'react';

export default function Logo({ size = 'md', showText = true, className = '' }) {
  const sizes = {
    sm: { container: 'w-8 h-8', text: 'text-sm' },
    md: { container: 'w-10 h-10', text: 'text-base' },
    lg: { container: 'w-16 h-16', text: 'text-2xl' },
    xl: { container: 'w-24 h-24', text: 'text-4xl' }
  };

  const { container, text } = sizes[size];

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Icon: Overlapping circles representing cognitive sync */}
      <div className={`relative ${container}`}>
        <svg
          viewBox="0 0 100 100"
          className="w-full h-full"
          style={{
            filter: 'drop-shadow(0 2px 8px rgba(99, 102, 241, 0.3))'
          }}
        >
          {/* Gradient Definitions */}
          <defs>
            <linearGradient id="cogito-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style={{ stopColor: '#7C3AED', stopOpacity: 1 }} />
              <stop offset="50%" style={{ stopColor: '#4F46E5', stopOpacity: 1 }} />
              <stop offset="100%" style={{ stopColor: '#06B6D4', stopOpacity: 1 }} />
            </linearGradient>
            
            <linearGradient id="cogito-gradient-light" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style={{ stopColor: '#A78BFA', stopOpacity: 0.6 }} />
              <stop offset="100%" style={{ stopColor: '#22D3EE', stopOpacity: 0.6 }} />
            </linearGradient>
          </defs>
          
          {/* Background circles - representing mind waves */}
          <circle
            cx="35"
            cy="50"
            r="28"
            fill="url(#cogito-gradient-light)"
            className="animate-pulse"
            style={{ animationDuration: '3s' }}
          />
          <circle
            cx="65"
            cy="50"
            r="28"
            fill="url(#cogito-gradient-light)"
            className="animate-pulse"
            style={{ animationDuration: '3s', animationDelay: '0.5s' }}
          />
          
          {/* Foreground circles - main logo */}
          <circle
            cx="35"
            cy="50"
            r="20"
            fill="none"
            stroke="url(#cogito-gradient)"
            strokeWidth="4"
          />
          <circle
            cx="65"
            cy="50"
            r="20"
            fill="none"
            stroke="url(#cogito-gradient)"
            strokeWidth="4"
          />
          
          {/* Intersection highlight - the "sync" moment */}
          <circle
            cx="50"
            cy="50"
            r="8"
            fill="url(#cogito-gradient)"
            className="animate-ping"
            style={{ animationDuration: '2s' }}
          />
          <circle
            cx="50"
            cy="50"
            r="6"
            fill="white"
          />
        </svg>
      </div>

      {/* Wordmark */}
      {showText && (
        <div className="flex flex-col leading-none">
          <span 
            className={`font-bold ${text} tracking-tight`}
            style={{
              background: 'linear-gradient(135deg, #6366F1 0%, #A855F7 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            CogitoSync
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400 tracking-wide">
            v3.0
          </span>
        </div>
      )}
    </div>
  );
}
