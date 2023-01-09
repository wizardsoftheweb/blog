---
title: "Chrome Remote Debugging on Windows"
slug: "chrome-remote-debugging-on-windows"
date: "2017-12-25T06:29:47.000Z"
feature_image: "/images/2017/12/allow-connection-1.jpg"
author: "CJ Harries"
description: "I've had trouble with this before so I'm documenting the process. The official Google docs leave out a couple of setup steps, which is very frustrating."
tags: 
  - Google Chrome
  - Android
  - debugging
  - adb
  - DevTools
  - Windows
draft: true
---

I've had trouble with this before, apparently, so this time I'm documenting the process. [The official Google docs](https://developers.google.com/web/tools/chrome-devtools/remote-debugging/) leave out a couple of setup steps, which is seriously frustrating.

<p class="nav-p"><a id="post-nav"></a></p>

- [Drivers](#drivers)
- [Install the Android Debug Bridge](#installtheandroiddebugbridge)
    - [Fast Installation](#fastinstallation)
    - [Manual Installation](#manualinstallation)
- [Enable USB Debugging](#enableusbdebugging)
- [Launch `adb`](#launchadb)
- [Access in DevTools](#accessindevtools)
- [Sources](#sources)
- [Environment](#environment)

## Drivers

You'll need to [find your OEM USB drivers](https://developer.android.com/studio/run/oem-usb.html#Drivers) and install them. Device Manager should report the correct device when connected:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">PS&gt;</span> mmc devmgmt.msc</span><br></pre></div>
</td></tr></table>

![successful-device-manager](/images/2017/12/successful-device-manager.png)
I'm using a couple of Samsung phones, as you can see from the list.

## Install the Android Debug Bridge

You need [the Android Debug Bridge](https://developer.android.com/studio/command-line/adb.html) in addition to OEM drivers.

### Fast Installation

If you use a package manager [like Chocolatey](https://chocolatey.org/), this is pretty easy. Swap `choco` for whatever you use:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">PS></span> choco install -y adb<br><span class="go" style="color:#888">Chocolatey v0.10.7</span><br><span class="go" style="color:#888">Installing the following packages:</span><br><span class="go" style="color:#888">adb</span><br><span class="go" style="color:#888">By installing you accept licenses for the packages.</span><br><span class="go" style="color:#888">Progress: Downloading adb 1.0.39.20171026... 100%</span><br><br><span class="go" style="color:#888">adb v1.0.39.20171026 [Approved]</span><br><span class="go" style="color:#888">adb package files install completed. Performing other installation steps.</span><br><span class="go" style="color:#888">Downloading adb</span><br><span class="go" style="color:#888">  from 'https://dl-ssl.google.com/android/repository/platform-tools_r26.0.2-windows.zip'</span><br><span class="go" style="color:#888">Progress: 100% - Completed download of C:\path\to\user\AppData\Local\Temp\chocolatey\adb\1.0.39.20171026\platform-tools_r26.0.2-windows.zip (9.31 MB).</span><br><span class="go" style="color:#888">Download of platform-tools_r26.0.2-windows.zip (9.31 MB) completed.</span><br><span class="go" style="color:#888">Hashes match.</span><br><span class="go" style="color:#888">Extracting C:\path\to\user\AppData\Local\Temp\chocolatey\adb\1.0.39.20171026\platform-tools_r26.0.2-windows.zip to C:\ProgramData\chocolatey\lib\adb\tools...</span><br><span class="go" style="color:#888">C:\path\to\chocolatey\lib\adb\tools</span><br><span class="go" style="color:#888"> ShimGen has successfully created a shim for adb.exe</span><br><span class="go" style="color:#888"> ShimGen has successfully created a shim for fastboot.exe</span><br><span class="go" style="color:#888"> The install of adb was successful.</span><br><span class="go" style="color:#888">  Software installed to 'C:\path\to\chocolatey\lib\adb\tools'</span><br><br><span class="go" style="color:#888">Chocolatey installed 1/1 packages.</span><br><span class="go" style="color:#888"> See the log for details (C:\path\to\chocolatey\logs\chocolatey.log).</span><br><span class="gp" style="color:#66d9ef">PS></span> refreshenv<br><span class="go" style="color:#888">Refreshing environment variables from registry for cmd.exe. Please wait...Finished..</span><br></pre></div>
</td></tr></table>

### Manual Installation

Check [the release page](https://developer.android.com/studio/releases/platform-tools.html) to make sure the link is still current. This will install it in your home directory; it's up to you to either remember the path or add it to the environment path.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">PS></span> <span class="nb" style="color:#f8f8f2">cd</span> ~<br><span class="gp" style="color:#66d9ef">PS></span> Invoke-WebRequest -Uri <span class="s2" style="color:#e6db74">"https://dl.google.com/android/repository/platform-tools-latest-windows.zip"</span> -OutFile <span class="s2" style="color:#e6db74">"platform-tools-latest-windows.zip"</span><br><span class="gp" style="color:#66d9ef">PS></span> Expand-Archive <span class="s2" style="color:#e6db74">".\platform-tools-latest-windows.zip"</span><br><span class="gp" style="color:#66d9ef">PS></span> Move-Item <span class="s2" style="color:#e6db74">".\platform-tools-latest-windows\platform-tools"</span> <span class="s2" style="color:#e6db74">".\"</span><br><span class="gp" style="color:#66d9ef">PS></span> Rename-Item <span class="s2" style="color:#e6db74">".\platform-tools"</span> <span class="s2" style="color:#e6db74">".\android-platform-tools"</span><br><span class="gp" style="color:#66d9ef">PS></span> <span class="nb" style="color:#f8f8f2">cd</span> <span class="s2" style="color:#e6db74">".\android-platform-tools"</span><br><span class="gp" style="color:#66d9ef">PS></span> <span class="nb" style="color:#f8f8f2">dir</span><br><br><span class="go" style="color:#888">    Directory: C:\path\to\home\android-platform-tools</span><br><br><span class="go" style="color:#888">Mode                LastWriteTime         Length Name</span><br><span class="go" style="color:#888">----                -------------         ------ ----</span><br><span class="go" style="color:#888">d-----       12/24/2017  11:43 PM                api</span><br><span class="go" style="color:#888">d-----       12/24/2017  11:43 PM                lib64</span><br><span class="go" style="color:#888">d-----       12/24/2017  11:43 PM                systrace</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM        1784320 adb.exe</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM          97792 AdbWinApi.dll</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM          62976 AdbWinUsbApi.dll</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM         145920 dmtracedump.exe</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM         333824 etc1tool.exe</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM         853504 fastboot.exe</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM          43008 hprof-conv.exe</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM         210625 libwinpthread-1.dll</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM         345600 make_f2fs.exe</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM           1184 mke2fs.conf</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM        1034240 mke2fs.exe</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM         323847 NOTICE.txt</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM             38 source.properties</span><br><span class="go" style="color:#888">-a----       12/13/2017   9:24 PM         793600 sqlite3.exe</span><br></pre></div>
</td></tr></table>

## Enable USB Debugging

Follow [the official instructions](https://developer.android.com/studio/debug/dev-options.html#enable) (most likely tap `Settings > About Phone > Build Number` several times) to enable Developer Options. After doing so, a new line, `Developer options`, will appear in `Settings`.

![settings-with-dev](/images/2017/12/settings-with-dev.jpg)

Somewhere in `Developer options` should be a toggle switch to enable USB debugging.

![dev-usb-debugging](/images/2017/12/dev-usb-debugging.jpg)

## Launch `adb`

With USB debugging turned on and the phone connected to your computer, launch `adb`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">PS></span> adb devices<br><span class="go" style="color:#888">List of devices attached</span><br><span class="go" style="color:#888">* daemon not running. starting it now at tcp:5037 *</span><br><span class="go" style="color:#888">* daemon started successfully *</span><br><span class="go" style="color:#888">somehash    unauthorized</span><br></pre></div>
</td></tr></table>

On your phone, allow the connection (if the fingerprint checks out).

![allow-connection](/images/2017/12/allow-connection.jpg)

Verify the device connected properly via `adb`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">PS></span> adb devices<br><span class="go" style="color:#888">List of devices attached</span><br><span class="go" style="color:#888">somehash    device</span><br></pre></div>
</td></tr></table>

## Access in DevTools

[Visit `chrome://inspect/#devices`](chrome://inspect/#devices) to make sure the device is connected. You must be signed in. [The official docs](https://developers.google.com/web/tools/chrome-devtools/remote-debugging/#debug) explain this part well.

## Sources

I used [this XDA post](https://www.xda-developers.com/install-adb-windows-macos-linux/) as a basis for `adb` installation. I later discovered [this StackOverflow answer](https://stackoverflow.com/a/22028058/2877698) while researching some issues. I wrote all the PowerShell and created all the images.

## Environment

<blockquote class="twitter-tweet" data-lang="en"><p lang="en" dir="ltr">That&#39;s a great question. I was using a Samsung Galaxy S6 and a Note8. I&#39;m not sure what the exact Chrome version was; I was running whatever was stable and current last December. The OS was Win10 Insider build 17025.</p>&mdash; CJ Harries (@wizardsoftheweb) <a href="https://twitter.com/wizardsoftheweb/status/951915376350285824?ref_src=twsrc%5Etfw">January 12, 2018</a></blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
