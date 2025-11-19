# CogitoSync v3.0 - Developer Documentation

## 🏗️ Architecture Overview

CogitoSync v3.0 is a full-stack **anonymous cognitive social platform** built with:
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + Tailwind CSS
- **Database**: MongoDB
- **AI**: OpenAI GPT-4o (text) + DALL-E 3 (images)
- **Real-time**: WebSocket for live updates
- **Deployment**: Docker + Supervisor

---

## 📂 Project Structure

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── models_v3.py            # Pydantic models (not directly used, reference)
│   ├── routes_v3.py            # Additional routes (not directly used, reference)
│   ├── seed_rooms.py           # Database seeding script
│   ├── .env                    # Environment variables
│   ├── requirements.txt        # Python dependencies
│   └── tests/                  # Test suite
│
├── frontend/
│   ├── public/
│   │   ├── manifest.json       # PWA manifest
│   │   └── service-worker.js   # PWA service worker
│   ├── src/
│   │   ├── App.js              # Main React app (v3 complete)
│   │   ├── App.css             # Global styles + design system
│   │   ├── components/         # Reusable components
│   │   │   ├── Logo.js         # Brand logo component
│   │   │   ├── MobileHeaderV3.js
│   │   │   ├── MobileNavV3.js
│   │   │   ├── VibeRadar.js
│   │   │   ├── MoodTimeline.js
│   │   │   ├── AICoachPanel.js
│   │   │   ├── MoodForecast.js
│   │   │   └── ui/             # Shadcn UI components
│   │   ├── pages/              # Page components
│   │   │   ├── AuthPage.js
│   │   │   ├── CreatePage.js
│   │   │   ├── ProfilePageV3.js
│   │   │   ├── FeedPageV3.js
│   │   │   ├── CoachChatPageV3.js
│   │   │   ├── CommunityRoomsPageV3.js
│   │   │   ├── RadarPage.js
│   │   │   └── InsightsPage.js
│   │   ├── context/
│   │   │   └── ThemeContext.js  # Dark/Light mode
│   │   └── .env                 # Frontend environment vars
│   └── package.json
│
└── DEV_NOTES.md                # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- MongoDB (running locally or via URI)
- OpenAI API Key

### Environment Setup

#### Backend (.env)
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="cogitosync_db"
CORS_ORIGINS="*"
OPENAI_API_KEY="sk-..."  # Your OpenAI API key
JWT_SECRET="cogitosync-super-secret-jwt-key-2025"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS=168
```

#### Frontend (.env)
```bash
REACT_APP_BACKEND_URL=https://your-domain.com
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

### Running Locally

#### Backend
```bash
cd /app/backend
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

#### Frontend
```bash
cd /app/frontend
yarn install
yarn start
```

#### Supervisor (Production)
```bash
sudo supervisorctl restart all
sudo supervisorctl status
```

---

## 🎨 Design System

### Color Palette

#### Light Mode
- **Primary**: `#6366F1` (Indigo)
- **Secondary**: `#22C6A8` (Teal)
- **Accent**: `#A855F7` (Purple)
- **Background**: `#F9FAFB`
- **Text**: `#111827`

#### Dark Mode
- **Background**: `#0F172A` (Dark blue)
- **Secondary BG**: `#1E293B`
- **Text**: `#F1F5F9`

### Typography
- **Headings**: Space Grotesk (Google Fonts)
- **Body**: Inter (Google Fonts)

### CSS Variables
All design tokens are defined in `/app/frontend/src/App.css` as CSS custom properties:
- `--color-primary`, `--color-secondary`, etc.
- `--shadow-sm`, `--shadow-md`, etc.
- `--radius-sm`, `--radius-md`, etc.

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login existing user

### CSS (Cognitive State Snapshots)
- `POST /api/css/create` - Create CSS (with OpenAI)
- `GET /api/css/my-history` - Get user's CSS history

### Profile (V3)
- `POST /api/v3/profile/create` - Create anonymous profile
- `GET /api/v3/profile/me` - Get current user profile
- `PUT /api/v3/profile/update` - Update profile

### Social (V3)
- `POST /api/v3/social/follow/{user_id}` - Follow user
- `POST /api/v3/social/unfollow/{user_id}` - Unfollow user
- `GET /api/v3/social/feed` - Get personalized feed
- `GET /api/v3/social/global-feed` - Get global feed

### AI Coach (V3)
- `POST /api/v3/coach/start-session` - Start chat session
- `POST /api/v3/coach/message` - Send message to coach
- `GET /api/v3/ai-coach/insights` - Get AI insights from CSS history

### Community Rooms (V3)
- `GET /api/v3/rooms/list` - List all rooms
- `GET /api/v3/rooms/trending` - Get trending rooms
- `POST /api/v3/rooms/{room_id}/join` - Join room
- `POST /api/v3/rooms/{room_id}/leave` - Leave room
- `GET /api/v3/room/{room_id}/dynamics` - Get room collective mood

### Vibe Radar (V3)
- `GET /api/v3/vibe-radar/nearby` - Find similar vibe users

### Avatar (V3)
- `POST /api/v3/avatar/generate` - Generate AI avatar with DALL-E
- `GET /api/v3/avatar/my` - Get current avatar

### Mood Journal (V3)
- `GET /api/v3/mood-journal/timeline?days=7` - Get timeline

### AI Forecast (V3)
- `GET /api/v3/ai-forecast/predict` - Get 24h mood forecast

### Empathy Match (V3)
- `GET /api/v3/empathy/find-match` - Find empathy match

### Reactions (V3)
- `POST /api/v3/css/react` - React to CSS
- `GET /api/v3/css/{css_id}/reactions` - Get reactions

### Premium (V3)
- `GET /api/v3/premium/check` - Check premium status
- `POST /api/v3/premium/subscribe` - Subscribe to premium

### WebSocket
- `WS /ws/live?room_id=global` - Live CSS updates

---

## 🤖 AI Integration

### OpenAI Configuration

The app uses OpenAI's API for:
1. **CSS Generation** (GPT-4o) - Converts emotional input to structured data
2. **AI Coach** (GPT-4o) - Conversational support
3. **Insights** (GPT-4o) - Pattern analysis
4. **Forecast** (GPT-4o) - Mood prediction
5. **Avatar** (DALL-E 3) - AI-generated avatars

### Graceful Fallbacks

All AI features have fallback mechanisms:
- If OpenAI API fails, the app returns default/placeholder responses
- Users can still use core features without AI
- UI shows clear indicators when in fallback mode

### Error Handling

```python
try:
    response = openai_client.chat.completions.create(...)
except Exception as e:
    logging.error(f"AI error: {e}")
    return fallback_response
```

---

## 📱 PWA Features

### Manifest
Located at `/app/frontend/public/manifest.json`:
- App name, icons, theme colors
- `display: standalone` for full-screen
- Portrait orientation

### Service Worker
Located at `/app/frontend/public/service-worker.js`:
- Registered in `App.js`
- Handles offline caching (basic implementation)

### Mobile Optimization
- Bottom navigation with safe area support
- Touch-friendly tap targets (min 44x44px)
- Responsive design (mobile-first)
- Dark mode support

---

## 🧪 Testing

### Backend Tests
```bash
cd /app/backend
pytest tests/ -v
```

Test files are organized by feature:
- `tests/test_auth.py`
- `tests/test_profile.py`
- `tests/test_css.py`
- `tests/test_social.py`
- `tests/test_coach.py`
- `tests/test_rooms.py`

### Frontend Testing
Frontend uses Playwright for E2E testing (handled by testing agents).

---

## 🔒 Security

### Authentication
- JWT-based token authentication
- Tokens stored in localStorage
- 168-hour (7 day) expiration by default
- Passwords hashed with bcrypt

### Anonymous Profiles
- Users identified by UUID
- Public handle format: `@vibe-XXXX`
- No real names or identifiable information required

### CORS
- Configurable via `CORS_ORIGINS` in backend .env
- Default: `*` (accepts all origins)

---

## 🐛 Debugging

### Backend Logs
```bash
# Check backend errors
tail -f /var/log/supervisor/backend.err.log

# Check backend output
tail -f /var/log/supervisor/backend.out.log
```

### Frontend Logs
```bash
# Check frontend errors
tail -f /var/log/supervisor/frontend.err.log

# Check frontend output
tail -f /var/log/supervisor/frontend.out.log
```

### Service Status
```bash
sudo supervisorctl status
```

### Restart Services
```bash
# Restart backend only
sudo supervisorctl restart backend

# Restart frontend only
sudo supervisorctl restart frontend

# Restart all services
sudo supervisorctl restart all
```

---

## 📦 Building for Production

### Backend
The backend runs via uvicorn under supervisor control. No separate build step required.

### Frontend
```bash
cd /app/frontend
yarn build
```

This creates an optimized production build in `/app/frontend/build/`.

---

## 🔄 Database

### MongoDB Collections

- `users` - User accounts
- `profiles` - Anonymous user profiles
- `css_snapshots` - Cognitive state snapshots
- `community_rooms` - Room definitions
- `room_memberships` - User-room associations
- `social_graph` - Follow relationships
- `coach_sessions` - AI coach chat history
- `reactions` - CSS reactions
- `avatar_evolutions` - Avatar generation history

### Indexes

Automatically created on startup (see `server.py`):
- `users.id` (unique)
- `users.email` (unique)
- `profiles.user_id` (unique)
- `profiles.handle` (unique)
- `css_snapshots.id` (unique)
- `css_snapshots.[user_id, timestamp]`
- `social_graph.[follower_id, following_id]` (unique)

### Seeding Data

```bash
cd /app/backend
python seed_rooms.py
```

This creates 6 default community rooms.

---

## 🎯 Key Features

### 1. Anonymous Profiles
Users get auto-generated handles like `@vibe-3f9a` for privacy.

### 2. CSS (Cognitive State Snapshots)
Real-time emotional state tracking with AI-generated color, frequency, texture.

### 3. Social Feed
Follow other anonymous users, see their CSS in your feed.

### 4. AI Coach
GPT-4o powered conversational coach that provides empathetic support.

### 5. Vibe Radar
Find users with similar emotional patterns.

### 6. Community Rooms
Themed spaces with collective mood dynamics.

### 7. Mood Timeline
Visual representation of emotional patterns over time.

### 8. AI Insights
Pattern analysis and actionable recommendations.

### 9. 24h Forecast
Predictive mood modeling based on history.

### 10. Empathy Match
Find emotionally resonant connections.

---

## 🚧 Known Limitations

1. **OpenAI Quota**: If API key runs out of quota, all AI features enter fallback mode
2. **Avatar Generation**: DALL-E 3 is slower (~15-30 seconds per image)
3. **WebSocket**: Basic implementation, may need reconnection logic improvements
4. **Offline Mode**: PWA caching is minimal, needs enhancement for full offline support

---

## 📞 Support & Contribution

For issues, feature requests, or contributions:
1. Check the API endpoints are responding: `curl https://your-domain.com/api/`
2. Verify OpenAI key is valid and has quota
3. Check supervisor logs for errors
4. Test in both light and dark modes
5. Verify PWA manifest is being served correctly

---

## 🎨 Branding

### Logo
The CogitoSync logo represents:
- **Overlapping circles**: Cognitive synchronization
- **Gradient**: Purple-blue spectrum of emotional states
- **Central intersection**: The moment of connection/resonance

See `/app/frontend/src/components/Logo.js` for the SVG implementation.

### Color Philosophy
- **Blue/Indigo**: Trust, calm, depth
- **Purple**: Creativity, introspection
- **Teal**: Growth, healing, balance

---

**Last Updated**: 2025-11-19  
**Version**: 3.0.0  
**Status**: Production Ready
