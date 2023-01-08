---
title: "Keepass Freerdp"
date: 2023-01-05T19:40:33-06:00
feature_image: "/images/2017/09/keepass-and-konsole-2.png"
author: CJ Harries
description: A great RDP-credential solution is KeePass (I recommend ~2; you'll see that here). Like other repetitive user-based CLI tasks, KeePass kills xfreerdp.
tags:
  - KeePass
  - CLI
  - Automation
  - Linux
  - RDP
  - FreeRDP
draft: true
---

One of my primary work responsibilities is to handle the Linux environments not related to our ecommerce platform (although, as one of few devs, one of my primary responsibilities is basically everything). We're a big fan of the RHEL pipeline, so I use CentOS as my work environment. It bites occasionally, but, by and large, we don't run bleeding-edge stacks because they're, well, unsupported bleeding-edge stacks. I can find most of the software I need with older versions of Fedora or by just manually building things.

The rest of our network, like most of the offices I've ever worked in, runs on Windows. Until Microsoft releases Office for Linux, that means I'm stuck RDPing into terminal servers for things like Excel and Word. I've spent a serious chunk of time researching RDP clients. One of these days, I'd like to use [Remmina](https://www.remmina.org/wp/), but their support for not-Ubuntu is pretty lacking. Instead, I settled on [FreeRDP](https://github.com/FreeRDP/FreeRDP), the tool behind Remmina. Unlike Remmina, it actually works on CentOS (and all of the other flavors of Linux I've tried it on so far).

I use `xfreerdp`, [the CLI for FreeRDP](https://github.com/FreeRDP/FreeRDP/wiki/CommandLineInterface). There are two exposed APIs at the moment, one of which is deprecated and will be removed at some point. Of course, using an older, more stable version of Linux means that I'm stuck on the old API (I could rebuild from source or I could keep using the thing that works). A typical session looks like this for me:

```bash
xfreerdp --plugin cliprdr -g 1920x1020 -u me -d workdomain 1.2.3.4
Password:
```

Converted to the new API, that should look like this (`g(eometry)` changed to `g(ateway)` so I use `size` instead):

```bash
xfreerdp +clipboard /size 1920x1020 /u me /d workdomain 1.2.3.4
Password:
```

For this article, I'll be using the older API because I'm too lazy to rebuild from source and I don't want to write about something without testing it.

On a given day, I'm in our financial VM, our SQL VM, an Office VM to work on TPS reports, our Windows testing VM, and maybe one or two others for various reasons. That's a lot of typing, especially since my work straddles two domains. I could alias all the commands using the password option, e.g.

```bash
xfreerdp --plugin cliprdr -g 1920x1020 -u me -d workdomain -p hunter2 1.2.3.4
```

I'm not a fan of that option because it exposes my password in my `history`. I could store my credentials in a file, e.g.

```bash
cat ~/secret
# username=me
# password=hunter2
xfreerdp --somehow-use-credentials
```

I'm not actually sure how that works, and I couldn't find it in the docs. Point is it's not a great idea and storing your credentials in plaintext (either accidentally in your `history` or on purpose in a `(chmod 400)` `secret` file) is an even worse idea. Anyone with `su` access to you (you or `root`) can see it, and if you don't know what you're doing, you might expose it to more than those two groups.

My `xfreerdp` credential solution is to use [KeePass](http://keepass.info/) (I recommend `~2`; that's what you'll see below.). Like other repetitive user-based CLI tasks, KeePass kills `xfreerdp`. You can see a finished copy of the database I'm about to build [in this repo](https://github.com/thecjharries/keepass-freerdp/blob/master/keepass-freerdp.kdbx). The master key is `hunter2`. First some setup:

![keepass-windows-user](https://blog.wotw.pro/content/images/2017/09/keepass-windows-user.png)

I make a Windows entry per account. Here you can see all of the account details:

![keepass-entry-entry](https://blog.wotw.pro/content/images/2017/09/keepass-entry-entry.png)

![keepass-entry-advanced](https://blog.wotw.pro/content/images/2017/09/keepass-entry-advanced.png)

Notice the custom string fields for each of the CLI options. To make sure I don't have enter/update those for every RDP entry, I next duplicate the account with references to the original fields and make a template:

![duplicate-keepass-entry](https://blog.wotw.pro/content/images/2017/09/duplicate-keepass-entry.png)

![keepass-template-with-references](https://blog.wotw.pro/content/images/2017/09/keepass-template-with-references.png)

Duplicating with references means all entries made from this template reference the original Windows user, so when I regularly change my password, I change it in one place. Same with a new domain, whatever. Next I make a subgroup of my Windows group and create a new [auto-type](http://keepass.info/help/base/autotype.html):

![keepass-freerdp-group](https://blog.wotw.pro/content/images/2017/09/keepass-freerdp-group.png)

![keepass-group-auto-type](https://blog.wotw.pro/content/images/2017/09/keepass-group-auto-type.png)

```bash
xfreerdp {S:RDP Plugins} -g {S:RDP Geometry} -d {S:Windows Domain} -u {USERNAME} {URL}{ENTER}{DELAY 1000}{PASSWORD}{ENTER}
```

The auto-type requires some explanation. I'm using KeePass to automatically type everything not in brackets. Everything in brackets is also typed by KeePass, but it's a variable. `{USERNAME}`, `{URL}`, and `{PASSWORD}` are all default KeePass variables (I haven't set the URL yet, in case you were about to point that out). `{S:Variable}` signifies a String Field. From the screenshots, I'm sure you can figure out what those were. The keystroke wizard (hit the star wand next to the text area) is a great resource and shows you everything you need to know, including other useful variables (like the `URL:<component>` variables). If you're familiar with tools like AutoHotkey, this will be a breeze.

![edit-keepass-auto-type](https://blog.wotw.pro/content/images/2017/09/edit-keepass-auto-type.png)

The last piece of the of the puzzle is the RDP entry:

![keepass-new-entry-from-template](https://blog.wotw.pro/content/images/2017/09/keepass-new-entry-from-template.png)

![keepass-freerdp-entry-with-url](https://blog.wotw.pro/content/images/2017/09/keepass-freerdp-entry-with-url.png)

As much as I'd like to show you a video of it in action, I don't actually like Windows enough to set up a dummy environment to demo and I'm not going to put work credentials/addresses online for the same reasons I don't store my credentials in my `history`. Pretend I did, and be amazed that managing multiple CLI RDP sessions on Linux is as simple as clicking a button (or using global hotkeys!).
