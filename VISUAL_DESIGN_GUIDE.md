# CogitoSync v3.0 - Visual Design System

## 🎨 Brand Identity

### Logo Concept
The CogitoSync logo represents the **intersection of two cognitive states** - the moment when minds synchronize and resonate.

```
  ◯     ◯
   \   /
    \ /
     ⬤  ← The sync moment
    / \
   /   \
  ◯     ◯
```

**Visual Elements**:
- Two overlapping circles (representing two people/states)
- Central dot (the moment of synchronization)
- Gradient fill (spectrum of emotional states)
- Smooth, organic curves (fluidity of thought)

**Implementation**: `/frontend/src/components/Logo.js`

---

## 🌈 Color Palette

### Primary Gradient
```
┌────────────────────────────────────┐
│  Indigo → Purple → Teal Gradient   │
│  #6366F1 → #A855F7 → #22C6A8      │
└────────────────────────────────────┘
```

**Usage**: Brand elements, buttons, highlights

### Semantic Colors

#### Light Mode
```css
Background:     #F9FAFB  (Soft white)
Cards:          rgba(255,255,255,0.7) + blur
Text Primary:   #111827  (Near black)
Text Secondary: #6B7280  (Gray)
Border:         #E5E7EB  (Light gray)
```

#### Dark Mode
```css
Background:     #0F172A  (Deep navy)
Cards:          rgba(30,41,59,0.7) + blur
Text Primary:   #F1F5F9  (Soft white)
Text Secondary: #94A3B8  (Light gray)
Border:         #334155  (Dark gray)
```

### Accent Colors

#### Status Colors
```
Success:  #10B981  (Green - positive states)
Warning:  #F59E0B  (Amber - attention needed)
Error:    #EF4444  (Red - critical issues)
Info:     #3B82F6  (Blue - informational)
```

#### Neon Accents (Soft Glow)
```
Purple:  rgba(168, 85, 247, 0.4)
Teal:    rgba(34, 198, 168, 0.4)
Amber:   rgba(251, 191, 36, 0.4)
```

---

## 📐 Layout System

### Grid & Spacing
```
Base unit: 4px (0.25rem)

Spacing scale:
- xs:  4px
- sm:  8px
- md:  16px
- lg:  24px
- xl:  32px
- 2xl: 48px
```

### Container Widths
```
Mobile:  100% (min-width: 320px)
Tablet:  720px
Desktop: 1200px
Max:     1400px
```

### Mobile-First Breakpoints
```css
sm:  640px   /* Large phone */
md:  768px   /* Tablet */
lg:  1024px  /* Desktop */
xl:  1280px  /* Large desktop */
2xl: 1536px  /* Extra large */
```

---

## 🔤 Typography

### Font Families
```css
Headings: 'Space Grotesk', sans-serif
Body:     'Inter', sans-serif
Mono:     'Fira Code', monospace (for handles)
```

### Type Scale
```
H1: text-4xl (36px)  - Page titles
H2: text-2xl (24px)  - Section headers
H3: text-xl (20px)   - Card titles
H4: text-lg (18px)   - Subheadings
Body: text-base (16px) - Main text
Small: text-sm (14px)  - Captions
Tiny: text-xs (12px)   - Labels
```

### Font Weights
```
Light:     300
Regular:   400
Medium:    500
Semibold:  600
Bold:      700
```

---

## 🎭 Effects & Interactions

### Glassmorphism
```css
.glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
```

**Usage**: All cards, modals, navigation bars

**Dark Mode Variant**:
```css
.dark .glass {
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Shadows
```css
Small:  0 1px 2px rgba(0, 0, 0, 0.05)
Medium: 0 4px 6px rgba(0, 0, 0, 0.1)
Large:  0 10px 15px rgba(0, 0, 0, 0.1)
XLarge: 0 20px 25px rgba(0, 0, 0, 0.1)
```

### Border Radius
```css
Small:  0.375rem (6px)
Medium: 0.5rem (8px)
Large:  0.75rem (12px)
XLarge: 1rem (16px)
Full:   9999px (pill shape)
```

---

## ✨ Animations

### Timing Functions
```css
Base:    cubic-bezier(0.4, 0, 0.2, 1)
Bounce:  cubic-bezier(0.68, -0.55, 0.265, 1.55)
Smooth:  cubic-bezier(0.25, 0.46, 0.45, 0.94)
```

### Standard Animations

#### Fade In
```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```
**Duration**: 300ms  
**Usage**: Page/component entry

#### Slide Up
```css
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
```
**Duration**: 400ms  
**Usage**: Navigation, modals

#### Scale In
```css
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```
**Duration**: 300ms  
**Usage**: Cards, buttons

#### Pulse Glow
```css
@keyframes pulse-glow {
  0%, 100% { 
    transform: scale(1); 
    box-shadow: 0 0 40px rgba(0,0,0,0.1); 
  }
  50% { 
    transform: scale(1.05); 
    box-shadow: 0 0 60px rgba(0,0,0,0.2); 
  }
}
```
**Duration**: 3s infinite  
**Usage**: CSS orbs, active indicators

### Hover Effects

#### Lift
```css
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}
```

#### Scale
```css
.hover-scale:hover {
  transform: scale(1.02);
}
```

#### Glow
```css
.hover-glow:hover {
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
}
```

---

## 🧩 Component Patterns

### Cards
```
┌─────────────────────────────────┐
│  [Icon] Title                   │
│  ─────────────────────────────  │
│                                 │
│  Content with proper spacing    │
│                                 │
│  [Action Button]                │
└─────────────────────────────────┘
```

**Anatomy**:
- Glassmorphic background
- 16-20px padding
- Rounded corners (12-16px)
- Subtle shadow
- Optional gradient border

### Buttons

#### Primary (Gradient)
```
┌────────────────────┐
│  [Icon] Action Text │
└────────────────────┘
```
- Gradient background
- White text
- Medium shadow
- Hover: opacity 90%
- Active: scale 98%

#### Secondary (Outline)
```
┌────────────────────┐
│  Action Text       │
└────────────────────┘
```
- Transparent background
- Colored border
- Colored text
- Hover: filled background

### Navigation Tabs
```
┌───────────────────────────────┐
│  [◯]   [◯]   [●]   [◯]   [◯]  │
│  Tab1  Tab2  Tab3  Tab4  Tab5 │
└───────────────────────────────┘
```

**Active State**:
- Colored icon
- Bold text
- Subtle background
- Scale 105%

**Inactive State**:
- Gray icon
- Regular text
- Transparent background

---

## 🌓 Dark Mode

### Transition
```css
transition: 
  background-color 0.3s ease,
  color 0.3s ease,
  border-color 0.3s ease;
```

### Contrast Adjustments
- Increased shadow intensity
- Reduced border opacity
- Adjusted text contrast (WCAG AA)
- Softer gradients

### Toggle Implementation
- Persistent in localStorage
- Icon: Sun ☀️ (light) / Moon 🌙 (dark)
- Located in header navigation
- Smooth transition animation

---

## 📱 Mobile Optimizations

### Touch Targets
```
Minimum size: 44x44px
Recommended:  48x48px
Spacing:      8px between targets
```

### Safe Areas
```css
padding-top: env(safe-area-inset-top);
padding-bottom: env(safe-area-inset-bottom);
```

### Viewport
```html
<meta 
  name="viewport" 
  content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"
/>
```

### Navigation Bar
- Floating with blur backdrop
- Bottom-positioned (thumb zone)
- Icons + labels for clarity
- Smooth transitions

---

## 🎯 CSS Orb Design

### Standard Orb
```
     ╭───────╮
    ╱         ╲
   │           │  ← Solid color fill
   │     ●     │  ← Pulsing glow
    ╲         ╱
     ╰───────╯
```

**Properties**:
- Perfect circle
- User's CSS color as fill
- Opacity based on light_frequency
- Subtle inner glow
- Outer shadow
- Pulse animation (3s)

### Enhanced Orb (v3.0)
```css
.css-orb-enhanced {
  border-radius: 50%;
  box-shadow: 
    0 0 40px rgba(0,0,0,0.1),
    inset 0 0 20px rgba(255,255,255,0.2);
  animation: pulse-glow 3s ease-in-out infinite;
}
```

**Enhancements**:
- Inset highlight
- Layered shadows
- Brightness filter
- Scale variation

---

## 🖼️ Image Treatment

### Avatars
```
  ╭─────╮
  │     │  ← Circular crop
  │ AI  │  ← DALL-E generated
  │     │  ← Gradient border
  ╰─────╯
```

**Specifications**:
- Size: 40px (small), 80px (medium), 120px (large)
- Border: 2px gradient
- Shadow: Soft glow matching primary color
- Placeholder: Gradient background with initials

### Loading States
```
╔═══════════════╗
║ ░░░░░░░░░░░░░ ║  ← Shimmer effect
║ ░░░░░░░░░░░░░ ║  ← Skeleton loader
╚═══════════════╝
```

---

## 🎪 Icon System

### Primary Icons (Lucide React)
```
Sparkles:      Create CSS
Activity:      Live mode
TrendingUp:    Feed/Insights
MessageCircle: Chat/Coach
Radar:         Vibe radar
User:          Profile
Crown:         Premium
Settings:      Settings
Moon/Sun:      Theme toggle
```

### Icon Styling
- Stroke width: 2 (default), 2.5 (active)
- Size: 20px (default), 24px (large)
- Color: Contextual (purple for active, gray for inactive)

---

## 🎨 Gradient Backgrounds

### Light Mode
```css
background: linear-gradient(
  135deg,
  #E8F4F8 0%,   /* Soft blue */
  #F5E6F0 50%,  /* Soft pink */
  #E6F3E8 100%  /* Soft green */
);
```

### Dark Mode
```css
background: linear-gradient(
  135deg,
  #0F172A 0%,   /* Deep navy */
  #1E1B4B 50%,  /* Deep indigo */
  #0F172A 100%  /* Deep navy */
);
```

### Brand Gradient
```css
background: linear-gradient(
  135deg,
  #6366F1 0%,   /* Indigo */
  #A855F7 50%,  /* Purple */
  #22C6A8 100%  /* Teal */
);
```

---

## 📐 Component Dimensions

### Cards
```
Min height: 120px
Padding:    16-20px
Margin:     12px (mobile), 16px (desktop)
Border:     1px solid (glass)
Shadow:     Medium to Large
```

### Inputs
```
Height:     44px (single line)
Min height: 120px (textarea)
Padding:    12px 16px
Font size:  16px (prevent zoom on iOS)
Border:     1px solid
Focus ring: 2px primary color
```

### Buttons
```
Height:     44px (default), 48px (large)
Padding:    12px 24px
Font size:  16px
Font weight: 500-600
Border radius: 8-12px
```

### Navigation
```
Height:     64px
Icon size:  20px
Label size: 9-10px
Active bg:  Subtle tint
```

---

## 🔍 Accessibility

### Color Contrast
- **WCAG AA**: All text meets 4.5:1 ratio
- **Focus States**: Visible 2px outline
- **Active States**: Clear visual feedback

### Screen Reader Support
- Semantic HTML structure
- ARIA labels on interactive elements
- Skip navigation links
- Alt text for images

### Keyboard Navigation
- Tab order follows visual flow
- Enter/Space activate buttons
- Esc closes modals
- Arrow keys for lists

---

## 💾 Asset Specifications

### App Icons
```
icon-192.png: 192x192px (PWA required)
icon-512.png: 512x512px (PWA required)
```

**Design**: 
- Gradient background (brand colors)
- Logo in center (white)
- No text
- PNG format with transparency

### Splash Screens
```
iOS:     1170x2532px (iPhone 13 Pro)
Android: 1080x1920px (standard)
```

**Design**:
- Gradient background
- Logo centered
- Optional tagline below

### Favicon
```
favicon.ico: 32x32px
```

**Design**: Simplified logo mark

---

## 🎬 Loading States

### Spinner
```
  ⟳  ← Rotating circle with gradient
```

**Implementation**:
```css
.spinner {
  border: 2px solid transparent;
  border-top-color: #6366F1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
```

### Skeleton
```
┌─────────────┐
│ ░░░░░░░░░░░ │  ← Animated shimmer
│ ░░░░░░░░░░░ │
│ ░░░░░░░░░░░ │
└─────────────┘
```

### Progress Bar
```
▓▓▓▓▓▓▓▓░░░░░░  60%
```

---

## 📊 Data Visualization

### CSS Orb
- **Primary**: Large circular indicator
- **Color**: User's CSS color
- **Glow**: Animated pulse
- **Size**: 120-160px

### Timeline Chart
- **Type**: Line chart
- **Color**: Purple gradient
- **Points**: CSS frequency over time
- **Axes**: Time (X), Intensity (Y)

### Mood Forecast
- **Type**: Bar chart or text prediction
- **Color**: Gradient bars
- **Labels**: Time periods
- **Confidence**: Visual indicator

---

## 🎁 Easter Eggs

### Logo Animation
- Hover: Circles rotate
- Click: Pulse effect
- Long press: Color cycle

### CSS Orb Interaction
- Tap: Ripple effect
- Hold: Reveals frequency data
- Swipe: View reaction options

---

## 📱 PWA Specific

### Install Prompt
```
┌─────────────────────────────────┐
│  Add CogitoSync to Home Screen  │
│                                 │
│  [App Icon]                     │
│                                 │
│  Get quick access to your       │
│  emotional state tracking       │
│                                 │
│  [Add]            [Cancel]      │
└─────────────────────────────────┘
```

### Standalone Mode Detection
```javascript
const isStandalone = 
  window.matchMedia('(display-mode: standalone)').matches;
```

**UI Adjustments**:
- Hide browser chrome references
- Add back button where needed
- Full-screen optimizations

---

## 🎯 Design Principles

1. **Mobile-First**: Design for thumb, expand for mouse
2. **Anonymous-Friendly**: No photos, only abstract visuals
3. **Calming**: Soft colors, smooth animations
4. **Clear Hierarchy**: Important info stands out
5. **Tactile**: Every tap gives feedback
6. **Accessible**: Works for everyone
7. **Fast**: Perceived and actual speed
8. **Consistent**: Same patterns throughout

---

**Design Version**: 3.0  
**Last Updated**: 2025-11-19  
**Design Language**: Cognitive Glassmorphism  
**Target Platforms**: iOS, Android, Desktop Web

