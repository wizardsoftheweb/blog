---
title: "rofi: Matching and Sorting"
slug: "rofi-matching-and-sorting"
date: "2018-01-29T00:00:00.000Z"
feature_image: "/images/2018/01/matching-and-sorting-header-1.png"
author: "CJ Harries"
description: "rofi is a neat tool that does so many  things. This post looks at configuring rofi's matching/sorting and continues investigating dmenu and script modi applications."
tags:
  - rofi
  - Linux
  - X11
  - CLI
  - tooling
  - launcher
  - awk
  - Python
draft: true
---
<!-- markdownlint-disable MD011 MD037 -->

This is the fifth in a series of several posts on how to do way more than you really need to with `rofi`. It's a neat little tool that does so many cool things. I don't have a set number of posts, and I don't have a set goal. I just want to share something I find useful.

This post looks at configuring `rofi`'s matching and sorting.

<p class="nav-p"><a id="post-nav"></a></p>

- [Assumptions](#assumptions)
- [Code](#code)
- [Overview](#overview)
  - [Comparison](#comparison)
- [Basic Sort Config](#basic-sort-config)
- [(Yet Another) `rofi` Options Script](#yet-another-rofi-options-script)
  - [Full Script](#full-script)
- [Change Matching and Sorting Via a `modi`](#change-matching-and-sorting-via-a-modi)

## Assumptions

I'm running Fedora 27. Most of the instructions are based on that OS. This will translate fairly well to other RHEL derivatives. The Debian ecosystem should also work fairly well, albeit with totally different package names. This probably won't work at all on Windows, and I have no intention of fixing that.

You're going to need a newer version of `rofi`, `>=1.4`. I'm currently running this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -version<br><span class="go" style="color:#888">Version: 1.4.2-131-git-5c5665ef (next)</span><br></pre></div>
</td></tr></table>

If you [installed from source](https://blog.wizardsoftheweb.pro/rofi-overview-and-installation#installation), you should be good to go.

## Code

You can view the code related to this post [under the `post-05-matching-and-sorting` tag](//github.com/thecjharries/posts-tooling-rofi/tree/post-05-matching-and-sorting).

## Overview

For the most part, `rofi` sorts via [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance). In a nutshell, the Levenshtein distance counts the number of changes necessary to go from one string to another. You can view [`rofi`'s implementation](https://github.com/DaveDavenport/rofi/blob/1.4.2/source/helper.c#L691). It's `utf-8`-aware, which is very nice.

When running `fuzzy` matches, `rofi` can also sort [via FZF](https://github.com/junegunn/fzf). Viewing [its implementation of FZF](https://github.com/DaveDavenport/rofi/blob/1.4.2/source/helper.c#L772) might be useful. I believe it too is `utf-8`-aware.

As for the other matching methods, they seem to be vanilla. While there can be fairly substantial differences in `regex` and `glob` implementations across different languages, I haven't been negatively affected by `rofi`'s spin yet (I've been too busy writing other things to really delve deep). `rofi`'s going to be better sometimes and worse other times. Using the Levenshtein distance makes things pretty easy to use.

### Comparison

I've made a quick chart to (quite briefly) highlight the differences. I just looked at sorting, Levenshtein distance, and `fuzzy` matching. `regex` and `glob` matching are too specialized to easily throw in a simple chart like this.

![comparison](/images/2018/01/comparison.png)

I used this script to compile all the information (plus a bunch more).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">generate-matching-and-sorting-comparison</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-tooling-rofi/blob/master/scripts/generate-matching-and-sorting-comparison" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
47</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><br><span class="nb" style="color:#f8f8f2">set</span> -x<br><br><span class="nv" style="color:#f8f8f2">OPTIONS</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'1000</span><br><span class="s1" style="color:#e6db74">000</span><br><span class="s1" style="color:#e6db74">100</span><br><span class="s1" style="color:#e6db74">0000</span><br><span class="s1" style="color:#e6db74">1001'</span><br><br><span class="nv" style="color:#f8f8f2">MATCHING</span><span class="o" style="color:#f92672">=(</span>normal regex glob fuzzy<span class="o" style="color:#f92672">)</span><br><span class="nv" style="color:#f8f8f2">FLAG_STATES</span><span class="o" style="color:#f92672">=(</span><span class="s1" style="color:#e6db74">'-no'</span> <span class="s1" style="color:#e6db74">''</span><span class="o" style="color:#f92672">)</span><br><br><span class="nv" style="color:#f8f8f2">SLEEP_TIME</span><span class="o" style="color:#f92672">=</span><span class="m" style="color:#ae81ff">0</span>.25<br><br><span class="k" style="color:#66d9ef">function</span> run_dmenu <span class="o" style="color:#f92672">{</span><br>    <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$OPTIONS</span><span class="s2" style="color:#e6db74">"</span> <span class="p">|</span> <span class="nb" style="color:#f8f8f2">eval</span> <span class="s2" style="color:#e6db74">"rofi -dmenu -no-lazy-grab -theme-str '#inputbar{children: [entry,case-indicator];}' -hide-scrollbar -width 6 -lines 5 -matching </span><span class="nv" style="color:#f8f8f2">$1</span><span class="s2" style="color:#e6db74"> </span><span class="nv" style="color:#f8f8f2">$2</span><span class="s2" style="color:#e6db74">-sort </span><span class="nv" style="color:#f8f8f2">$3</span><span class="s2" style="color:#e6db74">-levenshtein-sort"</span> <span class="p">&amp;</span><br><span class="o" style="color:#f92672">}</span><br><br><span class="k" style="color:#66d9ef">function</span> move_screenshot <span class="o" style="color:#f92672">{</span><br>    <span class="nv" style="color:#f8f8f2">SCREENSHOT</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span>find ~/Pictures -name <span class="s1" style="color:#e6db74">'rofi*'</span> -exec ls -t <span class="o" style="color:#f92672">{}</span> + <span class="p">|</span> head -1<span class="k" style="color:#66d9ef">)</span><br>    mv <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$SCREENSHOT</span><span class="s2" style="color:#e6db74">"</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$HOME</span><span class="s2" style="color:#e6db74">/Pictures/matching-</span><span class="nv" style="color:#f8f8f2">$1$2</span><span class="s2" style="color:#e6db74">-sort</span><span class="nv" style="color:#f8f8f2">$3</span><span class="s2" style="color:#e6db74">-levenshstein-sort.png"</span><br><span class="o" style="color:#f92672">}</span><br><br><span class="k" style="color:#66d9ef">function</span> ghost_keys <span class="o" style="color:#f92672">{</span><br>    sleep <span class="nv" style="color:#f8f8f2">$SLEEP_TIME</span><br>    xdotool key <span class="m" style="color:#ae81ff">0</span> key <span class="m" style="color:#ae81ff">0</span><br>    sleep <span class="nv" style="color:#f8f8f2">$SLEEP_TIME</span><br>    xdotool key alt+shift+s<br>    sleep <span class="nv" style="color:#f8f8f2">$SLEEP_TIME</span><br>    xdotool key Escape<br>    sleep <span class="nv" style="color:#f8f8f2">$SLEEP_TIME</span><br><span class="o" style="color:#f92672">}</span><br><br><span class="k" style="color:#66d9ef">function</span> execute_stage <span class="o" style="color:#f92672">{</span><br>    run_dmenu <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$1</span><span class="s2" style="color:#e6db74">"</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$2</span><span class="s2" style="color:#e6db74">"</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$3</span><span class="s2" style="color:#e6db74">"</span><br>    ghost_keys<br>    move_screenshot <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$1</span><span class="s2" style="color:#e6db74">"</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$2</span><span class="s2" style="color:#e6db74">"</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$3</span><span class="s2" style="color:#e6db74">"</span><br><span class="o" style="color:#f92672">}</span><br><br><span class="k" style="color:#66d9ef">for</span> matching_state in <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">MATCHING</span><span class="p">[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><span class="p">;</span> <span class="k" style="color:#66d9ef">do</span><br>    <span class="k" style="color:#66d9ef">for</span> sort_state in <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FLAG_STATES</span><span class="p">[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><span class="p">;</span> <span class="k" style="color:#66d9ef">do</span><br>        <span class="k" style="color:#66d9ef">for</span> levenshstein_state in <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FLAG_STATES</span><span class="p">[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><span class="p">;</span> <span class="k" style="color:#66d9ef">do</span><br>            execute_stage <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$matching_state</span><span class="s2" style="color:#e6db74">"</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$sort_state</span><span class="s2" style="color:#e6db74">"</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$levenshstein_state</span><span class="s2" style="color:#e6db74">"</span><br>        <span class="k" style="color:#66d9ef">done</span><br>    <span class="k" style="color:#66d9ef">done</span><br><span class="k" style="color:#66d9ef">done</span><br></pre></div>
</td>
</tr>
</table>

## Basic Sort Config

Personally, I find it useful to have things at least minimally sorted as I'm going.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sed <span class="se" style="color:#ae81ff">\</span><br>    --in-place<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    -E <span class="s1" style="color:#e6db74">'s/^.*\ssort:.*$/\tsort: true;/g'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br><span class="gp" style="color:#66d9ef">$</span> diff --color --unified<span class="o" style="color:#f92672">=</span><span class="m" style="color:#ae81ff">0</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/config.rasi"</span><span class="o" style="color:#f92672">{</span>.bak,<span class="o" style="color:#f92672">}</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -25 +25 @@</span><br><span class="gd" style="color:#f92672">-/* sort: false;*/</span><br><span class="gi" style="color:#a6e22e">+   sort: true;</span><br></pre></div>
</td></tr></table>

However, the `matching` method is very much situational. `normal` should work most of the time. `fuzzy` might be better, but I don't have any metrics so I'm not sure how it affects performance and all that. `glob` is amazing when moving files around, but might not be very useful when attempting to `drun`. You could always run `regex` but then no one else would want to read your scripts and you'd turn to a life of blogging like me.

## (Yet Another) `rofi` Options Script

I slapped together a quick script to handle matching and sorting.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> scripts/configure-matching-and-sorting -h<br><span class="go" style="color:#888">usage: configure-matching-and-sorting [-h] [--skip-diff]</span><br><span class="go" style="color:#888">                                      [-o {matching,sort,levenshtein-sort}]</span><br><span class="go" style="color:#888">                                      [-m [{fuzzy,glob,normal,regex}]]</span><br><span class="go" style="color:#888">                                      [-s [{true,false}]] [-l [{true,false}]]</span><br><br><span class="go" style="color:#888">Configure rofi's matching and sorting</span><br><br><span class="go" style="color:#888">optional arguments:</span><br><span class="go" style="color:#888">  -h, --help            show this help message and exit</span><br><span class="go" style="color:#888">  --skip-diff           Don't print the config diff</span><br><span class="go" style="color:#888">  -o {matching,sort,levenshtein-sort}, --only {matching,sort,levenshtein-sort}</span><br><span class="go" style="color:#888">                        Change only the specified option</span><br><br><span class="go" style="color:#888">  -m [{fuzzy,glob,normal,regex}], --matching [{fuzzy,glob,normal,regex}]</span><br><span class="go" style="color:#888">                        Sets the matching method</span><br><span class="go" style="color:#888">  -s [{true,false}], --sort [{true,false}]</span><br><span class="go" style="color:#888">                        Enables sorting</span><br><span class="go" style="color:#888">  -l [{true,false}], --levenshtein-sort [{true,false}]</span><br><span class="go" style="color:#888">                        Forces Levenshtein sorting</span><br></pre></div>
</td></tr></table>

I tried to make this easy. To use the existing config, just add the pertinent flag.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> scripts/configure-matching-and-sorting -m -s -l<br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -25,2 +25,2 @@</span><br><span class="gd" style="color:#f92672">-/*  sort: false;*/</span><br><span class="gd" style="color:#f92672">-/*  levenshtein-sort: false;*/</span><br><span class="gi" style="color:#a6e22e">+    sort: false;</span><br><span class="gi" style="color:#a6e22e">+    levenshtein-sort: false;</span><br><span class="gu" style="color:#75715e">@@ -35 +35 @@</span><br><span class="gd" style="color:#f92672">-/*  matching: "normal";*/</span><br><span class="gi" style="color:#a6e22e">+    matching: "normal";</span><br></pre></div>
</td></tr></table>

While it looks like that did something, it just uncommented the defaults. It didn't actually change anything.

To actually change something, you can either feed it in via the command or leave off the flag and feed it in via the GUI.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> scripts/configure-matching-and-sorting -o matching -m fuzzy<br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -35 +35 @@</span><br><span class="gd" style="color:#f92672">-    matching: "normal";</span><br><span class="gi" style="color:#a6e22e">+    matching: "fuzzy";</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> scripts/configure-matching-and-sorting -o matching<br></pre></div>
</td></tr></table>

![configure-matching-and-sorting-gui-matching-glob](/images/2018/01/configure-matching-and-sorting-gui-matching-glob.png)

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -35 +35 @@</span><br><span class="gd" style="color:#f92672">-    matching: "fuzzy";</span><br><span class="gi" style="color:#a6e22e">+    matching: "glob";</span><br></pre></div>
</td></tr></table>

### Full Script

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">configure-matching-and-sorting</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-tooling-rofi/blob/master/scripts/configure-matching-and-sorting" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
304</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/usr/bin/env python</span><br><br><span class="c1" style="color:#75715e"># pylint: disable=misplaced-comparison-constant,missing-docstring</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">__future__</span> <span class="kn" style="color:#f92672">import</span> <span class="n">print_function</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">os</span> <span class="kn" style="color:#f92672">import</span> <span class="n">environ</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">os.path</span> <span class="kn" style="color:#f92672">import</span> <span class="n">exists</span><span class="p">,</span> <span class="n">join</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">re</span> <span class="kn" style="color:#f92672">import</span> <span class="nb" style="color:#f8f8f2">compile</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">re_compile</span><span class="p">,</span> <span class="n">finditer</span><span class="p">,</span> <span class="n">match</span><span class="p">,</span> <span class="n">MULTILINE</span><span class="p">,</span> <span class="n">VERBOSE</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">shutil</span> <span class="kn" style="color:#f92672">import</span> <span class="n">copy</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">subprocess</span> <span class="kn" style="color:#f92672">import</span> <span class="n">check_output</span><span class="p">,</span> <span class="n">PIPE</span><span class="p">,</span> <span class="n">Popen</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">sys</span> <span class="kn" style="color:#f92672">import</span> <span class="n">argv</span><span class="p">,</span> <span class="nb" style="color:#f8f8f2">exit</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">sys_exit</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">tempfile</span> <span class="kn" style="color:#f92672">import</span> <span class="n">NamedTemporaryFile</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">types</span> <span class="kn" style="color:#f92672">import</span> <span class="n">StringTypes</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">argparse</span> <span class="kn" style="color:#f92672">import</span> <span class="n">ArgumentParser</span><span class="p">,</span> <span class="n">SUPPRESS</span><br><br><span class="n">CONFIG_FILE</span> <span class="o" style="color:#f92672">=</span> <span class="n">join</span><span class="p">(</span><span class="n">environ</span><span class="p">[</span><span class="s1" style="color:#e6db74">'XDG_USER_CONFIG_DIR'</span><span class="p">],</span> <span class="s1" style="color:#e6db74">'rofi'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'config.rasi'</span><span class="p">)</span><br><br><span class="n">ACTIVE_CHOICE_IDENTIFIER</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">" (active)"</span><br><br><span class="n">MATCHING_METHODS</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>    <span class="s1" style="color:#e6db74">'fuzzy'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'glob'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'normal'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'regex'</span><span class="p">,</span><br><span class="p">]</span><br><br><span class="n">FLAG_STATES</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>    <span class="s1" style="color:#e6db74">'true'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'false'</span><br><span class="p">]</span><br><br><span class="n">DEFAULTS</span> <span class="o" style="color:#f92672">=</span> <span class="p">{</span><br>    <span class="s1" style="color:#e6db74">'matching'</span><span class="p">:</span> <span class="s1" style="color:#e6db74">'normal'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'sort'</span><span class="p">:</span> <span class="s1" style="color:#e6db74">'true'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'levenshtein-sort'</span><span class="p">:</span> <span class="s1" style="color:#e6db74">'false'</span><br><span class="p">}</span><br><br><span class="n">MESSAGES</span> <span class="o" style="color:#f92672">=</span> <span class="p">{</span><br>    <span class="s1" style="color:#e6db74">'matching'</span><span class="p">:</span> <span class="s1" style="color:#e6db74">'change matching method'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'sort'</span><span class="p">:</span> <span class="s1" style="color:#e6db74">'enable sorting'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'levenshtein-sort'</span><span class="p">:</span> <span class="s1" style="color:#e6db74">'force levenshtein sorting'</span><br><span class="p">}</span><br><br><span class="n">CONFIG_OPTIONS_RAW_PATTERN</span> <span class="o" style="color:#f92672">=</span> <span class="sa" style="color:#e6db74">r</span><span class="s2" style="color:#e6db74">"""</span><br><span class="s2" style="color:#e6db74">^</span><br><span class="s2" style="color:#e6db74">.*?</span><br><span class="s2" style="color:#e6db74">\s</span><br><span class="s2" style="color:#e6db74">(?P&lt;option&gt;</span><br><span class="s2" style="color:#e6db74">    matching</span><br><span class="s2" style="color:#e6db74">    |</span><br><span class="s2" style="color:#e6db74">    (?:levenshtein-)?sort</span><br><span class="s2" style="color:#e6db74">)</span><br><span class="s2" style="color:#e6db74">:\s*</span><br><span class="s2" style="color:#e6db74">[\"']?</span><br><span class="s2" style="color:#e6db74">(?P&lt;value&gt;</span><br><span class="s2" style="color:#e6db74">    .*?</span><br><span class="s2" style="color:#e6db74">)</span><br><span class="s2" style="color:#e6db74">[\"']?;</span><br><span class="s2" style="color:#e6db74">.*?</span><br><span class="s2" style="color:#e6db74">$</span><br><span class="s2" style="color:#e6db74">"""</span><br><br><span class="n">CONFIG_OPTIONS_PATTERN</span> <span class="o" style="color:#f92672">=</span> <span class="n">re_compile</span><span class="p">(</span><br>    <span class="n">CONFIG_OPTIONS_RAW_PATTERN</span><span class="p">,</span><br>    <span class="n">VERBOSE</span> <span class="o" style="color:#f92672">|</span> <span class="n">MULTILINE</span><br><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">review_diff</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Compares the config before and after running"""</span><br>    <span class="k" style="color:#66d9ef">with</span> <span class="n">NamedTemporaryFile</span><span class="p">()</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">suppressed_output</span><span class="p">:</span><br>        <span class="n">result_pipe</span> <span class="o" style="color:#f92672">=</span> <span class="n">Popen</span><span class="p">(</span><br>            <span class="p">[</span><br>                <span class="s1" style="color:#e6db74">'diff'</span><span class="p">,</span><br>                <span class="s1" style="color:#e6db74">'--color=always'</span><span class="p">,</span><br>                <span class="s1" style="color:#e6db74">'--unified=0'</span><span class="p">,</span><br>                <span class="s1" style="color:#e6db74">'-t'</span><span class="p">,</span><br>                <span class="s1" style="color:#e6db74">'--tabsize=4'</span><span class="p">,</span><br>                <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">.bak"</span> <span class="o" style="color:#f92672">%</span> <span class="n">CONFIG_FILE</span><span class="p">,</span><br>                <span class="n">CONFIG_FILE</span><br>            <span class="p">],</span><br>            <span class="n">stdout</span><span class="o" style="color:#f92672">=</span><span class="n">suppressed_output</span><span class="p">,</span><br>        <span class="p">)</span><br>        <span class="n">result_pipe</span><span class="o" style="color:#f92672">.</span><span class="n">communicate</span><span class="p">()</span><br>        <span class="n">suppressed_output</span><span class="o" style="color:#f92672">.</span><span class="n">seek</span><span class="p">(</span><span class="mi" style="color:#ae81ff">0</span><span class="p">)</span><br>        <span class="n">result</span> <span class="o" style="color:#f92672">=</span> <span class="n">suppressed_output</span><span class="o" style="color:#f92672">.</span><span class="n">read</span><span class="p">()</span><br>    <span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="n">result</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">update_config</span><span class="p">(</span><span class="n">key</span><span class="p">,</span> <span class="n">value</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Updates the config file"""</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="nb" style="color:#f8f8f2">isinstance</span><span class="p">(</span><span class="n">value</span><span class="p">,</span> <span class="n">StringTypes</span><span class="p">):</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="ow" style="color:#f92672">not</span> <span class="n">match</span><span class="p">(</span><span class="s2" style="color:#e6db74">"true|false"</span><span class="p">,</span> <span class="n">value</span><span class="p">):</span><br>            <span class="n">value</span> <span class="o" style="color:#f92672">=</span> <span class="s1" style="color:#e6db74">'"</span><span class="si" style="color:#e6db74">%s</span><span class="s1" style="color:#e6db74">"'</span> <span class="o" style="color:#f92672">%</span> <span class="n">value</span><br>    <span class="n">check_output</span><span class="p">(</span><br>        <span class="p">[</span><br>            <span class="s1" style="color:#e6db74">'sed'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-i'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-e'</span><span class="p">,</span><br>            <span class="sa" style="color:#e6db74">r</span><span class="s2" style="color:#e6db74">"s/^.*\s</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">:.*$/\t</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">;/g"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">key</span><span class="p">,</span> <span class="n">key</span><span class="p">,</span> <span class="n">value</span><span class="p">),</span><br>            <span class="n">CONFIG_FILE</span><br>        <span class="p">],</span><br>    <span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">validate_item</span><span class="p">(</span><span class="n">item_possibilities</span><span class="p">,</span> <span class="n">defaults_key</span><span class="p">,</span> <span class="n">desired_value</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""</span><br><span class="sd" style="color:#e6db74">    Validates the passed-in value. On failure, validates the current default. On</span><br><span class="sd" style="color:#e6db74">    failure, returns the first possibility.</span><br><span class="sd" style="color:#e6db74">    """</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">desired_value</span> <span class="ow" style="color:#f92672">in</span> <span class="n">item_possibilities</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">return</span> <span class="n">desired_value</span><br>    <span class="n">desired_value</span> <span class="o" style="color:#f92672">=</span> <span class="n">DEFAULTS</span><span class="p">[</span><span class="n">defaults_key</span><span class="p">]</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">desired_value</span> <span class="ow" style="color:#f92672">in</span> <span class="n">item_possibilities</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">return</span> <span class="n">desired_value</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="n">item_possibilities</span><span class="p">[</span><span class="mi" style="color:#ae81ff">0</span><span class="p">]</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">pipe_choices_to_rofi</span><span class="p">(</span><span class="n">choices</span><span class="p">,</span> <span class="n">defaults_key</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Throws the choices out via rofi and returns the result"""</span><br>    <span class="n">rofi_pipe</span> <span class="o" style="color:#f92672">=</span> <span class="n">Popen</span><span class="p">(</span><br>        <span class="p">[</span><br>            <span class="s1" style="color:#e6db74">'rofi'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-dmenu'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-only-match'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-mesg'</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">MESSAGES</span><span class="p">[</span><span class="n">defaults_key</span><span class="p">],</span><br>            <span class="s1" style="color:#e6db74">'-no-fixed-num-lines'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-width'</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">%d</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="nb" style="color:#f8f8f2">len</span><span class="p">(</span><span class="n">MESSAGES</span><span class="p">[</span><span class="n">defaults_key</span><span class="p">])</span> <span class="o" style="color:#f92672">+</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">),</span><br>            <span class="s1" style="color:#e6db74">'-hide-scrollbar'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-theme-str'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'#inputbar {'</span><br>            <span class="s1" style="color:#e6db74">' children: [entry,case-indicator]; '</span><br>            <span class="s1" style="color:#e6db74">'}'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-theme-str'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'#listview {'</span><br>            <span class="s1" style="color:#e6db74">' dynamic: true; '</span><br>            <span class="s1" style="color:#e6db74">'}'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-theme-str'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'#mainbox {'</span><br>            <span class="s1" style="color:#e6db74">' children: [message,inputbar,listview]; '</span><br>            <span class="s1" style="color:#e6db74">'}'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-theme-str'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'#message {'</span><br>            <span class="s1" style="color:#e6db74">' border: 0;'</span><br>            <span class="s1" style="color:#e6db74">' background-color: @selected-normal-background;'</span><br>            <span class="s1" style="color:#e6db74">' text-color: @selected-normal-foreground; '</span><br>            <span class="s1" style="color:#e6db74">'}'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-theme-str'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'#textbox {'</span><br>            <span class="s1" style="color:#e6db74">' text-color: inherit; '</span><br>            <span class="s1" style="color:#e6db74">'}'</span><br>        <span class="p">],</span><br>        <span class="n">stdin</span><span class="o" style="color:#f92672">=</span><span class="n">PIPE</span><span class="p">,</span><br>        <span class="n">stdout</span><span class="o" style="color:#f92672">=</span><span class="n">PIPE</span><span class="p">,</span><br>    <span class="p">)</span><br>    <span class="n">choices_pipe</span> <span class="o" style="color:#f92672">=</span> <span class="n">Popen</span><span class="p">(</span><br>        <span class="p">[</span><br>            <span class="s1" style="color:#e6db74">'echo'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-e'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'</span><span class="se" style="color:#ae81ff">\n</span><span class="s1" style="color:#e6db74">'</span><span class="o" style="color:#f92672">.</span><span class="n">join</span><span class="p">(</span><span class="n">choices</span><span class="p">),</span><br>        <span class="p">],</span><br>        <span class="n">stdout</span><span class="o" style="color:#f92672">=</span><span class="n">rofi_pipe</span><span class="o" style="color:#f92672">.</span><span class="n">stdin</span><span class="p">,</span><br>    <span class="p">)</span><br>    <span class="n">result</span> <span class="o" style="color:#f92672">=</span> <span class="n">rofi_pipe</span><span class="o" style="color:#f92672">.</span><span class="n">communicate</span><span class="p">()[</span><span class="mi" style="color:#ae81ff">0</span><span class="p">]</span><br>    <span class="n">choices_pipe</span><span class="o" style="color:#f92672">.</span><span class="n">wait</span><span class="p">()</span><br>    <span class="n">result</span> <span class="o" style="color:#f92672">=</span> <span class="n">result</span><span class="o" style="color:#f92672">.</span><span class="n">strip</span><span class="p">()</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="ow" style="color:#f92672">not</span> <span class="n">result</span><span class="p">:</span><br>        <span class="n">result</span> <span class="o" style="color:#f92672">=</span> <span class="n">choices</span><span class="p">[</span><span class="mi" style="color:#ae81ff">0</span><span class="p">]</span><br>    <span class="n">result</span> <span class="o" style="color:#f92672">=</span> <span class="n">result</span><span class="o" style="color:#f92672">.</span><span class="n">replace</span><span class="p">(</span><span class="n">ACTIVE_CHOICE_IDENTIFIER</span><span class="p">,</span> <span class="s2" style="color:#e6db74">""</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="n">result</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">create_choices</span><span class="p">(</span><span class="n">all_choices</span><span class="p">,</span> <span class="n">current_choice</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Creates a list of choices for dmenu"""</span><br>    <span class="n">choices</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">%s%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">current_choice</span><span class="p">,</span> <span class="n">ACTIVE_CHOICE_IDENTIFIER</span><span class="p">)]</span><br>    <span class="n">all_choices</span><span class="o" style="color:#f92672">.</span><span class="n">sort</span><span class="p">()</span><br>    <span class="k" style="color:#66d9ef">for</span> <span class="n">choice</span> <span class="ow" style="color:#f92672">in</span> <span class="n">all_choices</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="n">current_choice</span> <span class="o" style="color:#f92672">!=</span> <span class="n">choice</span><span class="p">:</span><br>            <span class="n">choices</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">(</span><span class="n">choice</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="n">choices</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">find_desired_item</span><span class="p">(</span><span class="n">item_possibilities</span><span class="p">,</span> <span class="n">defaults_key</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Builds the dmenu list, polls the user, and validates the result"""</span><br>    <span class="n">choices</span> <span class="o" style="color:#f92672">=</span> <span class="n">create_choices</span><span class="p">(</span><span class="n">item_possibilities</span><span class="p">,</span> <span class="n">DEFAULTS</span><span class="p">[</span><span class="n">defaults_key</span><span class="p">])</span><br>    <span class="n">value</span> <span class="o" style="color:#f92672">=</span> <span class="n">pipe_choices_to_rofi</span><span class="p">(</span><span class="n">choices</span><span class="p">,</span> <span class="n">defaults_key</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="n">validate_item</span><span class="p">(</span><span class="n">item_possibilities</span><span class="p">,</span> <span class="n">defaults_key</span><span class="p">,</span> <span class="n">value</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">parse_and_update_desired_item</span><span class="p">(</span><span class="n">item_possibilities</span><span class="p">,</span> <span class="n">defaults_key</span><span class="p">,</span> <span class="n">options</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""</span><br><span class="sd" style="color:#e6db74">    Attempts to use passed-in values when possible. Otherwise polls the user for</span><br><span class="sd" style="color:#e6db74">    each value via dmenu (via rofi)</span><br><span class="sd" style="color:#e6db74">    """</span><br>    <span class="n">desired_value</span> <span class="o" style="color:#f92672">=</span> <span class="nb" style="color:#f8f8f2">getattr</span><span class="p">(</span><span class="n">options</span><span class="p">,</span> <span class="n">defaults_key</span><span class="p">,</span> <span class="bp" style="color:#f8f8f2">None</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><br>            <span class="ow" style="color:#f92672">not</span> <span class="n">desired_value</span><br>            <span class="ow" style="color:#f92672">or</span><br>            <span class="n">desired_value</span> <span class="o" style="color:#f92672">!=</span> <span class="n">validate_item</span><span class="p">(</span><br>                <span class="n">item_possibilities</span><span class="p">,</span><br>                <span class="n">defaults_key</span><span class="p">,</span><br>                <span class="n">desired_value</span><br>            <span class="p">)</span><br>    <span class="p">):</span><br>        <span class="n">desired_value</span> <span class="o" style="color:#f92672">=</span> <span class="n">find_desired_item</span><span class="p">(</span><span class="n">item_possibilities</span><span class="p">,</span> <span class="n">defaults_key</span><span class="p">)</span><br>    <span class="n">update_config</span><span class="p">(</span><span class="n">defaults_key</span><span class="p">,</span> <span class="n">desired_value</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">determine_everything</span><span class="p">(</span><span class="n">options</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Parses and updates matching, sorting, and Levenshstein sorting options"""</span><br>    <span class="n">parse_and_update_desired_item</span><span class="p">(</span><span class="n">MATCHING_METHODS</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'matching'</span><span class="p">,</span> <span class="n">options</span><span class="p">)</span><br>    <span class="n">parse_and_update_desired_item</span><span class="p">(</span><span class="n">FLAG_STATES</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'sort'</span><span class="p">,</span> <span class="n">options</span><span class="p">)</span><br>    <span class="n">parse_and_update_desired_item</span><span class="p">(</span><span class="n">FLAG_STATES</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'levenshtein-sort'</span><span class="p">,</span> <span class="n">options</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">parse_argv</span><span class="p">(</span><span class="n">args</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">None</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Parses CLI args"""</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">args</span> <span class="ow" style="color:#f92672">is</span> <span class="bp" style="color:#f8f8f2">None</span><span class="p">:</span><br>        <span class="n">args</span> <span class="o" style="color:#f92672">=</span> <span class="n">argv</span><span class="p">[</span><span class="mi" style="color:#ae81ff">1</span><span class="p">:]</span><br>    <span class="n">parser</span> <span class="o" style="color:#f92672">=</span> <span class="n">ArgumentParser</span><span class="p">(</span><br>        <span class="n">description</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"Configure rofi's matching and sorting"</span><br>    <span class="p">)</span><br>    <span class="n">parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'--skip-diff'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'skip_diff'</span><span class="p">,</span><br>        <span class="n">action</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'store_true'</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"Don't print the config diff"</span><br>    <span class="p">)</span><br>    <span class="n">exclusive_options</span> <span class="o" style="color:#f92672">=</span> <span class="n">parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_mutually_exclusive_group</span><span class="p">()</span><br>    <span class="n">exclusive_options</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'-o'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'--only'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'only'</span><span class="p">,</span><br>        <span class="n">default</span><span class="o" style="color:#f92672">=</span><span class="n">SUPPRESS</span><span class="p">,</span><br>        <span class="n">choices</span><span class="o" style="color:#f92672">=</span><span class="p">[</span><span class="s1" style="color:#e6db74">'matching'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'sort'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'levenshtein-sort'</span><span class="p">],</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'Change only the specified option'</span><span class="p">,</span><br>    <span class="p">)</span><br>    <span class="n">config_options</span> <span class="o" style="color:#f92672">=</span> <span class="n">parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument_group</span><span class="p">()</span><br>    <span class="n">config_options</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'-m'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'--matching'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'matching'</span><span class="p">,</span><br>        <span class="n">nargs</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'?'</span><span class="p">,</span><br>        <span class="n">const</span><span class="o" style="color:#f92672">=</span><span class="n">DEFAULTS</span><span class="p">[</span><span class="s1" style="color:#e6db74">'matching'</span><span class="p">],</span><br>        <span class="n">default</span><span class="o" style="color:#f92672">=</span><span class="n">SUPPRESS</span><span class="p">,</span><br>        <span class="n">choices</span><span class="o" style="color:#f92672">=</span><span class="n">MATCHING_METHODS</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'Sets the matching method'</span><span class="p">,</span><br>    <span class="p">)</span><br>    <span class="n">config_options</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'-s'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'--sort'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'sort'</span><span class="p">,</span><br>        <span class="n">nargs</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'?'</span><span class="p">,</span><br>        <span class="n">const</span><span class="o" style="color:#f92672">=</span><span class="n">DEFAULTS</span><span class="p">[</span><span class="s1" style="color:#e6db74">'sort'</span><span class="p">],</span><br>        <span class="n">default</span><span class="o" style="color:#f92672">=</span><span class="n">SUPPRESS</span><span class="p">,</span><br>        <span class="n">choices</span><span class="o" style="color:#f92672">=</span><span class="n">FLAG_STATES</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'Enables sorting'</span><span class="p">,</span><br>    <span class="p">)</span><br>    <span class="n">config_options</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'-l'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'--levenshtein-sort'</span><span class="p">,</span><br>        <span class="n">dest</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'levenshtein-sort'</span><span class="p">,</span><br>        <span class="n">nargs</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'?'</span><span class="p">,</span><br>        <span class="n">const</span><span class="o" style="color:#f92672">=</span><span class="n">DEFAULTS</span><span class="p">[</span><span class="s1" style="color:#e6db74">'levenshtein-sort'</span><span class="p">],</span><br>        <span class="n">default</span><span class="o" style="color:#f92672">=</span><span class="n">SUPPRESS</span><span class="p">,</span><br>        <span class="n">choices</span><span class="o" style="color:#f92672">=</span><span class="n">FLAG_STATES</span><span class="p">,</span><br>        <span class="n">help</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'Forces Levenshtein sorting'</span><span class="p">,</span><br>    <span class="p">)</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="n">parser</span><span class="o" style="color:#f92672">.</span><span class="n">parse_args</span><span class="p">(</span><span class="n">args</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">create_config_if_dne</span><span class="p">(</span><span class="n">raw_config</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Creates a new config file if it doesn't exist"""</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="ow" style="color:#f92672">not</span> <span class="n">exists</span><span class="p">(</span><span class="n">CONFIG_FILE</span><span class="p">):</span><br>        <span class="k" style="color:#66d9ef">with</span> <span class="nb" style="color:#f8f8f2">open</span><span class="p">(</span><span class="n">CONFIG_FILE</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'w+'</span><span class="p">)</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">config_file</span><span class="p">:</span><br>            <span class="n">config_file</span><span class="o" style="color:#f92672">.</span><span class="n">write</span><span class="p">(</span><span class="n">raw_config</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">load_config</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Loads the active rofi config"""</span><br>    <span class="n">raw_config</span> <span class="o" style="color:#f92672">=</span> <span class="n">check_output</span><span class="p">([</span><span class="s1" style="color:#e6db74">'rofi'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'-dump-config'</span><span class="p">])</span><br>    <span class="k" style="color:#66d9ef">for</span> <span class="n">config_match</span> <span class="ow" style="color:#f92672">in</span> <span class="n">finditer</span><span class="p">(</span><span class="n">CONFIG_OPTIONS_PATTERN</span><span class="p">,</span> <span class="n">raw_config</span><span class="p">):</span><br>        <span class="n">DEFAULTS</span><span class="p">[</span><span class="n">config_match</span><span class="o" style="color:#f92672">.</span><span class="n">group</span><span class="p">(</span><span class="s1" style="color:#e6db74">'option'</span><span class="p">)]</span> <span class="o" style="color:#f92672">=</span> <span class="n">config_match</span><span class="o" style="color:#f92672">.</span><span class="n">group</span><span class="p">(</span><span class="s1" style="color:#e6db74">'value'</span><span class="p">)</span><br>    <span class="n">create_config_if_dne</span><span class="p">(</span><span class="n">raw_config</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">backup_config</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Backs up the current config"""</span><br>    <span class="n">copy</span><span class="p">(</span><span class="n">CONFIG_FILE</span><span class="p">,</span> <span class="n">CONFIG_FILE</span> <span class="o" style="color:#f92672">+</span> <span class="s1" style="color:#e6db74">'.bak'</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">cli</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Bootstraps the app"""</span><br>    <span class="n">load_config</span><span class="p">()</span><br>    <span class="n">backup_config</span><span class="p">()</span><br>    <span class="n">options</span> <span class="o" style="color:#f92672">=</span> <span class="n">parse_argv</span><span class="p">()</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="nb" style="color:#f8f8f2">getattr</span><span class="p">(</span><span class="n">options</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'only'</span><span class="p">,</span> <span class="bp" style="color:#f8f8f2">None</span><span class="p">):</span><br>        <span class="k" style="color:#66d9ef">for</span> <span class="n">key</span><span class="p">,</span> <span class="n">value</span> <span class="ow" style="color:#f92672">in</span> <span class="n">DEFAULTS</span><span class="o" style="color:#f92672">.</span><span class="n">iteritems</span><span class="p">():</span><br>            <span class="k" style="color:#66d9ef">if</span> <span class="n">key</span> <span class="o" style="color:#f92672">!=</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">only</span><span class="p">:</span><br>                <span class="nb" style="color:#f8f8f2">setattr</span><span class="p">(</span><span class="n">options</span><span class="p">,</span> <span class="n">key</span><span class="p">,</span> <span class="n">value</span><span class="p">)</span><br>    <span class="n">determine_everything</span><span class="p">(</span><span class="n">options</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="ow" style="color:#f92672">not</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">skip_diff</span><span class="p">:</span><br>        <span class="n">review_diff</span><span class="p">()</span><br>    <span class="n">sys_exit</span><span class="p">(</span><span class="mi" style="color:#ae81ff">0</span><span class="p">)</span><br><br><span class="k" style="color:#66d9ef">if</span> <span class="s1" style="color:#e6db74">'__main__'</span> <span class="o" style="color:#f92672">==</span> <span class="vm" style="color:#f8f8f2">__name__</span><span class="p">:</span><br>    <span class="n">cli</span><span class="p">()</span><br></pre></div>
</td>
</tr>
</table>

## Change Matching and Sorting Via a `modi`

After [the last post's `modi`](https://blog.wizardsoftheweb.pro/rofi-change-window-location/#locationchangermodi), I wanted to see if I could repeat something similar here. This script is still pretty raw, but it gets the job done. Total GUI, like before.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">rofi-tweak-sort</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-tooling-rofi/blob/master/scripts/rofi-tweak-sort" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
306
307
308
309
310
311
312
313
314
315
316
317
318
319</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/usr/bin/env python</span><br><br><span class="c1" style="color:#75715e"># pylint: disable=misplaced-comparison-constant,missing-docstring</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">__future__</span> <span class="kn" style="color:#f92672">import</span> <span class="n">print_function</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">os</span> <span class="kn" style="color:#f92672">import</span> <span class="n">chmod</span><span class="p">,</span> <span class="n">environ</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">os.path</span> <span class="kn" style="color:#f92672">import</span> <span class="n">exists</span><span class="p">,</span> <span class="n">join</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">re</span> <span class="kn" style="color:#f92672">import</span> <span class="nb" style="color:#f8f8f2">compile</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">re_compile</span><span class="p">,</span> <span class="n">finditer</span><span class="p">,</span> <span class="n">match</span><span class="p">,</span> <span class="n">MULTILINE</span><span class="p">,</span> <span class="n">VERBOSE</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">shutil</span> <span class="kn" style="color:#f92672">import</span> <span class="n">copy</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">stat</span> <span class="kn" style="color:#f92672">import</span> <span class="n">S_IRUSR</span><span class="p">,</span> <span class="n">S_IWUSR</span><span class="p">,</span> <span class="n">S_IXUSR</span><span class="p">,</span> <span class="n">S_IRGRP</span><span class="p">,</span> <span class="n">S_IXGRP</span><span class="p">,</span> <span class="n">S_IROTH</span><span class="p">,</span> <span class="n">S_IXOTH</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">subprocess</span> <span class="kn" style="color:#f92672">import</span> <span class="n">check_output</span><span class="p">,</span> <span class="n">Popen</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">sys</span> <span class="kn" style="color:#f92672">import</span> <span class="n">argv</span><span class="p">,</span> <span class="nb" style="color:#f8f8f2">exit</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">sys_exit</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">types</span> <span class="kn" style="color:#f92672">import</span> <span class="n">StringTypes</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">argparse</span> <span class="kn" style="color:#f92672">import</span> <span class="n">ArgumentParser</span><br><br><span class="n">CONFIG_FILE</span> <span class="o" style="color:#f92672">=</span> <span class="n">join</span><span class="p">(</span><span class="n">environ</span><span class="p">[</span><span class="s1" style="color:#e6db74">'XDG_USER_CONFIG_DIR'</span><span class="p">],</span> <span class="s1" style="color:#e6db74">'rofi'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'config.rasi'</span><span class="p">)</span><br><br><span class="n">BASE_OPTIONS</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>    <span class="s1" style="color:#e6db74">'set matching'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'set sort'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'set levenshtein-sort'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'exit'</span><br><span class="p">]</span><br><br><span class="n">MATCHING_METHODS</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>    <span class="s1" style="color:#e6db74">'fuzzy'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'glob'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'normal'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'regex'</span><br><span class="p">]</span><br><br><span class="n">DEFAULTS</span> <span class="o" style="color:#f92672">=</span> <span class="p">{</span><br>    <span class="s1" style="color:#e6db74">'matching'</span><span class="p">:</span> <span class="s1" style="color:#e6db74">'normal'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'sort'</span><span class="p">:</span> <span class="s1" style="color:#e6db74">'true'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'levenshtein-sort'</span><span class="p">:</span> <span class="s1" style="color:#e6db74">'false'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'pid'</span><span class="p">:</span> <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">join</span><span class="p">(</span><span class="n">environ</span><span class="p">[</span><span class="s1" style="color:#e6db74">'XDG_RUNTIME_DIR'</span><span class="p">],</span> <span class="s2" style="color:#e6db74">"rofi.pid"</span><span class="p">)</span><br><span class="p">}</span><br><br><span class="n">MATCHING_OPTIONS</span> <span class="o" style="color:#f92672">=</span> <span class="p">[]</span><br><br><span class="n">FLAG_STATES</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>    <span class="s1" style="color:#e6db74">'true'</span><span class="p">,</span><br>    <span class="s1" style="color:#e6db74">'false'</span><br><span class="p">]</span><br><br><span class="n">SORT_OPTIONS</span> <span class="o" style="color:#f92672">=</span> <span class="p">[]</span><br><br><span class="n">LEVENSHTEIN_SORT_OPTIONS</span> <span class="o" style="color:#f92672">=</span> <span class="p">[]</span><br><br><span class="n">ACTIVE_CHOICE_IDENTIFIER</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">" (active)"</span><br><br><span class="n">CONFIG_OPTIONS_RAW_PATTERN</span> <span class="o" style="color:#f92672">=</span> <span class="sa" style="color:#e6db74">r</span><span class="s2" style="color:#e6db74">"""</span><br><span class="s2" style="color:#e6db74">^</span><br><span class="s2" style="color:#e6db74">.*?</span><br><span class="s2" style="color:#e6db74">\s</span><br><span class="s2" style="color:#e6db74">(?P&lt;option&gt;</span><br><span class="s2" style="color:#e6db74">    matching</span><br><span class="s2" style="color:#e6db74">    |</span><br><span class="s2" style="color:#e6db74">    (?:levenshtein-)?sort</span><br><span class="s2" style="color:#e6db74">    |</span><br><span class="s2" style="color:#e6db74">    pid</span><br><span class="s2" style="color:#e6db74">)</span><br><span class="s2" style="color:#e6db74">:\s*</span><br><span class="s2" style="color:#e6db74">[\"']?</span><br><span class="s2" style="color:#e6db74">(?P&lt;value&gt;</span><br><span class="s2" style="color:#e6db74">    .*?</span><br><span class="s2" style="color:#e6db74">)</span><br><span class="s2" style="color:#e6db74">[\"']?;</span><br><span class="s2" style="color:#e6db74">.*?</span><br><span class="s2" style="color:#e6db74">$</span><br><span class="s2" style="color:#e6db74">"""</span><br><br><span class="n">CONFIG_OPTIONS_PATTERN</span> <span class="o" style="color:#f92672">=</span> <span class="n">re_compile</span><span class="p">(</span><br>    <span class="n">CONFIG_OPTIONS_RAW_PATTERN</span><span class="p">,</span><br>    <span class="n">VERBOSE</span> <span class="o" style="color:#f92672">|</span> <span class="n">MULTILINE</span><br><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">clean_exit</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Exits with code 0"""</span><br>    <span class="n">sys_exit</span><span class="p">(</span><span class="mi" style="color:#ae81ff">0</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">print_and_exit</span><span class="p">(</span><span class="n">options</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Dumps everything to STDOUT for rofi"""</span><br>    <span class="k" style="color:#66d9ef">for</span> <span class="n">option</span> <span class="ow" style="color:#f92672">in</span> <span class="n">options</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">print</span><span class="p">(</span><span class="n">option</span><span class="p">)</span><br>    <span class="n">clean_exit</span><span class="p">()</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">spawn_and_die</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Creates a new process and dies"""</span><br>    <span class="n">runner</span> <span class="o" style="color:#f92672">=</span> <span class="n">create_new_runner</span><span class="p">()</span><br>    <span class="n">Popen</span><span class="p">([</span><span class="s1" style="color:#e6db74">'bash'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'-c'</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"coproc </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">runner</span><span class="p">])</span><br>    <span class="n">clean_exit</span><span class="p">()</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">parse_pid</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Snags the original rofi command"""</span><br>    <span class="k" style="color:#66d9ef">with</span> <span class="nb" style="color:#f8f8f2">open</span><span class="p">(</span><span class="n">DEFAULTS</span><span class="p">[</span><span class="s1" style="color:#e6db74">'pid'</span><span class="p">],</span> <span class="s1" style="color:#e6db74">'r'</span><span class="p">)</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">pid_file</span><span class="p">:</span><br>        <span class="n">process_id</span> <span class="o" style="color:#f92672">=</span> <span class="n">pid_file</span><span class="o" style="color:#f92672">.</span><span class="n">read</span><span class="p">()</span><span class="o" style="color:#f92672">.</span><span class="n">strip</span><span class="p">()</span><br>    <span class="n">result</span> <span class="o" style="color:#f92672">=</span> <span class="n">check_output</span><span class="p">(</span><br>        <span class="p">[</span><br>            <span class="s1" style="color:#e6db74">'ps'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'--no-headers'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-o'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'command'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-p'</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">process_id</span><br>        <span class="p">]</span><br>    <span class="p">)</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="n">result</span><span class="o" style="color:#f92672">.</span><span class="n">strip</span><span class="p">()</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">create_new_runner</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Creates a new runner script"""</span><br>    <span class="n">result</span> <span class="o" style="color:#f92672">=</span> <span class="n">check_output</span><span class="p">(</span><br>        <span class="p">[</span><br>            <span class="s1" style="color:#e6db74">'mktemp'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-p'</span><span class="p">,</span> <span class="n">environ</span><span class="p">[</span><span class="s1" style="color:#e6db74">'TMPDIR'</span><span class="p">],</span><br>            <span class="s1" style="color:#e6db74">'rofi-tweak-sort-XXXX'</span><br>        <span class="p">],</span><br>    <span class="p">)</span><br>    <span class="n">result</span> <span class="o" style="color:#f92672">=</span> <span class="n">result</span><span class="o" style="color:#f92672">.</span><span class="n">strip</span><span class="p">()</span><br>    <span class="n">root_command</span> <span class="o" style="color:#f92672">=</span> <span class="n">parse_pid</span><span class="p">()</span><br>    <span class="k" style="color:#66d9ef">with</span> <span class="nb" style="color:#f8f8f2">open</span><span class="p">(</span><span class="n">result</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'w'</span><span class="p">)</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">tempfile</span><span class="p">:</span><br>        <span class="n">tempfile</span><span class="o" style="color:#f92672">.</span><span class="n">write</span><span class="p">(</span><br>            <span class="sd" style="color:#e6db74">"""</span><br><span class="sd" style="color:#e6db74">            #!/bin/bash</span><br><span class="sd" style="color:#e6db74">            %s</span><br><span class="sd" style="color:#e6db74">            rm -rf %s</span><br><span class="sd" style="color:#e6db74">            """</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">root_command</span><span class="p">,</span> <span class="n">result</span><span class="p">)</span><br>        <span class="p">)</span><br>    <span class="n">chmod</span><span class="p">(</span><span class="n">result</span><span class="p">,</span> <span class="n">S_IRUSR</span> <span class="o" style="color:#f92672">|</span> <span class="n">S_IWUSR</span> <span class="o" style="color:#f92672">|</span> <span class="n">S_IXUSR</span> <span class="o" style="color:#f92672">|</span><br>          <span class="n">S_IRGRP</span> <span class="o" style="color:#f92672">|</span> <span class="n">S_IXGRP</span> <span class="o" style="color:#f92672">|</span> <span class="n">S_IROTH</span> <span class="o" style="color:#f92672">|</span> <span class="n">S_IXOTH</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="n">result</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">update_config</span><span class="p">(</span><span class="n">key</span><span class="p">,</span> <span class="n">value</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Updates the config file"""</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="nb" style="color:#f8f8f2">isinstance</span><span class="p">(</span><span class="n">value</span><span class="p">,</span> <span class="n">StringTypes</span><span class="p">):</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="ow" style="color:#f92672">not</span> <span class="n">match</span><span class="p">(</span><span class="s2" style="color:#e6db74">"true|false"</span><span class="p">,</span> <span class="n">value</span><span class="p">):</span><br>            <span class="n">value</span> <span class="o" style="color:#f92672">=</span> <span class="s1" style="color:#e6db74">'"</span><span class="si" style="color:#e6db74">%s</span><span class="s1" style="color:#e6db74">"'</span> <span class="o" style="color:#f92672">%</span> <span class="n">value</span><br>    <span class="n">check_output</span><span class="p">(</span><br>        <span class="p">[</span><br>            <span class="s1" style="color:#e6db74">'sed'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-i'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-e'</span><span class="p">,</span><br>            <span class="sa" style="color:#e6db74">r</span><span class="s2" style="color:#e6db74">"s/^.*\s</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">:.*$/\t</span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">: </span><span class="si" style="color:#e6db74">%s</span><span class="s2" style="color:#e6db74">;/g"</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><span class="n">key</span><span class="p">,</span> <span class="n">key</span><span class="p">,</span> <span class="n">value</span><span class="p">),</span><br>            <span class="n">CONFIG_FILE</span><br>        <span class="p">],</span><br>    <span class="p">)</span><br>    <span class="n">spawn_and_die</span><span class="p">()</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">base_options</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""The root options"""</span><br>    <span class="n">print_and_exit</span><span class="p">(</span><span class="n">BASE_OPTIONS</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">construct_matching_options</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Constructs the options for matching"""</span><br>    <span class="k" style="color:#66d9ef">for</span> <span class="n">value</span> <span class="ow" style="color:#f92672">in</span> <span class="n">MATCHING_METHODS</span><span class="p">:</span><br>        <span class="n">MATCHING_OPTIONS</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">(</span><br>            <span class="s1" style="color:#e6db74">'set matching </span><span class="si" style="color:#e6db74">%s%s</span><span class="s1" style="color:#e6db74">'</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><br>                <span class="n">value</span><span class="p">,</span><br>                <span class="n">ACTIVE_CHOICE_IDENTIFIER</span><br>                <span class="k" style="color:#66d9ef">if</span> <span class="n">value</span> <span class="o" style="color:#f92672">==</span> <span class="n">DEFAULTS</span><span class="p">[</span><span class="s1" style="color:#e6db74">'matching'</span><span class="p">]</span><br>                <span class="k" style="color:#66d9ef">else</span> <span class="s1" style="color:#e6db74">''</span><br>            <span class="p">)</span><br>        <span class="p">)</span><br>    <span class="n">MATCHING_OPTIONS</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">(</span><span class="s1" style="color:#e6db74">'set ^'</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">set_matching_options</span><span class="p">(</span><span class="n">value</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">None</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Sets matching options"""</span><br>    <span class="n">construct_matching_options</span><span class="p">()</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">value</span><span class="p">:</span><br>        <span class="n">value</span> <span class="o" style="color:#f92672">=</span> <span class="n">value</span><span class="o" style="color:#f92672">.</span><span class="n">replace</span><span class="p">(</span><span class="n">ACTIVE_CHOICE_IDENTIFIER</span><span class="p">,</span> <span class="s2" style="color:#e6db74">""</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">value</span> <span class="ow" style="color:#f92672">in</span> <span class="n">MATCHING_METHODS</span><span class="p">:</span><br>        <span class="n">update_config</span><span class="p">(</span><span class="s1" style="color:#e6db74">'matching'</span><span class="p">,</span> <span class="n">value</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>        <span class="n">print_and_exit</span><span class="p">(</span><span class="n">MATCHING_OPTIONS</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">construct_sort_options</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Constructs the options for basic sorting"""</span><br>    <span class="k" style="color:#66d9ef">for</span> <span class="n">value</span> <span class="ow" style="color:#f92672">in</span> <span class="n">FLAG_STATES</span><span class="p">:</span><br>        <span class="n">SORT_OPTIONS</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">(</span><br>            <span class="s1" style="color:#e6db74">'set sort </span><span class="si" style="color:#e6db74">%s%s</span><span class="s1" style="color:#e6db74">'</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><br>                <span class="n">value</span><span class="p">,</span><br>                <span class="n">ACTIVE_CHOICE_IDENTIFIER</span><br>                <span class="k" style="color:#66d9ef">if</span> <span class="n">value</span> <span class="o" style="color:#f92672">==</span> <span class="n">DEFAULTS</span><span class="p">[</span><span class="s1" style="color:#e6db74">'sort'</span><span class="p">]</span><br>                <span class="k" style="color:#66d9ef">else</span> <span class="s1" style="color:#e6db74">''</span><br>            <span class="p">)</span><br>        <span class="p">)</span><br>    <span class="n">SORT_OPTIONS</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">(</span><span class="s1" style="color:#e6db74">'set ^'</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">set_sort_options</span><span class="p">(</span><span class="n">value</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">None</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Sets sort options"""</span><br>    <span class="n">construct_sort_options</span><span class="p">()</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">value</span><span class="p">:</span><br>        <span class="n">value</span> <span class="o" style="color:#f92672">=</span> <span class="n">value</span><span class="o" style="color:#f92672">.</span><span class="n">replace</span><span class="p">(</span><span class="n">ACTIVE_CHOICE_IDENTIFIER</span><span class="p">,</span> <span class="s2" style="color:#e6db74">""</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">value</span> <span class="ow" style="color:#f92672">in</span> <span class="n">FLAG_STATES</span><span class="p">:</span><br>        <span class="n">update_config</span><span class="p">(</span><span class="s1" style="color:#e6db74">'sort'</span><span class="p">,</span> <span class="n">value</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>        <span class="n">print_and_exit</span><span class="p">(</span><span class="n">SORT_OPTIONS</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">construct_levenshtein_sort_options</span><span class="p">():</span>  <span class="c1" style="color:#75715e"># pylint:disable=invalid-name</span><br>    <span class="sd" style="color:#e6db74">"""Constructs the options for levenshtein sorting"""</span><br>    <span class="k" style="color:#66d9ef">for</span> <span class="n">value</span> <span class="ow" style="color:#f92672">in</span> <span class="n">FLAG_STATES</span><span class="p">:</span><br>        <span class="n">LEVENSHTEIN_SORT_OPTIONS</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">(</span><br>            <span class="s1" style="color:#e6db74">'set levenshtein-sort </span><span class="si" style="color:#e6db74">%s%s</span><span class="s1" style="color:#e6db74">'</span> <span class="o" style="color:#f92672">%</span> <span class="p">(</span><br>                <span class="n">value</span><span class="p">,</span><br>                <span class="n">ACTIVE_CHOICE_IDENTIFIER</span><br>                <span class="k" style="color:#66d9ef">if</span> <span class="n">value</span> <span class="o" style="color:#f92672">==</span> <span class="n">DEFAULTS</span><span class="p">[</span><span class="s1" style="color:#e6db74">'levenshtein-sort'</span><span class="p">]</span><br>                <span class="k" style="color:#66d9ef">else</span> <span class="s1" style="color:#e6db74">''</span><br>            <span class="p">)</span><br>        <span class="p">)</span><br>    <span class="n">LEVENSHTEIN_SORT_OPTIONS</span><span class="o" style="color:#f92672">.</span><span class="n">append</span><span class="p">(</span><span class="s1" style="color:#e6db74">'set ^'</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">set_levenshtein_sort_options</span><span class="p">(</span><span class="n">value</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">None</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Sets Levenshtein sort options"""</span><br>    <span class="n">construct_levenshtein_sort_options</span><span class="p">()</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">value</span><span class="p">:</span><br>        <span class="n">value</span> <span class="o" style="color:#f92672">=</span> <span class="n">value</span><span class="o" style="color:#f92672">.</span><span class="n">replace</span><span class="p">(</span><span class="n">ACTIVE_CHOICE_IDENTIFIER</span><span class="p">,</span> <span class="s2" style="color:#e6db74">""</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">value</span> <span class="ow" style="color:#f92672">in</span> <span class="n">FLAG_STATES</span><span class="p">:</span><br>        <span class="n">update_config</span><span class="p">(</span><span class="s1" style="color:#e6db74">'levenshtein-sort'</span><span class="p">,</span> <span class="n">value</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>        <span class="n">print_and_exit</span><span class="p">(</span><span class="n">LEVENSHTEIN_SORT_OPTIONS</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">parse_config_args</span><span class="p">(</span><span class="n">args</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Parses config arguments"""</span><br>    <span class="n">config_parser</span> <span class="o" style="color:#f92672">=</span> <span class="n">ArgumentParser</span><span class="p">()</span><br>    <span class="n">config_subparsers</span> <span class="o" style="color:#f92672">=</span> <span class="n">config_parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_subparsers</span><span class="p">()</span><br>    <span class="n">matching_parser</span> <span class="o" style="color:#f92672">=</span> <span class="n">config_subparsers</span><span class="o" style="color:#f92672">.</span><span class="n">add_parser</span><span class="p">(</span><span class="s1" style="color:#e6db74">'matching'</span><span class="p">)</span><br>    <span class="n">matching_parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><span class="s1" style="color:#e6db74">'value'</span><span class="p">,</span> <span class="n">default</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">None</span><span class="p">,</span> <span class="n">nargs</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'?'</span><span class="p">)</span><br>    <span class="n">matching_parser</span><span class="o" style="color:#f92672">.</span><span class="n">set_defaults</span><span class="p">(</span><span class="n">func</span><span class="o" style="color:#f92672">=</span><span class="n">set_matching_options</span><span class="p">)</span><br>    <span class="n">sort_parser</span> <span class="o" style="color:#f92672">=</span> <span class="n">config_subparsers</span><span class="o" style="color:#f92672">.</span><span class="n">add_parser</span><span class="p">(</span><span class="s1" style="color:#e6db74">'sort'</span><span class="p">)</span><br>    <span class="n">sort_parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><span class="s1" style="color:#e6db74">'value'</span><span class="p">,</span> <span class="n">default</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">None</span><span class="p">,</span> <span class="n">nargs</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'?'</span><span class="p">)</span><br>    <span class="n">sort_parser</span><span class="o" style="color:#f92672">.</span><span class="n">set_defaults</span><span class="p">(</span><span class="n">func</span><span class="o" style="color:#f92672">=</span><span class="n">set_sort_options</span><span class="p">)</span><br>    <span class="n">levenshtein_sort_parser</span> <span class="o" style="color:#f92672">=</span> <span class="n">config_subparsers</span><span class="o" style="color:#f92672">.</span><span class="n">add_parser</span><span class="p">(</span><br>        <span class="s1" style="color:#e6db74">'levenshtein-sort'</span><span class="p">)</span><br>    <span class="n">levenshtein_sort_parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_argument</span><span class="p">(</span><span class="s1" style="color:#e6db74">'value'</span><span class="p">,</span> <span class="n">default</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">None</span><span class="p">,</span> <span class="n">nargs</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'?'</span><span class="p">)</span><br>    <span class="n">levenshtein_sort_parser</span><span class="o" style="color:#f92672">.</span><span class="n">set_defaults</span><span class="p">(</span><span class="n">func</span><span class="o" style="color:#f92672">=</span><span class="n">set_levenshtein_sort_options</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">try</span><span class="p">:</span><br>        <span class="n">config_options</span> <span class="o" style="color:#f92672">=</span> <span class="n">config_parser</span><span class="o" style="color:#f92672">.</span><span class="n">parse_known_args</span><span class="p">(</span><span class="n">args</span><span class="p">)[</span><span class="mi" style="color:#ae81ff">0</span><span class="p">]</span><br>    <span class="k" style="color:#66d9ef">except</span> <span class="ne" style="color:#a6e22e">SystemExit</span><span class="p">:</span><br>        <span class="n">config_options</span> <span class="o" style="color:#f92672">=</span> <span class="bp" style="color:#f8f8f2">None</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">config_options</span><span class="p">:</span><br>        <span class="n">config_options</span><span class="o" style="color:#f92672">.</span><span class="n">func</span><span class="p">(</span><span class="n">config_options</span><span class="o" style="color:#f92672">.</span><span class="n">value</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">parse_root_args</span><span class="p">(</span><span class="n">args</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Parses base level args or escalates"""</span><br>    <span class="n">root_parser</span> <span class="o" style="color:#f92672">=</span> <span class="n">ArgumentParser</span><span class="p">()</span><br>    <span class="n">root_subparsers</span> <span class="o" style="color:#f92672">=</span> <span class="n">root_parser</span><span class="o" style="color:#f92672">.</span><span class="n">add_subparsers</span><span class="p">()</span><br>    <span class="n">set_parser</span> <span class="o" style="color:#f92672">=</span> <span class="n">root_subparsers</span><span class="o" style="color:#f92672">.</span><span class="n">add_parser</span><span class="p">(</span><span class="s1" style="color:#e6db74">'set'</span><span class="p">)</span><br>    <span class="n">exit_parser</span> <span class="o" style="color:#f92672">=</span> <span class="n">root_subparsers</span><span class="o" style="color:#f92672">.</span><span class="n">add_parser</span><span class="p">(</span><span class="s1" style="color:#e6db74">'exit'</span><span class="p">)</span><br>    <span class="n">set_parser</span><span class="o" style="color:#f92672">.</span><span class="n">set_defaults</span><span class="p">(</span><span class="n">func</span><span class="o" style="color:#f92672">=</span><span class="n">base_options</span><span class="p">)</span><br>    <span class="n">exit_parser</span><span class="o" style="color:#f92672">.</span><span class="n">set_defaults</span><span class="p">(</span><span class="n">func</span><span class="o" style="color:#f92672">=</span><span class="n">clean_exit</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">try</span><span class="p">:</span><br>        <span class="n">options</span><span class="p">,</span> <span class="n">command_args</span> <span class="o" style="color:#f92672">=</span> <span class="n">root_parser</span><span class="o" style="color:#f92672">.</span><span class="n">parse_known_args</span><span class="p">(</span><span class="n">args</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">except</span> <span class="ne" style="color:#a6e22e">SystemExit</span><span class="p">:</span><br>        <span class="k" style="color:#66d9ef">return</span> <span class="n">base_options</span><span class="p">()</span><br>    <span class="n">parse_config_args</span><span class="p">(</span><span class="n">command_args</span><span class="p">)</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="n">options</span><span class="o" style="color:#f92672">.</span><span class="n">func</span><span class="p">()</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">prepare_args</span><span class="p">(</span><span class="n">args</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">None</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Cleans the args for processing"""</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="n">args</span> <span class="ow" style="color:#f92672">is</span> <span class="bp" style="color:#f8f8f2">None</span><span class="p">:</span><br>        <span class="n">args</span> <span class="o" style="color:#f92672">=</span> <span class="n">argv</span><span class="p">[</span><span class="mi" style="color:#ae81ff">1</span><span class="p">:]</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="mi" style="color:#ae81ff">1</span> <span class="o" style="color:#f92672">&gt;</span> <span class="nb" style="color:#f8f8f2">len</span><span class="p">(</span><span class="n">args</span><span class="p">):</span><br>        <span class="n">base_options</span><span class="p">()</span><br>    <span class="k" style="color:#66d9ef">else</span><span class="p">:</span><br>        <span class="n">new_args</span> <span class="o" style="color:#f92672">=</span> <span class="p">[]</span><br>        <span class="k" style="color:#66d9ef">for</span> <span class="n">arg</span> <span class="ow" style="color:#f92672">in</span> <span class="n">args</span><span class="p">:</span><br>            <span class="n">new_args</span> <span class="o" style="color:#f92672">+=</span> <span class="n">arg</span><span class="o" style="color:#f92672">.</span><span class="n">split</span><span class="p">(</span><span class="s1" style="color:#e6db74">' '</span><span class="p">)</span><br>        <span class="n">args</span> <span class="o" style="color:#f92672">=</span> <span class="n">new_args</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="n">args</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">parse_argv</span><span class="p">(</span><span class="n">args</span><span class="o" style="color:#f92672">=</span><span class="bp" style="color:#f8f8f2">None</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Parses the input"""</span><br>    <span class="n">args</span> <span class="o" style="color:#f92672">=</span> <span class="n">prepare_args</span><span class="p">(</span><span class="n">args</span><span class="p">)</span><br>    <span class="n">parse_root_args</span><span class="p">(</span><span class="n">args</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">create_config_if_dne</span><span class="p">(</span><span class="n">raw_config</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Creates a new config file if it doesn't exist"""</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="ow" style="color:#f92672">not</span> <span class="n">exists</span><span class="p">(</span><span class="n">CONFIG_FILE</span><span class="p">):</span><br>        <span class="k" style="color:#66d9ef">with</span> <span class="nb" style="color:#f8f8f2">open</span><span class="p">(</span><span class="n">CONFIG_FILE</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'w+'</span><span class="p">)</span> <span class="k" style="color:#66d9ef">as</span> <span class="n">config_file</span><span class="p">:</span><br>            <span class="n">config_file</span><span class="o" style="color:#f92672">.</span><span class="n">write</span><span class="p">(</span><span class="n">raw_config</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">backup_config</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Backs up the current config"""</span><br>    <span class="n">copy</span><span class="p">(</span><span class="n">CONFIG_FILE</span><span class="p">,</span> <span class="n">CONFIG_FILE</span> <span class="o" style="color:#f92672">+</span> <span class="s1" style="color:#e6db74">'.bak'</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">load_config</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Loads the active rofi config"""</span><br>    <span class="n">raw_config</span> <span class="o" style="color:#f92672">=</span> <span class="n">check_output</span><span class="p">([</span><span class="s1" style="color:#e6db74">'rofi'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'-dump-config'</span><span class="p">])</span><br>    <span class="k" style="color:#66d9ef">for</span> <span class="n">config_match</span> <span class="ow" style="color:#f92672">in</span> <span class="n">finditer</span><span class="p">(</span><span class="n">CONFIG_OPTIONS_PATTERN</span><span class="p">,</span> <span class="n">raw_config</span><span class="p">):</span><br>        <span class="n">DEFAULTS</span><span class="p">[</span><span class="n">config_match</span><span class="o" style="color:#f92672">.</span><span class="n">group</span><span class="p">(</span><span class="s1" style="color:#e6db74">'option'</span><span class="p">)]</span> <span class="o" style="color:#f92672">=</span> <span class="n">config_match</span><span class="o" style="color:#f92672">.</span><span class="n">group</span><span class="p">(</span><span class="s1" style="color:#e6db74">'value'</span><span class="p">)</span><br>    <span class="n">create_config_if_dne</span><span class="p">(</span><span class="n">raw_config</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">cli</span><span class="p">():</span><br>    <span class="n">load_config</span><span class="p">()</span><br>    <span class="n">backup_config</span><span class="p">()</span><br>    <span class="n">parse_argv</span><span class="p">()</span><br><br><span class="k" style="color:#66d9ef">if</span> <span class="s1" style="color:#e6db74">'__main__'</span> <span class="o" style="color:#f92672">==</span> <span class="vm" style="color:#f8f8f2">__name__</span><span class="p">:</span><br>    <span class="n">cli</span><span class="p">()</span><br></pre></div>
</td>
</tr>
</table>

As before, I'd recommend actually installing this to a common location.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> mkdir -p <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/scripts<br><span class="gp" style="color:#66d9ef">$</span> cp scripts/rofi-tweak-sort <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/scripts/tweak-sort<br><span class="gp" style="color:#66d9ef">$</span> awk <span class="se" style="color:#ae81ff">\</span><br>    -i inplace <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">INPLACE_SUFFIX</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">MODI</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"tweak-sort:</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/scripts/tweak-sort"</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="s1" style="color:#e6db74">' \</span><br><span class="s1" style="color:#e6db74">    match($0, /\s(combi-)?modi:[^"]*"([^"]*)"/, option) { \</span><br><span class="s1" style="color:#e6db74">        current_modi = gensub(/tweak-sort:[^,]*/, "", "g", option[2]); \</span><br><span class="s1" style="color:#e6db74">        final_modi = MODI","current_modi; \</span><br><span class="s1" style="color:#e6db74">        printf "\t%smodi: \"%s\";\n", option[1], gensub(/,+/, ",", "g", final_modi); \</span><br><span class="s1" style="color:#e6db74">        next; \</span><br><span class="s1" style="color:#e6db74">    } \</span><br><span class="s1" style="color:#e6db74">    { \</span><br><span class="s1" style="color:#e6db74">        print; \</span><br><span class="s1" style="color:#e6db74">    }'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br></pre></div>
</td></tr></table>
