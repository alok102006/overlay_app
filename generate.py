"""
Writes the complete VideoGate Android project into ./videogate
Run by the GitHub Actions workflow before building. No need to run by hand.
"""
import os

FILES = {}

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
        versionCode = 1
        versionName = "1.0"
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

    <!-- Lets the app list launcher apps (Instagram, Telegram, X ...) without QUERY_ALL_PACKAGES -->
    <queries>
        <intent>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent>
    </queries>

    <application
        android:allowBackup="false"
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

/** Tiny storage helper: the chosen apps and the copied video file. */
object Store {
    private const val PREFS = "videogate"
    private const val KEY_APPS = "apps"

    fun videoFile(ctx: Context): File = File(ctx.filesDir, "gate_video.mp4")

    fun hasVideo(ctx: Context): Boolean {
        val f = videoFile(ctx)
        return f.exists() && f.length() > 0
    }

    fun apps(ctx: Context): Set<String> =
        ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getStringSet(KEY_APPS, emptySet()) ?: emptySet()

    fun setApps(ctx: Context, apps: Set<String>) {
        ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putStringSet(KEY_APPS, HashSet(apps))
            .apply()
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
        root.addView(button("Can't tap the service? Open app info") {
            // On Android 13+ open the 3-dot menu there and tap "Allow restricted settings"
            startActivity(
                Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                    .setData(Uri.parse("package:$packageName"))
            )
        })
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
        sb.append(if (serviceEnabled()) "[OK] Accessibility service is ON" else "[ ] Accessibility service is OFF")
        status.text = sb.toString()
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
import android.graphics.Color
import android.graphics.PixelFormat
import android.os.Build
import android.view.Gravity
import android.view.KeyEvent
import android.view.ViewGroup
import android.view.WindowManager
import android.view.accessibility.AccessibilityEvent
import android.view.inputmethod.InputMethodManager
import android.widget.FrameLayout
import android.widget.VideoView

/**
 * Watches which app comes to the foreground. When it is one of the chosen apps,
 * a full-screen black window with the video is drawn on top. When the video ends
 * the window is removed and the app underneath is revealed.
 */
class GateService : AccessibilityService() {

    companion object {
        @Volatile
        var instance: GateService? = null
    }

    private var overlay: FrameLayout? = null
    private var current: String? = null       // last real foreground package
    private var unlockedPkg: String? = null   // package that already played the video
    private var imePackages: Set<String> = emptySet()

    private val ignored = setOf("com.android.systemui", "android")

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        refreshIme()
    }

    private fun refreshIme() {
        try {
            val imm = getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager
            imePackages = imm.enabledInputMethodList.map { it.packageName }.toSet()
        } catch (e: Exception) {
            // keep the old list
        }
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null || event.eventType != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) return
        val pkg = event.packageName?.toString() ?: return

        // Our own overlay, system UI and keyboards are not "apps the user switched to"
        if (pkg == packageName || pkg in ignored || pkg in imePackages) return

        current = pkg
        if (overlay != null) return

        if (pkg in Store.apps(this)) {
            if (pkg != unlockedPkg && Store.hasVideo(this)) {
                showOverlay(pkg)
            }
        } else {
            // user is somewhere else (home screen, another app): next open of a gated app plays again
            unlockedPkg = null
        }
    }

    fun showOverlay(gated: String?) {
        if (overlay != null) return
        val file = Store.videoFile(this)
        if (!file.exists()) return
        refreshIme()

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

        video.setOnCompletionListener { hideOverlay(gated) }
        video.setOnErrorListener { _, _, _ ->
            hideOverlay(gated)   // never trap the user if the video cannot play
            true
        }
        video.setVideoPath(file.absolutePath)

        try {
            wm.addView(root, lp)
        } catch (e: Exception) {
            return
        }
        overlay = root
        root.requestFocus()
        video.start()
    }

    private fun hideOverlay(gated: String?) {
        val v = overlay ?: return
        overlay = null
        try {
            (v.getChildAt(0) as? VideoView)?.stopPlayback()
        } catch (e: Exception) {
        }
        try {
            val wm = getSystemService(WINDOW_SERVICE) as WindowManager
            wm.removeView(v)
        } catch (e: Exception) {
        }
        // if the user left the gated app while the video played, the next open must play again
        unlockedPkg = if (gated != null && current == gated) gated else null
    }

    override fun onInterrupt() {}

    override fun onUnbind(intent: android.content.Intent?): Boolean {
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


if __name__ == "__main__":
    main()
