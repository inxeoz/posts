---
title: React Native
date: '2026-01-27'
description: How to run React Native on Arch Linux and fix common errors
permalink: posts/{{ title | slug }}/index.html
tags:
- react-native
- android
- mobile
- arch-linux
categories:
- react-native
---

# 🐧 **How to Run React Native on Arch Linux (and Fix Common Errors)**

React Native works beautifully on Arch Linux — but because Arch uses newer packages (Java, SDK Tools, etc.), developers often run into version mismatches or Gradle issues that do not appear on Ubuntu or macOS.
This guide explains **how to correctly install the React Native Android toolchain on Arch**, run your app, and fix the most common errors.

---

# ⚙️ **1. Install Required Packages on Arch**

Install the base development environment:

```bash
sudo pacman -Syu
sudo pacman -S nodejs npm yarn git base-devel
```

Optional: use `nvm` or `fnm` to manage Node versions.

---

# 📱 **2. Install Android Development Tools**

### Install JDK 17 (recommended for React Native 0.73+ and Expo SDK 50+):

```bash
sudo pacman -S jdk17-openjdk
```

Set it as default:

```bash
sudo archlinux-java set java-17-openjdk
```

Check:

```bash
java -version
```

You should get:

```
openjdk 17.x.x
```

---

### Install Android Studio (recommended)

```bash
sudo pacman -S android-studio
```

OR without GUI:

```bash
sudo pacman -S android-sdk android-sdk-platform-tools android-sdk-build-tools android-sdk-cmdline-tools-latest
```

---

# 📁 **3. Set Environment Variables**

Add these to `~/.bashrc` or `~/.zshrc`:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/emulator:$PATH"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

# Java 17
export JAVA_HOME="/usr/lib/jvm/java-17-openjdk"
export PATH="$JAVA_HOME/bin:$PATH"
```

Reload:

```bash
source ~/.zshrc
```

---

# 📦 **4. Install Required Android Packages**

```bash
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
sdkmanager "emulator"
sdkmanager "system-images;android-34;default;x86_64"
sdkmanager --licenses
```

---

# ▶️ **5. Create an Android Emulator**

```bash
avdmanager create avd -n pixel -k "system-images;android-34;default;x86_64"
emulator -avd pixel
```

---

# 🚀 **6. Create and Run a React Native Project**

### Using React Native CLI

```bash
npx react-native init MyApp
cd MyApp
npx react-native start
```

In another terminal:

```bash
npx react-native run-android
```

---

### Using Expo

```bash
npx create-expo-app MyApp
cd MyApp
npm start   # or bun run android
```

---

# ❗ **7. Fixing Common React Native Errors on Arch Linux**

Because Arch Linux uses very fresh versions of Java, SDK tools, and kernel drivers, React Native often fails with errors like:

---

## 🔥 **Error: Unsupported class file major version 69 / 70**

This means you are using **Java 19/20/21/25**, but React Native only supports **Java 17**.

### Fix:

```bash
sudo pacman -S jdk17-openjdk
sudo archlinux-java set java-17-openjdk
java -version
```

---

## 🔥 **Error: No connected device found**

Fix by:

1. Enabling USB Debugging on your phone
2. Adding udev rules:

```bash
yay -S android-udev
sudo udevadm control --reload-rules
```

3. Verifying device:

```bash
adb devices
```

---

## 🔥 **Error: Could not find SDK root / sdkmanager not found**

Fix:

Make sure cmdline-tools is installed:

```bash
sdkmanager --install "cmdline-tools;latest"
```

Add to PATH:

```bash
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
```

---

## 🔥 **Error: NDK not found or missing source.properties**

This happens A LOT on Arch when NDK downloads get interrupted.

Fix:

```bash
rm -rf ~/Android/Sdk/ndk
sdkmanager "ndk;27.1.12297006"
```

Or install manually (much faster):

```bash
wget https://dl.google.com/android/repository/android-ndk-r27b-linux.zip
unzip android-ndk-r27b-linux.zip
mv android-ndk-r27b ~/Android/Sdk/ndk/27.1.12297006
```

---

## 🔥 **Error: Build stuck at 9% / 27% CONFIGURING**

This happens because:

* Gradle is downloading huge dependencies
* NDK missing
* Gradle Kotlin DSL accessors corrupted

### Fix corrupted Gradle cache:

```bash
./gradlew --stop
rm -rf ~/.gradle/caches/*/kotlin-dsl
rm -rf ~/.gradle/caches
```

Then rebuild:

```bash
./gradlew assembleRelease
```

---

## 🔥 **Error: Gradle build extremely slow**

Create `~/.gradle/gradle.properties`:

```text
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.configureondemand=true
org.gradle.caching=true
org.gradle.jvmargs=-Xmx4g
```

Speeds builds by 5–10×.

---

# 📦 **8. Creating a Release APK (React Native / Expo)**

### React Native CLI:

```bash
cd android
./gradlew assembleRelease
```

APK output:

```
android/app/build/outputs/apk/release/app-release.apk
```

---

### Expo (Production build)

```bash
npx expo prebuild
cd android
./gradlew assembleRelease
```

---

# 🎯 Final Tips for Arch Linux Users

✔ Always use **Java 17**
✔ Use the **latest cmdline-tools**
✔ Only install **NDK 27.X** unless your project requires another version
✔ Don’t interrupt `gradlew` — it corrupts caches
✔ If something is weird: delete `~/.gradle/caches` and rebuild

---
