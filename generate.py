"""
Writes the complete VideoGate Android project into ./videogate  (version 1.1)
Run by the GitHub Actions workflow before building. No need to run by hand.
"""
import base64
import os

FILES = {}

# Fixed debug signing key, so every build is signed the same way and
# new APKs install over the old one without uninstalling.
KEYSTORE_B64 = "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"

FILES["settings.gradle.kts"] = r'''pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "VideoGate"
include(":app")
'''

FILES["build.gradle.kts"] = r'''plugins {
    id("com.android.application") version "8.5.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.24" apply false
}
'''

FILES["gradle.properties"] = r'''org.gradle.jvmargs=-Xmx2g -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
kotlin.code.style=official
'''

FILES["app/build.gradle.kts"] = r'''plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.alok.videogate"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.alok.videogate"
        minSdk = 26
        targetSdk = 34
        versionCode = 2
        versionName = "1.1"
    }

    signingConfigs {
        getByName("debug") {
            storeFile = file("../debug.keystore")
            storePassword = "android"
            keyAlias = "androiddebugkey"
            keyPassword = "android"
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}
'''

FILES["app/src/main/AndroidManifest.xml"] = r'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Lets the app see launcher apps and the home screen app without QUERY_ALL_PACKAGES -->
    <queries>
        <intent>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent>
        <intent>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.HOME" />
        </intent>
    </queries>

    <application
        android:allowBackup="false"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:label="@string/app_name"
        android:theme="@android:style/Theme.Material.Light.DarkActionBar">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".GateService"
            android:exported="true"
            android:label="@string/app_name"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService" />
            </intent-filter>
            <meta-data
                android:name="android.accessibilityservice"
                android:resource="@xml/gate_service" />
        </service>

    </application>
</manifest>
'''

FILES["app/src/main/res/values/strings.xml"] = r'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">VideoGate</string>
    <string name="service_description">Detects when one of your chosen apps is opened so VideoGate can play your video first. It does not read screen content.</string>
</resources>
'''

FILES["app/src/main/res/values/colors.xml"] = r'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">#4F46E5</color>
</resources>
'''

FILES["app/src/main/res/drawable/ic_launcher_foreground.xml"] = r'''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <!-- ring -->
    <path
        android:fillColor="#00000000"
        android:strokeColor="#FFFFFF"
        android:strokeWidth="4"
        android:pathData="M54,29 A25,25 0 1,1 54,79 A25,25 0 1,1 54,29 Z" />
    <!-- play triangle -->
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M46,41 L46,67 L69,54 Z" />
</vector>
'''

FILES["app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml"] = r'''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
'''

FILES["app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml"] = r'''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_foreground" />
</adaptive-icon>
'''

FILES["app/src/main/res/xml/gate_service.xml"] = r'''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:description="@string/service_description"
    android:accessibilityEventTypes="typeWindowStateChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:notificationTimeout="50"
    android:canRetrieveWindowContent="false" />
'''

FILES["app/src/main/java/com/alok/videogate/Store.kt"] = r'''package com.alok.videogate

import android.content.Context
import java.io.File

/** Tiny storage helper: the chosen apps, the copied video file and the on/off switch. */
object Store {
    private const val PREFS = "videogate"
    private const val KEY_APPS = "apps"
    private const val KEY_ENABLED = "enabled"

    private fun prefs(ctx: Context) = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun videoFile(ctx: Context): File = File(ctx.filesDir, "gate_video.mp4")

    fun hasVideo(ctx: Context): Boolean {
        val f = videoFile(ctx)
        return f.exists() && f.length() > 0
    }

    fun apps(ctx: Context): Set<String> =
        prefs(ctx).getStringSet(KEY_APPS, emptySet()) ?: emptySet()

    fun setApps(ctx: Context, apps: Set<String>) {
        prefs(ctx).edit().putStringSet(KEY_APPS, HashSet(apps)).apply()
    }

    fun enabled(ctx: Context): Boolean = prefs(ctx).getBoolean(KEY_ENABLED, true)

    fun setEnabled(ctx: Context, value: Boolean) {
        prefs(ctx).edit().putBoolean(KEY_ENABLED, value).apply()
    }
}
'''

FILES["app/src/main/java/com/alok/videogate/MainActivity.kt"] = r'''package com.alok.videogate

import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import java.io.FileOutputStream

class MainActivity : Activity() {

    private val reqVideo = 101
    private lateinit var status: TextView
    private lateinit var toggle: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val pad = (16 * resources.displayMetrics.density).toInt()
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad, pad, pad)
        }

        root.addView(TextView(this).apply {
            text = "VideoGate"
            textSize = 26f
        })
        root.addView(TextView(this).apply {
            text = "Plays your video every time you open a chosen app. The app opens only after the video ends."
            setPadding(0, pad / 2, 0, pad)
        })

        status = TextView(this).apply {
            textSize = 16f
            setPadding(0, 0, 0, pad)
        }
        root.addView(status)

        root.addView(button("1. Choose video") { pickVideo() })
        root.addView(button("2. Choose apps") { pickApps() })
        root.addView(button("3. Turn on accessibility service") {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        })

        toggle = button("") {
            Store.setEnabled(this, !Store.enabled(this))
            refresh()
        }
        root.addView(toggle)

        root.addView(button("Test the video overlay now") {
            val svc = GateService.instance
            if (svc == null) {
                toast("Turn on the accessibility service first")
            } else if (!Store.hasVideo(this)) {
                toast("Choose a video first")
            } else {
                svc.showOverlay(null)
            }
        })
        root.addView(button("Can't switch the service on? Open app info") {
            // On Android 13+ open the 3-dot menu there and tap "Allow restricted settings"
            startActivity(
                Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                    .setData(Uri.parse("package:$packageName"))
            )
        })

        root.addView(TextView(this).apply {
            text = "Stuck on the video? Tap the screen 5 times quickly to skip it. " +
                "You can also open VideoGate and tap Pause."
            textSize = 13f
            setPadding(0, pad, 0, 0)
        })

        setContentView(ScrollView(this).apply { addView(root) })
    }

    override fun onResume() {
        super.onResume()
        refresh()
    }

    private fun button(label: String, onClick: () -> Unit): Button =
        Button(this).apply {
            text = label
            isAllCaps = false
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            )
            setOnClickListener { onClick() }
        }

    private fun toast(msg: String) = Toast.makeText(this, msg, Toast.LENGTH_LONG).show()

    private fun refresh() {
        val n = Store.apps(this).size
        val sb = StringBuilder()
        sb.append(if (Store.hasVideo(this)) "[OK] Video ready" else "[ ] No video chosen").append("\n")
        sb.append(if (n > 0) "[OK] Apps selected: $n" else "[ ] No apps selected").append("\n")
        sb.append(if (serviceEnabled()) "[OK] Accessibility service is ON" else "[ ] Accessibility service is OFF").append("\n")
        sb.append(if (Store.enabled(this)) "[OK] VideoGate is ACTIVE" else "[ ] VideoGate is PAUSED")
        status.text = sb.toString()
        toggle.text = if (Store.enabled(this)) "Pause VideoGate" else "Resume VideoGate"
    }

    private fun serviceEnabled(): Boolean {
        val enabled = Settings.Secure.getString(
            contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        ) ?: return false
        return enabled.contains("$packageName/") && enabled.contains("GateService")
    }

    private fun pickVideo() {
        val i = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "video/*"
        }
        startActivityForResult(i, reqVideo)
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != reqVideo || resultCode != RESULT_OK) return
        val uri = data?.data ?: return
        toast("Copying video...")
        Thread {
            var ok = true
            try {
                contentResolver.openInputStream(uri)?.use { input ->
                    FileOutputStream(Store.videoFile(this)).use { out -> input.copyTo(out) }
                } ?: run { ok = false }
            } catch (e: Exception) {
                ok = false
            }
            runOnUiThread {
                toast(if (ok) "Video saved" else "Could not read that video")
                refresh()
            }
        }.start()
    }

    private fun pickApps() {
        val pm = packageManager
        val launch = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        val apps = pm.queryIntentActivities(launch, 0)
            .map { it.activityInfo.packageName to it.loadLabel(pm).toString() }
            .filter { it.first != packageName }
            .distinctBy { it.first }
            .sortedBy { it.second.lowercase() }

        if (apps.isEmpty()) {
            toast("No apps found")
            return
        }

        val selected = Store.apps(this).toMutableSet()
        val labels = apps.map { it.second }.toTypedArray()
        val checked = BooleanArray(apps.size) { apps[it].first in selected }

        AlertDialog.Builder(this)
            .setTitle("Apps that must play the video first")
            .setMultiChoiceItems(labels, checked) { _, which, isChecked ->
                if (isChecked) selected.add(apps[which].first) else selected.remove(apps[which].first)
            }
            .setPositiveButton("Save") { _, _ ->
                Store.setApps(this, selected)
                refresh()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
'''

FILES["app/src/main/java/com/alok/videogate/GateService.kt"] = r'''package com.alok.videogate

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.graphics.Color
import android.graphics.PixelFormat
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.view.Gravity
import android.view.KeyEvent
import android.view.ViewGroup
import android.view.WindowManager
import android.view.accessibility.AccessibilityEvent
import android.view.inputmethod.InputMethodManager
import android.widget.FrameLayout
import android.widget.VideoView
import java.util.ArrayDeque

/**
 * Watches which app comes to the foreground. When it is one of the chosen apps,
 * a full-screen black window with the video is drawn on top. When the video ends
 * the window is removed and the app underneath is revealed.
 *
 * Loop protection (v1.1):
 *  - only real apps (launcher apps and the home screen) count as "the user switched app";
 *    system pop-ups, services and keyboards are ignored
 *  - after a video finishes, the same app is not gated again for a few seconds
 *  - if one app triggers the video 3 times within 75 s, it is paused for 3 minutes
 *  - tapping the overlay 5 times quickly skips the video
 *  - a watchdog removes the overlay shortly after the video should have ended
 */
class GateService : AccessibilityService() {

    companion object {
        @Volatile
        var instance: GateService? = null

        private const val GRACE_MS = 8_000L
        private const val NOISE_MS = 1_500L
        private const val LOOP_WINDOW_MS = 75_000L
        private const val LOOP_PAUSE_MS = 3 * 60_000L
        private const val APPS_REFRESH_MS = 60_000L
    }

    private val handler = Handler(Looper.getMainLooper())

    private var overlay: FrameLayout? = null
    private var gatedNow: String? = null
    private var shownAt = 0L
    private var leftDuringOverlay = false
    private var unlockedPkg: String? = null

    private var imePackages: Set<String> = emptySet()
    private var realApps: Set<String> = emptySet()
    private var appsRefreshedAt = 0L

    private val lastFinished = HashMap<String, Long>()
    private val pausedUntil = HashMap<String, Long>()
    private val showTimes = HashMap<String, ArrayDeque<Long>>()

    private val ignored = setOf("com.android.systemui", "android")

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        refreshApps(SystemClock.elapsedRealtime())
    }

    private fun refreshApps(now: Long) {
        appsRefreshedAt = now
        try {
            val imm = getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager
            imePackages = imm.enabledInputMethodList.map { it.packageName }.toSet()
        } catch (e: Exception) {
            // keep the old list
        }
        try {
            val set = HashSet<String>()
            val launcher = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
            val home = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME)
            packageManager.queryIntentActivities(launcher, 0).forEach { set.add(it.activityInfo.packageName) }
            packageManager.queryIntentActivities(home, 0).forEach { set.add(it.activityInfo.packageName) }
            if (set.isNotEmpty()) realApps = set
        } catch (e: Exception) {
            // keep the old list
        }
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null || event.eventType != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) return
        if (!Store.enabled(this)) return
        val pkg = event.packageName?.toString() ?: return
        val now = SystemClock.elapsedRealtime()

        if (realApps.isEmpty() || now - appsRefreshedAt > APPS_REFRESH_MS) refreshApps(now)

        // Our own overlay, system UI, keyboards and background services are not an app switch
        if (pkg == packageName || pkg in ignored || pkg in imePackages) return
        if (pkg !in realApps) return

        if (overlay != null) {
            // user went somewhere else while the video was playing
            if (pkg != gatedNow && now - shownAt > NOISE_MS) leftDuringOverlay = true
            return
        }

        if (pkg in Store.apps(this)) {
            if (pkg == unlockedPkg) return
            val finished = lastFinished[pkg]
            if (finished != null && now - finished < GRACE_MS) return
            if (!Store.hasVideo(this)) return
            if (loopTripped(pkg, now)) return
            showOverlay(pkg)
        } else {
            // user is on the home screen or another app: next open of a chosen app plays again
            unlockedPkg = null
        }
    }

    private fun loopTripped(pkg: String, now: Long): Boolean {
        val until = pausedUntil[pkg] ?: 0L
        if (now < until) return true
        val q = showTimes.getOrPut(pkg) { ArrayDeque<Long>() }
        while (q.isNotEmpty() && now - (q.peekFirst() ?: now) > LOOP_WINDOW_MS) q.pollFirst()
        if (q.size >= 2) {
            pausedUntil[pkg] = now + LOOP_PAUSE_MS
            q.clear()
            return true
        }
        q.addLast(now)
        return false
    }

    fun showOverlay(gated: String?) {
        if (overlay != null) return
        val file = Store.videoFile(this)
        if (!file.exists()) return

        val wm = getSystemService(WINDOW_SERVICE) as WindowManager

        val root = object : FrameLayout(this@GateService) {
            override fun dispatchKeyEvent(event: KeyEvent): Boolean {
                // swallow Back so the video cannot be dismissed
                if (event.keyCode == KeyEvent.KEYCODE_BACK) return true
                return super.dispatchKeyEvent(event)
            }
        }
        root.setBackgroundColor(Color.BLACK)
        root.isClickable = true               // eat touches so nothing underneath is tappable
        root.isFocusable = true
        root.isFocusableInTouchMode = true

        // emergency exit: 5 quick taps
        var taps = 0
        var firstTap = 0L
        root.setOnClickListener {
            val t = SystemClock.elapsedRealtime()
            if (t - firstTap > 2_500L) {
                firstTap = t
                taps = 0
            }
            taps++
            if (taps >= 5) {
                if (gated != null) pausedUntil[gated] = t + 2 * 60_000L
                hideOverlay(gated)
            }
        }

        val video = VideoView(this)
        root.addView(
            video,
            FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT,
                Gravity.CENTER
            )
        )

        val lp = WindowManager.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
            WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN or
                WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS or
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
            PixelFormat.OPAQUE
        )
        if (Build.VERSION.SDK_INT >= 28) {
            lp.layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
        }

        video.setOnPreparedListener { mp ->
            // watchdog: if completion never fires, remove the overlay anyway
            val ms = if (mp.duration > 0) mp.duration.toLong() else 30_000L
            handler.postDelayed({ hideOverlay(gated) }, ms + 4_000L)
        }
        video.setOnCompletionListener { hideOverlay(gated) }
        video.setOnErrorListener { _, _, _ ->
            hideOverlay(gated)   // never trap the user if the video cannot play
            true
        }
        video.setVideoPath(file.absolutePath)

        gatedNow = gated
        shownAt = SystemClock.elapsedRealtime()
        leftDuringOverlay = false

        try {
            wm.addView(root, lp)
        } catch (e: Exception) {
            gatedNow = null
            return
        }
        overlay = root
        root.requestFocus()
        video.start()
    }

    private fun hideOverlay(gated: String?) {
        val v = overlay ?: return
        overlay = null
        handler.removeCallbacksAndMessages(null)
        try {
            (v.getChildAt(0) as? VideoView)?.stopPlayback()
        } catch (e: Exception) {
            // ignore
        }
        try {
            val wm = getSystemService(WINDOW_SERVICE) as WindowManager
            wm.removeView(v)
        } catch (e: Exception) {
            // ignore
        }
        if (gated != null) lastFinished[gated] = SystemClock.elapsedRealtime()
        // if the user left the app while the video played, the next open must play again
        unlockedPkg = if (gated != null && !leftDuringOverlay) gated else null
        gatedNow = null
    }

    override fun onInterrupt() {}

    override fun onUnbind(intent: Intent?): Boolean {
        hideOverlay(null)
        instance = null
        return super.onUnbind(intent)
    }

    override fun onDestroy() {
        hideOverlay(null)
        instance = null
        super.onDestroy()
    }
}
'''


def main():
    root = "videogate"
    for path, content in FILES.items():
        full = os.path.join(root, path)
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print("wrote", full)

    os.makedirs(root, exist_ok=True)
    ks = os.path.join(root, "debug.keystore")
    with open(ks, "wb") as f:
        f.write(base64.b64decode(KEYSTORE_B64))
    print("wrote", ks)


if __name__ == "__main__":
    main()
