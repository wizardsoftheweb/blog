---
title: "Patched Powerline fonts via urxvt"
slug: "compiling-rxvt-unicode-on-fedora-27"
date: "2018-01-07T01:00:00.000Z"
feature_image: "/images/2018/01/urxvt.png"
author: "CJ Harries"
description: "This post breaks down building rxvt-unicode from source. It's targeted to Fedora 27 but might be useful elsewhere."
tags:
  - CLI
  - Fedora
  - powerline
  - urxvt
  - rxvt-unicode
  - build
  - terminal
  - Fedora 27
draft: true
---

I'm a huge fan of [the patched Powerline fonts](https://github.com/powerline/fonts). Those extra icons add a ton of useful information.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span><br><span class="gp" style="color:#66d9ef">$</span> git clone https://github.com/powerline/fonts.git<br><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> fonts<br><span class="gp" style="color:#66d9ef">$</span> ./install.sh<br><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</sThis post breaks down building rxvt-unicode from source. It's targeted to Fedora 27 but might be useful elsewhere.pan> ..<br><span class="gp" style="color:#66d9ef">$</span> rm -rf ./fonts<br></pre></div>
</td></tr></table>

I've also recently switched to `urxvt` as I figure out `i3` and the `X` server.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="10016:46%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install rxvt-unicode<br></pre></div>
</td></tr></table>

However, I quickly noticed the patched fonts aren't recognized by the repo `rxvt-unicode`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> urxvt -fn <span class="s1" style="color:#e6db74">'xft:Droid Sans Mono for Powerline'</span><br><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">echo</span> -e <span class="s1" style="color:#e6db74">'\xEE\x82\xB0'</span><br></pre></div>
</td></tr></table>

![missing-icon](/images/2018/01/missing-icon.png)

I tried almost all of the fonts without finding a complete set. The Fedora official package doesn't seem to be compiled with at least one necessary option for the Powerline stuff. Rebuilding it wasn't how I planned to spend my Saturday, but it's certainly how I spent it.

`rxvt-unicode` itself seems to come from [this master](https://github.com/exg/rxvt-unicode). You could start from there, but a couple of things are immediately blocking:

- [`libev` is a missing dependency](https://github.com/enki/libev)
- [`libptytty` is a missing dependency](https://github.com/yusiwen/libptytty)

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> git clone https://github.com/exg/rxvt-unicode<br><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> rxvt-unicode<br><span class="gp" style="color:#66d9ef">$</span> git submodule add https://github.com/enki/libev<br><span class="gp" style="color:#66d9ef">$</span> git submodule add https://github.com/yusiwen/libptytty<br></pre></div>
</td></tr></table>

The system dependencies are much more opaque. It took me forever to discover an implicit `redhat-rpm-config` connection; I had all but given up on actually duplicating the success I stumbled on earlier today.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install git gcc gcc-c++ perl automake redhat-rpm-config perl-ExtUtils-ParseXS<br></pre></div>
</td></tr></table>

These X packages are necessary as well:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install libX11 libX11-devel libXft libXft-devel<br></pre></div>
</td></tr></table>

I ran into a Fedora issue right after that. `xsubpp` is installed to `/usr/share/perl5/vendor_perl/ExtUtils/xsubpp`, not the desired `/usr/share/perl5/ExtUtils/xsubpp`. It sounds like there's not a consensus on where that file belongs, so you'll have to massage it. There are two good solutions:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ln -s /usr/share/perl5/vendor_perl/ExtUtils/xsubpp /usr/share/perl5/ExtUtils/xsubpp<br><span class="go" style="color:#888">or</span><br><span class="gp" style="color:#66d9ef">$</span> sed -i <span class="s1" style="color:#e6db74">'s/\/ExtUtils\/xsubpp/vendor_perl\/ExtUtils\/xsubpp/g'</span> src/Makefile.in<br></pre></div>
</td></tr></table>

I also had trouble with the compiler. I had to add some additional flags to get things to work properly.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sed -i <span class="s1" style="color:#e6db74">'s/CPPFLAGS = @CPPFLAGS@/CPPFLAGS = @CPPFLAGS@ -fPIC/'</span> src/Makefile.in<br></pre></div>
</td></tr></table>

After that, I was able to successfully run everything.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ./autogen.sh<br><span class="gp" style="color:#66d9ef">$</span> ./configure --prefix<span class="o" style="color:#f92672">=</span>/usr --enable-everything<br><span class="go" style="color:#888">or maybe just the things you need</span><br><span class="gp" style="color:#66d9ef">$</span> make<br><span class="gp" style="color:#66d9ef">$</span> sudo dnf remove rxvt-unicode<br><span class="gp" style="color:#66d9ef">$</span> sudo make install<br></pre></div>
</td></tr></table>

Which yielded the icons I was hoping for.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> urxvt -fn <span class="s1" style="color:#e6db74">'xft:Droid Sans Mono for Powerline'</span><br><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">echo</span> -e <span class="s1" style="color:#e6db74">'\xEE\x82\xB0'</span><br></pre></div>
</td></tr></table>

![icon-present](/images/2018/01/icon-present.png)

To make things easier, I've forked the repo with my changes. You can [snag it and improve it](https://github.com/thecjharries/rxvt-unicode.git) if you'd like. Don't forget to clonely `--recursive`ly to get the `submodule`s!

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span><br><span class="gp" style="color:#66d9ef">$</span> git clone https://github.com/thecjharries/rxvt-unicode.git --recursive<br><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">cd</span> rxvt-unicode<br><span class="gp" style="color:#66d9ef">$</span> ./autogen.sh<br><span class="gp" style="color:#66d9ef">$</span> ./configure --prefix<span class="o" style="color:#f92672">=</span><span class="nv" style="color:#f8f8f2"></span>/usr --enable-everything <span class="o" style="color:#f92672">&amp;&amp;</span> make<br><span class="gp" style="color:#66d9ef">$</span> sudo make install<br></pre></div>
</td></tr></table>
