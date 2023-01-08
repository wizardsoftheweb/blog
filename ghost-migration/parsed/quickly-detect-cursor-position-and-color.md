---
title: "Quickly Detect Cursor Position and Color"
slug: "quickly-detect-cursor-position-and-color"
date: "2018-01-14T20:00:00.000Z"
feature_image: "/images/2018/01/--Code-@wizardsoftheweb-wotw-macro-scratch.parser.py--wotw-macro----Sublime-Text_002.png"
author: "CJ Harries"
description: "I miss AutoHotkey. I spent this weekend in Google and Stack Overflow porting a couple of very basic features for the X world."
tags: 
  - Automation
  - Python
  - Xlib
  - python-xlib
  - pyautogui
  - X11
  - Linux
  - cursor
  - xdotool
  - bash
draft: true
---

I've been absolutely thrilled moving my home dev world back to Fedora. I'm not fighting OS ads, virtualization just works, and my settings actually stay the same after updates. I am, however, missing [AutoHotkey](https://autohotkey.com/). It's been an integral part of my computing world since undergrad. I've spent the better part of three years looking for a POSIX AHK clone with no luck.

I've tossed around the idea of starting something similar for some time now. Obviously I don't have the expertise to make anything near as streamlined as AHK, but I do have the muleheadness to spend an entire weekend trying to bum a word or two from an `awk` chain. Tenacity is a useful trait when you have absolutely no idea what you're doing.

<p class="nav-p"><a id="post-nav"></a></p>

- [Background](#background)
- [Software](#software)
- [My First Cursor Position](#myfirstcursorposition)
- [`pyautogui`](#pyautogui)
- [Frankenstein](#frankenstein)
  - [`bash`](#bash)
  - [Disconnected and Secure](#disconnectedandsecure)
  - [Chained](#chained)
  - [Shelled](#shelled)
- [Xlib](#xlib)
  - [Caveats](#caveats)

## Background

Several months ago I began drafting a project along these lines. I think [RobotJS](http://robotjs.io/) is pretty neat, and I've been looking for an excuse to use it. Bundling it via [Electron](https://electronjs.org/) would make the result consumable everywhere, sidestepping the AHK-proprietary concern.

However, Electron is a Chromium wrapper. It's got a ton of bloat and the whole Chromium thing to worry about. I typically hit my macros pretty hard, so an app that has to juggle many intensive GUI actions while being an intensive GUI might not be the best. (Note: I didn't actually pursue this, so I could be totally wrong and Electron might be faster.) I decided to mess around with a few other ideas this weekend.

I'd like to build something simple this weekend to figure out a few new components. I don't have any set goals, but these things are in the back of my head:

* Lightweight: When Electron is your baseline everything's an improvement
* Cross-platform: If nothing else, the RHEL and Debian ecosystems
* Fast: I feel like 10+ ops a second isn't asking too much

## Software

I mention some software during this post. I install everything here, but I remove some of it later. YMMV. If you're in the Debian ecosystem, this should work but the packages will probably have completely different names.

* [`xdotool` and its dependencies](http://www.semicomplete.com/projects/xdotool/)
    

    <table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
    <div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install xdotool<br></pre></div>
    </td></tr></table>

* [ImageMagick](https://www.imagemagick.org/script/download.php)
    

    <table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
    <div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install ImageMagick<br></pre></div>
    </td></tr></table>

* `xwd`: You might have to hunt for this executable's provider.
    

    <table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
    <div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> dnf provides xwd<br><span class="go" style="color:#888">Last metadata expiration check: 0:10:01 ago on Sun 14 Jan 2018 06:28:40 AM UTC.</span><br><span class="go" style="color:#888">xorg-x11-apps-7.7-18.fc27.x86_64 : X.Org X11 applications</span><br><span class="go" style="color:#888">Repo        : fedora</span><br><span class="go" style="color:#888">Matched from:</span><br><span class="go" style="color:#888">Provide    : xwd = 1.0.6</span><br><span class="gp" style="color:#66d9ef">$</span> sudo dnf install xorg-x11-apps<br></pre></div>
    </td></tr></table>

* Depending on your Python setup, you might already have these external dependencies.

    

    <table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
    <div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install <span class="se" style="color:#ae81ff">\</span><br>        python<span class="o" style="color:#f92672">{</span><span class="m" style="color:#ae81ff">2</span>,3<span class="o" style="color:#f92672">}</span>-<span class="o" style="color:#f92672">{</span>tkinter,xlib<span class="o" style="color:#f92672">}</span> <span class="se" style="color:#ae81ff">\</span><br>        scrot<br></pre></div>
    </td></tr></table>

* Finally, for good measure, check the `pip` dependencies:

    

    <table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
    <div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> pip install --user <span class="se" style="color:#ae81ff">\</span><br>        pyautogui <span class="se" style="color:#ae81ff">\</span><br>        Xlib<br></pre></div>
    </td></tr></table>

## My First Cursor Position

You can't automate the mouse if you don't know where it is. `xdotool` provides fast and easy access to the cursor (among other things!).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> xdotool getmouselocation<br><span class="go" style="color:#888">x:2478 y:1603 screen:0 window:48234503</span><br><span class="gp" style="color:#66d9ef">$</span> xdotool getmouselocation --shell<br><span class="go" style="color:#888">X=2468</span><br><span class="go" style="color:#888">Y=1265</span><br><span class="go" style="color:#888">SCREEN=0</span><br><span class="go" style="color:#888">WINDOW=48234503</span><br><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">eval</span> <span class="k" style="color:#66d9ef">$(</span>xdotool getmouselocation --shell<span class="k" style="color:#66d9ef">)</span><span class="p">;</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="nv" style="color:#f8f8f2">$X</span><br><span class="go" style="color:#888">2468</span><br><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">eval</span> <span class="k" style="color:#66d9ef">$(</span>xdotool getmouselocation --shell<span class="k" style="color:#66d9ef">)</span><span class="p">;</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="nv" style="color:#f8f8f2">$X</span><br><span class="go" style="color:#888">2873</span><br><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">eval</span> <span class="k" style="color:#66d9ef">$(</span>xdotool getmouselocation --shell<span class="k" style="color:#66d9ef">)</span><span class="p">;</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="nv" style="color:#f8f8f2">$X</span><br><span class="go" style="color:#888">2456</span><br></pre></div>
</td></tr></table>

The only downside is trying to consume this. It might be a better idea to try native options.

## `pyautogui`

`pyautogui` is one of those native options. Al Sweigart wrote [a great little intro](https://automatetheboringstuff.com/chapter18/) that I highly recommend reading. The tool is simple and fast, which is what we're looking for.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">pyautogui-geometry.py</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f"> 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="sd" style="color:#e6db74">"""This file illustrates a basic pyautogui setup"""</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">__future__</span> <span class="kn" style="color:#f92672">import</span> <span class="n">print_function</span><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">time</span><br><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">pyautogui</span><br><br><span class="n">START</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><span class="n">SCREEN_WIDTH</span><span class="p">,</span> <span class="n">SCREEN_HEIGHT</span> <span class="o" style="color:#f92672">=</span> <span class="n">pyautogui</span><span class="o" style="color:#f92672">.</span><span class="n">size</span><span class="p">()</span><br><span class="n">MOUSE_X</span><span class="p">,</span> <span class="n">MOUSE_Y</span> <span class="o" style="color:#f92672">=</span> <span class="n">pyautogui</span><span class="o" style="color:#f92672">.</span><span class="n">position</span><span class="p">()</span><br><span class="n">END</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Screen: </span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">x</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">SCREEN_WIDTH</span><span class="p">,</span> <span class="n">SCREEN_HEIGHT</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Mouse: (</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">,</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">)"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">MOUSE_X</span><span class="p">,</span> <span class="n">MOUSE_Y</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Start: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">START</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"End: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Difference: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span> <span class="o" style="color:#f92672">-</span> <span class="n">START</span><span class="p">))</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> python scripts/pyautogui-geometry.py<br><span class="go" style="color:#888">Screen: 3000x1920</span><br><span class="go" style="color:#888">Mouse: (2570,1597)</span><br><span class="go" style="color:#888">Start: 1515917871.17</span><br><span class="go" style="color:#888">End: 1515917871.17</span><br><span class="go" style="color:#888">Difference: 0.000105142593384</span><br></pre></div>
</td></tr></table>

`pyautogui` can also work with the screen's images and colors. Detecting color under the cursor is a great way to trigger actions, especially in routine applications.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">pyautogui-pixel-color.py</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f"> 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/usr/bin/env python</span><br><span class="sd" style="color:#e6db74">"""This file illustrates using pyautogui to check a pixel's color"""</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">__future__</span> <span class="kn" style="color:#f92672">import</span> <span class="n">print_function</span><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">time</span><br><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">pyautogui</span><br><br><span class="n">START</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><span class="n">SCREEN_WIDTH</span><span class="p">,</span> <span class="n">SCREEN_HEIGHT</span> <span class="o" style="color:#f92672">=</span> <span class="n">pyautogui</span><span class="o" style="color:#f92672">.</span><span class="n">size</span><span class="p">()</span><br><span class="n">MOUSE_X</span><span class="p">,</span> <span class="n">MOUSE_Y</span> <span class="o" style="color:#f92672">=</span> <span class="n">pyautogui</span><span class="o" style="color:#f92672">.</span><span class="n">position</span><span class="p">()</span><br><span class="n">PIXEL</span> <span class="o" style="color:#f92672">=</span> <span class="n">pyautogui</span><span class="o" style="color:#f92672">.</span><span class="n">screenshot</span><span class="p">(</span><br>    <span class="n">region</span><span class="o" style="color:#f92672">=</span><span class="p">(</span><br>        <span class="n">MOUSE_X</span><span class="p">,</span> <span class="n">MOUSE_Y</span><span class="p">,</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">,</span> <span class="mi" style="color:#ae81ff">1</span><br>    <span class="p">)</span><br><span class="p">)</span><br><span class="n">COLOR</span> <span class="o" style="color:#f92672">=</span> <span class="n">PIXEL</span><span class="o" style="color:#f92672">.</span><span class="n">getcolors</span><span class="p">()</span><br><span class="n">END</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Screen: </span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">x</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">SCREEN_WIDTH</span><span class="p">,</span> <span class="n">SCREEN_HEIGHT</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Mouse: (</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">,</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">)"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">MOUSE_X</span><span class="p">,</span> <span class="n">MOUSE_Y</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"RGB: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">COLOR</span><span class="p">[</span><span class="mi" style="color:#ae81ff">0</span><span class="p">][</span><span class="mi" style="color:#ae81ff">1</span><span class="p">]</span><span class="o" style="color:#f92672">.</span><span class="fm" style="color:#a6e22e">__str__</span><span class="p">()))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Start: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">START</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"End: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Difference: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span> <span class="o" style="color:#f92672">-</span> <span class="n">START</span><span class="p">))</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> python scripts/pyautogui-pixel-color.py<br><span class="go" style="color:#888">Screen: 3000x1920</span><br><span class="go" style="color:#888">Mouse: (2731,1766)</span><br><span class="go" style="color:#888">RGB: (20, 21, 22)</span><br><span class="go" style="color:#888">Start: 1515918345.91</span><br><span class="go" style="color:#888">End: 1515918346.19</span><br><span class="go" style="color:#888">Difference: 0.282289028168</span><br></pre></div>
</td></tr></table>

Unfortunately, `pyautogui` is super slow. No matter what, it screenshots everything, then returns what you requested.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">pyautogui-pixel-color.py</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f"> 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="sd" style="color:#e6db74">"""This file illustrates the similar run time between regions and full screenshots"""</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">__future__</span> <span class="kn" style="color:#f92672">import</span> <span class="n">print_function</span><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">time</span><br><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">pyautogui</span><br><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s1" style="color:#e6db74">'Using a region'</span><span class="p">)</span><br><span class="n">START</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><span class="n">SCREEN_WIDTH</span><span class="p">,</span> <span class="n">SCREEN_HEIGHT</span> <span class="o" style="color:#f92672">=</span> <span class="n">pyautogui</span><span class="o" style="color:#f92672">.</span><span class="n">size</span><span class="p">()</span><br><span class="n">MOUSE_X</span><span class="p">,</span> <span class="n">MOUSE_Y</span> <span class="o" style="color:#f92672">=</span> <span class="n">pyautogui</span><span class="o" style="color:#f92672">.</span><span class="n">position</span><span class="p">()</span><br><span class="n">PIXEL</span> <span class="o" style="color:#f92672">=</span> <span class="n">pyautogui</span><span class="o" style="color:#f92672">.</span><span class="n">screenshot</span><span class="p">(</span><br>    <span class="n">region</span><span class="o" style="color:#f92672">=</span><span class="p">(</span><br>        <span class="n">MOUSE_X</span><span class="p">,</span> <span class="n">MOUSE_Y</span><span class="p">,</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">,</span> <span class="mi" style="color:#ae81ff">1</span><br>    <span class="p">)</span><br><span class="p">)</span><br><span class="n">COLOR</span> <span class="o" style="color:#f92672">=</span> <span class="n">PIXEL</span><span class="o" style="color:#f92672">.</span><span class="n">getcolors</span><span class="p">()</span><br><span class="n">END</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Screen: </span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">x</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">SCREEN_WIDTH</span><span class="p">,</span> <span class="n">SCREEN_HEIGHT</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Mouse: (</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">,</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">)"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">MOUSE_X</span><span class="p">,</span> <span class="n">MOUSE_Y</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"RGB: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">COLOR</span><span class="p">[</span><span class="mi" style="color:#ae81ff">0</span><span class="p">][</span><span class="mi" style="color:#ae81ff">1</span><span class="p">]</span><span class="o" style="color:#f92672">.</span><span class="fm" style="color:#a6e22e">__str__</span><span class="p">()))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Start: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">START</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"End: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Difference: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span> <span class="o" style="color:#f92672">-</span> <span class="n">START</span><span class="p">))</span><br><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"="</span> <span class="o" style="color:#f92672">*</span> <span class="mi" style="color:#ae81ff">10</span><span class="p">)</span><br><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s1" style="color:#e6db74">'Full screen'</span><span class="p">)</span><br><span class="n">START</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><span class="n">SCREEN_WIDTH</span><span class="p">,</span> <span class="n">SCREEN_HEIGHT</span> <span class="o" style="color:#f92672">=</span> <span class="n">pyautogui</span><span class="o" style="color:#f92672">.</span><span class="n">size</span><span class="p">()</span><br><span class="n">MOUSE_X</span><span class="p">,</span> <span class="n">MOUSE_Y</span> <span class="o" style="color:#f92672">=</span> <span class="n">pyautogui</span><span class="o" style="color:#f92672">.</span><span class="n">position</span><span class="p">()</span><br><span class="n">PIXEL</span> <span class="o" style="color:#f92672">=</span> <span class="n">pyautogui</span><span class="o" style="color:#f92672">.</span><span class="n">screenshot</span><span class="p">()</span><br><span class="n">COLOR</span> <span class="o" style="color:#f92672">=</span> <span class="n">PIXEL</span><span class="o" style="color:#f92672">.</span><span class="n">getcolors</span><span class="p">()</span><br><span class="n">END</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Screen: </span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">x</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">SCREEN_WIDTH</span><span class="p">,</span> <span class="n">SCREEN_HEIGHT</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Mouse: (</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">,</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">)"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">MOUSE_X</span><span class="p">,</span> <span class="n">MOUSE_Y</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Start: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">START</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"End: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Difference: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span> <span class="o" style="color:#f92672">-</span> <span class="n">START</span><span class="p">))</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> python scripts/pyautogui-full-vs-region.py<br><span class="go" style="color:#888">Using a region</span><br><span class="go" style="color:#888">Screen: 3000x1920</span><br><span class="go" style="color:#888">Mouse: (2416,1456)</span><br><span class="go" style="color:#888">RGB: (20, 21, 22)</span><br><span class="go" style="color:#888">Start: 1515919266.8</span><br><span class="go" style="color:#888">End: 1515919267.09</span><br><span class="go" style="color:#888">Difference: 0.286885023117</span><br><span class="go" style="color:#888">==========</span><br><span class="go" style="color:#888">Full screen</span><br><span class="go" style="color:#888">Screen: 3000x1920</span><br><span class="go" style="color:#888">Mouse: (2416,1456)</span><br><span class="go" style="color:#888">Start: 1515919267.09</span><br><span class="go" style="color:#888">End: 1515919267.37</span><br><span class="go" style="color:#888">Difference: 0.281718969345</span><br></pre></div>
</td></tr></table>

Smaller screens will do better; [the docs mention this](https://pyautogui.readthedocs.io/en/latest/screenshot.html#the-screenshot-function). I was able to cut my time by disabling my second screen. That's neither fun nor practical, so I put `pyautogui` aside for now.

## Frankenstein

I have to admit, I was kinda stumped at this point. `pyautogui` is well-written and seriously vetted. I too would have gone the screenshot route, which means I too would be much too slow. A different approach is necessary, but I don't know what.

Luckily I stumbled into `xwd` via [a wonderfully succinct `bash` solution](https://stackoverflow.com/a/25498342/2877698). It's the [`X` `W`indow `D`umping utility](http://www.xfree86.org/current/xwd.1.html). That's insanely useful here, since X is what runs the system. `xwd`, in theory, has all of the screen information I could want. The linked solution uses ImageMagick [to convert the dump](https://github.com/ImageMagick/ImageMagick/blob/master/coders/xwd.c); not only did I not know it was possible to get an X dump, I also did not know ImageMagick would parse it beautifully (I would have guessed that part eventually).

### `bash`
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">xwd-convert.sh</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://stackoverflow.com/a/25498342/2877698" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f"> 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><span class="c1" style="color:#75715e"># Original:</span><br><span class="c1" style="color:#75715e"># https://stackoverflow.com/a/25498342/2877698</span><br><span class="c1" style="color:#75715e"># I've made a couple of tweaks; nothing substantial</span><br><span class="nv" style="color:#f8f8f2">start</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span>date +%s%3N<span class="k" style="color:#66d9ef">)</span><br><span class="nb" style="color:#f8f8f2">eval</span> <span class="k" style="color:#66d9ef">$(</span>xdotool getmouselocation --shell<span class="k" style="color:#66d9ef">)</span><br>xwd -root -screen -silent <span class="p">|</span> convert xwd:- -crop <span class="s2" style="color:#e6db74">"1x1+</span><span class="nv" style="color:#f8f8f2">$X</span><span class="s2" style="color:#e6db74">+</span><span class="nv" style="color:#f8f8f2">$Y</span><span class="s2" style="color:#e6db74">"</span> txt:-<br><span class="nv" style="color:#f8f8f2">end</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span>date +%s%3N<span class="k" style="color:#66d9ef">)</span><br><br><span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"Start: </span><span class="nv" style="color:#f8f8f2">$start</span><span class="s2" style="color:#e6db74">"</span><br><span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"End: </span><span class="nv" style="color:#f8f8f2">$end</span><span class="s2" style="color:#e6db74">"</span><br><span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"Difference: </span><span class="k" style="color:#66d9ef">$((</span><span class="nv" style="color:#f8f8f2">$end</span> <span class="o" style="color:#f92672">-</span> <span class="nv" style="color:#f8f8f2">$start</span><span class="k" style="color:#66d9ef">))</span><span class="s2" style="color:#e6db74">"</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> scripts/xwd-convert.sh<br><span class="go" style="color:#888">ImageMagick pixel enumeration: 1,1,65535,srgb</span><br><span class="go" style="color:#888">0,0: (5140,5397,5654)  #141516  srgb(20,21,22)</span><br><span class="go" style="color:#888">Start: 1515922099742</span><br><span class="go" style="color:#888">End: 1515922100086</span><br><span class="go" style="color:#888">Difference: 344</span><br></pre></div>
</td></tr></table>

That's even slower than `pyautogui`. To be fair, we should probably build it in Python.

### Disconnected and Secure

In order to convert it to Python, we'll have to break the pipes. [Shell injection](https://en.wikipedia.org/wiki/Code_injection#Shell_injection) is no joke.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">xwd-convert-disconnected.py</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f"> 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="sd" style="color:#e6db74">"""This file runs several commands without allowing them to communicate directly"""</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">__future__</span> <span class="kn" style="color:#f92672">import</span> <span class="n">print_function</span><br><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">re</span><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">subprocess</span><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">time</span><br><br><span class="n">FULL_XDO_PATTERN</span> <span class="o" style="color:#f92672">=</span> <span class="sa" style="color:#e6db74">r</span><span class="s2" style="color:#e6db74">"""</span><br><span class="s2" style="color:#e6db74">^\s*X=(?P&lt;x&gt;\d+)    # Name x for easy access</span><br><span class="s2" style="color:#e6db74">\s+</span><br><span class="s2" style="color:#e6db74">Y=(?P&lt;y&gt;\d+)        # Name y for easy access</span><br><span class="s2" style="color:#e6db74">\s+</span><br><span class="s2" style="color:#e6db74">[\s\S]+$            # Ditch everything else</span><br><span class="s2" style="color:#e6db74">"""</span><br><br><span class="n">COMPILED_PATTERN</span> <span class="o" style="color:#f92672">=</span> <span class="n">re</span><span class="o" style="color:#f92672">.</span><span class="n">compile</span><span class="p">(</span><span class="n">FULL_XDO_PATTERN</span><span class="p">,</span> <span class="n">re</span><span class="o" style="color:#f92672">.</span><span class="n">VERBOSE</span> <span class="o" style="color:#f92672">|</span> <span class="n">re</span><span class="o" style="color:#f92672">.</span><span class="n">MULTILINE</span><span class="p">)</span><br><br><span class="n">START</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><span class="n">COORD</span> <span class="o" style="color:#f92672">=</span> <span class="n">subprocess</span><span class="o" style="color:#f92672">.</span><span class="n">check_output</span><span class="p">([</span><br>    <span class="s1" style="color:#e6db74">'xdotool'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'getmouselocation'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'--shell'</span><br><span class="p">])</span><br><span class="n">MATCHED</span> <span class="o" style="color:#f92672">=</span> <span class="n">COMPILED_PATTERN</span><span class="o" style="color:#f92672">.</span><span class="n">match</span><span class="p">(</span><span class="n">COORD</span><span class="p">)</span><br><span class="n">DUMP</span> <span class="o" style="color:#f92672">=</span> <span class="n">subprocess</span><span class="o" style="color:#f92672">.</span><span class="n">check_output</span><span class="p">([</span><br>    <span class="s1" style="color:#e6db74">'xwd'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'-root'</span><span class="p">,</span>    <span class="c1" style="color:#75715e"># starts from the base up</span><br>    <span class="s1" style="color:#e6db74">'-screen'</span><span class="p">,</span>  <span class="c1" style="color:#75715e"># snags the visible screen for things like menus</span><br>    <span class="s1" style="color:#e6db74">'-silent'</span><span class="p">,</span>  <span class="c1" style="color:#75715e"># don't alert</span><br>    <span class="s1" style="color:#e6db74">'-out'</span><span class="p">,</span>     <span class="c1" style="color:#75715e"># outfile</span><br>    <span class="s1" style="color:#e6db74">'dump.xwd'</span><br><span class="p">])</span><br><span class="n">IMAGE</span> <span class="o" style="color:#f92672">=</span> <span class="n">subprocess</span><span class="o" style="color:#f92672">.</span><span class="n">check_output</span><span class="p">([</span><br>    <span class="s1" style="color:#e6db74">'convert'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'dump.xwd'</span><span class="p">,</span>  <span class="c1" style="color:#75715e"># infile</span><br>    <span class="s1" style="color:#e6db74">'-crop'</span><span class="p">,</span>    <span class="c1" style="color:#75715e"># restrict the image to the cursor</span><br>    <span class="s1" style="color:#e6db74">'1x1+</span><span class="si" style="color:#e6db74">%s</span><span class="s1" style="color:#e6db74">+</span><span class="si" style="color:#e6db74">%s</span><span class="s1" style="color:#e6db74">'</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">MATCHED</span><span class="o" style="color:#f92672">.</span><span class="n">group</span><span class="p">(</span><span class="s1" style="color:#e6db74">'x'</span><span class="p">),</span> <span class="n">MATCHED</span><span class="o" style="color:#f92672">.</span><span class="n">group</span><span class="p">(</span><span class="s1" style="color:#e6db74">'y'</span><span class="p">)),</span><br>    <span class="s1" style="color:#e6db74">'text:-'</span>    <span class="c1" style="color:#75715e"># throw out on stdout</span><br><span class="p">])</span><br><span class="n">END</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="n">COORD</span><span class="p">)</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="n">IMAGE</span><span class="p">)</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Start: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">START</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"End: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Difference: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span> <span class="o" style="color:#f92672">-</span> <span class="n">START</span><span class="p">))</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> python scripts/xwd-convert-disconnected.py<br><span class="go" style="color:#888">X=2291</span><br><span class="go" style="color:#888">Y=1551</span><br><span class="go" style="color:#888">SCREEN=0</span><br><span class="go" style="color:#888">WINDOW=48234503</span><br><br><span class="go" style="color:#888">ImageMagick pixel enumeration: 1,1,65535,srgb</span><br><span class="go" style="color:#888">0,0: (9766,35723,53970)  #268BD2  srgb(38,139,210)</span><br><br><span class="go" style="color:#888">Start: 1515923808.71</span><br><span class="go" style="color:#888">End: 1515923809.05</span><br><span class="go" style="color:#888">Difference: 0.338629961014</span><br></pre></div>
</td></tr></table>

However, that didn't seem to give us any extra time. Chaining the commands might work in our favor here.

### Chained

Rather than totally isolate the commands, we can redirect their output. It's not quite a shell, as the output from one is finished and sanitized before being sent on, but it functions in a similar manner.

I spent at least an hour trying to figure out how to multiplex stdin on the file command. If you know of a clever way to do that without setting environment variables, I'd love to hear about it. I wasn't able to come up with anything that worked, so the coordinates aren't part of the pipe chain.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">xwd-convert-chained.py</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f"> 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="sd" style="color:#e6db74">"""This file runs several commands by linking stdout and stdin in subprocesses"""</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">__future__</span> <span class="kn" style="color:#f92672">import</span> <span class="n">print_function</span><br><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">re</span><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">subprocess</span><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">time</span><br><br><span class="n">FULL_XDO_PATTERN</span> <span class="o" style="color:#f92672">=</span> <span class="sa" style="color:#e6db74">r</span><span class="s2" style="color:#e6db74">"""</span><br><span class="s2" style="color:#e6db74">^\s*X=(?P&lt;x&gt;\d+)    # Name x for easy access</span><br><span class="s2" style="color:#e6db74">\s+</span><br><span class="s2" style="color:#e6db74">Y=(?P&lt;y&gt;\d+)        # Name y for easy access</span><br><span class="s2" style="color:#e6db74">\s+</span><br><span class="s2" style="color:#e6db74">[\s\S]+$            # Ditch everything else</span><br><span class="s2" style="color:#e6db74">"""</span><br><br><span class="n">COMPILED_PATTERN</span> <span class="o" style="color:#f92672">=</span> <span class="n">re</span><span class="o" style="color:#f92672">.</span><span class="n">compile</span><span class="p">(</span><span class="n">FULL_XDO_PATTERN</span><span class="p">,</span> <span class="n">re</span><span class="o" style="color:#f92672">.</span><span class="n">VERBOSE</span> <span class="o" style="color:#f92672">|</span> <span class="n">re</span><span class="o" style="color:#f92672">.</span><span class="n">MULTILINE</span><span class="p">)</span><br><br><span class="n">START</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><span class="n">COORD</span> <span class="o" style="color:#f92672">=</span> <span class="n">subprocess</span><span class="o" style="color:#f92672">.</span><span class="n">check_output</span><span class="p">([</span><br>    <span class="s1" style="color:#e6db74">'xdotool'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'getmouselocation'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'--shell'</span><br><span class="p">])</span><br><span class="n">MATCHED</span> <span class="o" style="color:#f92672">=</span> <span class="n">COMPILED_PATTERN</span><span class="o" style="color:#f92672">.</span><span class="n">match</span><span class="p">(</span><span class="n">COORD</span><span class="p">)</span><br><span class="n">IMAGE</span> <span class="o" style="color:#f92672">=</span> <span class="n">subprocess</span><span class="o" style="color:#f92672">.</span><span class="n">Popen</span><span class="p">(</span><br>    <span class="p">[</span><br>        <span class="s1" style="color:#e6db74">'convert'</span><span class="p">,</span><br>        <span class="s1" style="color:#e6db74">'xwd:-'</span><span class="p">,</span><br>        <span class="s1" style="color:#e6db74">'-crop'</span><span class="p">,</span>    <span class="c1" style="color:#75715e"># restrict the image to the cursor</span><br>        <span class="s1" style="color:#e6db74">'1x1+</span><span class="si" style="color:#e6db74">%s</span><span class="s1" style="color:#e6db74">+</span><span class="si" style="color:#e6db74">%s</span><span class="s1" style="color:#e6db74">'</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">MATCHED</span><span class="o" style="color:#f92672">.</span><span class="n">group</span><span class="p">(</span><span class="s1" style="color:#e6db74">'x'</span><span class="p">),</span> <span class="n">MATCHED</span><span class="o" style="color:#f92672">.</span><span class="n">group</span><span class="p">(</span><span class="s1" style="color:#e6db74">'y'</span><span class="p">)),</span><br>        <span class="s1" style="color:#e6db74">'text:-'</span>    <span class="c1" style="color:#75715e"># throw out on stdout</span><br>    <span class="p">],</span><br>    <span class="n">stdin</span><span class="o" style="color:#f92672">=</span><span class="n">subprocess</span><span class="o" style="color:#f92672">.</span><span class="n">PIPE</span><span class="p">,</span><br>    <span class="n">stdout</span><span class="o" style="color:#f92672">=</span><span class="n">subprocess</span><span class="o" style="color:#f92672">.</span><span class="n">PIPE</span><span class="p">,</span><br><span class="p">)</span><br><span class="n">DUMP</span> <span class="o" style="color:#f92672">=</span> <span class="n">subprocess</span><span class="o" style="color:#f92672">.</span><span class="n">Popen</span><span class="p">(</span><br>    <span class="p">[</span><br>        <span class="s1" style="color:#e6db74">'xwd'</span><span class="p">,</span><br>        <span class="s1" style="color:#e6db74">'-root'</span><span class="p">,</span>    <span class="c1" style="color:#75715e"># starts from the base up</span><br>        <span class="s1" style="color:#e6db74">'-screen'</span><span class="p">,</span>  <span class="c1" style="color:#75715e"># snags the visible screen for things like menus</span><br>        <span class="s1" style="color:#e6db74">'-silent'</span><span class="p">,</span>  <span class="c1" style="color:#75715e"># don't alert</span><br>    <span class="p">],</span><br>    <span class="n">stdout</span><span class="o" style="color:#f92672">=</span><span class="n">IMAGE</span><span class="o" style="color:#f92672">.</span><span class="n">stdin</span><br><span class="p">)</span><br><span class="n">OUTPUT</span> <span class="o" style="color:#f92672">=</span> <span class="n">IMAGE</span><span class="o" style="color:#f92672">.</span><span class="n">communicate</span><span class="p">()[</span><span class="mi" style="color:#ae81ff">0</span><span class="p">]</span><br><span class="n">DUMP</span><span class="o" style="color:#f92672">.</span><span class="n">wait</span><span class="p">()</span><br><span class="n">END</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="n">OUTPUT</span><span class="p">)</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Start: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">START</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"End: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Difference: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span> <span class="o" style="color:#f92672">-</span> <span class="n">START</span><span class="p">))</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> python scripts/xwd-convert-chained.py<br><span class="go" style="color:#888">ImageMagick pixel enumeration: 1,1,65535,srgb</span><br><span class="go" style="color:#888">0,0: (5140,5397,5654)  #141516  srgb(20,21,22)</span><br><br><span class="go" style="color:#888">Start: 1515929723.34</span><br><span class="go" style="color:#888">End: 1515929723.65</span><br><span class="go" style="color:#888">Difference: 0.312852144241</span><br></pre></div>
</td></tr></table>

It's still absysmally slow. We haven't actually changed how we're getting the dump and parsing it, so that makes sense.

### Shelled

**DON'T DO THIS IN PRODUCTION**. The docs will [warn you too](https://docs.python.org/2/library/subprocess.html#frequently-used-arguments). I threw this script together quickly to make sure everything was working as intended.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">xwd-convert-dangerous.py</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f"> 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17
18</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="sd" style="color:#e6db74">"""This file contains code to monitor the desktop environment"""</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">__future__</span> <span class="kn" style="color:#f92672">import</span> <span class="n">print_function</span><br><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">subprocess</span><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">time</span><br><br><span class="n">START</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><span class="n">OUTPUT</span> <span class="o" style="color:#f92672">=</span> <span class="n">subprocess</span><span class="o" style="color:#f92672">.</span><span class="n">check_output</span><span class="p">(</span><br>    <span class="s1" style="color:#e6db74">'eval $(xdotool getmouselocation --shell); '</span><br>    <span class="s1" style="color:#e6db74">'xwd -root -screen -silent '</span><br>    <span class="s1" style="color:#e6db74">'| convert xwd:- -crop "1x1+$X+$Y" text:-'</span><span class="p">,</span><br>    <span class="n">shell</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">True</span><br><span class="p">)</span><br><span class="n">END</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="n">OUTPUT</span><span class="p">)</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"START: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">START</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"End: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Difference: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span> <span class="o" style="color:#f92672">-</span> <span class="n">START</span><span class="p">))</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> python scripts/xwd-convert-dangerous.py<br><span class="go" style="color:#888">ImageMagick pixel enumeration: 1,1,65535,srgb</span><br><span class="go" style="color:#888">0,0: (5140,5397,5654)  #141516  srgb(20,21,22)</span><br><br><span class="go" style="color:#888">START: 1515930641.2</span><br><span class="go" style="color:#888">End: 1515930641.52</span><br><span class="go" style="color:#888">Difference: 0.320123195648</span><br></pre></div>
</td></tr></table>

Once again, we're not seeing a time boost because we're just shuffling code around. The important bits haven't changed.

## Xlib

I spent most of Saturday trying to figure out how to parse a `xwd` result in Python. I got absolutely nowhere. There are many good resources and several example parsers, but nothing worked out of the box for me. [The header that describes the dump](https://www.x.org/archive/X11R7.5/doc/man/man1/xwd.1.html#toc5), `XWDFile.h`, is apparently different enough across distros that, in combination with having absolutely no idea how properly parse binary files, I couldn't figure it out. I discovered this morning that I had been using a newer (or older?) version of the file with some major differences (e.g. 32bit vs 64bit) as a reference.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo find /usr -type f -name <span class="s1" style="color:#e6db74">'XWDFile.h'</span><br><span class="go" style="color:#888">/usr/include/X11/XWDFile.h</span><br></pre></div>
</td></tr></table>

However, even knowing that in hindsight, I lost interest in parsing the dumps manually somewhere around the fourth hour of knowing the byte order was wrong but having no idea how to debug it. The image at the top of this post shows some of my failed attempts to test and retry. I learned quite a bit about X11 muddling my way through it, so I was able to refine my research and started getting useful hits. Eventually, I discovered [this SO answer](https://stackoverflow.com/a/17525571/2877698), which gave me the library I needed to track down.

[The Python X Library, `python-xlib`,](https://github.com/python-xlib/python-xlib) provides some of the items from Xlib and seems to be the best package at the moment. I neither know enough about X11 nor care to spend the time comparing interfaces to fully grok the differences; many elements covered in the X11 docs ([e.g. `AllPlanes`](https://tronche.com/gui/x/xlib/display/display-macros.html#AllPlanes)) are either missing from `python-xlib` or do not appear to work as the external docs suggest. The library works, I was able to stumble my way through the hand-wavy docs, and, best of all, it blows everything else out of the water.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">xlib-color.py</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f"> 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/usr/bin/env python</span><br><span class="sd" style="color:#e6db74">"""This file demonstrates color snooping with Xlib"""</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">__future__</span> <span class="kn" style="color:#f92672">import</span> <span class="n">print_function</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">os</span> <span class="kn" style="color:#f92672">import</span> <span class="n">getenv</span><br><span class="kn" style="color:#f92672">import</span> <span class="nn" style="color:#f8f8f2">time</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">Xlib.display</span> <span class="kn" style="color:#f92672">import</span> <span class="n">Display</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">Xlib.X</span> <span class="kn" style="color:#f92672">import</span> <span class="n">ZPixmap</span><br><br><span class="c1" style="color:#75715e"># Pull display from environment</span><br><span class="n">DISPLAY_NUM</span> <span class="o" style="color:#f92672">=</span> <span class="n">getenv</span><span class="p">(</span><span class="s1" style="color:#e6db74">'DISPLAY'</span><span class="p">)</span><br><span class="c1" style="color:#75715e"># Activate discovered display (or default)</span><br><span class="n">DISPLAY</span> <span class="o" style="color:#f92672">=</span> <span class="n">Display</span><span class="p">(</span><span class="n">DISPLAY_NUM</span><span class="p">)</span><br><span class="c1" style="color:#75715e"># Specify the display's screen for convenience</span><br><span class="n">SCREEN</span> <span class="o" style="color:#f92672">=</span> <span class="n">DISPLAY</span><span class="o" style="color:#f92672">.</span><span class="n">screen</span><span class="p">()</span><br><span class="c1" style="color:#75715e"># Specify the base element</span><br><span class="n">ROOT</span> <span class="o" style="color:#f92672">=</span> <span class="n">SCREEN</span><span class="o" style="color:#f92672">.</span><span class="n">root</span><br><span class="c1" style="color:#75715e"># Store width and height</span><br><span class="n">ROOT_GEOMETRY</span> <span class="o" style="color:#f92672">=</span> <span class="n">ROOT</span><span class="o" style="color:#f92672">.</span><span class="n">get_geometry</span><span class="p">()</span><br><br><span class="c1" style="color:#75715e"># Ensure we can run this</span><br><span class="n">EXTENSION_INFO</span> <span class="o" style="color:#f92672">=</span> <span class="n">DISPLAY</span><span class="o" style="color:#f92672">.</span><span class="n">query_extension</span><span class="p">(</span><span class="s1" style="color:#e6db74">'XInputExtension'</span><span class="p">)</span><br><br><span class="n">START</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><span class="n">COORDS</span> <span class="o" style="color:#f92672">=</span> <span class="n">ROOT</span><span class="o" style="color:#f92672">.</span><span class="n">query_pointer</span><span class="p">()</span><br><span class="c1" style="color:#75715e"># Create an X dump at the coordinate we want</span><br><span class="n">DISPLAY_IMAGE</span> <span class="o" style="color:#f92672">=</span> <span class="n">ROOT</span><span class="o" style="color:#f92672">.</span><span class="n">get_image</span><span class="p">(</span><br>    <span class="n">x</span><span class="o" style="color:#f92672">=</span><span class="n">COORDS</span><span class="o" style="color:#f92672">.</span><span class="n">root_x</span><span class="p">,</span><br>    <span class="n">y</span><span class="o" style="color:#f92672">=</span><span class="n">COORDS</span><span class="o" style="color:#f92672">.</span><span class="n">root_y</span><span class="p">,</span><br>    <span class="n">width</span><span class="o" style="color:#f92672">=</span><span class="mi" style="color:#ae81ff">1</span><span class="p">,</span><br>    <span class="n">height</span><span class="o" style="color:#f92672">=</span><span class="mi" style="color:#ae81ff">1</span><span class="p">,</span><br>    <span class="n">format</span><span class="o" style="color:#f92672">=</span><span class="n">ZPixmap</span><span class="p">,</span><br>    <span class="n">plane_mask</span><span class="o" style="color:#f92672">=</span><span class="nb" style="color:#f8f8f2">int</span><span class="p">(</span><span class="s2" style="color:#e6db74">"0xFFFFFF"</span><span class="p">,</span> <span class="mi" style="color:#ae81ff">16</span><span class="p">)</span><br><span class="p">)</span><br><span class="c1" style="color:#75715e"># Strip its color info</span><br><span class="n">PIXEL</span> <span class="o" style="color:#f92672">=</span> <span class="nb" style="color:#f8f8f2">getattr</span><span class="p">(</span><span class="n">DISPLAY_IMAGE</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'data'</span><span class="p">)</span><br><span class="c1" style="color:#75715e"># Look up the color</span><br><span class="n">RESULTS</span> <span class="o" style="color:#f92672">=</span> <span class="n">SCREEN</span><span class="o" style="color:#f92672">.</span><span class="n">default_colormap</span><span class="o" style="color:#f92672">.</span><span class="n">query_colors</span><span class="p">(</span><span class="n">PIXEL</span><span class="p">)</span><br><span class="c1" style="color:#75715e"># If there are multiple, just return the last one</span><br><span class="k" style="color:#66d9ef">for</span> <span class="n">raw_color</span> <span class="ow" style="color:#f92672">in</span> <span class="n">RESULTS</span><span class="p">:</span><br>    <span class="n">final</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>        <span class="n">raw_color</span><span class="o" style="color:#f92672">.</span><span class="n">red</span><span class="p">,</span><br>        <span class="n">raw_color</span><span class="o" style="color:#f92672">.</span><span class="n">green</span><span class="p">,</span><br>        <span class="n">raw_color</span><span class="o" style="color:#f92672">.</span><span class="n">blue</span><br>    <span class="p">)</span><br><span class="n">END</span> <span class="o" style="color:#f92672">=</span> <span class="n">time</span><span class="o" style="color:#f92672">.</span><span class="n">time</span><span class="p">()</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s1" style="color:#e6db74">'#</span><span class="si" style="color:#e6db74">%04x%04x%04x</span><span class="s1" style="color:#e6db74">'</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">final</span><span class="p">[</span><span class="mi" style="color:#ae81ff">0</span><span class="p">],</span> <span class="n">final</span><span class="p">[</span><span class="mi" style="color:#ae81ff">1</span><span class="p">],</span> <span class="n">final</span><span class="p">[</span><span class="mi" style="color:#ae81ff">2</span><span class="p">]))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Start: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">START</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"End: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span><span class="p">))</span><br><span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Difference: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">END</span> <span class="o" style="color:#f92672">-</span> <span class="n">START</span><span class="p">))</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> python scripts/xlib-color.py<br><span class="go" style="color:#888">e3fb6e6d2e25</span><br><span class="go" style="color:#888">Start: 1515954353.75</span><br><span class="go" style="color:#888">End: 1515954353.75</span><br><span class="go" style="color:#888">Difference: 0.000375986099243</span><br></pre></div>
</td></tr></table>

So far, it looks like this script can consistently poll cursor colors in fewer than five milliseconds. Everything else takes at least 250 milliseconds. Depending on how fast and loose you want to play with the numbers, this solution is at least a 97.5% reduction (200 to 5) and optimistically closer to a 99.<span style="text-decoration: overline">6</span>% reduction (300 to 1).

### Caveats

I'm sort of waving my hands at a few things here because I still don't fully understand them yet.

* I do not understand the bitmap side of things, [i.e. `XYPixmap`s](https://stackoverflow.com/a/32244336/2877698). I don't feel all that good about [`ZPixmap`s either](https://lists.freedesktop.org/archives/xorg/2017-August/058896.html) but they're at least composed of RGB triplets which is something I do get.
* Speaking of `ZPixmap`s, I had quite a bit of trouble with `plane_mask`s as well. They're used [to hide unwanted bit planes](https://tronche.com/gui/x/xlib/GC/manipulating.html), which I just realized writing this sentence isn't anything more special than masking bits. That being said, it's not documented well in X11 and at all in `python-xlib`.
* The pixels in `ZPixmap`s return strange data structures. This is 100% my inexperience with Python and its advanced data types. I will eventually break down the code and figure out what it's doing.

Also, `python-xlib` is really awesome. I've made some comments that could be taken as passive aggressive stabs at the devs, and I want to make sure that misconception is cleared up. They've built some amazing software, they're working hard to make the world a better place, and I'm stoked about their contributions.

I'm going to follow this up with another post or two playing with this stuff, doing some analysis, and trying out some implementations.