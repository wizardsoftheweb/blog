---
title: "rofi: Scripting modi Discovery"
slug: "rofi-scripting-modi-discovery"
date: "2018-01-28T18:00:00.000Z"
feature_image: "/images/2018/01/scripting-modi-discovery-header.png"
author: "CJ Harries"
description: "rofi is a neat little tool that does so many cool things. This post looks at automatically updating modi lists. It also covers some intro awk stuff."
tags:
  - rofi
  - Linux
  - X11
  - CLI
  - tooling
  - launcher
  - awk
---
<!-- markdownlint-disable MD010 MD037 -->

This is the third in a series of several posts on how to do way more than you really need to with `rofi`. It's a neat little tool that does so many cool things. I don't have a set number of posts, and I don't have a set goal. I just want to share something I find useful.

This post looks at automatically updating `modi` lists. It also covers some intro `awk` stuff, so feel free to skip around.

<p class="nav-p"><a id="post-nav"></a></p>

- [Assumptions](#assumptions)
- [Code](#code)
- [Script `modi` Discovery](#script-modi-discovery)
- [Available `modi`](#available-modi)
- [Updating the Config File](#updating-the-config-file)
  - [`-show`-able `modi`](#-show-able-modi)
  - [`combi` `modi`](#combi-modi)
- [All the `modi`](#all-the-modi)
  - [Shell Script](#shell-script)
  - [`glob`](#glob)

## Assumptions

I'm running Fedora 27. Most of the instructions are based on that OS. This will translate fairly well to other RHEL derivatives. The Debian ecosystem should also work fairly well, albeit with totally different package names. This probably won't work at all on Windows, and I have no intention of fixing that.

You're going to need a newer version of `rofi`, `>=1.4`. I'm currently running this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -version<br><span class="go" style="color:#888">Version: 1.4.2-131-git-5c5665ef (next)</span><br></pre></div>
</td></tr></table>

If you [installed from source](https://blog.wizardsoftheweb.pro/rofi-overview-and-installation#installation), you should be good to go.

## Code

You can view the code related to this post [under the `post-03-scripting-modi-discovery` tag](//github.com/thecjharries/posts-tooling-rofi/tree/post-03-scripting-modi-discovery).

## Script `modi` Discovery

If you look at the `man` page or check `rofi`'s help, you'll probably notice that not all the `modi`s are enabled. You can also force the issue by attempting to `-show` a nonexistent `modi`:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -show qqq<br><span class="go" style="color:#888">Mode qqq is not found.</span><br><span class="go" style="color:#888">The following modi are known:</span><br><span class="go" style="color:#888">        * +window</span><br><span class="go" style="color:#888">        * windowcd</span><br><span class="go" style="color:#888">        * +run</span><br><span class="go" style="color:#888">        * +ssh</span><br><span class="go" style="color:#888">        * drun</span><br><span class="go" style="color:#888">        * combi</span><br><span class="go" style="color:#888">        * keys</span><br></pre></div>
</td></tr></table>

A safer way to discover `modi`, on the off-chance you're running a `qqq` `modi`, is to check the tail end of `rofi --help`.

Using the default config, the currently enabled `modi` are as follows:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> grep -E <span class="s1" style="color:#e6db74">'\smodi:'</span> <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br><span class="go" style="color:#888">/*      modi: "window,run,ssh";*/</span><br></pre></div>
</td></tr></table>

The definition is pretty simple. It's just a comma-separated list of `modi` inside a string. Since `rofi` gives provides a convenient list of accessible `modi`, we have two choices:

1. manually pick desired `modi` and manually update the config like a peasant, or
2. stream the whole thing directly from the help into the config.

Of course, you could probably finish #1 before you get done reading the following code breakdown, but where's the fun in that?

The first thing we have to do is parse the list of available `modi`. At the moment, it looks like help [leads the list with `Detected modi`](https://github.com/DaveDavenport/rofi/blob/1.4.2/source/rofi.c#L287), prints [`modi` name and active state](https://github.com/DaveDavenport/rofi/blob/1.4.2/source/rofi.c#L248), and finishes [with an empty line](https://github.com/DaveDavenport/rofi/blob/1.4.2/source/rofi.c#L289). The rest of the help file isn't useful here. We're going to have to parse essentially the entire thing, since the pertinent help appears at the bottom. `sed` would be an okay solution, printing only the lines we're interested in and manipulating them. However, we'd have to pipe those results into something else to clean them up for use as a single-line string. `awk`, on the other hand, will let us parse the file and manipulate the return as needed.

## Available `modi`

To start, let's declare a list of `modi` and a flag that can be used to determine whether or not the list of `modi` has started. `awk`'s `BEGIN` section is only run once, at the beginning of the input.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">available-modi-parser snippet</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">BEGIN</span> <span class="p">{</span><br>    <span class="nx">modi</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">""</span><span class="p">;</span><br>    <span class="nx">grabbing</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

We'll need some way to let `awk` know when we should start grabbing. `next` lets us skip to the next record without processing anything else.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">available-modi-parser snippet</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="sr" style="color:#e6db74">/Detected modi/</span> <span class="p">{</span><br>    <span class="nx">grabbing</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">;</span><br>    <span class="kr" style="color:#66d9ef">next</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

If we're not `grabbing`, there's no reason to process any of the other conditionals.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">available-modi-parser snippet</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="o" style="color:#f92672">!</span><span class="nx">grabbing</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">next</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

Once we are grabbing, we should stop when we hit a line with no fields. The `NF` magic variable counts the number of fields per record. The `exit` command will shoot us straight to the `END` of the `awk` script, skipping any remaining records.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">available-modi-parser snippet</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nx">grabbing</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="o" style="color:#f92672">!</span><span class="nb" style="color:#f8f8f2">NF</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">exit</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

If we are grabbing and we have records, they're going to look something like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>        * +window<br></pre></div>
</td></tr></table>

That means the numbered inputs look something like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>$0:         * +window<br>$1: *<br>$2: +window<br></pre></div>
</td></tr></table>

So we want to consume `$2`, except we don't want `+`. `gsub` will replace any instance of a pattern in the record. String concatenation you should already understand; `awk` just glues things together without the need for extra operators.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">available-modi-parser snippet</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nx">grabbing</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">gsub</span><span class="p">(</span><span class="s2" style="color:#e6db74">"+"</span><span class="p">,</span> <span class="s2" style="color:#e6db74">""</span><span class="p">);</span><br>    <span class="nx">modi</span> <span class="o" style="color:#f92672">=</span> <span class="o" style="color:#f92672">$</span><span class="mi" style="color:#ae81ff">2</span><span class="s2" style="color:#e6db74">","</span><span class="nx">modi</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

Finally, at the tail end of the script, we want to print what we've found. Similar to the `BEGIN` block, the `END` block is run once, after all the records are processed (or `exit` is called). `gensub` takes a pattern, a replacement, the method, and input string. If you'll notice above, we're going to have an extra trailing comma at the end of `modi`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">available-modi-parser snippet</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">END</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">print</span> <span class="kr" style="color:#66d9ef">gensub</span><span class="p">(</span><span class="s2" style="color:#e6db74">",$"</span><span class="p">,</span> <span class="s2" style="color:#e6db74">""</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"g"</span><span class="p">,</span> <span class="nx">modi</span><span class="p">);</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

At this point, we could do something like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi --help <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'\</span><br><span class="s1" style="color:#e6db74">        BEGIN{ modi = ""; grabbing = 0 } \</span><br><span class="s1" style="color:#e6db74">        /Detected modi/{ grabbing = 1; next } \</span><br><span class="s1" style="color:#e6db74">        !grabbing { next } \</span><br><span class="s1" style="color:#e6db74">        grabbing &amp;&amp; !NF { exit } \</span><br><span class="s1" style="color:#e6db74">        grabbing { gsub("+",""); modi = $2","modi } \</span><br><span class="s1" style="color:#e6db74">        END{ print gensub(",$","","g",modi) }'</span><br><span class="go" style="color:#888">keys,combi,drun,ssh,run,windowcd,window</span><br></pre></div>
</td></tr></table>

However, that means we'd have to manually copy that and manually paste it into out config. Like a peasant. Or we could stream it. Guess what I want to do.

We have a small problem. (Or rather, I have a small problem, possibly related to my lack of `bash` knowledge.) `awk` dumps to `/dev/stdout`. That means consuming `awk` has to be done in a subshell, which is kinda boring, or `source`d (sorta), which is exotic (**AND POTENTIALLY VERY DANGEROUS**). I personally prefer creating variables, rather than throwing together a hot mess of nested subshells. Coming from JavaScript, I'm very wary of callback hell.

We can easily modify what we've written so far to dump a variable instead of a simple string.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">available-modi-parser snippet</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">END</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">print</span> <span class="s2" style="color:#e6db74">"DISCOVERED_MODI="</span><span class="kr" style="color:#66d9ef">gensub</span><span class="p">(</span><span class="s2" style="color:#e6db74">",$"</span><span class="p">,</span> <span class="s2" style="color:#e6db74">""</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"g"</span><span class="p">,</span> <span class="nx">modi</span><span class="p">);</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi --help <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'\</span><br><span class="s1" style="color:#e6db74">        BEGIN{ modi = ""; grabbing = 0 } \</span><br><span class="s1" style="color:#e6db74">        /Detected modi/{ grabbing = 1; next } \</span><br><span class="s1" style="color:#e6db74">        !grabbing { next } \</span><br><span class="s1" style="color:#e6db74">        grabbing &amp;&amp; !NF { exit } \</span><br><span class="s1" style="color:#e6db74">        grabbing { gsub("+",""); modi = $2","modi } \</span><br><span class="s1" style="color:#e6db74">        END{ print "DISCOVERED_MODI="gensub(",$","","g",modi) }'</span><br><span class="go" style="color:#888">DISCOVERED_MODI=keys,combi,drun,ssh,run,windowcd,window</span><br></pre></div>
</td></tr></table>

Consuming this is as simple as `source`ing the pipe.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi --help <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'\</span><br><span class="s1" style="color:#e6db74">        BEGIN{ modi = ""; grabbing = 0 } \</span><br><span class="s1" style="color:#e6db74">        /Detected modi/{ grabbing = 1; next } \</span><br><span class="s1" style="color:#e6db74">        !grabbing { next } \</span><br><span class="s1" style="color:#e6db74">        grabbing &amp;&amp; !NF { exit } \</span><br><span class="s1" style="color:#e6db74">        grabbing { gsub("+",""); modi = $2","modi } \</span><br><span class="s1" style="color:#e6db74">        END{ print "DISCOVERED_MODI="gensub(",$","","g",modi) }'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> <span class="nb" style="color:#f8f8f2">source</span> /dev/stdin <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">;</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="nv" style="color:#f8f8f2">$DISCOVERED_MODI</span><br><span class="go" style="color:#888">keys,combi,drun,ssh,run,windowcd,window</span><br></pre></div>
</td></tr></table>

## Updating the Config File

To edit the config, we'll have to parse the existing config line-by-line and update the desired values. `sed` is the go-to, but, once again, `awk` offers a couple of features that are useful here:

1. `bash` variable expansion is much easier (i.e. less messy) with `awk`, and
2. manipulating multiple things at the same time is a bit easier.

We'll need to figure out which config option we want to modify:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> cat <span class="nv" style="color:#f8f8f2">$XDG_CONFIG_HOME</span>/rofi/config.rasi <span class="p">|</span> grep modi<br><span class="go" style="color:#888">/*  modi: "window,run,ssh";*/</span><br><span class="go" style="color:#888">/*  combi-modi: "window,run";*/</span><br></pre></div>
</td></tr></table>

### `-show`-able `modi`

The first thing we want to do is limit ourselves to the `-show`-able `modi` config:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> cat <span class="nv" style="color:#f8f8f2">$XDG_CONFIG_HOME</span>/rofi/config.rasi <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'/\smodi/{ print }'</span><br><span class="go" style="color:#888">/*  modi: "window,run,ssh";*/</span><br></pre></div>
</td></tr></table>

Since we've built a desired list of `modi`, `$DISCOVERED_MODI`, we can simply replace the line. We can set variables in `awk` via `-v` By default, the file uses tab characters (`\t`) to align entries, so we'll need to lead with that.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> cat <span class="nv" style="color:#f8f8f2">$XDG_CONFIG_HOME</span>/rofi/config.rasi <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> awk -v <span class="nv" style="color:#f8f8f2">MODI</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DISCOVERED_MODI</span><span class="s2" style="color:#e6db74">"</span> <span class="s1" style="color:#e6db74">'/\smodi/{ print "\tmodi: \""MODI"\";" }'</span><br><span class="go" style="color:#888">    modi: "keys,combi,drun,ssh,run,windowcd,window";</span><br></pre></div>
</td></tr></table>

Provided `awk` is `>=4.1`, we can [edit streams `inplace`](https://www.gnu.org/software/gawk/manual/html_node/Extension-Sample-Inplace.html). We'll need to modify the script to `print` any unmatched lines as well.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> awk <span class="se" style="color:#ae81ff">\</span><br>    -i inplace <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">INPLACE_SUFFIX</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">MODI</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DISCOVERED_MODI</span><span class="s2" style="color:#e6db74">"</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="s1" style="color:#e6db74">'/\smodi/{ print "\tmodi: \""MODI"\";"; next }{ print }'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br><span class="gp" style="color:#66d9ef">$</span> diff <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<span class="o" style="color:#f92672">{</span>.bak,<span class="o" style="color:#f92672">}</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -2 +2 @@</span><br><span class="gd" style="color:#f92672">-/*  modi: "window,run,ssh";*/</span><br><span class="gi" style="color:#a6e22e">+    modi: "keys,combi,drun,ssh,run,windowcd,window";</span><br></pre></div>
</td></tr></table>

### `combi` `modi`

This process is almost identical to [`-show`-able `modi`](#-show-able-modi), so I'll skip the `awk` breakdown. The `combi` `modi` combines multiple `modi` into a single instance. This allows us to group multiple modes together by default.

The simplest solution would be to repeat exactly what we did above.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> awk <span class="se" style="color:#ae81ff">\</span><br>    -i inplace <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">INPLACE_SUFFIX</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">MODI</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DISCOVERED_MODI</span><span class="s2" style="color:#e6db74">"</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="s1" style="color:#e6db74">'/combi-modi/{ print "\tcombi-modi: \""MODI"\";"; next }{ print }'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br><span class="gp" style="color:#66d9ef">$</span> diff <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<span class="o" style="color:#f92672">{</span>.bak,<span class="o" style="color:#f92672">}</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -34 +34 @@</span><br><span class="gd" style="color:#f92672">-/*  combi-modi: "window,run";*/</span><br><span class="gi" style="color:#a6e22e">+    combi-modi: "keys,combi,drun,ssh,run,windowcd,window";</span><br></pre></div>
</td></tr></table>

However, this causes a fairly abrupt segfault.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi -show combi<br><span class="go" style="color:#888">[1]    1269 segmentation fault (core dumped)  rofi -show combi</span><br></pre></div>
</td></tr></table>

The problem is straight-forward to debug. `combi` loads the provided list of `modi`. Since `combi` contains itself, it tries to load itself. Ad infinitum. It's also straight-forward to fix.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> awk <span class="se" style="color:#ae81ff">\</span><br>    -i inplace <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">INPLACE_SUFFIX</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">MODI</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DISCOVERED_MODI</span><span class="s2" style="color:#e6db74">"</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="s1" style="color:#e6db74">'/combi-modi/{ print "\tcombi-modi: \""gensub("combi,?", "", "g", MODI)"\";"; next }{ print }'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<br><span class="gp" style="color:#66d9ef">$</span> diff <span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span>/rofi/config.rasi<span class="o" style="color:#f92672">{</span>.bak,<span class="o" style="color:#f92672">}</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -34 +34 @@</span><br><span class="gd" style="color:#f92672">-/*  combi-modi: "window,run";*/</span><br><span class="gi" style="color:#a6e22e">+    combi-modi: "keys,drun,ssh,run,windowcd,window";</span><br></pre></div>
</td></tr></table>

## All the `modi`

I've combined everything into a script and a `glob`. The first uses a subshell to discover available `modi` whereas the second `pipe`s and `source`s. The result should be the same.

### Shell Script

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">discover-and-set-modi</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-tooling-rofi/blob/master/scripts/discover-and-set-modi" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
52</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><br><span class="nv" style="color:#f8f8f2">CONFIG_FILE</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/config.rasi"</span><br><br><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> ! -f <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$CONFIG_FILE</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    rofi -dump-config &gt; <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$CONFIG_FILE</span><span class="s2" style="color:#e6db74">"</span><br><span class="k" style="color:#66d9ef">fi</span><br><br><span class="nv" style="color:#f8f8f2">DISCOVERED_MODI</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span><br>    rofi --help <span class="se" style="color:#ae81ff">\</span><br>        <span class="p">|</span> awk <span class="s1" style="color:#e6db74">'</span><br><span class="s1" style="color:#e6db74">            BEGIN {</span><br><span class="s1" style="color:#e6db74">                modi = "";</span><br><span class="s1" style="color:#e6db74">                grabbing = 0;</span><br><span class="s1" style="color:#e6db74">            }</span><br><span class="s1" style="color:#e6db74">            /Detected modi/ {</span><br><span class="s1" style="color:#e6db74">                grabbing = 1;</span><br><span class="s1" style="color:#e6db74">                next;</span><br><span class="s1" style="color:#e6db74">            }</span><br><span class="s1" style="color:#e6db74">            !grabbing {</span><br><span class="s1" style="color:#e6db74">                next;</span><br><span class="s1" style="color:#e6db74">            }</span><br><span class="s1" style="color:#e6db74">            grabbing &amp;&amp; !NF {</span><br><span class="s1" style="color:#e6db74">                exit;</span><br><span class="s1" style="color:#e6db74">            }</span><br><span class="s1" style="color:#e6db74">            grabbing {</span><br><span class="s1" style="color:#e6db74">                gsub("+","");</span><br><span class="s1" style="color:#e6db74">                modi = $2","modi;</span><br><span class="s1" style="color:#e6db74">            }</span><br><span class="s1" style="color:#e6db74">            END {</span><br><span class="s1" style="color:#e6db74">                print gensub(",$","","g",modi);</span><br><span class="s1" style="color:#e6db74">            }'</span><br><span class="k" style="color:#66d9ef">)</span><br><br>awk -i inplace <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">INPLACE_SUFFIX</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>    -v <span class="nv" style="color:#f8f8f2">MODI</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DISCOVERED_MODI</span><span class="s2" style="color:#e6db74">"</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="s1" style="color:#e6db74">'</span><br><span class="s1" style="color:#e6db74">    /\smodi:/ {</span><br><span class="s1" style="color:#e6db74">        print "\tmodi: \""MODI"\";";</span><br><span class="s1" style="color:#e6db74">        next;</span><br><span class="s1" style="color:#e6db74">    }</span><br><span class="s1" style="color:#e6db74">    /combi-modi:/ {</span><br><span class="s1" style="color:#e6db74">        print "\tcombi-modi: \""gensub("combi,?", "", "g", MODI)"\";";</span><br><span class="s1" style="color:#e6db74">        next;</span><br><span class="s1" style="color:#e6db74">    }</span><br><span class="s1" style="color:#e6db74">    {</span><br><span class="s1" style="color:#e6db74">        print;</span><br><span class="s1" style="color:#e6db74">    }'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$CONFIG_FILE</span><span class="s2" style="color:#e6db74">"</span><br><br>diff --color --unified<span class="o" style="color:#f92672">=</span><span class="m" style="color:#ae81ff">0</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$CONFIG_FILE</span><span class="s2" style="color:#e6db74">"</span><span class="o" style="color:#f92672">{</span>.bak,<span class="o" style="color:#f92672">}</span><br></pre></div>
</td>
</tr>
</table>

### `glob`

This can be used as copypasta. Probably.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> rofi --help <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> awk <span class="s1" style="color:#e6db74">' \</span><br><span class="s1" style="color:#e6db74">        BEGIN { modi = ""; grabbing = 0 } \</span><br><span class="s1" style="color:#e6db74">        /Detected modi/ { grabbing = 1; next } \</span><br><span class="s1" style="color:#e6db74">        !grabbing { next } \</span><br><span class="s1" style="color:#e6db74">        grabbing &amp;&amp; !NF { exit } \</span><br><span class="s1" style="color:#e6db74">        grabbing { gsub("+",""); modi = $2","modi } \</span><br><span class="s1" style="color:#e6db74">        END { print "DISCOVERED_MODI="gensub(",$","","g",modi) }'</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">|</span> <span class="nb" style="color:#f8f8f2">source</span> /dev/stdin <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">;</span> awk <span class="se" style="color:#ae81ff">\</span><br>        -i inplace <span class="se" style="color:#ae81ff">\</span><br>        -v <span class="nv" style="color:#f8f8f2">INPLACE_SUFFIX</span><span class="o" style="color:#f92672">=</span><span class="s1" style="color:#e6db74">'.bak'</span> <span class="se" style="color:#ae81ff">\</span><br>        -v <span class="nv" style="color:#f8f8f2">MODI</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$DISCOVERED_MODI</span><span class="s2" style="color:#e6db74">"</span> <span class="s1" style="color:#e6db74">' \</span><br><span class="s1" style="color:#e6db74">        /\smodi:/ { print "	modi: \""MODI"\";"; next } \</span><br><span class="s1" style="color:#e6db74">        /combi-modi:/ { print "	combi-modi: \""gensub("combi,?", "", "g", MODI)"\";"; next } \</span><br><span class="s1" style="color:#e6db74">        { print }'</span> <span class="se" style="color:#ae81ff">\</span><br>        <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/config.rasi"</span> <span class="se" style="color:#ae81ff">\</span><br>    <span class="p">;</span> diff <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$XDG_USER_CONFIG_DIR</span><span class="s2" style="color:#e6db74">/rofi/config.rasi"</span><span class="o" style="color:#f92672">{</span>.bak,<span class="o" style="color:#f92672">}</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gd" style="color:#f92672">--- $XDG_USER_CONFIG_DIR/rofi/config.rasi.bak</span><br><span class="gi" style="color:#a6e22e">+++ $XDG_USER_CONFIG_DIR/rofi/config.rasi</span><br><span class="gu" style="color:#75715e">@@ -2 +2 @@</span><br><span class="gd" style="color:#f92672">-/*  modi: "window,run,ssh";*/</span><br><span class="gi" style="color:#a6e22e">+    modi: "keys,combi,drun,ssh,run,windowcd,window";</span><br><span class="gu" style="color:#75715e">@@ -34 +34 @@</span><br><span class="gd" style="color:#f92672">-/*  combi-modi: "window,run";*/</span><br><span class="gi" style="color:#a6e22e">+    combi-modi: "keys,drun,ssh,run,windowcd,window";</span><br></pre></div>
</td></tr></table>
