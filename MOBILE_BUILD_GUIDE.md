# CogitoSync v3.1 - Mobile Build & Deployment Guide
## Android (Google Play) + iOS (App Store)

---

## 📱 MOBILE SETUP COMPLETE

### ✅ What's Been Configured:
- Capacitor installed and configured
- Android project created (`/app/frontend/android`)
- iOS project created (`/app/frontend/ios`)
- App ID: `com.cogitosync.app`
- App Name: `CogitoSync`
- Splash screen colors and branding set
- Status bar styling configured
- Deep linking enabled (cogitosync://)
- Emergent badge removed for mobile builds

---

## 🚀 BUILD INSTRUCTIONS

### Prerequisites:
1. **For Android:**
   - Android Studio (latest version)
   - JDK 17 or higher
   - Android SDK 33+ (API Level 33)

2. **For iOS:**
   - macOS computer
   - Xcode 15+ 
   - Apple Developer Account ($99/year)
   - Valid iOS Distribution Certificate
   - Valid Provisioning Profile

---

## 📦 ANDROID BUILD (APK/AAB for Google Play)

### Step 1: Build Web Assets
```bash
cd /app/frontend
yarn build:mobile
```

### Step 2: Open Android Studio
```bash
# From terminal
cd /app/frontend
yarn cap:android

# OR manually open Android Studio and select:
# File → Open → /app/frontend/android
```

### Step 3: Configure Build Settings

#### A) Update `android/app/build.gradle`:
```gradle
android {
    namespace "com.cogitosync.app"
    compileSdk 34
    
    defaultConfig {
        applicationId "com.cogitosync.app"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "3.1.0"
    }
    
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            
            // Sign with your keystore
            signingConfig signingConfigs.release
        }
    }
}
```

#### B) Create Keystore (First Time Only):
```bash
cd /app/frontend/android/app

# Generate keystore
keytool -genkey -v -keystore cogitosync.keystore \
  -alias cogitosync \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# You'll be prompted to enter:
# - Keystore password (SAVE THIS!)
# - Key password (SAVE THIS!)
# - Your name/organization details
```

#### C) Configure Signing (android/gradle.properties):
```properties
COGITOSYNC_KEYSTORE_PATH=../app/cogitosync.keystore
COGITOSYNC_KEYSTORE_PASSWORD=your_keystore_password
COGITOSYNC_KEY_ALIAS=cogitosync
COGITOSYNC_KEY_PASSWORD=your_key_password
```

### Step 4: Build APK (for testing)
```bash
cd /app/frontend/android
./gradlew assembleRelease

# APK location:
# android/app/build/outputs/apk/release/app-release.apk
```

### Step 5: Build AAB (for Google Play)
```bash
cd /app/frontend/android
./gradlew bundleRelease

# AAB location:
# android/app/build/outputs/bundle/release/app-release.aab
```

### Step 6: Upload to Google Play Console

1. Go to https://play.google.com/console
2. Create new app → "CogitoSync"
3. Fill out store listing:
   - Title: CogitoSync
   - Short description: Anonymous Cognitive Social Platform
   - Full description: (see STORE_LISTING.md)
   - Screenshots: Upload mobile screenshots
   - Feature graphic: 1024x500 banner
   - App icon: 512x512 PNG

4. Upload AAB:
   - Production → Create new release
   - Upload app-release.aab
   - Set release notes
   - Review & rollout

---

## 🍎 iOS BUILD (IPA for App Store)

### Step 1: Build Web Assets
```bash
cd /app/frontend
yarn build:mobile
```

### Step 2: Open Xcode
```bash
# From terminal
cd /app/frontend
yarn cap:ios

# OR manually open Xcode:
# Open: /app/frontend/ios/App/App.xcworkspace
```

### Step 3: Configure Code Signing

#### A) Select Team:
1. In Xcode, click project "App" in navigator
2. Go to "Signing & Capabilities" tab
3. Select your Apple Developer team
4. Bundle Identifier: `com.cogitosync.app`
5. Enable "Automatically manage signing"

#### B) Create App ID in Apple Developer:
1. Go to https://developer.apple.com/account
2. Certificates, IDs & Profiles → Identifiers
3. Click "+" to create new App ID
4. Description: CogitoSync
5. Bundle ID: com.cogitosync.app
6. Enable capabilities:
   - Push Notifications
   - Sign in with Apple (optional)
   - Associated Domains (for deep linking)

#### C) Create Provisioning Profile:
1. Profiles → "+" to create new
2. Distribution → App Store
3. Select App ID: com.cogitosync.app
4. Select Distribution Certificate
5. Name: "CogitoSync App Store"
6. Download and double-click to install

### Step 4: Configure Info.plist

Add to `ios/App/App/Info.plist`:
```xml
<key>NSUserTrackingUsageDescription</key>
<string>We use this to improve your experience</string>
<key>NSCameraUsageDescription</key>
<string>Take photos for your profile</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Choose photos from your library</string>
```

### Step 5: Build & Archive

1. In Xcode menu: Product → Scheme → Select "App"
2. Select device: "Any iOS Device (arm64)"
3. Product → Archive (⌘ + Shift + B)
4. Wait for build to complete
5. Organizer window opens with your archive

### Step 6: Distribute to App Store

1. In Organizer, select your archive
2. Click "Distribute App"
3. Select "App Store Connect"
4. Upload
5. Wait for processing (10-30 minutes)

### Step 7: Submit to App Store

1. Go to https://appstoreconnect.apple.com
2. My Apps → "+" → New App
3. Fill out app information:
   - Platform: iOS
   - Name: CogitoSync
   - Language: Turkish (primary), English
   - Bundle ID: com.cogitosync.app
   - SKU: COGITOSYNC001

4. App Store → Version Information:
   - Screenshots (6.7", 6.5", 5.5" required)
   - Description (see STORE_LISTING.md)
   - Keywords: cognitive, mood, emotion, wellness, social
   - Support URL: https://cogitosync.com/support
   - Privacy Policy URL: https://cogitosync.com/privacy

5. Build → Select uploaded build
6. Pricing: Free (or paid)
7. Submit for Review

---

## 🔐 ENVIRONMENT VARIABLES FOR MOBILE

Create `/app/frontend/.env.production` for mobile builds:

```env
REACT_APP_BACKEND_URL=https://api.cogitosync.com
REACT_APP_WS_URL=wss://api.cogitosync.com
REACT_APP_VERSION=3.1.0
REACT_APP_PLATFORM=mobile
```

**IMPORTANT:** Update backend URL to your production API endpoint.

---

## 📋 STORE LISTING ASSETS

### Required Screenshots:
- iPhone 6.7" (1290x2796) - 3-8 screenshots
- iPhone 6.5" (1242x2688) - 3-8 screenshots  
- iPhone 5.5" (1242x2208) - 3-8 screenshots
- iPad Pro 12.9" (2048x2732) - 3-8 screenshots

### App Icon:
- 1024x1024 PNG (iOS)
- 512x512 PNG (Android)
- No transparency, no rounded corners (iOS handles this)

### Feature Graphic (Android):
- 1024x500 PNG
- Landscape banner for Google Play

---

## 🧪 TESTING BEFORE RELEASE

### Android Testing:
```bash
# Install APK on device
adb install android/app/build/outputs/apk/release/app-release.apk

# View logs
adb logcat | grep CogitoSync
```

### iOS Testing:
1. TestFlight (recommended):
   - Upload build via Xcode
   - Add internal/external testers
   - Share TestFlight link

2. Ad-Hoc Distribution:
   - Create Ad Hoc provisioning profile
   - Export IPA
   - Install via Apple Configurator

---

## 🚨 COMMON ISSUES & FIXES

### Android:

**Issue:** Build fails with "SDK not found"
```bash
# Fix: Set ANDROID_HOME
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

**Issue:** Keystore password error
```bash
# Reset keystore and create new one
rm android/app/cogitosync.keystore
# Follow keystore creation steps again
```

### iOS:

**Issue:** "No signing identity found"
```bash
# Fix: 
# 1. Open Xcode Preferences → Accounts
# 2. Sign in with Apple ID
# 3. Download Manual Profiles
```

**Issue:** "Provisioning profile doesn't match"
```bash
# Fix: In Xcode
# 1. Clean Build Folder (Cmd+Shift+K)
# 2. Delete DerivedData
# 3. Refresh provisioning profiles
```

---

## 📊 ANALYTICS & MONITORING

### Recommended Integrations:
- Firebase Analytics (mobile-specific tracking)
- Crashlytics (crash reporting)
- Sentry (error monitoring)
- App Store Connect Analytics (built-in)
- Google Play Console Analytics (built-in)

---

## 🔄 UPDATE PROCESS

### Push Updates:
1. Increment version in `package.json`
2. Update versionCode (Android) and versionName
3. Update CFBundleShortVersionString (iOS)
4. Rebuild and upload new version
5. Submit update for review

### Hot Updates (for web content):
- Web assets update automatically via Capacitor
- No app store review needed for content changes
- Users get updates on next app launch

---

## 📞 SUPPORT & RESOURCES

### Official Documentation:
- Capacitor: https://capacitorjs.com/docs
- Android: https://developer.android.com
- iOS: https://developer.apple.com

### Useful Commands:
```bash
# Sync web assets to mobile
npx cap sync

# Copy web build only
npx cap copy

# Update native dependencies
npx cap update

# Check for issues
npx cap doctor

# Live reload during development
npx cap run android -l
npx cap run ios -l
```

---

## ✅ PRE-SUBMISSION CHECKLIST

### Android:
- [ ] App signed with release keystore
- [ ] Tested on physical device
- [ ] ProGuard rules configured
- [ ] Privacy policy link added
- [ ] Store listing complete with screenshots
- [ ] Content rating questionnaire filled
- [ ] AAB uploaded and reviewed

### iOS:
- [ ] Code signing configured
- [ ] Tested on physical device
- [ ] All required screenshots uploaded
- [ ] Privacy policy URL provided
- [ ] App Store description complete
- [ ] Build submitted for review
- [ ] Export compliance declared

---

## 🎯 EXPECTED REVIEW TIMES

- **Google Play:** 1-3 days (typically faster)
- **Apple App Store:** 1-7 days (average 2-3 days)

---

**BUILD STATUS:** ✅ READY FOR MOBILE DEPLOYMENT
**PLATFORMS:** Android (APK/AAB) + iOS (IPA)
**VERSION:** 3.1.0
**BUILD DATE:** November 20, 2025

---

