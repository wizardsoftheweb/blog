---
title: "rofi: Overview and Installation"
slug: "rofi-overview-and-installation"
date: "2018-01-27T22:00:00.000Z"
feature_image: "/images/2018/01/install-header.png"
author: "CJ Harries"
description: "rofi is a neat little tool that does so many cool things. This post provides a rofi overview and installation instructions."
tags:
  - rofi
  - Linux
  - X11
  - CLI
  - tooling
  - launcher
draft: true
---

This is the first in a series of several posts on how to do way more than you really need to with `rofi`. It's a neat little tool that does so many cool things. I don't have a set number of posts, and I don't have a set goal. I just want to share something I find useful.

This post provides a `rofi` overview and installation instructions.

<p class="nav-p"><a id="post-nav"></a></p>

- [Assumptions](#assumptions)
- [Code](#code)
- [Overview](#overview)
- [Installation](#installation)
  - [Dependencies](#dependencies)
  - [Source Code](#source-code)
  - [Options](#options)
  - [Standard](#standard)
  - [Debuggable](#debuggable)
- [Easy Mode](#easy-mode)
  - [Full Script](#full-script)

## Assumptions

I'm running Fedora 27. Most of the instructions are based on that OS. This will translate fairly well to other RHEL derivatives. The Debian ecosystem should also work fairly well, albeit with totally different package names. This probably won't work at all on Windows, and I have no intention of fixing that.

## Code

You can view the code related to this post [under the `post-01-overview-and-installation` tag](//github.com/thecjharries/posts-tooling-rofi/tree/post-01-overview-and-installation).

## Overview

`rofi` makes it really easy to do things via simple shortcuts. It's super useful if you're trying to up your nerd cred, streamline your workflow, beef up `i3`, or make Linux that much more pleasant to run.

Rather than make my own shoddy feature list, I'm just going to link [the official docs](https://github.com/DaveDavenport/rofi/blob/1.4.2/README.md), whose screenshots are already very pretty. `rofi` can, among other things, do this stuff:

- [switch windows](https://github.com/DaveDavenport/rofi/blob/1.4.2/README.md#window-switcher),
- [launch applications](https://github.com/DaveDavenport/rofi/blob/1.4.2/README.md#application-launcher),
- [launch `.desktop` applications](https://github.com/DaveDavenport/rofi/blob/1.4.2/README.md#desktop-file-application-launcher),
- [run `ssh` via `~/.ssh/config`](https://github.com/DaveDavenport/rofi/blob/1.4.2/README.md#ssh-launcher),
- [run scripts](https://github.com/DaveDavenport/rofi/blob/1.4.2/README.md#script-mode), and
- [replace `dmenu`](https://github.com/DaveDavenport/rofi/blob/1.4.2/README.md#dmenu-replacement) (with more features!).

It also does a few more things that I'll probably explore later.

## Installation

Instructions were mostly sourced from [the official docs](https://github.com/DaveDavenport/rofi/blob/1.4.2/INSTALL.md). I tweaked a couple of things and made sure everything worked easily on Fedora.

I tested installation from start to finish in a fresh Vagrant box.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> vagrant init fedora/27-cloud-base<br></pre></div>
</td></tr></table>

I'm (mostly) certain everything will work there. Unless you configure the box to handle or pass off `X` events, you won't actually be able to view `rofi` via Vagrant, but you can ensure the build process works as intended.

### Dependencies

I make heavy use of [`bash`'s brace expansion](https://www.gnu.org/software/bash/manual/html_node/Brace-Expansion.html). If you're not using `bash`, I'm sorry. To make things easier, I'll turn on debug mode.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">set</span> -x<br></pre></div>
</td></tr></table>

Install build dependencies.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install -y gcc make auto<span class="o" style="color:#f92672">{</span>conf,make<span class="o" style="color:#f92672">}</span> pkg-config flex bison git<br><span class="go" style="color:#888">+ sudo dnf install -y gcc make autoconf automake pkg-config flex bison git</span><br></pre></div>
</td></tr></table>

Install external libraries.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install -y <span class="o" style="color:#f92672">{</span>pango,cairo,glib2,lib<span class="o" style="color:#f92672">{</span>rsvg2,xkbcommon<span class="o" style="color:#f92672">{</span>,-x11<span class="o" style="color:#f92672">}</span>,xcb<span class="o" style="color:#f92672">}</span>,startup-notification,xcb-util<span class="o" style="color:#f92672">{</span>,-<span class="o" style="color:#f92672">{</span>w,xr<span class="o" style="color:#f92672">}</span>m<span class="o" style="color:#f92672">}</span>,check<span class="o" style="color:#f92672">}{</span>,-devel<span class="o" style="color:#f92672">}</span><br><span class="go" style="color:#888">+ sudo dnf install -y pango pango-devel cairo cairo-devel glib2 glib2-devel librsvg2 librsvg2-devel libxkbcommon libxkbcommon-devel libxkbcommon-x11 libxkbcommon-x11-devel libxcb libxcb-devel startup-notification startup-notification-devel xcb-util xcb-util-devel xcb-util-wm xcb-util-wm-devel xcb-util-xrm xcb-util-xrm-devel check check-devel</span><br></pre></div>
</td></tr></table>

(Optional) Install [debugging](#debuggable) dependencies.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install -y libasan<br><span class="go" style="color:#888">+ sudo dnf install -y libasan</span><br></pre></div>
</td></tr></table>

There are no more brace expansions.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">set</span> +x<br></pre></div>
</td></tr></table>

### Source Code

We'll need to get a current copy of the source.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> /desired/path/for/source/code<br><span class="gp" style="color:#66d9ef">$</span> git clone https://github.com/DaveDavenport/rofi --recursive<br><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> rofi<br></pre></div>
</td></tr></table>

Alternatively, if you've already got a clone of the repo, just update it.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> /desired/path/for/source/code/rofi<br><span class="gp" style="color:#66d9ef">$</span> git reset --hard<br><span class="gp" style="color:#66d9ef">$</span> git pull<br><span class="gp" style="color:#66d9ef">$</span> git submodule init <span class="o" style="color:#f92672">&amp;&amp;</span> git submodule update<br><span class="gp" style="color:#66d9ef">$</span> rm -rf build<br></pre></div>
</td></tr></table>

Finally, rebuild the tooling and create a build directory.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> /desired/path/for/source/code/rofi<br><span class="gp" style="color:#66d9ef">$</span> autoreconf -i<br><span class="gp" style="color:#66d9ef">$</span> mkdir build <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nb" style="color:#f8f8f2">cd</span> build<br></pre></div>
</td></tr></table>

### Options

It's useful to check out the current build options to understand what's going on.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> /desired/path/for/source/code/rofi/build<br><span class="gp" style="color:#66d9ef">$</span> ../configure --help<br></pre></div>
</td></tr></table>

For example, by default, `rofi` is installed to `/usr/local`, which means the final product will do this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> which rofi<br><span class="go" style="color:#888">/usr/local/bin/rofi</span><br></pre></div>
</td></tr></table>

You can change that in the next steps via

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ../configure --prefix<span class="o" style="color:#f92672">=</span>/some/other/path<br></pre></div>
</td></tr></table>

If you're using Fedora 27+, you shouldn't need to adjust any of the options. Older Fedora (and probably CentOS) might require some tweaking. Debian derivatives will also require tweaking.

### Standard

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> /desired/path/for/source/code/rofi/build<br><span class="gp" style="color:#66d9ef">$</span> ../configure<br><br><span class="go" style="color:#888">...</span><br><br><span class="go" style="color:#888">-------------------------------------</span><br><span class="go" style="color:#888">Timing output:               Disabled</span><br><span class="go" style="color:#888">Desktop File drun dialog     Enabled</span><br><span class="go" style="color:#888">Window Switcher dialog       Enabled</span><br><span class="go" style="color:#888">Asan address sanitize        Disabled</span><br><span class="go" style="color:#888">Code Coverage                Disabled</span><br><span class="go" style="color:#888">Check based tests            Enabled</span><br><span class="go" style="color:#888">-------------------------------------</span><br><span class="go" style="color:#888">Now type 'make' to build</span><br></pre></div>
</td></tr></table>

If you're missing some of these options, you'll need to wade through the `configure` log and figure out which libraries are missing.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> make<br><span class="go" style="color:#888">...</span><br><span class="gp" style="color:#66d9ef">$</span> sudo make install<br><span class="go" style="color:#888">...</span><br><span class="gp" style="color:#66d9ef">$</span> which rofi<br><span class="go" style="color:#888">/usr/local/bin/rofi</span><br><span class="gp" style="color:#66d9ef">$</span> rofi --help<br></pre></div>
</td></tr></table>

### Debuggable

If you're fighting issues, or want to see how things work, you can also build `rofi` with some debugging options. You can either replace the existing `rofi` or you can install them side-by-side using the `--program-suffix` installation option (which is what I do below). More information can be found [in the official debugging docs](https://github.com/DaveDavenport/rofi/wiki/Debugging-Rofi)

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> /desired/path/for/source/code/rofi/build<br><span class="gp" style="color:#66d9ef">$</span> ../configure <span class="se" style="color:#ae81ff">\</span><br>    --enable-timings <span class="se" style="color:#ae81ff">\</span><br>    --enable-asan <span class="se" style="color:#ae81ff">\</span><br>    --enable-gcov <span class="se" style="color:#ae81ff">\</span><br>    --program-suffix<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'-debug'</span><br><br><span class="go" style="color:#888">...</span><br><br><span class="go" style="color:#888">-------------------------------------</span><br><span class="go" style="color:#888">Timing output:               Enabled</span><br><span class="go" style="color:#888">Desktop File drun dialog     Enabled</span><br><span class="go" style="color:#888">Window Switcher dialog       Enabled</span><br><span class="go" style="color:#888">Asan address sanitize        Enabled</span><br><span class="go" style="color:#888">Code Coverage                Enabled</span><br><span class="go" style="color:#888">Check based tests            Enabled</span><br><span class="go" style="color:#888">-------------------------------------</span><br><span class="go" style="color:#888">Now type 'make' to build</span><br></pre></div>
</td></tr></table>

If you're missing some of these options, you'll need to wade through the `configure` log and figure out which libraries are missing.

I'd be lying if I said I fully understand the debug build. I had to first `make` without debug symbols, then re`make` with debug symbols. Without the initial `make`, a couple of important headers aren't built, and I wasn't able to trace how to `make` just those files (`rofi` has a fairly involved build process and I'm weak at best with the GNU build system).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> make<br><span class="go" style="color:#888">...</span><br><span class="gp" style="color:#66d9ef">$</span> make <span class="nv" style="color:#f8f8f2">CFLAGS</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'-O0 -g3'</span> clean rofi<br><span class="go" style="color:#888">...</span><br><span class="gp" style="color:#66d9ef">$</span> sudo make install<br><span class="go" style="color:#888">...</span><br><span class="gp" style="color:#66d9ef">$</span> which rofi<br><span class="go" style="color:#888">/usr/local/bin/rofi</span><br><span class="gp" style="color:#66d9ef">$</span> which rofi-debug<br><span class="go" style="color:#888">/usr/local/bin/rofi-debug</span><br><span class="gp" style="color:#66d9ef">$</span> rofi-debug --help<br></pre></div>
</td></tr></table>

## Easy Mode

I've collected everything in [a simple installation script](#full-script). Pull requests are absolutely welcome.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> curl -fLo ./install-from-source https://raw.githubusercontent.com/thecjharries/posts-tooling-rofi/feature/post-01-overview-and-installation/scripts/install-from-source<br><span class="gp" style="color:#66d9ef">$</span> chmod +x ./install-from-source<br></pre></div>
</td></tr></table>

Its help provides a good overview:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ./install-from-source --help<br><span class="go" style="color:#888">usage: install-from-source [-h] [-d SOURCE] [-b BUILD] [-p INSTALL_PREFIX]</span><br><span class="go" style="color:#888">                           [--dry-run] [--skip-debug | -s DEBUG_SUFFIX]</span><br><span class="go" style="color:#888">                           [-u | -f]</span><br><br><span class="go" style="color:#888">Installs rofi from source</span><br><br><span class="go" style="color:#888">optional arguments:</span><br><span class="go" style="color:#888">  -h, --help            show this help message and exit</span><br><span class="go" style="color:#888">  -d SOURCE, --source-directory SOURCE</span><br><span class="go" style="color:#888">                        source directory (default /opt/rofi)</span><br><span class="go" style="color:#888">  -b BUILD, --build-directory BUILD</span><br><span class="go" style="color:#888">                        build directory (default /opt/rofi/build)</span><br><span class="go" style="color:#888">  -p INSTALL_PREFIX, --prefix INSTALL_PREFIX</span><br><span class="go" style="color:#888">                        root installation directory (default /usr/local)</span><br><span class="go" style="color:#888">  --dry-run             dry run</span><br><span class="go" style="color:#888">  --skip-debug          skip the debuggable build</span><br><span class="go" style="color:#888">  -s DEBUG_SUFFIX, --debug-suffix DEBUG_SUFFIX</span><br><span class="go" style="color:#888">                        debug suffix, (default -debug, e.g. rofi-debug)</span><br><span class="go" style="color:#888">  -u, --update          update using an existing clone</span><br><span class="go" style="color:#888">  -f, --force           wipes the source directory and clones a fresh copy</span><br></pre></div>
</td></tr></table>

I used Python's APIs for directory manipulation, which means you'll have to run it as the user that owns the `source` and `build` directories. `sudo` is required for the default `/opt/rofi` location. This means the whole script is run as `root`. For example,

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> stat -c <span class="s1" style="color:#e6db74">'%A %U %G'</span> /opt<br><span class="go" style="color:#888">drwxr-xr-x root root</span><br><span class="gp" style="color:#66d9ef">$</span> sudo ./install-from-source<br></pre></div>
</td></tr></table>

If that makes you nervous (it should), you can build it in a temporary directory. You'll have to manage the source code yourself (e.g. updates).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ./install-from-source -d <span class="k" style="color:#66d9ef">$(</span>mktemp -d<span class="k" style="color:#66d9ef">)</span><br></pre></div>
</td></tr></table>

I'm a fan of the debug mode, so the script installs both side-by-side. It triples the installation size, bringing the total installation size to `~5M`, up from `~1.5M`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> find /usr/local -type f -name <span class="s1" style="color:#e6db74">'rofi*'</span> -exec stat -c %s <span class="o" style="color:#f92672">{}</span> + <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'{ total+=$1 }END{ print total }'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> numfmt --to<span class="o" style="color:#f92672">=</span>iec<br><span class="go" style="color:#888">4.8M</span><br><span class="gp" style="color:#66d9ef">$</span> find /usr/local -type f -name <span class="s1" style="color:#e6db74">'rofi*'</span> -not -name <span class="s1" style="color:#e6db74">'*debug'</span> -exec stat -c %s <span class="o" style="color:#f92672">{}</span> + <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'{ total+=$1 }END{ print total }'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> numfmt --to<span class="o" style="color:#f92672">=</span>iec<br><span class="go" style="color:#888">1.5M</span><br></pre></div>
</td></tr></table>

If that's too big, or you don't see yourself doing much debugging (honestly you probably won't), the `--skip-debug` flag will just install plain `rofi` without debug features.

### Full Script

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">install-from-source</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-tooling-rofi/blob/master/scripts/install-from-source" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">  1
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
 52
 53
 54
 55
 56
 57
 58
 59
 60
 61
 62
 63
 64
 65
 66
 67
 68
 69
 70
 71
 72
 73
 74
 75
 76
 77
 78
 79
 80
 81
 82
 83
 84
 85
 86
 87
 88
 89
 90
 91
 92
 93
 94
 95
 96
 97
 98
 99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
217
218
219
220
221
222
223
224
225
226
227
228
229
230
231
232
233
234
235
236
237
238
239
240
241
242
243
244
245
246
247
248
249
250
251
252
253
254
255
256
257
258
259
260
261
262
263
264
265
266
267
268
269
270
271
272
273
274
275
276
277
278
279
280
281
282
283
284
285
286
287
288
289
290
291
292
293
294
295
296
297
298
299
300
301
302
303
304
305
306</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/usr/bin/env python</span><br><br><span class="c1" style="color:#75715e"># pylint: disable=misplaced-comparison-constant,missing-docstring</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">errno</span> <span class="kn" style="color:#f92672">import</span> <span class="n">EEXIST</span><span class="p">,</span> <span class="n">ENOENT</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">os</span> <span class="kn" style="color:#f92672">import</span> <span class="n">chdir</span><span class="p">,</span> <span class="n">makedirs</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">os.path</span> <span class="kn" style="color:#f92672">import</span> <span class="n">join</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">shutil</span> <span class="kn" style="color:#f92672">import</span> <span class="n">rmtree</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">subprocess</span> <span class="kn" style="color:#f92672">import</span> <span class="n">CalledProcessError</span><span class="p">,</span> <span class="n">call</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">sys</span> <span class="kn" style="color:#f92672">import</span> <span class="n">argv</span><span class="p">,</span> <span class="nb" style="color:#f8f8f2">exit</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">sys_exit</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">argparse</span> <span class="kn" style="color:#f92672">import</span> <span class="n">ArgumentParser</span><br><br><span class="c1" style="color:#75715e"># Directory for source code</span><br><span class="n">DEFAULT_SOURCE_DIRECTORY</span> <span class="o" style="color:#f92672">=</span> <span class="n">join</span><span class="p">(</span><span class="s1" style="color:#e6db74">'/'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'opt'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'rofi'</span><span class="p">)</span><br><span class="c1" style="color:#75715e"># Directory for build artifacts</span><br><span class="n">DEFAULT_BUILD_DIRECTORY</span> <span class="o" style="color:#f92672">=</span> <span class="n">join</span><span class="p">(</span><span class="n">DEFAULT_SOURCE_DIRECTORY</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'build'</span><span class="p">)</span><br><span class="c1" style="color:#75715e"># Debuggable executable suffix</span><br><span class="n">DEFAULT_DEBUG_SUFFIX</span> <span class="o" style="color:#f92672">=</span> <span class="s1" style="color:#e6db74">'-debug'</span><br><span class="c1" style="color:#75715e"># Root installation directory</span><br><span class="n">DEFAULT_INSTALL_PREFIX</span> <span class="o" style="color:#f92672">=</span> <span class="s1" style="color:#e6db74">'/usr/local'</span><br><br><span class="c1" style="color:#75715e"># Error codes from git</span><br><span class="n">ERROR_NOT_A_REPO</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">128</span><br><span class="n">ERROR_NOT_EMPTY</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">128</span><br><br><span class="c1" style="color:#75715e"># Tooling dependencies</span><br><span class="n">BUILD_DEPENDENCIES</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>    <span class="s1" style="color:#e6db74">'gcc'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'make'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'autoconf'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'automake'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'pkg-config'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'flex'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'bison'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'git'</span><span class="p">,</span><br><span class="p">]</span><br><br><span class="c1" style="color:#75715e"># External libraries</span><br><span class="n">EXTERNAL_DEPENDENCIES</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>    <span class="s1" style="color:#e6db74">'pango'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'cairo'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'glib2'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'librsvg2'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'libxkbcommon'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'libxkbcommon-x11'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'libxcb'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'startup-notification'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'xcb-util'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'xcb-util-wm'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'xcb-util-xrm'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'check'</span><span class="p">,</span><br><span class="p">]</span><br><br><span class="c1" style="color:#75715e"># External libraries + headers</span><br><span class="n">DEVEL_DEPENDENCIES</span> <span class="o" style="color:#f92672">=</span> <span class="n">EXTERNAL_DEPENDENCIES</span> <span class="o" style="color:#f92672">+</span> <span class="p">[</span><br>    <span class="n">dependency</span> <span class="o" style="color:#f92672">+</span> <span class="s1" style="color:#e6db74">'-devel'</span> <span class="k" style="color:#66d9ef">for</span> <span class="n">dependency</span> <span class="ow" style="color:#f92672">in</span> <span class="n">EXTERNAL_DEPENDENCIES</span><br><span class="p">]</span><br><br><span class="c1" style="color:#75715e"># Debug-only dependencies</span><br><span class="n">DEBUG_DEPENDENCIES</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>    <span class="s1" style="color:#e6db74">'libasan'</span><br><span class="p">]</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">run_commands</span><span class="p">(</span><span class="n">commands</span><span class="p">,</span> <span class="n">dry_run</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">False</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Executes a list of commands via call"""</span><br>    <span class="k" style="color:#66d9ef">for</span> <span class="n">command</span> <span class="ow" style="color:#f92672">in</span> <span class="n">commands</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">print</span> <span class="s1" style="color:#e6db74">' '</span><span class="o" style="color:#f92672">.</span><span class="n">join</span><span class="p">(</span><span class="n">command</span><span class="p">)</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="ow" style="color:#f92672">not</span> <span class="n">dry_run</span><span class="p">:</span><br>            <span class="n">call</span><span class="p">(</span><span class="n">command</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">cd</span><span class="p">(</span><span class="n">directory_path</span><span class="p">,</span> <span class="n">dry_run</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">False</span><span class="p">):</span>  <span class="c1" style="color:#75715e"># pylint: disable=invalid-name</span><br>    <span class="sd" style="color:#e6db74">"""Change directory"""</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">dry_run</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">print</span> <span class="s2" style="color:#e6db74">"cd </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">directory_path</span><br>    <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>        <span class="n">chdir</span><span class="p">(</span><span class="n">directory_path</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">wipe_directory</span><span class="p">(</span><span class="n">directory_path</span><span class="p">,</span> <span class="n">dry_run</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">False</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Wipes a directory"""</span><br>    <span class="k" style="color:#66d9ef">try</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="n">dry_run</span><span class="p">:</span><br>            <span class="k" style="color:#66d9ef">print</span> <span class="s2" style="color:#e6db74">"rm -rf </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">directory_path</span><br>        <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>            <span class="n">rmtree</span><span class="p">(</span><span class="n">directory_path</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">except</span> <span class="ne" style="color:#a6e22e">OSError</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">error</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="n">ENOENT</span> <span class="o" style="color:#f92672">==</span> <span class="n">error</span><span class="o" style="color:#f92672">.</span><span class="n">errno</span><span class="p">:</span><br>            <span class="k" style="color:#66d9ef">pass</span><br>        <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>            <span class="k" style="color:#66d9ef">raise</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">create_directory</span><span class="p">(</span><span class="n">directory_path</span><span class="p">,</span> <span class="n">dry_run</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">False</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Creates a directory"""</span><br>    <span class="k" style="color:#66d9ef">try</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="n">dry_run</span><span class="p">:</span><br>            <span class="k" style="color:#66d9ef">print</span> <span class="s2" style="color:#e6db74">"mkdir -p </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">directory_path</span><br>        <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>            <span class="n">makedirs</span><span class="p">(</span><span class="n">directory_path</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">except</span> <span class="ne" style="color:#a6e22e">OSError</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">error</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="n">EEXIST</span> <span class="o" style="color:#f92672">==</span> <span class="n">error</span><span class="o" style="color:#f92672">.</span><span class="n">errno</span><span class="p">:</span><br>            <span class="k" style="color:#66d9ef">pass</span><br>        <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>            <span class="k" style="color:#66d9ef">raise</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">review_commands</span><span class="p">(</span><span class="n">options</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Provides a quick review of everything installed"""</span><br>    <span class="n">commands</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>        <span class="p">[</span><span class="s1" style="color:#e6db74">'which'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'rofi'</span><span class="p">],</span><br>        <span class="p">[</span><span class="s1" style="color:#e6db74">'rofi'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'-version'</span><span class="p">]</span><br>    <span class="p">]</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="ow" style="color:#f92672">not</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">skip_debug</span><span class="p">:</span><br>        <span class="n">commands</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">([</span><span class="s1" style="color:#e6db74">'which'</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"rofi</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">debug_suffix</span><span class="p">])</span><br>        <span class="n">commands</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">([</span><span class="s2" style="color:#e6db74">"rofi</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">debug_suffix</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'-version'</span><span class="p">])</span><br>    <span class="n">run_commands</span><span class="p">(</span><span class="n">commands</span><span class="p">,</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">prep_build</span><span class="p">(</span><span class="n">options</span><span class="p">):</span><br>    <span class="n">cd</span><span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">source</span><span class="p">,</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br>    <span class="n">wipe_directory</span><span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">build</span><span class="p">,</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br>    <span class="n">create_directory</span><span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">build</span><span class="p">,</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">build</span><span class="p">(</span><span class="n">options</span><span class="p">,</span> <span class="n">is_debuggable</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">False</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Builds the rofi executable"""</span><br>    <span class="n">prep_build</span><span class="p">(</span><span class="n">options</span><span class="p">)</span><br>    <span class="n">cd</span><span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">build</span><span class="p">,</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br>    <span class="n">commands</span> <span class="o" style="color:#f92672">=</span> <span class="p">[]</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">is_debuggable</span><span class="p">:</span><br>        <span class="n">commands</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">([</span><br>            <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">configure</span><span class="p">,</span><br>            <span class="s2" style="color:#e6db74">"--prefix='</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">'"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">install_prefix</span><span class="p">),</span><br>            <span class="s1" style="color:#e6db74">'--enable-timings'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'--enable-asan'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'--enable-gcov'</span><span class="p">,</span><br>            <span class="s2" style="color:#e6db74">"--program-suffix='</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">'"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">debug_suffix</span><span class="p">),</span><br>        <span class="p">])</span><br>    <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>        <span class="n">commands</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">([</span><br>            <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">configure</span><span class="p">,</span><br>            <span class="s2" style="color:#e6db74">"--prefix='</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">'"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">install_prefix</span><span class="p">),</span><br>        <span class="p">])</span><br>    <span class="n">commands</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">([</span><span class="s1" style="color:#e6db74">'make'</span><span class="p">])</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">is_debuggable</span><span class="p">:</span><br>        <span class="n">commands</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">([</span><span class="s1" style="color:#e6db74">'make'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'CFLAGS=</span><span class="se" style="color:#ae81ff">\'</span><span class="s1" style="color:#e6db74">-O0 -g3</span><span class="se" style="color:#ae81ff">\'</span><span class="s1" style="color:#e6db74">'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'clean'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'rofi'</span><span class="p">])</span><br>    <span class="n">commands</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">([</span><span class="s1" style="color:#e6db74">'sudo'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'make'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'install'</span><span class="p">])</span><br>    <span class="n">run_commands</span><span class="p">(</span><span class="n">commands</span><span class="p">,</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">build_and_install</span><span class="p">(</span><span class="n">options</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Builds and installs rofi (and possibly rofi-debug)"""</span><br>    <span class="n">build</span><span class="p">(</span><span class="n">options</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="ow" style="color:#f92672">not</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">skip_debug</span><span class="p">:</span><br>        <span class="n">build</span><span class="p">(</span><span class="n">options</span><span class="p">,</span> <span class="bp" style="color:#f8f8f2">True</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">restore_tooling</span><span class="p">(</span><span class="n">options</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Builds missing build files"""</span><br>    <span class="n">commands</span> <span class="o" style="color:#f92672">=</span> <span class="p">[[</span><span class="s1" style="color:#e6db74">'autoreconf'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'-i'</span><span class="p">]]</span><br>    <span class="n">run_commands</span><span class="p">(</span><span class="n">commands</span><span class="p">,</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">clone_repo</span><span class="p">(</span><span class="n">dry_run</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">False</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Clones the repo"""</span><br>    <span class="n">commands</span> <span class="o" style="color:#f92672">=</span> <span class="p">[[</span><br>        <span class="s1" style="color:#e6db74">'git'</span><span class="p">,</span><br>        <span class="s1" style="color:#e6db74">'clone'</span><span class="p">,</span><br>        <span class="s1" style="color:#e6db74">'https://github.com/DaveDavenport/rofi'</span><span class="p">,</span><br>        <span class="s1" style="color:#e6db74">'--recursive'</span><span class="p">,</span><br>        <span class="s1" style="color:#e6db74">'.'</span><br>    <span class="p">]]</span><br>    <span class="n">run_commands</span><span class="p">(</span><span class="n">commands</span><span class="p">,</span> <span class="n">dry_run</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">update_existing_repo</span><span class="p">(</span><span class="n">dry_run</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">False</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Attempts to update. Falls back to clone if repo DNE"""</span><br>    <span class="k" style="color:#66d9ef">try</span><span class="p">:</span><br>        <span class="n">call</span><span class="p">([</span><span class="s1" style="color:#e6db74">'git'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'status'</span><span class="p">])</span><br>    <span class="k" style="color:#66d9ef">except</span> <span class="n">CalledProcessError</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">error</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="n">ERROR_NOT_A_REPO</span> <span class="o" style="color:#f92672">==</span> <span class="n">error</span><span class="o" style="color:#f92672">.</span><span class="n">returncode</span><span class="p">:</span><br>            <span class="k" style="color:#66d9ef">return</span> <span class="n">clone_repo</span><span class="p">(</span><span class="n">dry_run</span><span class="p">)</span><br>        <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>            <span class="k" style="color:#66d9ef">raise</span><br>    <span class="n">commands</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>        <span class="p">[</span><span class="s1" style="color:#e6db74">'git'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'stash'</span><span class="p">],</span><br>        <span class="p">[</span><span class="s1" style="color:#e6db74">'git'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'reset'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'--hard'</span><span class="p">],</span><br>        <span class="p">[</span><span class="s1" style="color:#e6db74">'git'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'pull'</span><span class="p">],</span><br>        <span class="p">[</span><span class="s1" style="color:#e6db74">'git'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'submodule'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'init'</span><span class="p">],</span><br>        <span class="p">[</span><span class="s1" style="color:#e6db74">'git'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'submodule'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'update'</span><span class="p">],</span><br>    <span class="p">]</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="n">run_commands</span><span class="p">(</span><span class="n">commands</span><span class="p">,</span> <span class="n">dry_run</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">refresh_source</span><span class="p">(</span><span class="n">options</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Refreshes the source code via update or clone"""</span><br>    <span class="n">cd</span><span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">source</span><span class="p">,</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">update</span><span class="p">:</span><br>        <span class="n">update_existing_repo</span><span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>        <span class="n">clone_repo</span><span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">prep_source_directory</span><span class="p">(</span><span class="n">options</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Preps the source directory"""</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="ow" style="color:#f92672">not</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">update</span><span class="p">:</span><br>        <span class="n">wipe_directory</span><span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">source</span><span class="p">,</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br>    <span class="n">create_directory</span><span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">source</span><span class="p">,</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">install_dependencies</span><span class="p">(</span><span class="n">options</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Installs necessary system packages"""</span><br>    <span class="n">commands</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>        <span class="p">[</span><span class="s1" style="color:#e6db74">'sudo'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'dnf'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'install'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'-y'</span><span class="p">]</span> <span class="o" style="color:#f92672">+</span> <span class="n">BUILD_DEPENDENCIES</span><span class="p">,</span><br>        <span class="p">[</span><span class="s1" style="color:#e6db74">'sudo'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'dnf'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'install'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'-y'</span><span class="p">]</span> <span class="o" style="color:#f92672">+</span> <span class="n">DEVEL_DEPENDENCIES</span><span class="p">,</span><br>    <span class="p">]</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="ow" style="color:#f92672">not</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">skip_debug</span><span class="p">:</span><br>        <span class="n">commands</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">(</span><br>            <span class="p">[</span><span class="s1" style="color:#e6db74">'sudo'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'dnf'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'install'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'-y'</span><span class="p">]</span> <span class="o" style="color:#f92672">+</span> <span class="n">DEBUG_DEPENDENCIES</span><br>        <span class="p">)</span><br>    <span class="n">run_commands</span><span class="p">(</span><span class="n">commands</span><span class="p">,</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">dry_run</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">parse_argv</span><span class="p">(</span><span class="n">args</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">None</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Parses CLI args"""</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">args</span> <span class="ow" style="color:#f92672">is</span> <span class="bp" style="color:#f8f8f2">None</span><span class="p">:</span><br>        <span class="n">args</span> <span class="o" style="color:#f92672">=</span> <span class="n">argv</span><span class="p">[</span><span class="mi" style="color:#ae81ff">1</span><span class="p">:]</span><br>    <span class="n">parser</span> <span class="o" style="color:#f92672">=</span> <span class="n">ArgumentParser</span><span class="p">(</span><br>        <span class="n">description</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'Installs rofi from source'</span><br>    <span class="p">)</span><br>    <span class="n">parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'-d'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'--source-directory'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'source'</span><span class="p">,</span><br>        <span class="n">default</span><span class="o" style="color:#f92672">=</span><span class="n">DEFAULT_SOURCE_DIRECTORY</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"source directory (default </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">)"</span> <span class="o" style="color:#f92672">%</span> <span class="n">DEFAULT_SOURCE_DIRECTORY</span><br>    <span class="p">)</span><br>    <span class="n">parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'-b'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'--build-directory'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'build'</span><span class="p">,</span><br>        <span class="n">default</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">None</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'build directory (default &lt;source path&gt;/build)'</span><br>    <span class="p">)</span><br>    <span class="n">parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'-p'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'--prefix'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'install_prefix'</span><span class="p">,</span><br>        <span class="n">default</span><span class="o" style="color:#f92672">=</span><span class="n">DEFAULT_INSTALL_PREFIX</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"root installation directory (default </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">)"</span> <span class="o" style="color:#f92672">%</span> <span class="n">DEFAULT_INSTALL_PREFIX</span><br>    <span class="p">)</span><br>    <span class="n">parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'--dry-run'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'dry_run'</span><span class="p">,</span><br>        <span class="n">action</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'store_true'</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'dry run'</span><br>    <span class="p">)</span><br>    <span class="n">debug_opts</span> <span class="o" style="color:#f92672">=</span> <span class="n">parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_mutually_exclusive_group</span><span class="p">()</span><br>    <span class="n">debug_opts</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'--skip-debug'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'skip_debug'</span><span class="p">,</span><br>        <span class="n">action</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'store_true'</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'skip the debuggable build'</span><br>    <span class="p">)</span><br>    <span class="n">debug_opts</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'-s'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'--debug-suffix'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'debug_suffix'</span><span class="p">,</span><br>        <span class="n">default</span><span class="o" style="color:#f92672">=</span><span class="n">DEFAULT_DEBUG_SUFFIX</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"debug suffix, (default </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">, e.g. rofi</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">)"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><br>            <span class="n">DEFAULT_DEBUG_SUFFIX</span><span class="p">,</span><br>            <span class="n">DEFAULT_DEBUG_SUFFIX</span><br>        <span class="p">)</span><br>    <span class="p">)</span><br>    <span class="n">refresh_opts</span> <span class="o" style="color:#f92672">=</span> <span class="n">parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_mutually_exclusive_group</span><span class="p">()</span><br>    <span class="n">refresh_opts</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'-u'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'--update'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'update'</span><span class="p">,</span><br>        <span class="n">action</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'store_true'</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'update using an existing clone'</span><br>    <span class="p">)</span><br>    <span class="n">refresh_opts</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'-f'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'--force'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'force'</span><span class="p">,</span><br>        <span class="n">action</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'store_true'</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'wipes the source directory and clones a fresh copy'</span><br>    <span class="p">)</span><br>    <span class="n">options</span> <span class="o" style="color:#f92672">=</span> <span class="n">parser</span><span class="o" style="color:#f92672">.</span><span class="n">parse_args</span><span class="p">(</span><span class="n">args</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">build</span> <span class="ow" style="color:#f92672">is</span> <span class="bp" style="color:#f8f8f2">None</span><span class="p">:</span><br>        <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">build</span> <span class="o" style="color:#f92672">=</span> <span class="n">join</span><span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">source</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'build'</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="n">options</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">cli</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Bootstraps the script"""</span><br>    <span class="n">options</span> <span class="o" style="color:#f92672">=</span> <span class="n">parse_argv</span><span class="p">()</span><br>    <span class="nb" style="color:#f8f8f2">setattr</span><span class="p">(</span><span class="n">options</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'configure'</span><span class="p">,</span> <span class="n">join</span><span class="p">(</span><span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">source</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'configure'</span><span class="p">))</span><br>    <span class="n">install_dependencies</span><span class="p">(</span><span class="n">options</span><span class="p">)</span><br>    <span class="n">prep_source_directory</span><span class="p">(</span><span class="n">options</span><span class="p">)</span><br>    <span class="n">refresh_source</span><span class="p">(</span><span class="n">options</span><span class="p">)</span><br>    <span class="n">restore_tooling</span><span class="p">(</span><span class="n">options</span><span class="p">)</span><br>    <span class="n">build_and_install</span><span class="p">(</span><span class="n">options</span><span class="p">)</span><br>    <span class="n">review_commands</span><span class="p">(</span><span class="n">options</span><span class="p">)</span><br>    <span class="n">sys_exit</span><span class="p">(</span><span class="mi" style="color:#ae81ff">0</span><span class="p">)</span><br><br><span class="k" style="color:#66d9ef">if</span> <span class="s1" style="color:#e6db74">'__main__'</span> <span class="o" style="color:#f92672">==</span> <span class="vm" style="color:#f8f8f2">__name__</span><span class="p">:</span><br>    <span class="n">cli</span><span class="p">()</span><br></pre></div>
</td>
</tr>
</table>
