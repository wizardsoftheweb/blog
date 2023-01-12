---
title: "Manage Many Keys with SSH Config and KeePass"
slug: "ssh-config-with-keeagent"
date: "2018-02-25T18:30:00.000Z"
feature_image: "/images/2018/02/all-in-keeagent.png"
author: "CJ Harries"
description: "Simply put, managing a ton of keys is a serious pain. If you've never really delved into the myriad ways to beef up your settings, this is a good place to start."
tags:
  - KeePass
  - ssh
  - ssh_config
  - KeeAgent
  - tooling
  - ssh-agent
  - security
---

I'll be the first to admit my security has room for improvement. Until last year, I was reusing passwords intermixed with a terribly simple mnemonic. Until a few months ago, my phone and computer were totally unencrypted. I've been fighting the change because it's scary. I'm also very lazy and have been dreading the extra work involved with good security. I've put off updating SSH credentials for about two years now for that exact reason.

I decided to at least pretend like I was doing something about that this morning. It's a gargantuan task: managing many keys with many passphrases on many machines with so much typing involved. Rather than actually sitting down to update things, I poked around man pages and Stack Overflow for a bit, avoiding more than anything else. Somehow I managed to put together a halfway decent solution that, so far, seems to remove almost all the heavy lifting.

<p class="nav-p"><a id="post-nav"></a></p>

- [Requirements](#requirements)
- [Note](#note)
- [Problem](#problem)
- [Solution](#solution)
- [Example](#example)
  - [Generate Keys](#generate-keys)
  - [Populate KeePass](#populate-keepass)
  - [Create Environment](#create-environment)
  - [Easy Failure](#easy-failure)
  - [Easier Success](#easier-success)
- [Recap](#recap)
- [Full Scripts](#full-scripts)
  - [`keygen`](#keygen)
  - [`Vagrantfile`](#vagrantfile)

## Requirements

- [KeePass 2.X](https://keepass.info/download.html)
- [KeeAgent](https://keepass.info/plugins.html#keeagent)
- [`ssh_config`](https://linux.die.net/man/5/ssh_config)

If you've never used KeePass or KeeAgent, [start here](https://blog.wizardsoftheweb.pro/keepass-ssh/). I've written about the two together before.

On the other hand, it should be possible to set up most of this with the vanilla `ssh-agent` or something more opinionated like `gnome-keyring-daemon` or `kdewallet5`. Taking KeePass and KeeAgent out of the equation, in my opinion, generates way more work, but YMMV.

## Note

KeePass hasn't been thrilled with `i3` and my theme choices. I apologize for the strange layouts. Unless you decide to go and change everything it doesn't normally look this bad. I was too excited about the solution to go and undo all my tweaks.

## Problem

Simply put, managing a ton of keys is a serious pain. If, like me, you've never really delved into the myriad ways to beef up your settings, you'll hit a few snags:

- You have to manually add a ton of keys to `ssh-agent`, which means typing passphrases for days when your power goes out, killing the longest continuous uptime you've had in months
- You have to juggle keys in the agent, as most servers have a fairly low retry count (default is, I believe, six)
- You have to manually enter the passphrases for anything specified in your config that's not active in your agent, which seems like a waste of time if you're just going to have to juggle anyway

## Solution

Those statements, built on experience and [prevailing wisdom](https://serverfault.com/a/820048/446829), touch on some pretty major annoyances. However, they all suffer from a perspective problem. They begin with the assumption that a user has many keys and connects to many machines. That's very true. But it ignores a very important detail: while there are many possible permutations of key and machine, the number of successful permutations is much smaller and (in theory) proper matchings are already known.

`ssh_config` defines a vehicle to specify proper matchings. Providing an `IdentityFile` (or several) per host establishes a match. `IdentitiesOnly` prevents `ssh` from trying anything not specified in the config or CLI, effectively sidestepping the retry issue. `IdentityAgent` provides an agent failsafe (or multiple agents in tandem). KeePass and KeeAgent glue everything together with remembered credentials, making the config much more powerful.

Assuming `~/.ssh/some_key` is in KeePass and available to KeeAgent, this simple config is enough to get you started:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">~/.ssh/config</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>Host simple_name<br>    HostName fqdn<br>    User remote_user<br>    IdentitiesOnly yes<br>    IdentityFile ~/.ssh/some_key<br>    IdentityAgent SSH_AUTH_SOCK<br></pre></div>
</td>
</tr>
</table>

## Example

All of this will make much more sense after a good example. I'm going to build everything from scratch and try to illustrate the pain points I believe I've mitigated.

### Generate Keys

To demonstrate something closer to an ideal environment, I've generated ten keys. They're all ridiculously weak and shouldn't be used in production (passphrase was passed via the CLI, which should be enough warning).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ssh-keygen <span class="se" style="color:#ae81ff">\</span><br>    -t rsa <span class="se" style="color:#ae81ff">\</span><br>    -P password03 <span class="se" style="color:#ae81ff">\</span><br>    -C user03@host <span class="se" style="color:#ae81ff">\</span><br>    -f dummy_key_03<br><span class="go" style="color:#888">Generating public/private rsa key pair.</span><br><span class="go" style="color:#888">Your identification has been saved in dummy_key_03.</span><br><span class="go" style="color:#888">Your public key has been saved in dummy_key_03.pub.</span><br><span class="go" style="color:#888">The key fingerprint is:</span><br><span class="go" style="color:#888">SHA256:SxGPZn/19LYMIEA05z+4sezZ9ruBG1cQdaaBf0sr5Tc user03@host</span><br><span class="go" style="color:#888">The key's randomart image is:</span><br><span class="go" style="color:#888">+---[RSA 2048]----+</span><br><span class="go" style="color:#888">|      o=..   oo.o|</span><br><span class="go" style="color:#888">|        =+  . .+.|</span><br><span class="go" style="color:#888">|        =o.. oo .|</span><br><span class="go" style="color:#888">|       o o+ ..o=o|</span><br><span class="go" style="color:#888">|        So.o..+o*|</span><br><span class="go" style="color:#888">|       ...+.o.+Eo|</span><br><span class="go" style="color:#888">|        .+ o o.oo|</span><br><span class="go" style="color:#888">|        . o.+ .  |</span><br><span class="go" style="color:#888">|         o.o.+o  |</span><br><span class="go" style="color:#888">+----[SHA256]-----+</span><br></pre></div>
</td></tr></table>

### Populate KeePass

With the keys in hand, I populated the KeePass database next. Each entry's password is the passphrase to the key, and the keys themselves are attached to the entries.

![loaded-db](/images/2018/02/loaded-db.png)

The easiest way to make things work is to allow KeeAgent to use each entry. If you don't, you'll have to manually add the key later (which has its uses).

![keeagent-enabled](/images/2018/02/keeagent-enabled.png)

All told, this is about seven more active keys than I'm used to having around. It's a strange feeling, to say the least.

![all-in-keeagent](/images/2018/02/all-in-keeagent.png)

### Create Environment

To make things as simple as possible, I created a `vagrant` box that will act as the remote. I did a few things:

- Created `dummy_user`
- Assigned `dummy_key_10` (the last in the list) as `dummy_user`'s primary key (also `authorized_key`)
- Removed password access (forcing a key exchange)
- Lowered the number of attempts to three

`vagrant` exposes its own `ssh_config` via `ssh-config`, which we'll use to to access the box and later as a template for our own.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> vagrant ssh-config<br><span class="go" style="color:#888">Host default</span><br><span class="go" style="color:#888">  HostName 192.168.121.150</span><br><span class="go" style="color:#888">  User vagrant</span><br><span class="go" style="color:#888">  Port 22</span><br><span class="go" style="color:#888">  UserKnownHostsFile /dev/null</span><br><span class="go" style="color:#888">  StrictHostKeyChecking no</span><br><span class="go" style="color:#888">  PasswordAuthentication no</span><br><span class="go" style="color:#888">  IdentityFile ...</span><br><span class="go" style="color:#888">  IdentitiesOnly yes</span><br><span class="go" style="color:#888">  LogLevel FATAL</span><br></pre></div>
</td></tr></table>

### Easy Failure

We're going to try to connect with all the keys active.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ssh-add -l<br><span class="go" style="color:#888">2048 SHA256:7Fd0YO1OENizISLV+rzBHc+KHpsDKnfkZoPEOKNoGt4 user01@host (RSA)</span><br><span class="go" style="color:#888">2048 SHA256:/alv7iswhB0YMgYtUYbVu4UTHCLpqa7M/o7PXBf5NJk user02@host (RSA)</span><br><span class="go" style="color:#888">2048 SHA256:7FBCSXS7hWUWV7PxRvw65PytkoF65gh/b4vJU49jBNU user03@host (RSA)</span><br><span class="go" style="color:#888">2048 SHA256:CL4UsKgCscVv3WyFY0RgiZfRrfOPI+etatN779C7fX0 user04@host (RSA)</span><br><span class="go" style="color:#888">2048 SHA256:IWSIHh8A3ApK0s0SaxIxeyRpSTmoMjMFW827iPvc3OE user05@host (RSA)</span><br><span class="go" style="color:#888">2048 SHA256:E3ovjpFD524ZoYmzUO/ucBDAfGAyeP7jzwlaLqi0Mi0 user06@host (RSA)</span><br><span class="go" style="color:#888">2048 SHA256:Qh/Nss0znxMwpTGlOqpxacsrj8in3xYv4A8bcRhH/Ik user07@host (RSA)</span><br><span class="go" style="color:#888">2048 SHA256:md1KsOzJ/BsYtZBgFA5PxhR4eyEfUwFPdoTurhHDEao user08@host (RSA)</span><br><span class="go" style="color:#888">2048 SHA256:SEu3eaPbHPRgyp/7lpkbT1Wpcv2oZ45vOWshTgXiZp0 user09@host (RSA)</span><br><span class="go" style="color:#888">2048 SHA256:3nzgRuofhgfPHgfQQERk0b1TmRLufV0ppWwixojFjlk user10@host (RSA)</span><br><span class="gp" style="color:#66d9ef">$</span> ssh dummy_user@192.168.121.150<br><span class="go" style="color:#888">Received disconnect from 192.168.121.150 port 22:2: Too many authentication failures</span><br><span class="go" style="color:#888">Disconnected from 192.168.121.150 port 22</span><br></pre></div>
</td></tr></table>

Quick and unsurprising.

### Easier Success

We can just as quickly get in with a simple config file.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">~/.ssh/config</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>Host vagrant-box<br>    HostName 192.168.121.150<br>    User dummy_user<br>    IdentitiesOnly yes<br>    IdentityFile /path/to/dummy_key_10<br>    IdentityAgent SSH_AUTH_SOCK<br></pre></div>
</td>
</tr>
</table>

The key path is fairly important. `ssh` attempts to load the key, sees KeeAgent already has it available, and moves on. Without a local copy of the key, there's nothing for `ssh` to go off of. (I think; this is an educated guess using the debug logs. Might not be 100% accurate.)

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ssh vagrant-box<br><span class="go" style="color:#888">Last login: Sun Feb 25 17:09:45 2018</span><br><span class="gp" style="color:#66d9ef">[dummy_user@localhost ~]$</span> <span class="nb" style="color:#f8f8f2">exit</span><br><span class="go" style="color:#888">logout</span><br><span class="go" style="color:#888">Connection to 192.168.121.150 closed.</span><br></pre></div>
</td></tr></table>

## Recap

By themselves, `ssh_config` and KeePass/KeeAgent are very powerful tools. Together they mitigate the need to juggle keys and constantly enter passphrases. `IdentityFile`, `IdentitiesOnly`, and a little bit of setup will make using more than one key a painless endeavor. Until you have to update them all...

## Full Scripts

These are in [the repo](https://github.com/thecjharries/posts-ssh-config-with-keeagent) but I also wanted to lay out everything here.

### `keygen`

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">keygen</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-ssh-config-with-keeagent/tree/master/scripts/keygen" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
79</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/usr/bin/env python</span><br><span class="c1" style="color:#75715e"># coding: utf8</span><br><br><span class="sd" style="color:#e6db74">"""This file provides a script to generate dummy ssh keys"""</span><br><br><span class="c1" style="color:#75715e"># pylint: disable=misplaced-comparison-constant</span><br><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">os</span> <span class="kn" style="color:#f92672">import</span> <span class="n">makedirs</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">os.path</span> <span class="kn" style="color:#f92672">import</span> <span class="n">abspath</span><span class="p">,</span> <span class="n">dirname</span><span class="p">,</span> <span class="n">join</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">shutil</span> <span class="kn" style="color:#f92672">import</span> <span class="n">rmtree</span><br><span class="kn" style="color:#f92672">from</span> <span class="nn" style="color:#f8f8f2">subprocess</span> <span class="kn" style="color:#f92672">import</span> <span class="n">check_call</span><br><br><span class="n">KEY_COUNT</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">10</span><br><span class="n">SCRIPTS_DIR</span> <span class="o" style="color:#f92672">=</span> <span class="n">abspath</span><span class="p">(</span><span class="n">dirname</span><span class="p">(</span><span class="vm" style="color:#f8f8f2">__file__</span><span class="p">))</span><br><span class="n">KEY_DIR</span> <span class="o" style="color:#f92672">=</span> <span class="n">abspath</span><span class="p">(</span><span class="n">join</span><span class="p">(</span><span class="n">SCRIPTS_DIR</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'..'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'keys'</span><span class="p">))</span><br><span class="n">KEEPASS_DIR</span> <span class="o" style="color:#f92672">=</span> <span class="n">abspath</span><span class="p">(</span><span class="n">join</span><span class="p">(</span><span class="n">SCRIPTS_DIR</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'..'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'keepass'</span><span class="p">))</span><br><span class="n">DATABASE_PATH</span> <span class="o" style="color:#f92672">=</span> <span class="n">join</span><span class="p">(</span><span class="n">KEEPASS_DIR</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'NewDatabase.kdbx'</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">rebuild_key_dir</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Erase and remake key dir"""</span><br>    <span class="n">rmtree</span><span class="p">(</span><span class="n">KEY_DIR</span><span class="p">,</span> <span class="bp" style="color:#f8f8f2">True</span><span class="p">)</span><br>    <span class="n">makedirs</span><span class="p">(</span><span class="n">KEY_DIR</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">wipe_database</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Wipes all KeePass entries"""</span><br>    <span class="n">check_call</span><span class="p">(</span><br>        <span class="p">[</span><br>            <span class="s1" style="color:#e6db74">'kpscript'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-c:DeleteAllEntries'</span><span class="p">,</span><br>            <span class="n">DATABASE_PATH</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-pw:'</span><span class="p">,</span><br>        <span class="p">]</span><br>    <span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">create_single_key</span><span class="p">(</span><span class="n">index</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Creates a key for a given index"""</span><br>    <span class="n">check_call</span><span class="p">(</span><br>        <span class="p">[</span><br>            <span class="s1" style="color:#e6db74">'ssh-keygen'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-t'</span><span class="p">,</span> <span class="s1" style="color:#e6db74">'rsa'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-P'</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"password</span><span class="si" style="color:#e6db74">%02d</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">index</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-C'</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"user</span><span class="si" style="color:#e6db74">%02d</span><span class="s2" style="color:#e6db74">@host"</span> <span class="o" style="color:#f92672">%</span> <span class="n">index</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-f'</span><span class="p">,</span> <span class="n">join</span><span class="p">(</span><span class="n">KEY_DIR</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"dummy_key_</span><span class="si" style="color:#e6db74">%02d</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">index</span><span class="p">)</span><br>        <span class="p">]</span><br>    <span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">update_database</span><span class="p">(</span><span class="n">index</span><span class="p">):</span><br>    <span class="sd" style="color:#e6db74">"""Adds the entry to the database"""</span><br>    <span class="n">check_call</span><span class="p">(</span><br>        <span class="p">[</span><br>            <span class="s1" style="color:#e6db74">'kpscript'</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-c:AddEntry'</span><span class="p">,</span><br>            <span class="n">DATABASE_PATH</span><span class="p">,</span><br>            <span class="s1" style="color:#e6db74">'-pw:'</span><span class="p">,</span><br>            <span class="s2" style="color:#e6db74">"-UserName:dummy_key_</span><span class="si" style="color:#e6db74">%02d</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">index</span><span class="p">,</span><br>            <span class="s2" style="color:#e6db74">"-Password:password</span><span class="si" style="color:#e6db74">%02d</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">%</span> <span class="n">index</span><br>        <span class="p">]</span><br>    <span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">create_keys</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Creates all the necessary keys"""</span><br>    <span class="k" style="color:#66d9ef">for</span> <span class="n">index</span> <span class="ow" style="color:#f92672">in</span> <span class="nb" style="color:#f8f8f2">range</span><span class="p">(</span><span class="n">KEY_COUNT</span><span class="p">):</span><br>        <span class="n">create_single_key</span><span class="p">(</span><span class="n">index</span> <span class="o" style="color:#f92672">+</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">)</span><br>        <span class="n">update_database</span><span class="p">(</span><span class="n">index</span> <span class="o" style="color:#f92672">+</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">)</span><br><br><br><span class="k" style="color:#66d9ef">def</span> <span class="nf" style="color:#a6e22e">cli</span><span class="p">():</span><br>    <span class="sd" style="color:#e6db74">"""Runs everything"""</span><br>    <span class="n">rebuild_key_dir</span><span class="p">()</span><br>    <span class="n">wipe_database</span><span class="p">()</span><br>    <span class="n">create_keys</span><span class="p">()</span><br><br><span class="k" style="color:#66d9ef">if</span> <span class="s1" style="color:#e6db74">'__main__'</span> <span class="o" style="color:#f92672">==</span> <span class="vm" style="color:#f8f8f2">__name__</span><span class="p">:</span><br>    <span class="n">cli</span><span class="p">()</span><br></pre></div>
</td>
</tr>
</table>

### `Vagrantfile`

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">Vagrantfile</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-ssh-config-with-keeagent/tree/master/Vagrantfile" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e"># -*- mode: ruby -*-</span><br><span class="c1" style="color:#75715e"># vi: set ft=ruby :</span><br><br><span class="no" style="color:#66d9ef">Vagrant</span><span class="o" style="color:#f92672">.</span><span class="n">configure</span><span class="p">(</span><span class="s2" style="color:#e6db74">"2"</span><span class="p">)</span> <span class="k" style="color:#66d9ef">do</span> <span class="o" style="color:#f92672">|</span><span class="n">config</span><span class="o" style="color:#f92672">|</span><br>  <span class="n">config</span><span class="o" style="color:#f92672">.</span><span class="n">vm</span><span class="o" style="color:#f92672">.</span><span class="n">box</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"fedora/27-cloud-base"</span><br><br>  <span class="n">config</span><span class="o" style="color:#f92672">.</span><span class="n">vm</span><span class="o" style="color:#f92672">.</span><span class="n">provision</span> <span class="s2" style="color:#e6db74">"shell"</span> <span class="k" style="color:#66d9ef">do</span> <span class="o" style="color:#f92672">|</span><span class="n">shell</span><span class="o" style="color:#f92672">|</span><br>    <span class="n">shell</span><span class="o" style="color:#f92672">.</span><span class="n">privileged</span> <span class="o" style="color:#f92672">=</span> <span class="kp" style="color:#66d9ef">true</span><br>    <span class="n">shell</span><span class="o" style="color:#f92672">.</span><span class="n">inline</span> <span class="o" style="color:#f92672">=</span> <span class="o" style="color:#f92672">&lt;&lt;-</span><span class="dl" style="color:#e6db74">SHELL</span><br><span class="sh" style="color:#e6db74">    useradd dummy_user</span><br><span class="sh" style="color:#e6db74">    echo dummy_password | passwd dummy_user --stdin</span><br><span class="sh" style="color:#e6db74">    mkdir -p /home/dummy_user/.ssh</span><br><span class="sh" style="color:#e6db74">    chmod 'u=rwx,go=' /home/dummy_user/.ssh</span><br><span class="sh" style="color:#e6db74">    cp /vagrant/keys/dummy_key_10* /home/dummy_user/.ssh/</span><br><span class="sh" style="color:#e6db74">    chown -R dummy_user:dummy_user /home/dummy_user</span><br><span class="sh" style="color:#e6db74">    cp /vagrant/keys/dummy_key_10.pub /home/dummy_user/.ssh/authorized_keys</span><br><span class="sh" style="color:#e6db74">    chmod 'u=rw,go=' /home/dummy_user/.ssh/authorized_keys</span><br><span class="sh" style="color:#e6db74">    sed -i \</span><br><span class="sh" style="color:#e6db74">        -e 's/PermitRootLogin/#PermitRootLogin/g' \</span><br><span class="sh" style="color:#e6db74">        -e 's/#MaxAuthTries 6/MaxAuthTries 3/g' \</span><br><span class="sh" style="color:#e6db74">        -e 's/PasswordAuthentication yes/PasswordAuthentication no/g' \</span><br><span class="sh" style="color:#e6db74">        /etc/ssh/sshd_config</span><br><span class="sh" style="color:#e6db74">    systemctl restart sshd</span><br><span class="dl" style="color:#e6db74">    SHELL</span><br>  <span class="k" style="color:#66d9ef">end</span><br><span class="k" style="color:#66d9ef">end</span><br></pre></div>
</td>
</tr>
</table>
