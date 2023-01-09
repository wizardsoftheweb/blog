---
title: "rofi: Useful Options I"
slug: "rofi-useful-options-i"
date: "2018-01-29T02:00:00.000Z"
feature_image: "/images/2018/01/useful-options-i-header.png"
author: "CJ Harries"
description: "rofi is a neat little tool that does so many cool things. This post highlights several useful rofi options. I don't try to script anything here, so it's a fairly short read."
tags:
  - rofi
  - Linux
  - X11
  - CLI
  - tooling
  - launcher
  - sed
draft: true
---
<!-- markdownlint-disable MD037 -->

This is the sixth in a series of several posts on how to do way more than you really need to with `rofi`. It's a neat little tool that does so many cool things. I don't have a set number of posts, and I don't have a set goal. I just want to share something I find useful.

This post highlights several useful `rofi` options. I don't try to script anything here, so it's a fairly short read.

<p class="nav-p"><a id="post-nav"></a></p>

- [Assumptions](#assumptions)
- [Code](#code)
- [`combi`](#combi)
- [Cycling `modi`](#cycling-modi)
- [`sidebar-mode`](#sidebar-mode)

## Assumptions

I'm running Fedora 27. Most of the instructions are based on that OS. This will translate fairly well to other RHEL derivatives. The Debian ecosystem should also work fairly well, albeit with totally different package names. This probably won't work at all on Windows, and I have no intention of fixing that.

You're going to need a newer version of `rofi`, `>=1.4`. I'm currently running this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -version<br><span class="go" style="color:#888">Version: 1.4.2-131-git-5c5665ef (next)</span><br></pre></div>
</td></tr></table>

If you [installed from source](https://blog.wizardsoftheweb.pro/rofi-overview-and-installation#installation), you should be good to go.

## Code

You can view the code related to this post [under the `post-06-useful-options-i` tag](//github.com/thecjharries/posts-tooling-rofi/tree/post-06-useful-options-i).

## `combi`

The `combi` `modi` is, depending on your perspective, very useful or very intimidating. It combines the options from everything in its list, making it easy to look at several things without leaving the window.

At the moment, I have mine set to everything I have enabled. A nice thing about `rofi` is that it's very easy to swap out config on the fly, so I could quick run `combi` on a smaller set of of my `modi`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -show combi -combi-modi <span class="s2" style="color:#e6db74">"drun,ssh"</span><br><span class="go" style="color:#888">as opposed to</span><br><span class="gp" style="color:#66d9ef">$</span> rofi -dump-config <span class="p">|</span> grep combi-modi:<br><span class="go" style="color:#888">    combi-modi: "file_browser,top,myplugin,keys,drun,ssh,run,windowcd,window";</span><br></pre></div>
</td></tr></table>

## Cycling `modi`

Being able to switch between enabled `modi` makes `rofi` a very useful tool. Cycling should be on by default, but it never hurts to forcibly enable it.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sed <span class="se" style="color:#ae81ff">\</span><br>    --in-place<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    -E <span class="s1" style="color:#e6db74">'s/^.*\scycle:.*$/\tcycle: true;/g'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br><span class="gp" style="color:#66d9ef">$</span> diff --color --unified<span class="o" style="color:#f92672">=</span><span class="m" style="color:#ae81ff">0</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/config.rasi"</span><span class="o" style="color:#f92672">{</span>.bak,<span class="o" style="color:#f92672">}</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -28 +28 @@</span><br><span class="gd" style="color:#f92672">-/* cycle: true;*/</span><br><span class="gi" style="color:#a6e22e">+   cycle: true;</span><br></pre></div>
</td></tr></table>

The shortcuts are also useful to know.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -dump-config <span class="p">|</span> grep kb-mode<br><span class="go" style="color:#888">    kb-mode-next: "Shift+Right,Control+Tab";</span><br><span class="go" style="color:#888">    kb-mode-previous: "Shift+Left,Control+ISO_Left_Tab";</span><br></pre></div>
</td></tr></table>

## `sidebar-mode`

Another useful cycling option is `sidebar-mode`. By default, the main window gives no notification of its `modi`.

![basic-config-without-sidebar](/images/2018/01/basic-config-without-sidebar.png)

However, in `sidebar-mode`, `rofi` adds a `modi` bar that shows the active `modi` and lists other available `modi` in the current session. It also adds mouse interaction on top of the `kb-mode-*` shortcuts.

![basic-config-with-sidebar](/images/2018/01/basic-config-with-sidebar.png)

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sed <span class="se" style="color:#ae81ff">\</span><br>    --in-place<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    -E <span class="s1" style="color:#e6db74">'s/^.*\ssidebar-mode:.*$/\tsidebar-mode: true;/g'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br><span class="gp" style="color:#66d9ef">$</span> diff --color --unified<span class="o" style="color:#f92672">=</span><span class="m" style="color:#ae81ff">0</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/config.rasi"</span><span class="o" style="color:#f92672">{</span>.bak,<span class="o" style="color:#f92672">}</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -29 +29 @@</span><br><span class="gd" style="color:#f92672">-/* sidebar-mode: false;*/</span><br><span class="gi" style="color:#a6e22e">+   sidebar-mode: true;</span><br></pre></div>
</td></tr></table>

It can get a bit cramped the more `modi` you enable. I don't mind it while I'm learning everything, but I will eventually slim it down. YMMV.
