# 🚀 CogitoSync v3.0 - Anonymous Cognitive Social Network

## Platform Overview

CogitoSync v3.0 is the world's first cognitive-state social network where users share emotions, mental states, and AI-generated cognitive signatures instead of photos or text. Everything is anonymous but socially interactive.

---

## ✨ What's New in v3.0

### 1. Anonymous Profile System ✅
- **Auto-generated handles**: @vibe-xxxx format
- **Vibe Identities**: 7 emotional archetypes
  - 🔥 Ember (Energetic)
  - 🌫️ Mist (Calm)
  - ⚡ Flux (Chaotic)
  - ✨ Nova (Inspired)
  - 💫 Echo (Empathic)
  - 🌊 Drift (Tired)
  - 🌈 Prism (Curious)
- **Profile Stats**: CSS count, followers, following
- **Complete anonymity**: No real names or emails exposed

**Routes:**
- `POST /api/v3/profile/create` - Create profile with vibe identity
- `GET /api/v3/profile/me` - Get own profile
- `GET /api/v3/profile/{user_id}` - View any profile

### 2. Social Feed + Follow System ✅
- **Follow/Unfollow** anonymous users
- **Personalized Feed**: CSS updates from followed users
- **Global Feed**: Explore public CSS signals
- **CSS Reactions**: Wave, Pulse, Spiral, Color-shift

**Routes:**
- `POST /api/v3/social/follow/{target_user_id}` - Follow user
- `POST /api/v3/social/unfollow/{target_user_id}` - Unfollow
- `GET /api/v3/social/feed` - Personalized feed
- `GET /api/v3/social/global-feed` - Global timeline

### 3. AI Coach 2.0 (Conversational) ✅
- **Real-time chat interface**
- **Context-aware**: Uses CSS history
- **Empathetic mentor**: GPT-4o powered
- **Session persistence**: Save conversations

**Routes:**
- `POST /api/v3/coach/start-session` - Start new session
- `POST /api/v3/coach/message` - Send message to coach

### 4. Community Rooms 2.0 ✅
- **6 Room Categories**:
  - Deep Focus Zone
  - Chill Lounge
  - Overthinking Anonymous
  - Study Grind
  - Night Owls
  - Creator's Corner
- **Trending rooms**
- **Join/Leave freely**
- **Member counts**

**Routes:**
- `GET /api/v3/rooms/list` - All rooms (filter by category)
- `GET /api/v3/rooms/trending` - Trending rooms
- `POST /api/v3/rooms/{room_id}/join` - Join room
- `POST /api/v3/rooms/{room_id}/leave` - Leave room

### 5. Avatar Evolution System ✅
- **AI-generated avatars** based on CSS patterns
- **Evolution tracking**: Stage-based progression
- **Trigger system**: Evolves with emotional changes
- **History view**: See all evolution stages

**Routes:**
- `POST /api/v3/avatar/evolve` - Trigger evolution
- `GET /api/v3/avatar/history` - View evolution history

---

## 🎨 Frontend v3.0 Features

### New Navigation (5 Tabs)
1. **CSS** - Create cognitive snapshots
2. **Feed** - Social timeline (Following/Global)
3. **Coach** - AI chat interface
4. **Rooms** - Community spaces
5. **Profile** - Anonymous profile & stats

### New Pages
- `/profile` - ProfilePageV3 (setup vibe identity)
- `/feed` - FeedPageV3 (personalized/global toggle)
- `/coach` - CoachChatPageV3 (messaging UI)
- `/community-rooms` - CommunityRoomsPageV3 (category browser)

### UI/UX Enhancements
- **Glass morphism design**
- **Smooth animations**
- **Mobile-first PWA optimized**
- **Touch-friendly interactions**
- **Bottom tab navigation**

---

## 📊 Database Collections (New in v3.0)

### anonymous_profiles
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "handle": "@vibe-1234",
  "vibe_identity": "Nova",
  "avatar_url": "...",
  "bio": "...",
  "followers_count": 0,
  "following_count": 0,
  "css_count": 0
}
```

### social_graph
```json
{
  "id": "uuid",
  "follower_id": "uuid",
  "following_id": "uuid",
  "created_at": "ISO"
}
```

### coach_sessions
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### community_rooms
```json
{
  "id": "uuid",
  "name": "Deep Focus Zone",
  "category": "Focus",
  "description": "...",
  "member_count": 0,
  "is_trending": true
}
```

### room_memberships
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "room_id": "uuid",
  "joined_at": "ISO"
}
```

### avatar_evolutions
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "stage": 0,
  "evolution_snapshots": [],
  "last_evolved_at": "ISO"
}
```

---

## 🔐 Privacy & Security

### Anonymous by Design
- No real names stored
- Auto-generated handles
- No personal data exposure
- Cognitive profiles only

### Data Protection
- JWT authentication
- Location hashing (100m radius)
- No tracking across sessions
- Minimal data retention

---

## 🚀 Deployment Status

### Backend
- ✅ FastAPI + WebSocket
- ✅ MongoDB with 11+ collections
- ✅ OpenAI GPT-4o integration
- ✅ DALL-E image generation
- ✅ 30+ API endpoints

### Frontend
- ✅ React 19 + PWA
- ✅ 5-tab mobile navigation
- ✅ Socket.io WebSocket client
- ✅ Recharts visualization
- ✅ Full offline support

### AI Features
- ✅ CSS generation (GPT-4o)
- ✅ Conversational coach
- ✅ Vibe identity classification
- ✅ Mood forecasting
- ✅ Avatar generation (DALL-E)

---

## 📱 Mobile PWA Experience

### iOS
1. Open Safari
2. Visit: `https://babel-cogito.preview.emergentagent.com`
3. Tap Share → "Add to Home Screen"
4. Open from home screen (fullscreen app)

### Android
1. Open Chrome
2. Visit app URL
3. Tap menu → "Install app"
4. Open from app drawer

### Features
- Offline caching (service worker)
- Native-like navigation
- Safe area support (notches)
- Background/foreground handling
- Auto-reconnect WebSocket

---

## 🎯 User Journey

### First Time User
1. **Register** with email/password
2. **Choose Vibe Identity** (7 options)
3. **Create first CSS** (emotional snapshot)
4. **Explore Global Feed** (anonymous users)
5. **Follow interesting profiles**
6. **Chat with AI Coach**
7. **Join Community Rooms**
8. **Watch Avatar Evolve**

### Return User
1. Open app from home screen
2. See personalized feed
3. Create new CSS
4. Chat with AI coach
5. Check room dynamics
6. React to others' CSS

---

## 🎨 Design System

### Colors (Vibe-based)
- **Ember**: Red-Orange gradient
- **Mist**: Soft grey-blue
- **Flux**: Electric purple
- **Nova**: Gold-yellow
- **Echo**: Teal-cyan
- **Drift**: Deep blue
- **Prism**: Rainbow gradient

### Typography
- **Headings**: Space Grotesk
- **Body**: Inter
- **Mobile-friendly**: 16px+ base

### Components
- Glass morphism cards
- Smooth transitions
- Touch-friendly (44px targets)
- Bottom tab bar
- Floating action buttons

---

## 🛠️ Technical Stack

**Backend:**
- FastAPI 0.104+
- MongoDB (Motor)
- OpenAI API (GPT-4o, DALL-E 3)
- WebSocket (python-socketio)
- JWT authentication

**Frontend:**
- React 19
- Tailwind CSS
- shadcn/ui components
- socket.io-client
- Recharts
- React Router v6

**Infrastructure:**
- Kubernetes deployment
- Supervisor process manager
- Service worker (PWA)
- MongoDB indexes optimized

---

## 📈 Performance

### Lighthouse Scores (Target)
- Performance: 85+
- PWA: 95+
- Accessibility: 90+
- Best Practices: 90+

### Optimizations
- Code splitting
- Lazy loading
- WebSocket reconnection
- Database indexing
- Response caching

---

## 🔄 v2.0 → v3.0 Migration

### Preserved Features
- All v2.0 features remain functional
- CSS creation system
- Real-time WebSocket
- Vibe Radar (location-based)
- Mood Journal
- Premium system

### New Additions
- Anonymous profiles (+6 endpoints)
- Social graph (+4 endpoints)
- AI coach chat (+2 endpoints)
- Community rooms 2.0 (+4 endpoints)
- Avatar evolution (+2 endpoints)

### Breaking Changes
- None! v3.0 is fully backward compatible

---

## 🎉 Production Ready

### v3.0 Status: LIVE ✅

**Backend:** Running (CogitoSync v3.0)
**Frontend:** Deployed (5-tab navigation)
**Database:** MongoDB with all collections
**AI:** OpenAI integrated
**PWA:** Installable on iOS/Android

### Testing Complete
- ✅ Profile creation
- ✅ Social follow/feed
- ✅ AI coach sessions
- ✅ Community rooms
- ✅ Mobile responsive
- ✅ PWA manifest
- ✅ Service worker

---

## 📞 Support & Documentation

**API Docs:** `/docs` (FastAPI auto-generated)
**Mobile Guide:** `/app/MOBILE_PWA_GUIDE.md`
**v3.0 Changes:** This document

**Platform:** CogitoSync v3.0 - Anonymous Cognitive Social Network
**Status:** Production Ready 🚀
**Last Updated:** November 2025

---

**Welcome to the future of emotional social networking! 💜**
