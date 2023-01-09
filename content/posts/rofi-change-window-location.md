---
title: "rofi: Change Window Location"
slug: "rofi-change-window-location"
date: "2018-01-28T20:00:00.000Z"
feature_image: "/images/2018/01/change-window-location-header.png"
author: "CJ Harries"
description: "rofi is a neat tool that does so many things. This post looks at changing rofi's window location, introduces rofi's dmenu capabilities, and investigates script modi."
tags:
  - rofi
  - Linux
  - X11
  - CLI
  - tooling
  - launcher
  - dmenu
  - awk
---
<!-- markdownlint-disable MD037 -->

This is the fourth in a series of several posts on how to do way more than you really need to with `rofi`. It's a neat little tool that does so many cool things. I don't have a set number of posts, and I don't have a set goal. I just want to share something I find useful.

This post looks at changing `rofi`'s window location. It also introduces some `rofi` `dmenu` usage to handle input and ends with a introduction to `script` `modi`.

<p class="nav-p"><a id="post-nav"></a></p>

- [Assumptions](#assumptions)
- [Code](#code)
- [Window Location](#window-location)
- [Scripted](#scripted)
  - [Basic CLI Location Changer](#basic-cli-location-changer)
  - [CLI Location Changer with GUI](#cli-location-changer-with-gui)
  - [Full Location Changer](#full-location-changer)
- [Location Changer `modi`](#location-changer-modi)
  - [Create a `script` `modi`](#create-a-script-modi)
  - [Process-Spawning `modi`](#process-spawning-modi)
  - [Consuming `script` `modi`](#consuming-script-modi)
  - [Full `window-location` `modi`](#full-window-location-modi)

## Assumptions

I'm running Fedora 27. Most of the instructions are based on that OS. This will translate fairly well to other RHEL derivatives. The Debian ecosystem should also work fairly well, albeit with totally different package names. This probably won't work at all on Windows, and I have no intention of fixing that.

You're going to need a newer version of `rofi`, `>=1.4`. I'm currently running this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -version<br><span class="go" style="color:#888">Version: 1.4.2-131-git-5c5665ef (next)</span><br></pre></div>
</td></tr></table>

If you [installed from source](https://blog.wizardsoftheweb.pro/rofi-overview-and-installation#installation), you should be good to go.

## Code

You can view the code related to this post [under the `post-04-change-window-location` tag](//github.com/thecjharries/posts-tooling-rofi/tree/post-04-change-window-location).

## Window Location

By default, `rofi` launches dead-center of the owning screen.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -show run<br><span class="go" style="color:#888">should be in the center</span><br></pre></div>
</td></tr></table>

There's a config option, `location`, that allows us to change that position. We can instead place the launcher on any of the cardinals, any of the ordinals, or dead center. The locations follow a pattern like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>1 2 3<br>8 0 4<br>7 6 5<br></pre></div>
</td></tr></table>

Manipulating the location doesn't require much effort.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sed <span class="se" style="color:#ae81ff">\</span><br>    --in-place<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    -E <span class="s1" style="color:#e6db74">'s/^.*\slocation:.*$/\tlocation: 5;/g'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br><span class="gp" style="color:#66d9ef">$</span> diff --color --unified<span class="o" style="color:#f92672">=</span><span class="m" style="color:#ae81ff">0</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/config.rasi"</span><span class="o" style="color:#f92672">{</span>.bak,<span class="o" style="color:#f92672">}</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -8 +8 @@</span><br><span class="gd" style="color:#f92672">-/* location: 0;*/</span><br><span class="gi" style="color:#a6e22e">+   location: 5;</span><br></pre></div>
</td></tr></table>

## Scripted

However, manually running `sed` every time isn't that fun. We should write something.

### Basic CLI Location Changer

The first thing we'll need to do is detect the current location for comparison. Once again, `awk` is very useful. We'll need to remove comment characters, if the option isn't set yet, and we'll want to strip semicolons to make grabbing easier.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">current-location</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="sr" style="color:#e6db74">/\slocation:/</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">gsub</span><span class="p">(</span><span class="sr" style="color:#e6db74">/\/?\*\/?|;/</span><span class="p">,</span> <span class="s2" style="color:#e6db74">""</span><span class="p">);</span><br>    <span class="kr" style="color:#66d9ef">print</span> <span class="o" style="color:#f92672">$</span><span class="mi" style="color:#ae81ff">2</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">exit</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -dump-config <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'\</span><br><span class="s1" style="color:#e6db74">        /\slocation:/ { \</span><br><span class="s1" style="color:#e6db74">            gsub(/\/?\*\/?|;/, ""); \</span><br><span class="s1" style="color:#e6db74">            print $2; \</span><br><span class="s1" style="color:#e6db74">            exit; \</span><br><span class="s1" style="color:#e6db74">        }'</span><br><span class="go" style="color:#888">0</span><br></pre></div>
</td></tr></table>

Next we'll need to enumerate the directions. I spent a massive amount of time thinking about this last night, and I haven't been able to come up with anything more clever than some half-hearted expansion and associative arrays. It's a very interesting problem, and I'll probably come back to it.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">directions</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6
7</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nv" style="color:#f8f8f2">DIRECTIONS</span><span class="o" style="color:#f92672">=(</span>c n<span class="o" style="color:#f92672">{</span>w,,e<span class="o" style="color:#f92672">}</span> e s<span class="o" style="color:#f92672">{</span>e,,w<span class="o" style="color:#f92672">}</span> w<span class="o" style="color:#f92672">)</span><br><span class="nb" style="color:#f8f8f2">declare</span> -A DIRECTION_INDICES<br><br><span class="k" style="color:#66d9ef">for</span> index in <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="p">!DIRECTIONS[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><span class="p">;</span> <span class="k" style="color:#66d9ef">do</span><br>    <span class="nv" style="color:#f8f8f2">key</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">DIRECTIONS</span><span class="p">[</span><span class="nv" style="color:#f8f8f2">$index</span><span class="p">]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br>    DIRECTION_INDICES<span class="o" style="color:#f92672">[</span><span class="nv" style="color:#f8f8f2">$key</span><span class="o" style="color:#f92672">]=</span><span class="nv" style="color:#f8f8f2">$index</span><br><span class="k" style="color:#66d9ef">done</span><br></pre></div>
</td>
</tr>
</table>

This will allow us to find the direction with an index via `DIRECTIONS` or the index with a direction via `DIRECTION_INDICES`.

Somehow we've got to pass a location to the script. `argv` never hurt anyone, so we'll go that route. However, if there's one thing you should never do, it's trust your users. We'll need to sanitize and munge the input. Once again, `awk` is a great tool.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">directions</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nv" style="color:#f8f8f2">DESIRED_LOCATION_KEY</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span><br>    <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$1</span><span class="s2" style="color:#e6db74">"</span> <span class="se" style="color:#ae81ff">\</span><br>        <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'...'</span><br><span class="k" style="color:#66d9ef">)</span><br></pre></div>
</td>
</tr>
</table>

The first thing we should do is ensure the string contains only the things we're interested in.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">parse-location-input</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="p">{</span><br>    <span class="nx">input</span> <span class="o" style="color:#f92672">=</span> <span class="kr" style="color:#66d9ef">tolower</span><span class="p">(</span><span class="o" style="color:#f92672">$</span><span class="mi" style="color:#ae81ff">1</span><span class="p">);</span><br>    <span class="nx">input</span> <span class="o" style="color:#f92672">=</span> <span class="kr" style="color:#66d9ef">gensub</span><span class="p">(</span><span class="sr" style="color:#e6db74">/[^a-z]/</span><span class="p">,</span> <span class="s2" style="color:#e6db74">""</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"g"</span><span class="p">,</span> <span class="nx">input</span><span class="p">);</span><br>    <span class="p">...</span><br></pre></div>
</td>
</tr>
</table>

With a clean input, we should look for easy strings. `[ns]o[ru]th` leads six of the compass points, so stripping those is a good idea. `awk`'s regex is fairly limited, but we can run basic capture groups via `match`. If `input` begins with `[ns]`, we'll snag it and clean `input` before moving on. If it doesn't, we'll set `result` to the empty string to make combos easier.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">parse-location-input</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6
7
8
9</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>    <span class="p">...</span><br>    <span class="nx">where</span> <span class="o" style="color:#f92672">=</span> <span class="kr" style="color:#66d9ef">match</span><span class="p">(</span><span class="nx">input</span><span class="p">,</span> <span class="sr" style="color:#e6db74">/^([ns])(o[ru]th)?/</span><span class="p">,</span> <span class="nx">cardinal</span><span class="p">);</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">where</span> <span class="o" style="color:#f92672">!=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">)</span> <span class="p">{</span><br>        <span class="nx">result</span> <span class="o" style="color:#f92672">=</span> <span class="nx">cardinal</span><span class="p">[</span><span class="mi" style="color:#ae81ff">1</span><span class="p">];</span><br>        <span class="nx">input</span> <span class="o" style="color:#f92672">=</span> <span class="kr" style="color:#66d9ef">gensub</span><span class="p">(</span><span class="sr" style="color:#e6db74">/^([ns])(o[ru]th)?/</span><span class="p">,</span> <span class="s2" style="color:#e6db74">""</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"g"</span><span class="p">,</span> <span class="nx">input</span><span class="p">);</span><br>    <span class="p">}</span> <span class="k" style="color:#66d9ef">else</span> <span class="p">{</span><br>        <span class="nx">result</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">""</span><span class="p">;</span><br>    <span class="p">}</span><br>    <span class="p">...</span><br></pre></div>
</td>
</tr>
</table>

The capture group logic is the same for the remaining cardinals. However, we've got to glue things together now, as the ordinals look like `[ns][ew]`. That's why we dropped a blank `result` above.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">parse-location-input</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>    <span class="p">...</span><br>    <span class="nx">where</span> <span class="o" style="color:#f92672">=</span> <span class="kr" style="color:#66d9ef">match</span><span class="p">(</span><span class="nx">input</span><span class="p">,</span> <span class="sr" style="color:#e6db74">/^([ew])([ae]st)?/</span><span class="p">,</span> <span class="nx">cardinal</span><span class="p">);</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">where</span> <span class="o" style="color:#f92672">!=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">)</span> <span class="p">{</span><br>        <span class="nx">result</span> <span class="o" style="color:#f92672">=</span> <span class="nx">result</span><span class="s2" style="color:#e6db74">""</span><span class="nx">cardinal</span><span class="p">[</span><span class="mi" style="color:#ae81ff">1</span><span class="p">];</span><br>    <span class="p">}</span><br>    <span class="p">...</span><br></pre></div>
</td>
</tr>
</table>

After attempting to capture the directions, `result` will only be empty if

1. `center` was passed, or
2. we couldn't process and sanitize the input.

We can kill two birds with one stone by providing a default `c` result.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">parse-location-input</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>    <span class="p">...</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="s2" style="color:#e6db74">""</span> <span class="o" style="color:#f92672">==</span> <span class="nx">result</span><span class="p">)</span> <span class="p">{</span><br>        <span class="nx">result</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"c"</span><span class="p">;</span><br>    <span class="p">}</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

Finally, we need to send off `result`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">parse-location-input</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">END</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">print</span> <span class="nx">result</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

We can easily convert text directions to the proper index via the arrays we built above.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">directions</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nv" style="color:#f8f8f2">DESIRED_LOCATION</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">DIRECTION_INDICES</span><span class="p">[</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION_KEY</span><span class="p">]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br></pre></div>
</td>
</tr>
</table>

With the new location, we can finally update the config.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">directions</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6
7
8
9</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>sed <span class="se" style="color:#ae81ff">\</span><br>    --in-place<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    --regexp-extended <span class="se" style="color:#ae81ff">\</span><br>    -e <span class="s2" style="color:#e6db74">"s/^.*\slocation:.*</span>$<span class="s2" style="color:#e6db74">/\tlocation: </span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">;/g"</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br>diff <span class="se" style="color:#ae81ff">\</span><br>    --color<span class="o" style="color:#f92672">=</span>always <span class="se" style="color:#ae81ff">\</span><br>    --unified<span class="o" style="color:#f92672">=</span><span class="m" style="color:#ae81ff">0</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/config.rasi"</span><span class="o" style="color:#f92672">{</span>.bak,<span class="o" style="color:#f92672">}</span><br></pre></div>
</td>
</tr>
</table>

### CLI Location Changer with GUI

While this will run beautifully, we've completely ignored a very useful tool. `rofi` can, with minimal config, build very simple menus to make interaction easier.

The first thing we'll need to do is build a human-readable list of options.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">directions-gui</div></td>
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
11</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="o" style="color:#f92672">=(</span><br>    <span class="s1" style="color:#e6db74">'0 Center'</span><br>    <span class="s1" style="color:#e6db74">'1 Northwest'</span><br>    <span class="s1" style="color:#e6db74">'2 North'</span><br>    <span class="s1" style="color:#e6db74">'3 Northeast'</span><br>    <span class="s1" style="color:#e6db74">'4 East'</span><br>    <span class="s1" style="color:#e6db74">'5 Southeast'</span><br>    <span class="s1" style="color:#e6db74">'6 South'</span><br>    <span class="s1" style="color:#e6db74">'7 Southwest'</span><br>    <span class="s1" style="color:#e6db74">'8 West'</span><br><span class="o" style="color:#f92672">)</span><br></pre></div>
</td>
</tr>
</table>

It would also be useful if the user knew which `location` was currently active. We can modify the `DIRECTION_INDICES` `for` loop to do just that. On a related note, it would also be much nicer for the active option to be the first in the list in case the user changes their mind quickly. We can accomplish that with a simple swap.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">directions-gui</div></td>
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
10</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">for</span> index in <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="p">!DIRECTIONS[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><span class="p">;</span> <span class="k" style="color:#66d9ef">do</span><br>    <span class="nv" style="color:#f8f8f2">key</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">DIRECTIONS</span><span class="p">[</span><span class="nv" style="color:#f8f8f2">$index</span><span class="p">]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br>    DIRECTION_INDICES<span class="o" style="color:#f92672">[</span><span class="nv" style="color:#f8f8f2">$key</span><span class="o" style="color:#f92672">]=</span><span class="nv" style="color:#f8f8f2">$index</span><br>    <span class="nv" style="color:#f8f8f2">full_string</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[</span><span class="nv" style="color:#f8f8f2">$index</span><span class="p">]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> <span class="nv" style="color:#f8f8f2">$CURRENT_LOCATION</span> -eq <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">full_string</span><span class="p">//[^0-9]/</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>        <span class="nv" style="color:#f8f8f2">first_direction</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[0]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br>        FULL_DIRECTIONS<span class="o" style="color:#f92672">[</span><span class="nv" style="color:#f8f8f2">$index</span><span class="o" style="color:#f92672">]=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$first_direction</span><span class="s2" style="color:#e6db74">"</span><br>        FULL_DIRECTIONS<span class="o" style="color:#f92672">[</span><span class="m" style="color:#ae81ff">0</span><span class="o" style="color:#f92672">]=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[</span><span class="nv" style="color:#f8f8f2">$index</span><span class="p">]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74"> (active)"</span><br>    <span class="k" style="color:#66d9ef">fi</span><br><span class="k" style="color:#66d9ef">done</span><br></pre></div>
</td>
</tr>
</table>

While we're building a GUI (sorta), we don't want to remove the CLI. The goal is to build something that works together in tandem. If the script is called with an argument, we'll try to parse it. Otherwise, we'll launch `rofi`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">directions-gui</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> -n <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$1</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    <span class="c1" style="color:#75715e"># same logic from above</span><br><span class="k" style="color:#66d9ef">else</span><br>    <span class="c1" style="color:#75715e"># new rofi logic</span><br><span class="k" style="color:#66d9ef">fi</span><br></pre></div>
</td>
</tr>
</table>

The first thing we have to do is print the array (I use `printf`; I can never get `echo` to do what I want). `rofi` will then consume that (via `/dev/stdout`) to construct its GUI list. I've added a few style things that you can ignore. You really only need to pipe something into `rofi -dmenu`; everything else is just window-dressing.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">directions-gui</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>    <span class="nv" style="color:#f8f8f2">INPUT</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span><br>        <span class="nb" style="color:#f8f8f2">printf</span> <span class="s1" style="color:#e6db74">'%s\n'</span> <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span> <span class="se" style="color:#ae81ff">\</span><br>            <span class="p">|</span> rofi <span class="se" style="color:#ae81ff">\</span><br>                -dmenu <span class="se" style="color:#ae81ff">\</span><br>                -mesg <span class="s1" style="color:#e6db74">'choose location'</span> <span class="se" style="color:#ae81ff">\</span><br>                -no-fixed-num-lines <span class="se" style="color:#ae81ff">\</span><br>                -width <span class="m" style="color:#ae81ff">20</span> <span class="se" style="color:#ae81ff">\</span><br>                -hide-scrollbar <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#inputbar { children: [entry,case-indicator]; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#listview { dynamic: true; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#mainbox { children: [message,inputbar,listview]; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#message { border: 0; background-color: @selected-normal-background; text-color: @selected-normal-foreground; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#textbox { text-color: inherit; }'</span><br>    <span class="k" style="color:#66d9ef">)</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> -z <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$INPUT</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>        <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">0</span><br>    <span class="k" style="color:#66d9ef">fi</span><br>    <span class="nv" style="color:#f8f8f2">DESIRED_LOCATION</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">INPUT</span><span class="p">//[^0-9]/</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br></pre></div>
</td>
</tr>
</table>

### Full Location Changer

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">location-changer</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-tooling-rofi/blob/master/scripts/location-changer" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
90</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><br><span class="nv" style="color:#f8f8f2">CURRENT_LOCATION</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span><br>    rofi -dump-config <span class="se" style="color:#ae81ff">\</span><br>        <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'\</span><br><span class="s1" style="color:#e6db74">            /\slocation:/ { \</span><br><span class="s1" style="color:#e6db74">                gsub(/\/?\*\/?|;/, ""); \</span><br><span class="s1" style="color:#e6db74">                print $2; \</span><br><span class="s1" style="color:#e6db74">                exit; \</span><br><span class="s1" style="color:#e6db74">            }'</span><br><span class="k" style="color:#66d9ef">)</span><br><br><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="o" style="color:#f92672">=(</span><br>    <span class="s1" style="color:#e6db74">'0 Center'</span><br>    <span class="s1" style="color:#e6db74">'1 Northwest'</span><br>    <span class="s1" style="color:#e6db74">'2 North'</span><br>    <span class="s1" style="color:#e6db74">'3 Northeast'</span><br>    <span class="s1" style="color:#e6db74">'4 East'</span><br>    <span class="s1" style="color:#e6db74">'5 Southeast'</span><br>    <span class="s1" style="color:#e6db74">'6 South'</span><br>    <span class="s1" style="color:#e6db74">'7 Southwest'</span><br>    <span class="s1" style="color:#e6db74">'8 West'</span><br><span class="o" style="color:#f92672">)</span><br><br><span class="nv" style="color:#f8f8f2">DIRECTIONS</span><span class="o" style="color:#f92672">=(</span>c n<span class="o" style="color:#f92672">{</span>w,,e<span class="o" style="color:#f92672">}</span> e s<span class="o" style="color:#f92672">{</span>e,,w<span class="o" style="color:#f92672">}</span> w<span class="o" style="color:#f92672">)</span><br><span class="nb" style="color:#f8f8f2">declare</span> -A DIRECTION_INDICES<br><br><span class="k" style="color:#66d9ef">for</span> index in <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="p">!DIRECTIONS[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><span class="p">;</span> <span class="k" style="color:#66d9ef">do</span><br>    <span class="nv" style="color:#f8f8f2">key</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">DIRECTIONS</span><span class="p">[</span><span class="nv" style="color:#f8f8f2">$index</span><span class="p">]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br>    DIRECTION_INDICES<span class="o" style="color:#f92672">[</span><span class="nv" style="color:#f8f8f2">$key</span><span class="o" style="color:#f92672">]=</span><span class="nv" style="color:#f8f8f2">$index</span><br>    <span class="nv" style="color:#f8f8f2">full_string</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[</span><span class="nv" style="color:#f8f8f2">$index</span><span class="p">]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> <span class="nv" style="color:#f8f8f2">$CURRENT_LOCATION</span> -eq <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">full_string</span><span class="p">//[^0-9]/</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>        <span class="nv" style="color:#f8f8f2">first_direction</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[0]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br>        FULL_DIRECTIONS<span class="o" style="color:#f92672">[</span><span class="nv" style="color:#f8f8f2">$index</span><span class="o" style="color:#f92672">]=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$first_direction</span><span class="s2" style="color:#e6db74">"</span><br>        FULL_DIRECTIONS<span class="o" style="color:#f92672">[</span><span class="m" style="color:#ae81ff">0</span><span class="o" style="color:#f92672">]=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[</span><span class="nv" style="color:#f8f8f2">$index</span><span class="p">]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74"> (active)"</span><br>    <span class="k" style="color:#66d9ef">fi</span><br><span class="k" style="color:#66d9ef">done</span><br><br><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> -n <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$1</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    <span class="nv" style="color:#f8f8f2">INPUT</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$1</span><span class="s2" style="color:#e6db74">"</span><br>    <span class="nv" style="color:#f8f8f2">DESIRED_LOCATION_KEY</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span><br>        <span class="nb" style="color:#f8f8f2">echo</span> <span class="nv" style="color:#f8f8f2">$INPUT</span> <span class="se" style="color:#ae81ff">\</span><br>            <span class="p">|</span> awk <span class="s1" style="color:#e6db74">' \</span><br><span class="s1" style="color:#e6db74">                { \</span><br><span class="s1" style="color:#e6db74">                    input = tolower($1); \</span><br><span class="s1" style="color:#e6db74">                    input = gensub(/[^a-z]/, "", "g", input); \</span><br><span class="s1" style="color:#e6db74">                    where = match(input, /^([ns])(o[ru]th)?/, cardinal); \</span><br><span class="s1" style="color:#e6db74">                    if (where != 0) { \</span><br><span class="s1" style="color:#e6db74">                        result = cardinal[1]; \</span><br><span class="s1" style="color:#e6db74">                        input = gensub(/^([ns])(o[ru]th)?/, "", "g", input); \</span><br><span class="s1" style="color:#e6db74">                    } else { \</span><br><span class="s1" style="color:#e6db74">                        result = ""; \</span><br><span class="s1" style="color:#e6db74">                    } \</span><br><span class="s1" style="color:#e6db74">                    where = match(input, /^([ew])([ae]st)?/, cardinal); \</span><br><span class="s1" style="color:#e6db74">                    if (where != 0) { \</span><br><span class="s1" style="color:#e6db74">                        result = result""cardinal[1]; \</span><br><span class="s1" style="color:#e6db74">                    } \</span><br><span class="s1" style="color:#e6db74">                    if ("" == result) { \</span><br><span class="s1" style="color:#e6db74">                        result = "c"; \</span><br><span class="s1" style="color:#e6db74">                    } \</span><br><span class="s1" style="color:#e6db74">                } \</span><br><span class="s1" style="color:#e6db74">                END { \</span><br><span class="s1" style="color:#e6db74">                    print result; \</span><br><span class="s1" style="color:#e6db74">                }'</span><br>    <span class="k" style="color:#66d9ef">)</span><br>    <span class="nv" style="color:#f8f8f2">DESIRED_LOCATION</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">DIRECTION_INDICES</span><span class="p">[</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION_KEY</span><span class="p">]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br><span class="k" style="color:#66d9ef">else</span><br>    <span class="nv" style="color:#f8f8f2">INPUT</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span><br>        <span class="nb" style="color:#f8f8f2">printf</span> <span class="s1" style="color:#e6db74">'%s\n'</span> <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span> <span class="se" style="color:#ae81ff">\</span><br>            <span class="p">|</span> rofi <span class="se" style="color:#ae81ff">\</span><br>                -dmenu <span class="se" style="color:#ae81ff">\</span><br>                -mesg <span class="s1" style="color:#e6db74">'choose location'</span> <span class="se" style="color:#ae81ff">\</span><br>                -no-fixed-num-lines <span class="se" style="color:#ae81ff">\</span><br>                -width <span class="m" style="color:#ae81ff">20</span> <span class="se" style="color:#ae81ff">\</span><br>                -hide-scrollbar <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#inputbar { children: [entry,case-indicator]; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#listview { dynamic: true; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#mainbox { children: [message,inputbar,listview]; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#message { border: 0; background-color: @selected-normal-background; text-color: @selected-normal-foreground; }'</span> <span class="se" style="color:#ae81ff">\</span><br>                -theme-str <span class="s1" style="color:#e6db74">'#textbox { text-color: inherit; }'</span><br>    <span class="k" style="color:#66d9ef">)</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> -z <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$INPUT</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>        <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">0</span><br>    <span class="k" style="color:#66d9ef">fi</span><br>    <span class="nv" style="color:#f8f8f2">DESIRED_LOCATION</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">INPUT</span><span class="p">//[^0-9]/</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br><span class="k" style="color:#66d9ef">fi</span><br><br>sed --in-place<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> -E <span class="s2" style="color:#e6db74">"s/^.*\slocation:.*</span>$<span class="s2" style="color:#e6db74">/\tlocation: </span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">;/g"</span> <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br><br>diff --color --unified<span class="o" style="color:#f92672">=</span><span class="m" style="color:#ae81ff">0</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/config.rasi"</span><span class="o" style="color:#f92672">{</span>.bak,<span class="o" style="color:#f92672">}</span><br></pre></div>
</td>
</tr>
</table>

It's very simple to use. Like `rofi`, it defaults to the center position.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> scripts/location-changer n<br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -8 +8 @@</span><br><span class="gd" style="color:#f92672">-/* location: 0;*/</span><br><span class="gi" style="color:#a6e22e">+   location: 2;</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> scripts/location-changer qqq<br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -8 +8 @@</span><br><span class="gd" style="color:#f92672">-   location: 2;</span><br><span class="gi" style="color:#a6e22e">+   location: 0;</span><br></pre></div>
</td></tr></table>

The GUI provides an alternate way to get at things.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> scripts/location-changer<br><span class="go" style="color:#888">...</span><br></pre></div>
</td></tr></table>

![location-changer-gui-south](/images/2018/01/location-changer-gui-south.png)

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -8 +8 @@</span><br><span class="gd" style="color:#f92672">-   location: 0;</span><br><span class="gi" style="color:#a6e22e">+   location: 5;</span><br></pre></div>
</td></tr></table>

## Location Changer `modi`

Taking what we've learned, we should be able to build a `script` `modi` capable of updating the window location. Essentially, a `script` `modi` is a never-ending pipe. `rofi` launches the script, the user interacts, and the script finishes. Its output is then piped back into the original script to run again. It will run until an external close action (e.g. `Esc`) is fired or the script sends nothing out on `/dev/stdout`.

### Create a `script` `modi`

Like before, we'll want to start with a list of options. I wanted to include an exit option this time around. We'll also need to parse the current `location` for comparison.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">location-changer-modi</div></td>
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
22</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="o" style="color:#f92672">=(</span><br>    <span class="s1" style="color:#e6db74">'0 Center'</span><br>    <span class="s1" style="color:#e6db74">'1 Northwest'</span><br>    <span class="s1" style="color:#e6db74">'2 North'</span><br>    <span class="s1" style="color:#e6db74">'3 Northeast'</span><br>    <span class="s1" style="color:#e6db74">'4 East'</span><br>    <span class="s1" style="color:#e6db74">'5 Southeast'</span><br>    <span class="s1" style="color:#e6db74">'6 South'</span><br>    <span class="s1" style="color:#e6db74">'7 Southwest'</span><br>    <span class="s1" style="color:#e6db74">'8 West'</span><br>    <span class="s1" style="color:#e6db74">'9 Exit'</span><br><span class="o" style="color:#f92672">)</span><br><br><span class="nv" style="color:#f8f8f2">CURRENT_LOCATION</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span><br>    rofi -dump-config <span class="se" style="color:#ae81ff">\</span><br>        <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'\</span><br><span class="s1" style="color:#e6db74">            /\slocation:/ { \</span><br><span class="s1" style="color:#e6db74">                gsub(/\/?\*\/?|;/, ""); \</span><br><span class="s1" style="color:#e6db74">                print $2; \</span><br><span class="s1" style="color:#e6db74">                exit; \</span><br><span class="s1" style="color:#e6db74">            }'</span><br><span class="k" style="color:#66d9ef">)</span><br></pre></div>
</td>
</tr>
</table>

I was a bit tidier this time around, and threw the setup into a function. We'll update the option list and print the options, just like before.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">location-changer-modi</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">function</span> rebuild_directions <span class="o" style="color:#f92672">{</span><br>    FULL_DIRECTIONS<span class="o" style="color:#f92672">[</span><span class="nv" style="color:#f8f8f2">$CURRENT_LOCATION</span><span class="o" style="color:#f92672">]=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[</span><span class="nv" style="color:#f8f8f2">$CURRENT_LOCATION</span><span class="p">]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74"> (active)"</span><br>    <span class="nb" style="color:#f8f8f2">printf</span> <span class="s1" style="color:#e6db74">'%s\n'</span> <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br><span class="o" style="color:#f92672">}</span><br></pre></div>
</td>
</tr>
</table>

We'll want to run that no matter what to keep things fresh. However, we won't want to update the config unless the location changes.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">location-changer-modi</div></td>
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
13</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> ! -z <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$@</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    <span class="nv" style="color:#f8f8f2">DESIRED_LOCATION</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">1</span><span class="p">//[^0-9]/</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$CURRENT_LOCATION</span><span class="s2" style="color:#e6db74">"</span> -ne <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> <span class="m" style="color:#ae81ff">0</span> -le <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="o" style="color:#f92672">[[</span> <span class="m" style="color:#ae81ff">8</span> -ge <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>            sed --in-place<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> -e <span class="s2" style="color:#e6db74">"s/^.*\slocation:.*</span>$<span class="s2" style="color:#e6db74">/\tlocation: </span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">;/g"</span> <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br>        <span class="k" style="color:#66d9ef">elif</span> <span class="o" style="color:#f92672">[[</span> <span class="m" style="color:#ae81ff">9</span> -eq <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>            <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">0</span><br>        <span class="k" style="color:#66d9ef">else</span><br>            <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">1</span><br>        <span class="k" style="color:#66d9ef">fi</span><br>    <span class="k" style="color:#66d9ef">fi</span><br><span class="k" style="color:#66d9ef">fi</span><br>rebuild_directions<br></pre></div>
</td>
</tr>
</table>

This works quite well. As the user interacts, the config gets updated. It does what it says on the tin. Like this:

![rofi-location-changer-frozen](/images/2018/01/rofi-location-changer-frozen.png)

On the surface, that looks awesome. However, if you look closely, the `location` is dead center but `rofi` is reporting `East` is active. This presents a very interesting problem with `script` `modi`. Because they're pipes, `rofi` isn't reloading each time. The `modi` can't call `rofi` again, because it's already running. More importantly, even if it could, it's going to lose the original command, which could contain extra configuration.

### Process-Spawning `modi`

I spent a decent chunk of time beating my head against this, and then I realized that `rofi` stores its `pid`. We can access the `pid` file via the config, which in turn gives us access to all the information we need. Before I get to the exciting stuff, though, it's important to mention safety. It's a really good idea to limit your process count (somehow) in case you create a runaway script. Speaking from experience, it could be half an hour before you can free up enough memory to switch to another `tty` and kill everything.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">location-changer-respawning-modi</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> <span class="m" style="color:#ae81ff">10</span> -lt <span class="k" style="color:#66d9ef">$(</span>pgrep -c -f <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$0</span><span class="s2" style="color:#e6db74">"</span><span class="k" style="color:#66d9ef">)</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    pkill -f rofi<br>    pkill -f <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$0</span><span class="s2" style="color:#e6db74">"</span><br>    <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">1</span><br><span class="k" style="color:#66d9ef">fi</span><br></pre></div>
</td>
</tr>
</table>

Using `awk`, we can set up variables that are immediately consumed by `eval`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">location-changer-respawning-modi</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">eval</span> <span class="k" style="color:#66d9ef">$(</span><br>    rofi -dump-config         <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'</span><br><span class="s1" style="color:#e6db74">            /\slocation:/ {</span><br><span class="s1" style="color:#e6db74">                gsub(/\/?\*\/?|;/, "");</span><br><span class="s1" style="color:#e6db74">                print "CURRENT_LOCATION="$2;</span><br><span class="s1" style="color:#e6db74">                location = 1;</span><br><span class="s1" style="color:#e6db74">                next;</span><br><span class="s1" style="color:#e6db74">            }</span><br><span class="s1" style="color:#e6db74">            /\spid:/ {</span><br><span class="s1" style="color:#e6db74">                gsub(/\/?\*\/?|;|"/, "");</span><br><span class="s1" style="color:#e6db74">                print "ROFI_PID="$2;</span><br><span class="s1" style="color:#e6db74">                pid = 1;</span><br><span class="s1" style="color:#e6db74">                next;</span><br><span class="s1" style="color:#e6db74">            }</span><br><span class="s1" style="color:#e6db74">            location &amp;&amp; pid {</span><br><span class="s1" style="color:#e6db74">                exit;</span><br><span class="s1" style="color:#e6db74">            }'</span><br><span class="k" style="color:#66d9ef">)</span><br></pre></div>
</td>
</tr>
</table>

Why exactly do we need the `pid`? It's so we can duplicate the currently running script with all its arguments.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ps --no-headers -o <span class="nb" style="color:#f8f8f2">command</span> -p <span class="k" style="color:#66d9ef">$(</span>cat <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$ROFI_PID</span><span class="s2" style="color:#e6db74">"</span><span class="k" style="color:#66d9ef">)</span><br><span class="go" style="color:#888">rofi -show drun</span><br></pre></div>
</td></tr></table>

The command by itself isn't going to do us very much good. Attempting to run `rofi` from inside a `script` `modi` hits the process lock. (I supposed we could unlock it, but that's a whole new can of bugs to crush.) Happily enough, we can dump the command out to another script and execute in the background to refresh `rofi`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">location-changer-respawning-modi</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">function</span> create_and_spawn_runner <span class="o" style="color:#f92672">{</span><br>    <span class="nv" style="color:#f8f8f2">ROFI_COMMAND</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span>ps --no-headers -o <span class="nb" style="color:#f8f8f2">command</span> -p <span class="k" style="color:#66d9ef">$(</span>cat <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$ROFI_PID</span><span class="s2" style="color:#e6db74">"</span><span class="k" style="color:#66d9ef">))</span><br>    <span class="nv" style="color:#f8f8f2">new_source</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span>mktemp -p <span class="nv" style="color:#f8f8f2">$TMPDIR</span> rofi-location-XXXX<span class="k" style="color:#66d9ef">)</span><br>    chmod +x <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$new_source</span><span class="s2" style="color:#e6db74">"</span><br>    cat <span class="s" style="color:#e6db74">&lt;&lt;EOF &gt;$new_source</span><br><span class="s" style="color:#e6db74">#!/bin/bash</span><br><br><span class="s" style="color:#e6db74">$ROFI_COMMAND</span><br><span class="s" style="color:#e6db74">rm -rf "$new_source"</span><br><span class="s" style="color:#e6db74">EOF</span><br>    coproc <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$new_source</span><span class="s2" style="color:#e6db74">"</span> &gt;/dev/null<br><span class="o" style="color:#f92672">}</span><br></pre></div>
</td>
</tr>
</table>

Finally, we need to update some of the parsing logic. If the `location` changes, we'll need to spawn a new process and exit instead of continuing along.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">location-changer-respawning-modi</div></td>
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
15</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> ! -z <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$@</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    <span class="nv" style="color:#f8f8f2">DESIRED_LOCATION</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">1</span><span class="p">//[^0-9]/</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$CURRENT_LOCATION</span><span class="s2" style="color:#e6db74">"</span> -ne <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> <span class="m" style="color:#ae81ff">0</span> -le <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="o" style="color:#f92672">[[</span> <span class="m" style="color:#ae81ff">8</span> -ge <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>            sed --in-place<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> -e <span class="s2" style="color:#e6db74">"s/^.*\slocation:.*</span>$<span class="s2" style="color:#e6db74">/\tlocation: </span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">;/g"</span> <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br>            create_and_spawn_runner<br>            <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">0</span><br>        <span class="k" style="color:#66d9ef">elif</span> <span class="o" style="color:#f92672">[[</span> <span class="m" style="color:#ae81ff">9</span> -eq <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>            <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">0</span><br>        <span class="k" style="color:#66d9ef">else</span><br>            <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">1</span><br>        <span class="k" style="color:#66d9ef">fi</span><br>    <span class="k" style="color:#66d9ef">fi</span><br><span class="k" style="color:#66d9ef">fi</span><br>rebuild_directions<br></pre></div>
</td>
</tr>
</table>

### Consuming `script` `modi`

`script` `modi` are listed in config options as `<prompt>:<path>`. You can add them to the `modi` or `combi-modi` lists. I'd recommend creating a directory for `script`s to keep things organized. I did this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> mkdir -p <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/scripts<br><span class="gp" style="color:#66d9ef">$</span> cp scripts/rofi-location-changer <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/scripts/window-location<br><span class="gp" style="color:#66d9ef">$</span> awk <span class="se" style="color:#ae81ff">\</span><br>    -i inplace <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">INPLACE_SUFFIX</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">MODI</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"window-location:</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/scripts/window-location"</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="s1" style="color:#e6db74">' \</span><br><span class="s1" style="color:#e6db74">    match($0, /\s(combi-)?modi:[^"]*"([^"]*)"/, option) { \</span><br><span class="s1" style="color:#e6db74">        current_modi = gensub(/window-location:[^,]*/, "", "g", option[2]); \</span><br><span class="s1" style="color:#e6db74">        final_modi = MODI","current_modi; \</span><br><span class="s1" style="color:#e6db74">        printf "\t%smodi: \"%s\";\n", option[1], gensub(/,+/, ",", "g", final_modi); \</span><br><span class="s1" style="color:#e6db74">        next; \</span><br><span class="s1" style="color:#e6db74">    } \</span><br><span class="s1" style="color:#e6db74">    { \</span><br><span class="s1" style="color:#e6db74">        print; \</span><br><span class="s1" style="color:#e6db74">    }'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br></pre></div>
</td></tr></table>

If you don't want it in the `combi`, strip that logic.

### Full `window-location` `modi`

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">rofi-location-changer</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-tooling-rofi/blob/master/scripts/rofi-location-changer" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
89</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><br><span class="c1" style="color:#75715e"># Ensure the process count isn't running out of control</span><br><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> <span class="m" style="color:#ae81ff">10</span> -lt <span class="k" style="color:#66d9ef">$(</span>pgrep -c -f <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$0</span><span class="s2" style="color:#e6db74">"</span><span class="k" style="color:#66d9ef">)</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    pkill -f rofi<br>    pkill -f <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$0</span><span class="s2" style="color:#e6db74">"</span><br>    <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">1</span><br><span class="k" style="color:#66d9ef">fi</span><br><br><span class="c1" style="color:#75715e"># Array of options</span><br><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="o" style="color:#f92672">=(</span><br>    <span class="s1" style="color:#e6db74">'0 Center'</span><br>    <span class="s1" style="color:#e6db74">'1 Northwest'</span><br>    <span class="s1" style="color:#e6db74">'2 North'</span><br>    <span class="s1" style="color:#e6db74">'3 Northeast'</span><br>    <span class="s1" style="color:#e6db74">'4 East'</span><br>    <span class="s1" style="color:#e6db74">'5 Southeast'</span><br>    <span class="s1" style="color:#e6db74">'6 South'</span><br>    <span class="s1" style="color:#e6db74">'7 Southwest'</span><br>    <span class="s1" style="color:#e6db74">'8 West'</span><br>    <span class="s1" style="color:#e6db74">'9 Exit'</span><br><span class="o" style="color:#f92672">)</span><br><br><span class="c1" style="color:#75715e"># Parse the current config for location and pid</span><br><span class="nb" style="color:#f8f8f2">eval</span> <span class="k" style="color:#66d9ef">$(</span><br>    rofi -dump-config <span class="se" style="color:#ae81ff">\</span><br>        <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'</span><br><span class="s1" style="color:#e6db74">            /\slocation:/ {</span><br><span class="s1" style="color:#e6db74">                gsub(/\/?\*\/?|;/, "");</span><br><span class="s1" style="color:#e6db74">                print "CURRENT_LOCATION="$2;</span><br><span class="s1" style="color:#e6db74">                location = 1;</span><br><span class="s1" style="color:#e6db74">                next;</span><br><span class="s1" style="color:#e6db74">            }</span><br><span class="s1" style="color:#e6db74">            /\spid:/ {</span><br><span class="s1" style="color:#e6db74">                gsub(/\/?\*\/?|;|"/, "");</span><br><span class="s1" style="color:#e6db74">                print "ROFI_PID="$2;</span><br><span class="s1" style="color:#e6db74">                pid = 1;</span><br><span class="s1" style="color:#e6db74">                next;</span><br><span class="s1" style="color:#e6db74">            }</span><br><span class="s1" style="color:#e6db74">            location &amp;&amp; pid {</span><br><span class="s1" style="color:#e6db74">                exit;</span><br><span class="s1" style="color:#e6db74">            }'</span><br><span class="k" style="color:#66d9ef">)</span><br><br><span class="k" style="color:#66d9ef">function</span> rebuild_directions <span class="o" style="color:#f92672">{</span><br>    <span class="c1" style="color:#75715e"># Mark it in the options</span><br>    FULL_DIRECTIONS<span class="o" style="color:#f92672">[</span><span class="nv" style="color:#f8f8f2">$CURRENT_LOCATION</span><span class="o" style="color:#f92672">]=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[</span><span class="nv" style="color:#f8f8f2">$CURRENT_LOCATION</span><span class="p">]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74"> (active)"</span><br>    <span class="c1" style="color:#75715e"># Print the options</span><br>    <span class="nb" style="color:#f8f8f2">printf</span> <span class="s1" style="color:#e6db74">'%s\n'</span> <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">FULL_DIRECTIONS</span><span class="p">[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br><span class="o" style="color:#f92672">}</span><br><br><span class="k" style="color:#66d9ef">function</span> create_and_spawn_runner <span class="o" style="color:#f92672">{</span><br>    <span class="c1" style="color:#75715e"># Snag the current command</span><br>    <span class="nv" style="color:#f8f8f2">ROFI_COMMAND</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span>ps --no-headers -o <span class="nb" style="color:#f8f8f2">command</span> -p <span class="k" style="color:#66d9ef">$(</span>cat <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$ROFI_PID</span><span class="s2" style="color:#e6db74">"</span><span class="k" style="color:#66d9ef">))</span><br>    <span class="c1" style="color:#75715e"># Create a temp file</span><br>    <span class="nv" style="color:#f8f8f2">new_source</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span>mktemp -p <span class="nv" style="color:#f8f8f2">$TMPDIR</span> rofi-location-XXXX<span class="k" style="color:#66d9ef">)</span><br>    <span class="c1" style="color:#75715e"># Ensure it's executable</span><br>    chmod +x <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$new_source</span><span class="s2" style="color:#e6db74">"</span><br>    <span class="c1" style="color:#75715e"># Create the runner</span><br>    cat <span class="s" style="color:#e6db74">&lt;&lt;EOF &gt;$new_source</span><br><span class="s" style="color:#e6db74">#!/bin/bash</span><br><br><span class="s" style="color:#e6db74">$ROFI_COMMAND</span><br><span class="s" style="color:#e6db74">rm -rf "$new_source"</span><br><span class="s" style="color:#e6db74">EOF</span><br>    <span class="c1" style="color:#75715e"># Spawn it in the background</span><br>    coproc <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$new_source</span><span class="s2" style="color:#e6db74">"</span> &gt;/dev/null<br><span class="o" style="color:#f92672">}</span><br><br><span class="c1" style="color:#75715e"># Something was passed</span><br><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> ! -z <span class="nv" style="color:#f8f8f2">$@</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    <span class="c1" style="color:#75715e"># Parse the new location</span><br>    <span class="nv" style="color:#f8f8f2">DESIRED_LOCATION</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">1</span><span class="p">//[^0-9]/</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$CURRENT_LOCATION</span><span class="s2" style="color:#e6db74">"</span> -ne <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>        <span class="c1" style="color:#75715e"># Check to see if location is in the proper range</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> <span class="m" style="color:#ae81ff">0</span> -le <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="o" style="color:#f92672">[[</span> <span class="m" style="color:#ae81ff">8</span> -ge <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>            <span class="c1" style="color:#75715e"># It is; update the config</span><br>            sed --in-place<span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> -e <span class="s2" style="color:#e6db74">"s/^.*\slocation:.*</span>$<span class="s2" style="color:#e6db74">/\tlocation: </span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">;/g"</span> <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br>            <span class="c1" style="color:#75715e"># Create next instance</span><br>            create_and_spawn_runner<br>            <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">0</span><br>        <span class="k" style="color:#66d9ef">elif</span> <span class="o" style="color:#f92672">[[</span> <span class="m" style="color:#ae81ff">9</span> -eq <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DESIRED_LOCATION</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>            <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">0</span><br>        <span class="k" style="color:#66d9ef">else</span><br>            <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">1</span><br>        <span class="k" style="color:#66d9ef">fi</span><br>    <span class="k" style="color:#66d9ef">fi</span><br><span class="k" style="color:#66d9ef">fi</span><br>rebuild_directions<br></pre></div>
</td>
</tr>
</table>
