---
title: "rofi: Basic Configuration"
slug: "rofi-basic-configuration"
date: "2018-01-28T14:00:00.000Z"
feature_image: "/images/2018/01/config-header.png"
author: "CJ Harries"
description: "rofi is a neat little tool that does so many cool things. This post looks at basic rofi configuration."
tags:
  - rofi
  - Linux
  - X11
  - CLI
  - tooling
  - launcher
  - bash
  - sed
---

This is the second in a series of several posts on how to do way more than you really need to with `rofi`. It's a neat little tool that does so many cool things. I don't have a set number of posts, and I don't have a set goal. I just want to share something I find useful.

This post looks at basic `rofi` configuration.

<p class="nav-p"><a id="post-nav"></a></p>

- [Assumptions](#assumptions)
- [Code](#code)
- [Config File](#config-file)
- [Theme File](#theme-file)
- [Scripted](#scripted)

## Assumptions

I'm running Fedora 27. Most of the instructions are based on that OS. This will translate fairly well to other RHEL derivatives. The Debian ecosystem should also work fairly well, albeit with totally different package names. This probably won't work at all on Windows, and I have no intention of fixing that.

You're going to need a newer version of `rofi`, `>=1.4`. I'm currently running this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -version<br><span class="go" style="color:#888">Version: 1.4.2-131-git-5c5665ef (next)</span><br></pre></div>
</td></tr></table>

If you [installed from source](https://blog.wizardsoftheweb.pro/rofi-overview-and-installation#installation), you should be good to go.

## Code

You can view the code related to this post [under the `post-02-basic-config` tag](//github.com/thecjharries/posts-tooling-rofi/tree/post-02-basic-config).

## Config File

At the momemnt, `rofi` is using default values and (probably) refers to a config file that doesn't exist.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi --help <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> awk -F<span class="s1" style="color:#e6db74">':'</span> <span class="s1" style="color:#e6db74">'/Configuration/{ print "cat "$2 }'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> . /dev/stdin<br><br><span class="go" style="color:#888">cat: $XDG_USER_CONFIG_DIR/rofi/config: No such file or directory</span><br></pre></div>
</td></tr></table>

`rofi` provides a couple of ways [to load config](https://github.com/DaveDavenport/rofi/blob/1.4.2/doc/rofi.1.markdown#configuration) (plus templating it for new users). We'll need to create the user directory via `$XDG_USER_CONFIG_DIR` first:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span> <span class="o" style="color:#f92672">||</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"export XDG_USER_CONFIG_DIR=/path/to/desired/.config"</span> &gt;&gt; ~/.whateverrc <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nb" style="color:#f8f8f2">source</span> ~/.whateverrc<br><span class="gp" style="color:#66d9ef">$</span> mkdir -p <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi<br></pre></div>
</td></tr></table>

Since we're running `>=1.4`, we can use [the new config format](https://github.com/DaveDavenport/rofi/blob/1.4.2/doc/rofi-theme.5.markdown).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -dump-config &gt; <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br></pre></div>
</td></tr></table>

We've now got a super basic config file that contains every possible option (I think) commented out.

## Theme File

While we're at it, we might as well dump the theme too.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -dump-theme &gt; <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/theme.rasi<br></pre></div>
</td></tr></table>

To ensure the theme is actually consumed, we'll need to update the config.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sed <span class="se" style="color:#ae81ff">\</span><br>    --in-place<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    --regexp-extended <span class="se" style="color:#ae81ff">\</span><br>    -e <span class="s2" style="color:#e6db74">"s~^.*\stheme:.*</span>$<span class="s2" style="color:#e6db74">~\ttheme: \"</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/theme.rasi\";~g"</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br></pre></div>
</td></tr></table>

## Scripted

If you're like me, you're going to mess up the config on a fairly regular basis. Same goes if you're actively developing with `rofi`. It's useful to have a quick method to rebuild defaults.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">force-default-config</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-tooling-rofi/blob/master/scripts/force-default-config" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
61</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><br><span class="nv" style="color:#f8f8f2">ROOT_DIR</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi"</span><br><br><span class="k" style="color:#66d9ef">function</span> rebuild_config <span class="o" style="color:#f92672">{</span><br>    rm -rf <span class="nv" style="color:#f8f8f2">$ROOT_DIR</span>/config*<br>    rofi -dump-config &gt; <span class="nv" style="color:#f8f8f2">$ROOT_DIR</span>/config.rasi<br><span class="o" style="color:#f92672">}</span><br><br><span class="k" style="color:#66d9ef">function</span> rebuild_theme <span class="o" style="color:#f92672">{</span><br>    rm -rf <span class="nv" style="color:#f8f8f2">$ROOT_DIR</span>/theme*<br>    rofi -dump-theme &gt; <span class="nv" style="color:#f8f8f2">$ROOT_DIR</span>/theme.rasi<br><span class="o" style="color:#f92672">}</span><br><br><span class="k" style="color:#66d9ef">function</span> reconnect_theme <span class="o" style="color:#f92672">{</span><br>    sed <span class="se" style="color:#ae81ff">\</span><br>        --in-place<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>        --regexp-extended <span class="se" style="color:#ae81ff">\</span><br>        -e <span class="s2" style="color:#e6db74">"s~^.*\stheme:.*</span>$<span class="s2" style="color:#e6db74">~\ttheme: \"</span><span class="nv" style="color:#f8f8f2">$ROOT_DIR</span><span class="s2" style="color:#e6db74">/theme.rasi\";~g"</span> <span class="se" style="color:#ae81ff">\</span><br>        <span class="nv" style="color:#f8f8f2">$ROOT_DIR</span>/config.rasi<br><span class="o" style="color:#f92672">}</span><br><br><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> -n <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$1</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    <span class="nv" style="color:#f8f8f2">INPUT</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$1</span><span class="s2" style="color:#e6db74">"</span><br><span class="k" style="color:#66d9ef">else</span><br>    <span class="nv" style="color:#f8f8f2">INPUT</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span><br>        <span class="nb" style="color:#f8f8f2">echo</span> -e <span class="s2" style="color:#e6db74">"config\ntheme\nall"</span> <span class="se" style="color:#ae81ff">\</span><br>            <span class="p">|</span> rofi <span class="se" style="color:#ae81ff">\</span><br>                -dmenu <span class="se" style="color:#ae81ff">\</span><br>                -mesg <span class="s1" style="color:#e6db74">'forcibly rebuild config'</span> <span class="se" style="color:#ae81ff">\</span><br>                -no-fixed-num-lines <span class="se" style="color:#ae81ff">\</span><br>                -width <span class="m" style="color:#ae81ff">24</span> <span class="se" style="color:#ae81ff">\</span><br>                -hide-scrollbar <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#inputbar { children: [entry,case-indicator]; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#listview { dynamic: true; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#mainbox { children: [message,inputbar,listview]; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#message { border: 0; background-color: @selected-normal-background; text-color: @selected-normal-foreground; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#textbox { text-color: inherit; }'</span><br>    <span class="k" style="color:#66d9ef">)</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> -z <span class="nv" style="color:#f8f8f2">$INPUT</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>        <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">0</span><br>    <span class="k" style="color:#66d9ef">fi</span><br><span class="k" style="color:#66d9ef">fi</span><br><br><span class="k" style="color:#66d9ef">case</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$INPUT</span><span class="s2" style="color:#e6db74">"</span> in<br>    config<span class="o" style="color:#f92672">)</span><br>        rebuild_config<br>        <span class="p">;;</span><br>    theme<span class="o" style="color:#f92672">)</span><br>        rebuild_theme<br>        <span class="p">;;</span><br>    all<span class="o" style="color:#f92672">)</span><br>        rebuild_config<br>        rebuild_theme<br>        <span class="p">;;</span><br>    *<span class="o" style="color:#f92672">)</span><br>        <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"usage: </span><span class="nv" style="color:#f8f8f2">$0</span><span class="s2" style="color:#e6db74"> {config,theme,all}"</span><br>        <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">1</span><br>        <span class="p">;;</span><br><span class="k" style="color:#66d9ef">esac</span><br>reconnect_theme<br></pre></div>
</td>
</tr>
</table>

This script works both via the CLI and via the GUI, thanks to `rofi`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> scripts/force-default-config all<br><span class="go" style="color:#888">(rebuilds everything)</span><br><span class="gp" style="color:#66d9ef">$</span> scripts/force-default-config<br></pre></div>
</td></tr></table>

![basic-config-scripted-gui](/images/2018/01/basic-config-scripted-gui.png)
