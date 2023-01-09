---
title: "Remove Consecutive Duplicate Lines With awk"
slug: "remove-consecutive-duplicate-lines-with-awk"
date: "2018-01-09T00:00:00.000Z"
author: "CJ Harries"
description: "I needed a way remove consecutive duplicate lines while ignoring whitespace and nonconsecutive duplicates. The top awk search results don't work for this use case, so I built my own."
tags: 
  - CLI
  - awk
  - terminal
  - scripting
draft: true
---

I ran into an interesting problem yesterday. At some point, while scripting updates to a collection of repos, I managed to duplicate a few lines in several files. I ended up with something like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">README.md</div></td>
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
26</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gh" style="font-weight:bold; color:#66d9ef">#</span> `dotfiles-role-javascript`<br><span class="gh" style="font-weight:bold; color:#66d9ef">#</span> `dotfiles-role-javascript`<br><br>[<span class="nt" style="color:#f92672">![Build Status</span>](<span class="na" style="color:#a6e22e">https://travis-ci.org/thecjharries/dotfiles-role-javascript.svg?branch=master</span>)](https://travis-ci.org/thecjharries/dotfiles-role-javascript)<br>[<span class="nt" style="color:#f92672">![GitHub tag</span>](<span class="na" style="color:#a6e22e">https://img.shields.io/github/tag/thecjharries/dotfiles-role-javascript.svg</span>)](https://github.com/thecjharries/dotfiles-role-javascript)<br>[<span class="nt" style="color:#f92672">![GitHub tag</span>](<span class="na" style="color:#a6e22e">https://img.shields.io/github/tag/thecjharries/dotfiles-role-javascript.svg</span>)](https://github.com/thecjharries/dotfiles-role-javascript)<br><br>...<br><br>Finally, these variables must be set:<br><br><span class="s" style="color:#e6db74">```yml</span><br><span class="s" style="color:#e6db74">author_name</span><br><span class="s" style="color:#e6db74">author_email</span><br><span class="s" style="color:#e6db74">author_url</span><br><span class="s" style="color:#e6db74">```</span><br><br><span class="gu" style="color:#75715e">##</span> Dependencies<br><br><span class="s" style="color:#e6db74">```yml</span><br><span class="s" style="color:#e6db74">---</span><br><span class="s" style="color:#e6db74">- src: git+https://github.com/thecjharries/dotfiles-role-common-software.git</span><br><span class="s" style="color:#e6db74">- src: git+https://github.com/thecjharries/dotfiles-role-common-software.git</span><br><span class="s" style="color:#e6db74">- src: git+https://github.com/thecjharries/dotfiles-role-package-installer.git</span><br><span class="s" style="color:#e6db74">- src: git+https://github.com/thecjharries/dotfiles-role-package-installer.git</span><br><span class="s" style="color:#e6db74">```</span><br></pre></div>
</td>
</tr>
</table>

I figured there had to be an easy solution using `awk`, so I grabbed the first SO thread I saw and ran with it.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> awk <span class="s1" style="color:#e6db74">'!seen[$0]++'</span> README.md<br></pre></div>
</td></tr></table>

This one's particularly opaque. Before using it, lets see how it works.

- `seen[$0]` creates an entry in [the `seen` associative array](http://kirste.userpage.fu-berlin.de/chemnet/use/info/gawk/gawk_12.html) whose key is the current line, `$0`. `seen` isn't a magic array; it's just easy convention. `qqq[$0]` achieves the same results.
- `x++` [post-increments the value](http://www.delorie.com/gnu/docs/gawk/gawk_87.html#IDX621). That means the value will stay the same for this operation, but increases immediately afterward.
- `!x` negates the following statement, which, in this case, will stop `awk` from doing anything.

Normally `awk` prints every line. In this script, the first time `awk` sees a line, `seen[$0]` will be empty, so the post-increment will coerce it to a number after the operation completes. However, at the moment, it's empty, and the post-increment waits for any preceding operations, so the empty value is negated and then coerced to a number.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>(!(seen[$0]))++<br>(!( ))++<br>(1)++<br>2<br></pre></div>
</td>
</tr></table>

As clever as it is, it's got some major flaws, especially for my use case:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> awk <span class="s1" style="color:#e6db74">'!seen[$0]++'</span> README.md &gt; tmp.md<br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">tmp.md</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gh" style="font-weight:bold; color:#66d9ef">#</span> `dotfiles-role-javascript`<br><br>[<span class="nt" style="color:#f92672">![Build Status</span>](<span class="na" style="color:#a6e22e">https://travis-ci.org/thecjharries/dotfiles-role-javascript.svg?branch=master</span>)](https://travis-ci.org/thecjharries/dotfiles-role-javascript)<br>[<span class="nt" style="color:#f92672">![GitHub tag</span>](<span class="na" style="color:#a6e22e">https://img.shields.io/github/tag/thecjharries/dotfiles-role-javascript.svg</span>)](https://github.com/thecjharries/dotfiles-role-javascript)<br>...<br>Finally, these variables must be set:<br><span class="s" style="color:#e6db74">```yml</span><br><span class="s" style="color:#e6db74">author_name</span><br><span class="s" style="color:#e6db74">author_email</span><br><span class="s" style="color:#e6db74">author_url</span><br><span class="s" style="color:#e6db74">```</span><br><span class="gu" style="color:#75715e">##</span> Dependencies<br>---<br><span class="k" style="color:#66d9ef">-</span> src: git+https://github.com/thecjharries/dotfiles-role-common-software.git<br><span class="k" style="color:#66d9ef">-</span> src: git+https://github.com/thecjharries/dotfiles-role-package-installer.git<br></pre></div>
</td>
</tr>
</table>

It's removed the duplicate lines, empty lines, and necessary repeated elements (see how the second fenced block lost its fence). The whitespace is pretty easy to get back; empty lines won't have any fields, so <strong>`N`</strong>umber of <strong>`F`</strong>ields will be empty. We can run `awk`, that is print a line, when `NF` is empty or the line hasn't been seen. In other words,

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> awk <span class="s1" style="color:#e6db74">'!NF || !seen[$0]++'</span> README.md &gt; tmp2.md<br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">tmp2.md</div></td>
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
20</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gh" style="font-weight:bold; color:#66d9ef">#</span> `dotfiles-role-javascript`<br><br>[<span class="nt" style="color:#f92672">![Build Status</span>](<span class="na" style="color:#a6e22e">https://travis-ci.org/thecjharries/dotfiles-role-javascript.svg?branch=master</span>)](https://travis-ci.org/thecjharries/dotfiles-role-javascript)<br>[<span class="nt" style="color:#f92672">![GitHub tag</span>](<span class="na" style="color:#a6e22e">https://img.shields.io/github/tag/thecjharries/dotfiles-role-javascript.svg</span>)](https://github.com/thecjharries/dotfiles-role-javascript)<br><br>...<br><br>Finally, these variables must be set:<br><br><span class="s" style="color:#e6db74">```yml</span><br><span class="s" style="color:#e6db74">author_name</span><br><span class="s" style="color:#e6db74">author_email</span><br><span class="s" style="color:#e6db74">author_url</span><br><span class="s" style="color:#e6db74">```</span><br><br><span class="gu" style="color:#75715e">##</span> Dependencies<br><br>---<br><span class="k" style="color:#66d9ef">-</span> src: git+https://github.com/thecjharries/dotfiles-role-common-software.git<br><span class="k" style="color:#66d9ef">-</span> src: git+https://github.com/thecjharries/dotfiles-role-package-installer.git<br></pre></div>
</td>
</tr>
</table>

As it turns out, I need a few lines to appear more than once, so common `awk` solutions don't work very well. My problem is really centered around evaluating each line against its immediate neighbors.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> awk <span class="s1" style="color:#e6db74">'BEGIN{ old = "" } { new = $0 } old == new &amp;&amp; old != "" { next } { old = $0; print }'</span> README.md &gt; tmp3.md<br></pre></div>
</td></tr></table>

- `BEGIN{ old = "" }` seeds `old` at file load, rather than at each line
- `{ new = $0 }` is run each line, updating the value of `new`
- `old == new && old != ""` will be true only if the lines are equal and nonempty
- `{ next }` is fired if the conditional is true, skipping immediately to the next record (i.e. not printing the second, duplicated line)
- `{ old = $0; print }` will update the value of `old` and pass the line on to `stdout`

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">tmp3.md</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gh" style="font-weight:bold; color:#66d9ef">#</span> `dotfiles-role-javascript`<br><br>[<span class="nt" style="color:#f92672">![Build Status</span>](<span class="na" style="color:#a6e22e">https://travis-ci.org/thecjharries/dotfiles-role-javascript.svg?branch=master</span>)](https://travis-ci.org/thecjharries/dotfiles-role-javascript)<br>[<span class="nt" style="color:#f92672">![GitHub tag</span>](<span class="na" style="color:#a6e22e">https://img.shields.io/github/tag/thecjharries/dotfiles-role-javascript.svg</span>)](https://github.com/thecjharries/dotfiles-role-javascript)<br><br>...<br><br>Finally, these variables must be set:<br><br><span class="s" style="color:#e6db74">```yml</span><br><span class="s" style="color:#e6db74">author_name</span><br><span class="s" style="color:#e6db74">author_email</span><br><span class="s" style="color:#e6db74">author_url</span><br><span class="s" style="color:#e6db74">```</span><br><br><span class="gu" style="color:#75715e">##</span> Dependencies<br><br><span class="s" style="color:#e6db74">```yml</span><br><span class="s" style="color:#e6db74">---</span><br><span class="s" style="color:#e6db74">- src: git+https://github.com/thecjharries/dotfiles-role-common-software.git</span><br><span class="s" style="color:#e6db74">- src: git+https://github.com/thecjharries/dotfiles-role-package-installer.git</span><br><span class="s" style="color:#e6db74">```</span><br></pre></div>
</td>
</tr>
</table>

I'm still pretty new to `awk` scripting, so there might be a better way to do this. If there is, I'd love to know about it!
