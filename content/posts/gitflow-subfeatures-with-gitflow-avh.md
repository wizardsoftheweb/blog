---
title: "gitflow Subfeatures with gitflow-avh"
slug: "gitflow-subfeatures-with-gitflow-avh"
date: "2018-02-19T00:00:00.000Z"
feature_image: "/images/2018/02/branch-graph.png"
author: "CJ Harries"
description: "I'm a huge fan of git flow. However, as the codebase grows, features can become disorganized or unwieldy. gitflow-avh solves this problem by allowing features to be based off any branch."
tags:
  - gitflow
  - gitflow-avh
  - git
  - repo
  - CLI
draft: true
---

I'm a huge fan of `gitflow`. It's made my life much easier. However, I've noticed recently that, as the codebase grows, features can become disorganized or unwieldy. `gitflow-avh` solves this problem incredibly well by allowing features to be based off any branch.

<p class="nav-p"><a id="post-nav"></a></p>

- [Note](#note)
- [Code](#code)
- [Problem](#problem)
  - [Feature Per Item](#feature-per-item)
  - [Two Features](#two-features)
  - [One Feature](#one-feature)
- [Solution](#solution)
  - [Installation](#installation)
  - [Using Subfeatures](#using-subfeatures)
  - [Problem Solved with Subfeatures](#problem-solved-with-subfeatures)

## Note

This is not a `gitflow` overview. Check out [the original branching model](http://nvie.com/posts/a-successful-git-branching-model/) and [the `gitflow` repo](https://github.com/nvie/gitflow) for more information on those.

## Code

You can view the code related to this post [in its repo](//github.com/thecjharries/posts-gitflow-subfeatures-with-gitflow-avh). To see how I generated everything, check out [the `scripts` directory](//github.com/thecjharries/posts-gitflow-subfeatures-with-gitflow-avh/tree/master/scripts).

## Problem

After reading the intro, you might be thinking that my features are too large. On the contrary, I'm a pedant with a penchant for pigeonholing things. Let's say you want to add feature `foo`:

- `foo-dependency` must be built for `foo`
- `foo-dependency` must be tested
- `foo` must be built
- `foo` must be tested

Assume `foo-dependency` is only used by `foo`.

### Feature Per Item

Your flow could look like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> git flow feature start add-foo-dependency<br><span class="gp" style="color:#66d9ef">$</span> touch src/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git add src/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Create foo-dependency'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff add-foo-dependency<br><span class="gp" style="color:#66d9ef">$</span> git flow feature start test-foo-dependency<br><span class="gp" style="color:#66d9ef">$</span> touch tests/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git add tests/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Test foo-dependency'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff test-foo-dependency<br><span class="gp" style="color:#66d9ef">$</span> git flow feature start add-foo<br><span class="gp" style="color:#66d9ef">$</span> touch src/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git add src/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Create foo'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff add-foo<br><span class="gp" style="color:#66d9ef">$</span> git flow feature start test-foo<br><span class="gp" style="color:#66d9ef">$</span> touch tests/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git add tests/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Test foo'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff test-foo<br><span class="gp" style="color:#66d9ef">$</span> git log --graph --all --topo-order --decorate --oneline --boundary --color<span class="o" style="color:#f92672">=</span>always<br></pre></div>
</td></tr></table>

<!-- markdownlint-disable MD037-->
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0">*   <span style="color: #aa5500">03d94f9</span><span style="color: #aa5500"> (</span><span style="font-weight: bold; color: #00aaaa">HEAD -&gt; </span><span style="font-weight: bold; color: #00aa00">dev</span><span style="color: #aa5500">)</span> Merge branch 'feature/test-foo' into dev
<span style="color: #aa0000">|</span><span style="color: #00aa00">\</span>
<span style="color: #aa0000">|</span> * <span style="color: #aa5500">842ac3a</span> Test foo
<span style="color: #aa0000">|</span><span style="color: #aa0000">/</span>
*   <span style="color: #aa5500">2a84d06</span> Merge branch 'feature/add-foo' into dev
<span style="color: #aa5500">|</span><span style="color: #0000aa">\</span>
<span style="color: #aa5500">|</span> * <span style="color: #aa5500">052adc7</span> Create foo
<span style="color: #aa5500">|</span><span style="color: #aa5500">/</span>
*   <span style="color: #aa5500">a9b2d78</span> Merge branch 'feature/test-foo-dependency' into dev
<span style="color: #E850A8">|</span><span style="color: #00aaaa">\</span>
<span style="color: #E850A8">|</span> * <span style="color: #aa5500">7cdf67e</span> Test foo-dependency
<span style="color: #E850A8">|</span><span style="color: #E850A8">/</span>
*   <span style="color: #aa5500">14cb44b</span> Merge branch 'feature/add-foo-dependency' into dev
<span style="font-weight: bold; color: #aa0000">|</span><span style="font-weight: bold; color: #00aa00">\</span>
<span style="font-weight: bold; color: #aa0000">|</span> * <span style="color: #aa5500">ba5c2c8</span> Create foo-dependency
<span style="font-weight: bold; color: #aa0000">|</span><span style="font-weight: bold; color: #aa0000">/</span>
* <span style="color: #aa5500">a2a682a</span><span style="color: #aa5500"> (</span><span style="font-weight: bold; color: #00aa00">master</span><span style="color: #aa5500">)</span> Initial commit
</pre></div>
</td></tr></table>
<!-- markdownlint-enable MD037 -->

I'm not a huge fan of this approach, because `add-foo-dependency` and `add-foo` both merge untested code directly into the `dev` branch. While each feature does exactly one thing, the one thing sorta causes organizational problems. I don't like untested code floating around in a main branch when I can avoid it.

### Two Features

It could also look like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> git flow feature start add-foo-dependency<br><span class="gp" style="color:#66d9ef">$</span> touch src/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git add src/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Create foo-dependency'</span><br><span class="gp" style="color:#66d9ef">$</span> touch tests/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git add tests/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Test foo-dependency'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff add-foo-dependency<br><span class="gp" style="color:#66d9ef">$</span> git flow feature start add-foo<br><span class="gp" style="color:#66d9ef">$</span> touch src/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git add src/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Create foo'</span><br><span class="gp" style="color:#66d9ef">$</span> touch tests/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git add tests/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Test foo'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff add-foo<br><span class="gp" style="color:#66d9ef">$</span> git log --graph --all --topo-order --decorate --oneline --boundary --color<span class="o" style="color:#f92672">=</span>always<br></pre></div>
</td></tr></table>

<!-- markdownlint-disable MD037-->
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0">*   <span style="color: #aa5500">76dada7</span><span style="color: #aa5500"> (</span><span style="font-weight: bold; color: #00aaaa">HEAD -&gt; </span><span style="font-weight: bold; color: #00aa00">dev</span><span style="color: #aa5500">)</span> Merge branch 'feature/add-foo' into dev
<span style="color: #aa0000">|</span><span style="color: #00aa00">\</span>
<span style="color: #aa0000">|</span> * <span style="color: #aa5500">54d82ae</span> Test foo
<span style="color: #aa0000">|</span> * <span style="color: #aa5500">152b98c</span> Create foo
<span style="color: #aa0000">|</span><span style="color: #aa0000">/</span>
*   <span style="color: #aa5500">1d841a7</span> Merge branch 'feature/add-foo-dependency' into dev
<span style="color: #aa5500">|</span><span style="color: #0000aa">\</span>
<span style="color: #aa5500">|</span> * <span style="color: #aa5500">0e062b5</span> Test foo-dependency
<span style="color: #aa5500">|</span> * <span style="color: #aa5500">d730279</span> Create foo-dependency
<span style="color: #aa5500">|</span><span style="color: #aa5500">/</span>
* <span style="color: #aa5500">ac908e3</span><span style="color: #aa5500"> (</span><span style="font-weight: bold; color: #00aa00">master</span><span style="color: #aa5500">)</span> Initial commit
</pre></div>
</td></tr></table>
<!-- markdownlint-enable MD037-->

While this avoids merging untested code, it merges totally useless code with `foo-dependency`. If there's any appreciable time between `add-foo-dependency` and `add-foo`, someone else might create a feature that removes `foo-dependency` by merit of its unnecessary inclusion.

### One Feature

Or it could look like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> git flow feature start add-foo<br><span class="gp" style="color:#66d9ef">$</span> touch src/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git add src/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Create foo-dependency'</span><br><span class="gp" style="color:#66d9ef">$</span> touch tests/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git add tests/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Test foo-dependency'</span><br><span class="gp" style="color:#66d9ef">$</span> touch src/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git add src/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Create foo'</span><br><span class="gp" style="color:#66d9ef">$</span> touch tests/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git add tests/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Test foo'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff add-foo<br><span class="gp" style="color:#66d9ef">$</span> git log --graph --all --topo-order --decorate --oneline --boundary --color<span class="o" style="color:#f92672">=</span>always<br></pre></div>
</td></tr></table>

<!-- markdownlint-disable MD037-->
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0">*   <span style="color: #aa5500">5f83929</span><span style="color: #aa5500"> (</span><span style="font-weight: bold; color: #00aaaa">HEAD -&gt; </span><span style="font-weight: bold; color: #00aa00">dev</span><span style="color: #aa5500">)</span> Merge branch 'feature/add-foo' into dev
<span style="color: #aa0000">|</span><span style="color: #00aa00">\</span>
<span style="color: #aa0000">|</span> * <span style="color: #aa5500">dc4edaa</span> Test foo
<span style="color: #aa0000">|</span> * <span style="color: #aa5500">20e3801</span> Create foo
<span style="color: #aa0000">|</span> * <span style="color: #aa5500">aea02da</span> Test foo-dependency
<span style="color: #aa0000">|</span> * <span style="color: #aa5500">113e27f</span> Create foo-dependency
<span style="color: #aa0000">|</span><span style="color: #aa0000">/</span>
* <span style="color: #aa5500">8bff3c8</span><span style="color: #aa5500"> (</span><span style="font-weight: bold; color: #00aa00">master</span><span style="color: #aa5500">)</span> Initial commit
</pre></div>
</td></tr></table>
<!-- markdownlint-enable MD037-->

If `foo` is a bit more complicated than `touch`ing a few files, this gets messy fast. `foo-dependency` and `foo` (as well as their associated tests) will probably have a ton of commits, which defeats the purpose of splitting out the branches.

## Solution

[The `gitflow-avh` project](https://github.com/petervanderdoes/gitflow-avh) attempts to update and extend `gitflow` with some useful features. As far as I know, it's a drop-in replacement for `gitflow`, so you won't notice a difference.

### Installation

See [the official docs](https://github.com/petervanderdoes/gitflow-avh/wiki/Installation) for detailed instructions. Depending on your OS, you might be able to find it via a package manager as `gitflow-avh`. If not, you can [install manually](https://github.com/petervanderdoes/gitflow-avh/wiki/Installing-on-Linux,-Unix,-etc.#manual) without much trouble:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">install-gitflow-avh</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/petervanderdoes/gitflow-avh/wiki/Installing-on-Linux,-Unix,-etc.#manual" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
13</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><span class="c1" style="color:#75715e"># This is basically the wiki's installation script except more complicated</span><br><br><span class="k" style="color:#66d9ef">if</span> which wget &gt;/dev/null<span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    wget --no-check-certificate -q  https://raw.githubusercontent.com/petervanderdoes/gitflow-avh/develop/contrib/gitflow-installer.sh<br><span class="k" style="color:#66d9ef">elif</span> which curl &gt;/dev/null<span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    curl -fLO https://raw.githubusercontent.com/petervanderdoes/gitflow-avh/develop/contrib/gitflow-installer.sh<br><span class="k" style="color:#66d9ef">else</span><br>    <span class="nb" style="color:#f8f8f2">echo</span> <span class="s1" style="color:#e6db74">'Unable to download installer'</span><br>    <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">1</span><br><span class="k" style="color:#66d9ef">fi</span><br>sudo bash gitflow-installer.sh<br>rm -f gitflow-installer.sh<br></pre></div>
</td>
</tr>
</table>

### Using Subfeatures

Vanilla `gitflow` bases all features off the `dev` branch.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> git flow feature start <span class="k" style="color:#66d9ef">do</span>-something<br><span class="go" style="color:#888">Switched to a new branch 'feature/do-something'</span><br><br><span class="go" style="color:#888">Summary of actions:</span><br><span class="go" style="color:#888">- A new branch 'feature/do-something' was created, based on 'dev'</span><br><span class="go" style="color:#888">- You are now on branch 'feature/do-something'</span><br><br><span class="go" style="color:#888">Now, start committing on your feature. When done, use:</span><br><br><span class="go" style="color:#888">     git flow feature finish do-something</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish <span class="k" style="color:#66d9ef">do</span>-something<br><span class="go" style="color:#888">Switched to branch 'dev'</span><br><span class="go" style="color:#888">Already up to date.</span><br><span class="go" style="color:#888">Deleted branch feature/do-something (was 6c3fe58).</span><br><br><span class="go" style="color:#888">Summary of actions:</span><br><span class="go" style="color:#888">- The feature branch 'feature/do-something' was merged into 'dev'</span><br><span class="go" style="color:#888">- Feature branch 'feature/do-something' has been locally deleted</span><br><span class="go" style="color:#888">- You are now on branch 'dev'</span><br></pre></div>
</td></tr></table>

With `gitflow-avh`, you can base features off any branch, which means when you finish it, it's merged back into the source branch.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> git flow feature start <span class="k" style="color:#66d9ef">do</span>-something<br><span class="go" style="color:#888">Switched to a new branch 'feature/do-something'</span><br><br><span class="go" style="color:#888">Summary of actions:</span><br><span class="go" style="color:#888">- A new branch 'feature/do-something' was created, based on 'dev'</span><br><span class="go" style="color:#888">- You are now on branch 'feature/do-something'</span><br><br><span class="go" style="color:#888">Now, start committing on your feature. When done, use:</span><br><br><span class="go" style="color:#888">     git flow feature finish do-something</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature start subtask feature/do-something<br><span class="go" style="color:#888">Switched to a new branch 'feature/subtask'</span><br><br><span class="go" style="color:#888">Summary of actions:</span><br><span class="go" style="color:#888">- A new branch 'feature/subtask' was created, based on 'feature/do-something'</span><br><span class="go" style="color:#888">- You are now on branch 'feature/subtask'</span><br><br><span class="go" style="color:#888">Now, start committing on your feature. When done, use:</span><br><br><span class="go" style="color:#888">     git flow feature finish subtask</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish subtask<br><span class="go" style="color:#888">Switched to branch 'feature/do-something'</span><br><span class="go" style="color:#888">Already up to date.</span><br><span class="go" style="color:#888">Deleted branch feature/subtask (was 6c3fe58).</span><br><br><span class="go" style="color:#888">Summary of actions:</span><br><span class="go" style="color:#888">- The feature branch 'feature/subtask' was merged into 'feature/do-something'</span><br><span class="go" style="color:#888">- Feature branch 'feature/subtask' has been locally deleted</span><br><span class="go" style="color:#888">- You are now on branch 'feature/do-something'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish <span class="k" style="color:#66d9ef">do</span>-something<br><span class="go" style="color:#888">Switched to branch 'dev'</span><br><span class="go" style="color:#888">Already up to date.</span><br><span class="go" style="color:#888">Deleted branch feature/do-something (was 6c3fe58).</span><br><br><span class="go" style="color:#888">Summary of actions:</span><br><span class="go" style="color:#888">- The feature branch 'feature/do-something' was merged into 'dev'</span><br><span class="go" style="color:#888">- Feature branch 'feature/do-something' has been locally deleted</span><br><span class="go" style="color:#888">- You are now on branch 'dev'</span><br></pre></div>
</td></tr></table>

### Problem Solved with Subfeatures

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> git flow feature start add-foo<br><span class="gp" style="color:#66d9ef">$</span> git flow feature start add-foo-dependency feature/add-foo<br><span class="gp" style="color:#66d9ef">$</span> git flow feature start create-foo-dependency feature/add-foo-dependency<br><span class="gp" style="color:#66d9ef">$</span> touch src/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git add src/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Create foo-dependency'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff create-foo-dependency<br><span class="gp" style="color:#66d9ef">$</span> git flow feature start test-foo-dependency feature/add-foo-dependency<br><span class="gp" style="color:#66d9ef">$</span> touch test/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git add tests/foo-dependency.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Test foo-dependency'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff test-foo-dependency<br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff add-foo-dependency<br><span class="gp" style="color:#66d9ef">$</span> git flow feature start create-foo feature/add-foo<br><span class="gp" style="color:#66d9ef">$</span> touch src/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git add src/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Create foo'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff create-foo<br><span class="gp" style="color:#66d9ef">$</span> git flow feature start test-foo feature/add-foo<br><span class="gp" style="color:#66d9ef">$</span> touch tests/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git add tests/foo.ext<br><span class="gp" style="color:#66d9ef">$</span> git commit -m <span class="s1" style="color:#e6db74">'Test foo'</span><br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff test-foo<br><span class="gp" style="color:#66d9ef">$</span> git flow feature finish --no-ff add-foo<br><span class="gp" style="color:#66d9ef">$</span> git log --graph --all --topo-order --decorate --oneline --boundary --color<span class="o" style="color:#f92672">=</span>always<br></pre></div>
</td></tr></table>

<!-- markdownlint-disable MD037-->
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0">*   <span style="color: #aa5500">bd73c92</span><span style="color: #aa5500"> (</span><span style="font-weight: bold; color: #00aaaa">HEAD -&gt; </span><span style="font-weight: bold; color: #00aa00">dev</span><span style="color: #aa5500">)</span> Merge branch 'feature/add-foo' into dev
<span style="color: #aa0000">|</span><span style="color: #00aa00">\</span>
<span style="color: #aa0000">|</span> *   <span style="color: #aa5500">4ee685f</span> Merge branch 'feature/test-foo' into feature/add-foo
<span style="color: #aa0000">|</span> <span style="color: #aa5500">|</span><span style="color: #0000aa">\</span>
<span style="color: #aa0000">|</span> <span style="color: #aa5500">|</span> * <span style="color: #aa5500">6ca71ec</span> Test foo
<span style="color: #aa0000">|</span> <span style="color: #aa5500">|</span><span style="color: #aa5500">/</span>
<span style="color: #aa0000">|</span> *   <span style="color: #aa5500">2472346</span> Merge branch 'feature/create-foo' into feature/add-foo
<span style="color: #aa0000">|</span> <span style="color: #E850A8">|</span><span style="color: #00aaaa">\</span>
<span style="color: #aa0000">|</span> <span style="color: #E850A8">|</span> * <span style="color: #aa5500">c4f870a</span> Create foo
<span style="color: #aa0000">|</span> <span style="color: #E850A8">|</span><span style="color: #E850A8">/</span>
<span style="color: #aa0000">|</span> *   <span style="color: #aa5500">e081189</span> Merge branch 'feature/add-foo-dependency' into feature/add-foo
<span style="color: #aa0000">|</span> <span style="color: #aa0000">|</span><span style="font-weight: bold; color: #00aa00">\</span>
<span style="color: #aa0000">|</span><span style="color: #aa0000">/</span> <span style="font-weight: bold; color: #00aa00">/</span>
<span style="color: #aa0000">|</span> *   <span style="color: #aa5500">7334e3e</span> Merge branch 'feature/create-foo-dependency' into feature/add-foo-dependency
<span style="color: #aa0000">|</span> <span style="color: #aa0000">|</span><span style="font-weight: bold; color: #0000aa">\</span>
<span style="color: #aa0000">|</span><span style="color: #aa0000">/</span> <span style="font-weight: bold; color: #0000aa">/</span>
<span style="color: #aa0000">|</span> * <span style="color: #aa5500">bb4c45e</span> Create foo-dependency
<span style="color: #aa0000">|</span><span style="color: #aa0000">/</span>
* <span style="color: #aa5500">26ddd97</span><span style="color: #aa5500"> (</span><span style="font-weight: bold; color: #00aa00">master</span><span style="color: #aa5500">)</span> Initial commit
</pre></div>
</td></tr></table>
<!-- markdownlint-enable MD037-->
