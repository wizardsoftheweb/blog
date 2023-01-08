---
title: "Syntax Highlighting in LaTeX with minted"
slug: "syntax-highlighting-in-latex-with-minted"
date: "2018-03-26T12:00:00.000Z"
feature_image: "/images/2018/03/style-1.png"
author: "CJ Harries"
description: "This post serves as an introduction to minted, a pygments-based syntax highlighter for LaTeX. The post covers a few examples, the installation process, and  some basic security."
tags: 
  - minted
  - LaTeX
  - pygments
  - TeX
  - CLI
  - markup
  - syntax highlighting
draft: true
---

This post serves as an introduction to `minted`, a `pygments`-based syntax highlighter for LaTeX. Adding `pygments` to LaTeX streamlines so many things. The post provides a few examples of things you can do with `minted`, details the installation process, and covers some basic security.

<p class="nav-p"><a id="post-nav"></a></p>

- [Code](#code)
- [Overview](#overview)
- [Installing](#installing)
  - [Python](#python)
  - [`pip`](#pip)
  - [`pygments`](#pygments)
  - [TeX Dependencies](#texdependencies)
  - [`minted`](#minted)
- [`-shell-escape`](#shellescape)
- [Useful features](#usefulfeatures)
- [What's Next](#whatsnext)

## Code

You can view the code related to this post [under the `post-01-overview` tag](//github.com/thecjharries/posts-latex-minted/tree/post-01-overview).

## Overview

The easiest way to present code in LaTeX is to [use the `verbatim` environment](https://en.wikibooks.org/wiki/LaTeX/Paragraph_Formatting#Verbatim_text). It's quick, it preserves formatting, and it requires no set up. It's also very bland. Its ease of use comes at the cost of basically all the context clues well-formatted and styled code can provide.

The next step up (or rather many steps up) is [the `listings` package](https://en.wikibooks.org/wiki/LaTeX/Source_Code_Listings). Out the box, it supports a broad range of languages. It's eminently configurable. You can define new languages yourself, add different keywords, and style to your heart's content. It's very good at being straightforward. Moving beyond its predefined scopes (or [easily discoverable internet styles](https://www.google.com/search?q=listings+styles+latex)) is a challenge, though, because parsing and tokenizing code in LaTeX is just about as hard and ridiculous as it sounds.

`minted` has become [a solid competitor](https://github.com/gpoore/minted). It uses [the `pygments` project](http://pygments.org/) to parse and highlight. You've probably seen `pygments` in action [already](http://pygments.org/faq/#who-uses-pygments). It's a beast of an application that can do just about anything you want re: syntax highlighting. `minted` isn't quite as flexible, but it does have access to most of the `pygments` features. Recognizable styles, a massive library of lexers, and simple customization through Python make `minted`, by way of `pygments`, a veritable utility knife.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">sample.tex</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-latex-minted/blob/master/latex/overview/sample.tex" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
46</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">\documentclass</span><span class="nb" style="color:#f8f8f2">{</span>article<span class="nb" style="color:#f8f8f2">}</span><br><span class="c" style="color:#75715e">% chktex-file 18</span><br><span class="k" style="color:#66d9ef">\usepackage</span>[<br>    paperwidth=2.5in,<br>    paperheight=3in,<br>    total=<span class="nb" style="color:#f8f8f2">{</span>2in,2.8in<span class="nb" style="color:#f8f8f2">}</span><br>]<span class="nb" style="color:#f8f8f2">{</span>geometry<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\usepackage</span><span class="nb" style="color:#f8f8f2">{</span>listings<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\usepackage</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\setlength</span><span class="nb" style="color:#f8f8f2">{</span><span class="k" style="color:#66d9ef">\parindent</span><span class="nb" style="color:#f8f8f2">}{</span>0pt<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>document<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>center<span class="nb" style="color:#f8f8f2">}</span><br><br>This is verbatim:<br><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>verbatim<span class="nb" style="color:#f8f8f2">}</span><br>#!/bin/bash<br><br>echo "Hello, world!"<br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>verbatim<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\hrule</span><br><span class="k" style="color:#66d9ef">\vspace</span><span class="nb" style="color:#f8f8f2">{</span>6pt<span class="nb" style="color:#f8f8f2">}</span><br><br>This is vanilla <span class="nb" style="color:#f8f8f2">{</span><span class="k" style="color:#66d9ef">\ttfamily</span> listings<span class="nb" style="color:#f8f8f2">}</span>:<br><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>lstlisting<span class="nb" style="color:#f8f8f2">}</span>[language=Bash]<br>#!/bin/bash<br><br>echo "Hello, world!"<br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>lstlisting<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\hrule</span><br><span class="k" style="color:#66d9ef">\vspace</span><span class="nb" style="color:#f8f8f2">{</span>6pt<span class="nb" style="color:#f8f8f2">}</span><br><br>This is vanilla <span class="nb" style="color:#f8f8f2">{</span><span class="k" style="color:#66d9ef">\ttfamily</span> minted<span class="nb" style="color:#f8f8f2">}</span>:<br><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}{</span>bash<span class="nb" style="color:#f8f8f2">}</span><br>#!/bin/bash<br><br>echo "Hello, world!"<br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>center<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>document<span class="nb" style="color:#f8f8f2">}</span><br></pre></div>
</td>
</tr>
</table>

![sample-3](/images/2018/03/sample-3.png)

There's [a bit more to the `listings` vs. `minted` debate](https://tex.stackexchange.com/questions/389191/minted-vs-listings-pros-and-cons). Essentially it boils down to where you want to customize. Personally, I feel like a general-purpose scripting language used in all areas of tech is a stronger contender than a typesetting system many of my peers have struggled to learn. I don't know, though (and if I'm wrong, I'd love to hear about it). At its core, TeX tokenizes everything. I'm just not sure that it can achieve the same level of regex wizardry that goes into some of the `pygments` code.

## Installing

`minted` requires a few things to get up and running.

### Python

You'll need Python to get started. Pygments [needs `>=2.6` or `>=3.3`](http://pygments.org/faq/#what-are-the-system-requirements), depending on your version of Python. You can lazily install both with any trouble. For example, via `dnf`,

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install python<span class="o" style="color:#f92672">{</span><span class="m" style="color:#ae81ff">2</span>,3<span class="o" style="color:#f92672">}</span><br></pre></div>
</td></tr></table>

### `pip`

Next you'll need `pip`, a wonderful package manager for Python. It's [ridiculously easy to install](https://github.com/pypa/get-pip#usage). Rather than install it globally (i.e. to `/usr/bin`), we're going to install it locally via the `--user` flag.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> wget https://bootstrap.pypa.io/get-pip.py<span class="p">;</span> python get-pip.py --user<span class="p">;</span> rm get-pip.py<br><span class="go" style="color:#888">This should be sufficient</span><br><span class="gp" style="color:#66d9ef">$</span> wget https://bootstrap.pypa.io/get-pip.py<span class="p">;</span> python2 get-pip.py --user<span class="p">;</span> rm get-pip.py<br><span class="go" style="color:#888">This will install for Python 2 explicitly</span><br><span class="gp" style="color:#66d9ef">$</span> wget https://bootstrap.pypa.io/get-pip.py<span class="p">;</span> python3 get-pip.py --user<span class="p">;</span> rm get-pip.py<br><span class="go" style="color:#888">This will install for Python 3 explicitly</span><br></pre></div>
</td></tr></table>

However, this doesn't put `pip` on our path.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> which pip<br><span class="go" style="color:#888">/usr/bin/which: no pip in (&lt;path directories&gt;)</span><br></pre></div>
</td></tr></table>

The `--user` flag installed `pip` to our [user site packages](https://docs.python.org/2.7/library/site.html#cmdoption-site-user-site). We can check the base directory, which should have the desired `bin`, via

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> python -m site --user-base<br><span class="go" style="color:#888">~/.local</span><br></pre></div>
</td></tr></table>

Since we have an easy way to discover the directory, we have an easy way to add it to our `.whateverrc`:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="s1" style="color:#e6db74">'export PATH="$(python -m site --user-base)/bin:$PATH"'</span> &gt;&gt; .whateverrc<br></pre></div>
</td></tr></table>

You can also manually add it, which might be a good idea if you're doing other `PATH` manipulations.

### `pygments`

With `pip` installed, we can quickly install `pygments`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> pip install --user pygments<br><span class="go" style="color:#888">This should be sufficient</span><br><span class="gp" style="color:#66d9ef">$</span> pip2 install --user pygments<br><span class="go" style="color:#888">This will install for Python 2 explicitly</span><br><span class="gp" style="color:#66d9ef">$</span> pip3 install --user pygments<br><span class="go" style="color:#888">This will install for Python 3 explicitly</span><br><br><span class="go" style="color:#888">Installing both isn't necessary. As of writing, Pygments is compatible with</span><br><span class="go" style="color:#888">both major versions of Python.</span><br></pre></div>
</td></tr></table>

### TeX Dependencies

`minted` provides a [list of its dependencies](https://github.com/gpoore/minted/blob/master/source/minted.pdf). If you've got access to [something like `tlmgr`](http://tug.org/texlive/tlmgr.html), it should be pretty easy to update them.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>keyval kvoptions fancyvrb fvextra upquote float ifthen calc ifplatform pdftexcmds etoolbox xstring xcolor lineno framed shellesc<br></pre></div>
</td></tr></table>

If you don't (e.g. modern RHEL derivatives, I think), you'll have to get creative. This is the easiest route:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install <span class="s1" style="color:#e6db74">'texlive-*'</span><br><span class="go" style="color:#888">...</span><br><span class="go" style="color:#888">Install  &gt;5779 Packages</span><br><br><span class="go" style="color:#888">Total download size: &gt;2.4 G</span><br><span class="go" style="color:#888">Installed size: &gt;3.8 G</span><br><span class="go" style="color:#888">Is this ok [y/N]:</span><br></pre></div>
</td></tr></table>

If, like me, you're running an SSD on a budget, the easiest isn't very convenient. Maybe you just don't feel like warehousing all of TeX Live to snag 16 dependencies. If you're not going to install everything, you need to figure out what you have to install. `dnf`/`yum` makes this somewhat trivial. If you're stuck with `dpkg`/`dpkg-query`, the discovery will be [much more involved](https://tex.stackexchange.com/a/39776) (but also I think you can run `tlmgr` so there's that).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">install-texlive-dependencies</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-latex-minted/blob/master/scripts/install-texlive-dependencies" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
34</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><br><span class="c1" style="color:#75715e"># Pulled from https://github.com/gpoore/minted/blob/master/source/minted.pdf</span><br><span class="nv" style="color:#f8f8f2">DEPENDENCIES</span><span class="o" style="color:#f92672">=(</span><br>    keyval<br>    kvoptions<br>    fancyvrb<br>    fvextra<br>    upquote<br>    float<br>    ifthen<br>    calc<br>    ifplatform<br>    pdftexcmds<br>    etoolbox<br>    xstring<br>    xcolor<br>    lineno<br>    framed<br>    shellesc<br><span class="o" style="color:#f92672">)</span><br><span class="nv" style="color:#f8f8f2">PACKAGES</span><span class="o" style="color:#f92672">=()</span><br><span class="c1" style="color:#75715e"># Loop over all the dependencies</span><br><span class="k" style="color:#66d9ef">for</span> dependency in <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">DEPENDENCIES</span><span class="p">[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><span class="p">;</span> <span class="k" style="color:#66d9ef">do</span><br>    <span class="c1" style="color:#75715e"># Check dnf for the parent package and trim its output</span><br>    <span class="nv" style="color:#f8f8f2">PACKAGES</span><span class="o" style="color:#f92672">+=(</span><span class="k" style="color:#66d9ef">$(</span><br>        dnf provides <span class="s2" style="color:#e6db74">"tex(</span><span class="nv" style="color:#f8f8f2">$dependency</span><span class="s2" style="color:#e6db74">.sty)"</span> <span class="se" style="color:#ae81ff">\</span><br>            <span class="p">|</span> awk -F<span class="s1" style="color:#e6db74">':'</span> <span class="s1" style="color:#e6db74">'/^texlive/{ gsub("-[0-9]+$", "", $1); print $1 }'</span><br>    <span class="k" style="color:#66d9ef">)</span><span class="o" style="color:#f92672">)</span><br><span class="k" style="color:#66d9ef">done</span><br><span class="c1" style="color:#75715e"># Remove duplicates</span><br><span class="nv" style="color:#f8f8f2">PACKAGES</span><span class="o" style="color:#f92672">=(</span><span class="k" style="color:#66d9ef">$(</span><span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">PACKAGES</span><span class="p">[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span> <span class="p">|</span> tr <span class="s1" style="color:#e6db74">' '</span> <span class="s1" style="color:#e6db74">'\n'</span> <span class="p">|</span> sort -u<span class="k" style="color:#66d9ef">)</span><span class="o" style="color:#f92672">)</span><br><span class="c1" style="color:#75715e"># Install dependencies</span><br>sudo dnf install <span class="s2" style="color:#e6db74">"</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">PACKAGES</span><span class="p">[@]</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74">"</span><br></pre></div>
</td>
</tr>
</table>

### `minted`

Convoluted dependency resolution aside, `minted` itself is a breeze to install (like `pygments`; we've already done all the hard work).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo dnf install texlive-minted<br></pre></div>
</td></tr></table>

## `-shell-escape`

Because `minted` relies on an external application (`pygments`) to highlight, it can't just run in a tiny, neatly contained environment. TeX [essentially exposes streams](http://www.tex.ac.uk/FAQ-spawnprog.html) but, by default, access to the operating system is locked down. `-shell-escape` neatly sidesteps those restrictions, but it doesn't come without risk. Just like anything else, it's probably not a great idea to provide shell access until you understand what's going on. Don't download random things off the internet and execute them blindly. Don't run in superuser mode all the time. You know, basic stuff.

This is what happens when you try to run `minted` without `-shell-escape`. Notice at the beginning that external actions are limited (`restricted \write18 enabled`). The document will not compile (even without `-halt-on-error`).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> pdflatex -interaction<span class="o" style="color:#f92672">=</span>nonstopmode -halt-on-error sample.tex<br><span class="go" style="color:#888">This is pdfTeX, Version 3.14159265-2.6-1.40.17 (TeX Live 2016) (preloaded format=pdflatex)</span><br><span class="go" style="color:#888"> restricted \write18 enabled.</span><br><span class="go" style="color:#888">entering extended mode</span><br><span class="go" style="color:#888">(./sample.tex</span><br><span class="go" style="color:#888">LaTeX2e &lt;2016/03/31&gt;</span><br><span class="go" style="color:#888">...</span><br><br><span class="go" style="color:#888">Package ifplatform Warning:</span><br><span class="go" style="color:#888">    shell escape is disabled, so I can only detect \ifwindows.</span><br><br><span class="go" style="color:#888">...</span><br><br><span class="go" style="color:#888">! Package minted Error: You must invoke LaTeX with the -shell-escape flag.</span><br><br><span class="go" style="color:#888">See the minted package documentation for explanation.</span><br><span class="go" style="color:#888">Type  H &lt;return&gt;  for immediate help.</span><br><span class="go" style="color:#888"> ...</span><br><br><span class="go" style="color:#888">l.9</span><br><br><span class="go" style="color:#888">!  ==&gt; Fatal error occurred, no output PDF file produced!</span><br><span class="go" style="color:#888">Transcript written on sample.log.</span><br></pre></div>
</td></tr></table>

With `-shell-escape`, any external action is available (`\write18 enabled`) and the document compiles.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> pdflatex -interaction<span class="o" style="color:#f92672">=</span>nonstopmode -halt-on-error -shell-escape sample.tex<br><span class="go" style="color:#888">This is pdfTeX, Version 3.14159265-2.6-1.40.17 (TeX Live 2016) (preloaded format=pdflatex)</span><br><span class="go" style="color:#888"> \write18 enabled.</span><br><span class="go" style="color:#888">entering extended mode</span><br><span class="go" style="color:#888">(./sample.tex</span><br><span class="go" style="color:#888">LaTeX2e &lt;2016/03/31&gt;</span><br><span class="go" style="color:#888">...</span><br><span class="go" style="color:#888">Output written on sample.pdf (1 page, 48380 bytes).</span><br><span class="go" style="color:#888">Transcript written on sample.log.</span><br></pre></div>
</td></tr></table>

Chances are you're not actually building from the CLI every time. You've probably got an editor with some build commands stored. Don't add `-shell-escape` to all of your build profiles. It's a pain to toggle custom builds off and on, but having to rebuild your system after an attack is worse. Look for something like User Builds, Custom Commands, or the like.

For example, [in TeXstudio](https://www.texstudio.org/), you can add custom builds via Configure TeXstudio > Builds > User Commands. [In Texmaker](http://www.xm1math.net/texmaker/), the same menu is available via User > User Commands > Edit User Commands.

Similarly, [in Sublime](https://www.sublimetext.com/) via [the LaTeXTools package](https://github.com/SublimeText/LaTeXTools), you can add custom builds to your project file (or anywhere else, for that matter).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">posts-latex-minted.sublime-project</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-latex-minted/blob/master/posts-latex-minted.sublime-project" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
26</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="p">{</span><br>  <span class="nt" style="color:#f92672">"folders"</span><span class="p">:</span><br>  <span class="p">[</span><br>    <span class="p">{</span><br>      <span class="nt" style="color:#f92672">"path"</span><span class="p">:</span> <span class="s2" style="color:#e6db74">"."</span><br>    <span class="p">}</span><br>  <span class="p">],</span><br>  <span class="nt" style="color:#f92672">"build_systems"</span><span class="p">:</span><br>  <span class="p">[</span><br>    <span class="p">{</span><br>      <span class="nt" style="color:#f92672">"name"</span><span class="p">:</span> <span class="s2" style="color:#e6db74">"Escalated pdflatex"</span><span class="p">,</span><br>      <span class="nt" style="color:#f92672">"target"</span><span class="p">:</span> <span class="s2" style="color:#e6db74">"make_pdf"</span><span class="p">,</span><br>      <span class="nt" style="color:#f92672">"selector"</span><span class="p">:</span> <span class="s2" style="color:#e6db74">"text.tex.latex"</span><span class="p">,</span><br>      <span class="nt" style="color:#f92672">"builder"</span><span class="p">:</span> <span class="s2" style="color:#e6db74">"script"</span><span class="p">,</span><br>      <span class="nt" style="color:#f92672">"script_commands"</span><span class="p">:</span> <span class="p">[</span><br>        <span class="p">[</span><br>          <span class="s2" style="color:#e6db74">"pdflatex"</span><span class="p">,</span><br>          <span class="s2" style="color:#e6db74">"-synctex=1"</span><span class="p">,</span><br>          <span class="s2" style="color:#e6db74">"-interaction=nonstopmode"</span><span class="p">,</span><br>          <span class="s2" style="color:#e6db74">"-shell-escape"</span><span class="p">,</span><br>          <span class="s2" style="color:#e6db74">"$file_base_name"</span><br>        <span class="p">]</span><br>      <span class="p">]</span><br>    <span class="p">}</span><br>  <span class="p">]</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

## Useful features

You've already seen how simple it is to add code to a `tex` file. `minted` also makes it easy to include external source code without worrying about getting it to play well with your editor. The `\inputminted` macro lets you load any file while specifying the lexer.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">input.tex</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-latex-minted/blob/master/latex/overview/input.tex" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
15</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">\documentclass</span><span class="nb" style="color:#f8f8f2">{</span>article<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\usepackage</span>[<br>    paperwidth=6in,<br>    paperheight=4in,<br>    total=<span class="nb" style="color:#f8f8f2">{</span>5.5in,3.9in<span class="nb" style="color:#f8f8f2">}</span><br>]<span class="nb" style="color:#f8f8f2">{</span>geometry<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\usepackage</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\setlength</span><span class="nb" style="color:#f8f8f2">{</span><span class="k" style="color:#66d9ef">\parindent</span><span class="nb" style="color:#f8f8f2">}{</span>0pt<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>document<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>center<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\inputminted</span><span class="nb" style="color:#f8f8f2">{</span>bash<span class="nb" style="color:#f8f8f2">}{</span>../convert-pdf-to-png<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>center<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>document<span class="nb" style="color:#f8f8f2">}</span><br></pre></div>
</td>
</tr>
</table>

![input](/images/2018/03/input.png)

The default style is one of many available to `minted`. You can check the styles available on your system via

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> pygmentize -L styles<br><span class="go" style="color:#888">Pygments version 2.2.0, (c) 2006-2017 by Georg Brandl.</span><br><br><span class="go" style="color:#888">Styles:</span><br><span class="go" style="color:#888">~~~~~~~</span><br><span class="go" style="color:#888">* default:</span><br><span class="go" style="color:#888">    The default style (inspired by Emacs 22).</span><br><span class="go" style="color:#888">* emacs:</span><br><span class="go" style="color:#888">    The default style (inspired by Emacs 22).</span><br><span class="go" style="color:#888">* friendly:</span><br><span class="go" style="color:#888">    A modern style based on the VIM pyte theme.</span><br><span class="go" style="color:#888">* colorful:</span><br><span class="go" style="color:#888">    A colorful style, inspired by CodeRay.</span><br><span class="go" style="color:#888">* autumn:</span><br><span class="go" style="color:#888">    A colorful style, inspired by the terminal highlighting style.</span><br><span class="go" style="color:#888">* murphy:</span><br><span class="go" style="color:#888">    Murphy's style from CodeRay.</span><br><span class="go" style="color:#888">* manni:</span><br><span class="go" style="color:#888">    A colorful style, inspired by the terminal highlighting style.</span><br><span class="go" style="color:#888">* monokai:</span><br><span class="go" style="color:#888">    This style mimics the Monokai color scheme.</span><br><span class="go" style="color:#888">* perldoc:</span><br><span class="go" style="color:#888">    Style similar to the style used in the perldoc code blocks.</span><br><span class="go" style="color:#888">* pastie:</span><br><span class="go" style="color:#888">    Style similar to the pastie default style.</span><br><span class="go" style="color:#888">* borland:</span><br><span class="go" style="color:#888">    Style similar to the style used in the borland IDEs.</span><br><span class="go" style="color:#888">* trac:</span><br><span class="go" style="color:#888">    Port of the default trac highlighter design.</span><br><span class="go" style="color:#888">* native:</span><br><span class="go" style="color:#888">    Pygments version of the "native" vim theme.</span><br><span class="go" style="color:#888">* fruity:</span><br><span class="go" style="color:#888">    Pygments version of the "native" vim theme.</span><br><span class="go" style="color:#888">* bw:</span><br><br><span class="go" style="color:#888">* vim:</span><br><span class="go" style="color:#888">    Styles somewhat like vim 7.0</span><br><span class="go" style="color:#888">* vs:</span><br><br><span class="go" style="color:#888">* tango:</span><br><span class="go" style="color:#888">    The Crunchy default Style inspired from the color palette from the Tango Icon Theme Guidelines.</span><br><span class="go" style="color:#888">* rrt:</span><br><span class="go" style="color:#888">    Minimalistic "rrt" theme, based on Zap and Emacs defaults.</span><br><span class="go" style="color:#888">* xcode:</span><br><span class="go" style="color:#888">    Style similar to the Xcode default colouring theme.</span><br><span class="go" style="color:#888">* igor:</span><br><span class="go" style="color:#888">    Pygments version of the official colors for Igor Pro procedures.</span><br><span class="go" style="color:#888">* paraiso-light:</span><br><br><span class="go" style="color:#888">* paraiso-dark:</span><br><br><span class="go" style="color:#888">* lovelace:</span><br><span class="go" style="color:#888">    The style used in Lovelace interactive learning environment. Tries to avoid the "angry fruit salad" effect with desaturated and dim colours.</span><br><span class="go" style="color:#888">* algol:</span><br><br><span class="go" style="color:#888">* algol_nu:</span><br><br><span class="go" style="color:#888">* arduino:</span><br><span class="go" style="color:#888">    The Arduino® language style. This style is designed to highlight the Arduino source code, so exepect the best results with it.</span><br><span class="go" style="color:#888">* rainbow_dash:</span><br><span class="go" style="color:#888">    A bright and colorful syntax highlighting theme.</span><br><span class="go" style="color:#888">* abap:</span><br></pre></div>
</td></tr></table>

You can preview any of the styles by [visiting the `pygments` demo](http://pygments.org/demo/) and trying out a highlighter. Once `pygments` has parsed the code, you'll be able to change the style at whim.

The default styles alone add a tremendous amount of utility to `minted`. There are [many other settings that may be tweaked](https://github.com/gpoore/minted/blob/master/source/minted.pdf). Sharing style changes is an easy way to underscore `minted`'s versatility.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">style.tex</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-latex-minted/blob/master/latex/overview/style.tex" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
57</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">\documentclass</span><span class="nb" style="color:#f8f8f2">{</span>article<span class="nb" style="color:#f8f8f2">}</span><br><span class="c" style="color:#75715e">% chktex-file 18</span><br><span class="k" style="color:#66d9ef">\usepackage</span>[<br>    paperwidth=2.5in,<br>    paperheight=3in,<br>    total=<span class="nb" style="color:#f8f8f2">{</span>2in,2.8in<span class="nb" style="color:#f8f8f2">}</span><br>]<span class="nb" style="color:#f8f8f2">{</span>geometry<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\usepackage</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\usepackage</span><span class="nb" style="color:#f8f8f2">{</span>xcolor<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\setlength</span><span class="nb" style="color:#f8f8f2">{</span><span class="k" style="color:#66d9ef">\parindent</span><span class="nb" style="color:#f8f8f2">}{</span>0pt<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\definecolor</span><span class="nb" style="color:#f8f8f2">{</span>monokaibg<span class="nb" style="color:#f8f8f2">}{</span>HTML<span class="nb" style="color:#f8f8f2">}{</span>272822<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\definecolor</span><span class="nb" style="color:#f8f8f2">{</span>friendlybg<span class="nb" style="color:#f8f8f2">}{</span>HTML<span class="nb" style="color:#f8f8f2">}{</span>f0f0f0<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>document<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>center<span class="nb" style="color:#f8f8f2">}</span><br><br>This is the <span class="nb" style="color:#f8f8f2">{</span><span class="k" style="color:#66d9ef">\ttfamily</span> monokai<span class="nb" style="color:#f8f8f2">}</span> style.<br><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span>[<br>    style=monokai,<br>    bgcolor=monokaibg<br>]<span class="nb" style="color:#f8f8f2">{</span>bash<span class="nb" style="color:#f8f8f2">}</span><br>#!/bin/bash<br><br>echo "Hello, world!"<br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\hrule</span><br><span class="k" style="color:#66d9ef">\vspace</span><span class="nb" style="color:#f8f8f2">{</span>6pt<span class="nb" style="color:#f8f8f2">}</span><br><br>This is the <span class="nb" style="color:#f8f8f2">{</span><span class="k" style="color:#66d9ef">\ttfamily</span> colorful<span class="nb" style="color:#f8f8f2">}</span> style.<br><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span>[<br>    style=colorful,<br>]<span class="nb" style="color:#f8f8f2">{</span>bash<span class="nb" style="color:#f8f8f2">}</span><br>#!/bin/bash<br><br>echo "Hello, world!"<br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\hrule</span><br><span class="k" style="color:#66d9ef">\vspace</span><span class="nb" style="color:#f8f8f2">{</span>6pt<span class="nb" style="color:#f8f8f2">}</span><br><br>This is the <span class="nb" style="color:#f8f8f2">{</span><span class="k" style="color:#66d9ef">\ttfamily</span> friendly<span class="nb" style="color:#f8f8f2">}</span> style.<br><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span>[<br>    style=friendly,<br>    bgcolor=friendlybg<br>]<span class="nb" style="color:#f8f8f2">{</span>bash<span class="nb" style="color:#f8f8f2">}</span><br>#!/bin/bash<br><br>echo "Hello, world!"<br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>center<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>document<span class="nb" style="color:#f8f8f2">}</span><br></pre></div>
</td>
</tr>
</table>

![style](/images/2018/03/style.png)

If you want to use the same style throughout your document, `minted` makes that simple too. The `\newminted` macro defines a configuration for a specific language, e.g. `python`. It can then be used as an environment in place of `minted` by appending `code` to the end, e.g. `pythoncode`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">newminted.tex</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-latex-minted/blob/master/latex/overview/newminted.tex" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
49</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">\documentclass</span><span class="nb" style="color:#f8f8f2">{</span>article<span class="nb" style="color:#f8f8f2">}</span><br><span class="c" style="color:#75715e">% chktex-file 16</span><br><span class="c" style="color:#75715e">% chktex-file 18</span><br><span class="c" style="color:#75715e">% chktex-file 36</span><br><span class="k" style="color:#66d9ef">\usepackage</span>[<br>    paperwidth=2.5in,<br>    paperheight=3in,<br>    total=<span class="nb" style="color:#f8f8f2">{</span>2in,2.8in<span class="nb" style="color:#f8f8f2">}</span><br>]<span class="nb" style="color:#f8f8f2">{</span>geometry<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\usepackage</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\usepackage</span><span class="nb" style="color:#f8f8f2">{</span>xcolor<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\setlength</span><span class="nb" style="color:#f8f8f2">{</span><span class="k" style="color:#66d9ef">\parindent</span><span class="nb" style="color:#f8f8f2">}{</span>0pt<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\setlength</span><span class="nb" style="color:#f8f8f2">{</span><span class="k" style="color:#66d9ef">\parskip</span><span class="nb" style="color:#f8f8f2">}{</span>0pt<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\definecolor</span><span class="nb" style="color:#f8f8f2">{</span>monokaibg<span class="nb" style="color:#f8f8f2">}{</span>HTML<span class="nb" style="color:#f8f8f2">}{</span>272822<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\definecolor</span><span class="nb" style="color:#f8f8f2">{</span>monokaifg<span class="nb" style="color:#f8f8f2">}{</span>rgb<span class="nb" style="color:#f8f8f2">}{</span>0.97,0.97,0.95<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\newminted</span><span class="nb" style="color:#f8f8f2">{</span>bash<span class="nb" style="color:#f8f8f2">}{</span><br>    style=monokai,<br>    bgcolor=monokaibg<br><span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\BeforeBeginEnvironment</span><span class="nb" style="color:#f8f8f2">{</span>bashcode<span class="nb" style="color:#f8f8f2">}{</span><span class="k" style="color:#66d9ef">\color</span><span class="nb" style="color:#f8f8f2">{</span>monokaifg<span class="nb" style="color:#f8f8f2">}}</span><br><span class="k" style="color:#66d9ef">\AfterEndEnvironment</span><span class="nb" style="color:#f8f8f2">{</span>bashcode<span class="nb" style="color:#f8f8f2">}{</span><span class="k" style="color:#66d9ef">\color</span><span class="nb" style="color:#f8f8f2">{</span>black<span class="nb" style="color:#f8f8f2">}}</span><br><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>document<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>center<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>bashcode<span class="nb" style="color:#f8f8f2">}</span><br>#!/bin/bash<br><br>echo "Hello, world!"<br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>bashcode<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\hrule</span><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}{</span>bash<span class="nb" style="color:#f8f8f2">}</span><br>#!/bin/bash<br><br>echo "Hello, world!"<br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\hrule</span><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>bashcode<span class="nb" style="color:#f8f8f2">}</span><br>#!/bin/bash<br><br>FOO=(<span class="s" style="color:#e6db74">$</span><span class="o" style="color:#f92672">(</span><span class="nb" style="color:#f8f8f2">find . </span><span class="o" style="color:#f92672">-</span><span class="nb" style="color:#f8f8f2">type f</span><span class="o" style="color:#f92672">))</span><span class="nb" style="color:#f8f8f2"></span><br><span class="nb" style="color:#f8f8f2"># Nothing's perfect</span><br><span class="nb" style="color:#f8f8f2">echo "</span><span class="s" style="color:#e6db74">$</span><span class="nb" style="color:#f8f8f2">{</span>FOO[@]<span class="nb" style="color:#f8f8f2">}</span>"<br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>bashcode<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>center<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>document<span class="nb" style="color:#f8f8f2">}</span><br></pre></div>
</td>
</tr>
</table>

![newminted](/images/2018/03/newminted.png)

You can use the same logic with `\inputminted` via `\newmintedfile`. Rather than defining a new environment, `\newmintedfile` creates a new macro. It has an optional name parameter to make things easier (otherwise the macro is called `\<language>file`).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">newmintedfile.tex</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-latex-minted/blob/master/latex/overview/newmintedfile.tex" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
23</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">\documentclass</span><span class="nb" style="color:#f8f8f2">{</span>article<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\usepackage</span>[<br>    paperwidth=6in,<br>    paperheight=4in,<br>    total=<span class="nb" style="color:#f8f8f2">{</span>5.5in,3.9in<span class="nb" style="color:#f8f8f2">}</span><br>]<span class="nb" style="color:#f8f8f2">{</span>geometry<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\usepackage</span><span class="nb" style="color:#f8f8f2">{</span>minted<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\usepackage</span><span class="nb" style="color:#f8f8f2">{</span>xcolor<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\setlength</span><span class="nb" style="color:#f8f8f2">{</span><span class="k" style="color:#66d9ef">\parindent</span><span class="nb" style="color:#f8f8f2">}{</span>0pt<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\definecolor</span><span class="nb" style="color:#f8f8f2">{</span>mannibg<span class="nb" style="color:#f8f8f2">}{</span>HTML<span class="nb" style="color:#f8f8f2">}{</span>f0f3f3<span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\newmintedfile</span><span class="na" style="color:#a6e22e">[bashcode]</span><span class="nb" style="color:#f8f8f2">{</span>bash<span class="nb" style="color:#f8f8f2">}{</span><br>    style=manni,<br>    bgcolor=mannibg<br><span class="nb" style="color:#f8f8f2">}</span><br><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>document<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\begin</span><span class="nb" style="color:#f8f8f2">{</span>center<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\bashcode</span><span class="nb" style="color:#f8f8f2">{</span>../convert-pdf-to-png<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>center<span class="nb" style="color:#f8f8f2">}</span><br><span class="k" style="color:#66d9ef">\end</span><span class="nb" style="color:#f8f8f2">{</span>document<span class="nb" style="color:#f8f8f2">}</span><br></pre></div>
</td>
</tr>
</table>

![newmintedfile](/images/2018/03/newmintedfile.png)

## What's Next

Sometime very soon I hope to look explore `minted` in combination with some other tools to build on its features. I've got some examples in use right now but I need to break them out and annotate them.