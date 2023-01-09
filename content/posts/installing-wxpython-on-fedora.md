---
title: "Installing wxPython 4.0 (Project Phoenix) on Fedora 27"
slug: "installing-wxpython-on-fedora"
date: "2018-02-11T22:30:00.000Z"
feature_image: "/images/2018/02/splash.png"
author: "CJ Harries"
tags:
  - wxPython
  - Fedora
  - CLI
  - Linux
  - dnf
  - Python
---

I've stayed away from [wxPython](https://wxpython.org/) in the past because updates were slow and Python 3 wasn't supported. Within the last couple of weeks, `4.0` was completed, which at least answers the Python 3 problem. I've been pounding my head against X11 idiosyncracies all weekend, so I thought I'd take a break and try it out.

## Dependencies

It looks like [the prequisites](https://github.com/wxWidgets/Phoenix/#prerequisites) were sourced from Debian.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install -y <span class="o" style="color:#f92672">{</span>dpkg,freeglut,gstreamer<span class="o" style="color:#f92672">{</span>,1<span class="o" style="color:#f92672">}</span>-plugins-ba<span class="o" style="color:#f92672">{</span>se,d-free<span class="o" style="color:#f92672">}</span>,gtk3,lib<span class="o" style="color:#f92672">{</span>jpeg,notify,SM,tiff<span class="o" style="color:#f92672">}</span>,python<span class="o" style="color:#f92672">{</span><span class="m" style="color:#ae81ff">2</span>,3<span class="o" style="color:#f92672">}</span>,SDL<span class="o" style="color:#f92672">}{</span>,-devel<span class="o" style="color:#f92672">}</span> @development-tools<br><span class="go" style="color:#888">sudo dnf install -y dpkg dpkg-devel freeglut freeglut-devel gstreamer-plugins-base gstreamer-plugins-base-devel gstreamer-plugins-bad-free gstreamer-plugins-bad-free-devel gstreamer1-plugins-base gstreamer1-plugins-base-devel gstreamer1-plugins-bad-free gstreamer1-plugins-bad-free-devel gtk3 gtk3-devel libjpeg libjpeg-devel libnotify libnotify-devel libSM libSM-devel libtiff libtiff-devel python2 python2-devel python3 python3-devel SDL SDL-devel @development-tools</span><br></pre></div>
</td></tr></table>

Feel free [to skip ahead](#back-on-track); the tangent is here because it's funny.

## Tangent

One of the primary dependencies, `libwebkitgtk-3.0`, hasn't been updated [for over a year](https://rpmfind.net/linux/rpm2html/search.php?query=libwebkitgtk-3.0.so.0%28%29%2864bit%29) (in the official repos). If you want, you can install that via something like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install https://rpmfind.net/linux/fedora/linux/releases/26/Everything/x86_64/os/Packages/w/webkitgtk3-2.4.11-5.fc26.x86_64.rpm<br></pre></div>
</td></tr></table>

However, [the prerequisites](https://github.com/wxWidgets/Phoenix/#prerequisites) ask for some newer files, so I'd recommend building from source. Get a fresh release [from the source](https://www.webkitgtk.org/) and [follow the build instructions](https://trac.webkit.org/wiki/BuildingGtk). There are, unsurprisingly, a plethora of additional dependencies.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install -y ninja-build gperf <span class="o" style="color:#f92672">{</span>geoclue2,gobject-introspection,gtk2,hyphen,lib<span class="o" style="color:#f92672">{</span>secret,soup,tasn1,webp,xslt<span class="o" style="color:#f92672">}</span>,sqlite<span class="o" style="color:#f92672">}{</span>,-devel<span class="o" style="color:#f92672">}</span><br><span class="go" style="color:#888">sudo dnf install -y ninja-build gperf geoclue2 geoclue2-devel gobject-introspection gobject-introspection-devel gtk2 gtk2-devel hyphen hyphen-devel libsecret libsecret-devel libsoup libsoup-devel libtasn1 libtasn1-devel libwebp libwebp-devel libxslt libxslt-devel sqlite sqlite-devel</span><br></pre></div>
</td></tr></table>

I had a really strange issue with `libEGL.so.1.0.0` being missing. There were [some good threads](https://ask.fedoraproject.org/en/question/100988/broken-dependecies/?answer=100999#post-id-100999) that [sent me down some rabbit trails](https://forums.opensuse.org/showthread.php/518010-how-can-I-install-usr-lib64-libEGL-so). I ended up relinking the file because I can't for the life of me figure out why it wasn't rebuilding.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> symlinks /usr/lib64/ <span class="p">|</span> grep EGL<br><span class="go" style="color:#888">dangling: /usr/lib64/libEGL.so -&gt; /usr/lib64/libEGL.so.1.0.0</span><br><span class="gp" style="color:#66d9ef">$</span> sudo ln -sf /usr/lib64/libEGL.so.1 /usr/lib64/libEGL.so<br></pre></div>
</td></tr></table>

I actually did these steps first. I discovered each of those extra dependencies above the hard way.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> curl -fLO https://www.webkitgtk.org/releases/webkitgtk-2.18.6.tar.xz<br><span class="gp" style="color:#66d9ef">$</span> tar -xf webkitgtk-2.18.6.tar.xz<br><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> webkitgtk*<br><span class="gp" style="color:#66d9ef">$</span> cmake -DPORT<span class="o" style="color:#f92672">=</span>GTK -DCMAKE_BUILD_TYPE<span class="o" style="color:#f92672">=</span>RelWithDebInfo -GNinja<br><span class="gp" style="color:#66d9ef">$</span> ninja<br><span class="gp" style="color:#66d9ef">$</span> sudo ninja install<br></pre></div>
</td></tr></table>

It took my machine about an hour to build (13:03-13:55). So much for a quick and simple distraction.

![screenshot.1518377055](/images/2018/02/screenshot.1518377055.png)

It also consumes a substantial amount of storage to build. When you're done, don't forget to nuke the build directory.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> ..<br><span class="gp" style="color:#66d9ef">$</span> du webkitgtk-2.18.6 <span class="p">|</span> sort -rh <span class="p">|</span> head -1<br><span class="go" style="color:#888">25G webkitgtk-2.18.6</span><br><span class="gp" style="color:#66d9ef">$</span> rm -rf webkitgtk*<br></pre></div>
</td></tr></table>

Of course, immediately after I did that, I learned why I couldn't find `webkitgtk3`. It's because `webkitgtk4` is in the repos. And a newer release to boot.

## Back on Track

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install webkitgtk4<span class="o" style="color:#f92672">{</span>,-jsc<span class="o" style="color:#f92672">}{</span>,-devel<span class="o" style="color:#f92672">}</span> webkitgtk4-plugin-process-gtk2<br><span class="go" style="color:#888">sudo dnf install webkitgtk4 webkitgtk4-devel webkitgtk4-jsc webkitgtk4-jsc-devel webkitgtk4-plugin-process-gtk2</span><br></pre></div>
</td></tr></table>

Once that's done, you should be able to install wxPython via `pip`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> pip install --user wxpython<br><span class="gp" style="color:#66d9ef">$</span> pip list --format<span class="o" style="color:#f92672">=</span>columns <span class="p">|</span> grep wxPython<br><span class="go" style="color:#888">wxPython                      4.0.1</span><br></pre></div>
</td></tr></table>

Having spent two hours installing this (when it should have taken 30 minutes), I think I'm done with wxPython for the day. More later, most likely.

## Caveat

I might have already installed some of the necessary dependencies and missed them. I did most of an installation in Vagrant before I ran out of memory (wxPython also pegs things out). But actually having `webkitgtk4` accessible in the repos made a world of difference.

## Full Dependency List

Some of these might be unnecessary, e.g. you might not need Python 2 unless you work with it.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>@development-tools<br>dpkg<br>dpkg-devel<br>freeglut<br>freeglut-devel<br>gstreamer-plugins-bad-free<br>gstreamer-plugins-bad-free-devel<br>gstreamer-plugins-base<br>gstreamer-plugins-base-devel<br>gstreamer1-plugins-bad-free<br>gstreamer1-plugins-bad-free-devel<br>gstreamer1-plugins-base<br>gstreamer1-plugins-base-devel<br>gtk3<br>gtk3-devel<br>libjpeg<br>libjpeg-devel<br>libnotify<br>libnotify-devel<br>libSM<br>libSM-devel<br>libtiff<br>libtiff-devel<br>python2<br>python2-devel<br>python3<br>python3-devel<br>SDL<br>SDL-devel<br>webkitgtk4<br>webkitgtk4-devel<br>webkitgtk4-jsc<br>webkitgtk4-jsc-devel<br>webkitgtk4-plugin-process-gtk2<br></pre></div>
</td></tr></table>

## Legal

[The old wxPython logo](https://commons.wikimedia.org/wiki/File:WxPython-logo.png) is licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/deed.en). [The new logo](https://github.com/wxWidgets/Phoenix/blob/master/demo/bitmaps/splash.png) doesn't include a similar CC license in the repo but, at bare minimum, is covered by the [wxWindows Library Licence](https://opensource.org/licenses/wxwindows.php). Stay awesome.
