---
title: "Package Manager Showdown: Yarn and NPM on a VPS"
slug: "package-manager-showdown-yarn-npm-vps-memory"
date: "2017-12-13T03:00:00.000Z"
feature_image: "/images/2017/12/tmux-comp-resized.png"
author: "CJ Harries"
tags:
  - NPM
  - Yarn
  - JavaScript
  - package manager
  - asciicast
  - Digital Ocean
  - VPS
draft: true
---

I've worked pretty hard to stay out the whole JS package manager debate. NPM's always done what I needed. Prior to yesterday evening, I had no baseline for comparison. Sure, like everyone else, I've read articles that point out how slow NPM is in comparison to Yarn. I tend to switch tabs/windows/whatever the second I forget what I was doing (i.e. every five minutes), so I don't often wait on NPM. Yarn's API also apparently comes from a totally different methodology. I've grown used to the madness surrounding NPM's method, so I've honestly had no reason to change.

<!-- MarkdownTOC -->

- [Note](#note)
- [Background](#background)
  - [Digital Ocean](#digital-ocean)
  - [Ghost](#ghost)
- [Origin](#origin)
- [NPM](#npm)
  - [CLI](#cli)
  - [Analysis](#analysis)
  - [Memory Usage](#memory-usage)
- [Yarn](#yarn)
  - [CLI](#cli-1)
  - [Analysis](#analysis-1)
  - [Memory Usage](#memory-usage-1)
- [Side-By-Side](#side-by-side)
- [Verdict](#verdict)

<!-- /MarkdownTOC -->

## Note

I'm still trying to figure out how to properly build content for AMP. I recorded a few [asciicasts](https://asciinema.org/) for this post and haven't yet figured out how to load and scale them well with a bunch of external stuff. For now, you'll have to load them externally. Sorry about that. While you're there, you might consider [donating because asciinema is hella rad](https://asciinema.org/contributing#donating).

## Background

### Digital Ocean

The one thing that I actually require from my package managers is that they have to work in my environments. In production mode at work, that's almost never an issue. Companies understand the need for good hardware to match traffic. In production mode at home, I'm pretty cheap. I don't maintain apps with massive hardware needs because a) that's expensive and b) I don't ever have good ideas. I've gotten away with the penultimate [Digital Ocean Standard Droplet](https://www.digitalocean.com/community/tutorials/choosing-the-right-droplet-for-your-application#standard-droplets) for years and I have the traffic to prove it.

![standard-droplet-penultimate-tier](/images/2017/12/standard-droplet-penultimate-tier.png)

### Ghost

I use [Ghost](https://ghost.org/) as a blogging platform. It runs rather well on basic droplets. It's a well-constructed JS app, so it's not massively bloated. At the same time, I'm not running an enterprise server and my traffic is so small Ghost doesn't ever get a chance to run out of memory. MySQL is typically using at least twice as many resources as Ghost, which is probably a good thing because it's only running for Ghost.

Today, after applying [a really important Node security patch](https://nodejs.org/en/blog/vulnerability/december-2017-security-releases/), I decided to finally update Ghost. [Ghost-CLI](https://github.com/TryGhost/Ghost-CLI) is a great little tool that basic does everything for me. Sort of. Like normal, I ran

```bash
ghost update
```

but the script failed. I didn't initially notice what had happened, so, after trying all sorts of things that didn't work, I reverted the updates and cracked open the directory in question.

## Origin

If you'd like to test this as well, [snag Ghost `v1.18.4`](https://github.com/TryGhost/Ghost/releases/tag/1.18.4), nuke `node_modules`, and remove any `.lock` files.

## NPM

### CLI

```bash
$ cd path/to/1.18.4
$ rm -rf node_modules
$ rm -rf *.lock
$ ls -alh
total 76K
drwxrwxr-x   4 cjharries cjharries 4.0K Dec 12 03:56 .
drwxrwxrwt. 39 root      root      4.0K Dec 12 03:47 ..
drwxr-xr-x   8 cjharries cjharries 4.0K Dec 12 02:03 content
drwxr-xr-x   4 cjharries cjharries 4.0K Dec 12 02:03 core
-rw-r--r--   1 cjharries cjharries  32K Dec 12 02:03 Gruntfile.js
-rw-r--r--   1 cjharries cjharries 1.4K Dec 12 02:03 index.js
-rw-r--r--   1 cjharries cjharries 1.1K Dec 12 02:03 LICENSE
-rw-r--r--   1 cjharries cjharries  453 Dec 12 02:03 MigratorConfig.js
-rw-r--r--   1 cjharries cjharries 4.2K Dec 12 02:03 package.json
-rw-r--r--   1 cjharries cjharries 2.9K Dec 12 02:03 PRIVACY.md
-rw-r--r--   1 cjharries cjharries 4.0K Dec 12 02:03 README.md
$ npm install
npm WARN deprecated nodemailer@0.7.1: All versions below 4.0.1 of Nodemailer are deprecated. See https://nodemailer.com/status/
npm WARN deprecated node-uuid@1.4.8: Use uuid module instead
npm WARN deprecated mimelib@0.2.19: This module is deprecated
npm WARN deprecated lodash.isarray@4.0.0: This package is deprecated. Use Array.isArray.
npm WARN deprecated coffee-script@1.10.0: CoffeeScript on NPM has moved to "coffeescript" (no hyphen)
npm WARN deprecated minimatch@0.2.14: Please update to minimatch 3.0.2 or higher to avoid a RegExp DoS issue
npm WARN deprecated coffee-script@1.3.3: CoffeeScript on NPM has moved to "coffeescript" (no hyphen)
npm WARN deprecated minimatch@0.3.0: Please update to minimatch 3.0.2 or higher to avoid a RegExp DoS issue
npm WARN deprecated graceful-fs@1.2.3: graceful-fs v3.0.0 and before will fail on node releases >= v7.0. Please update to graceful-fs@^4.0.0 as soon as possible. Use 'npm ls graceful-fs' to find it in the tree.
[1]    16161 killed     npm installecode: sill doParallel extract 1263
```

### Analysis

I can honestly say I've never seen `npm` kill an installation script. After running it again a few times to make sure, I hit Google. It turns out that this is [a fairly common Digital Ocean issue](https://www.digitalocean.com/community/questions/npm-gets-killed-no-matter-what). That thread suggests creating a swap file to increase memory. On an HDD, I'd do that in a heartbeat. On an SSD, that's an invitation to never see my data again. Of course Digital Ocean suggests [beefing up the droplet](https://www.digitalocean.com/community/tutorials/how-to-add-swap-on-centos-7#introduction), because they need to make money. I get it.

Neither solution makes any sense, though. All I wanted to do was install a list of remote dependencies properly built for my system. I rarely run that command. What am I supposed to do, temporarily bulk up for a single command? That's ridiculous.

### Memory Usage

To make sure I wasn't making this up, I ran the installation beside `htop` to track everything.

[![asciicast](https://asciinema.org/a/O8NudfqAaAtct7T2ShNTMvqAB.png)](https://asciinema.org/a/O8NudfqAaAtct7T2ShNTMvqAB)

## Yarn

After a bit more Googling, I quickly learned that's there no way to, say, install dependencies one-by-one via NPM unless I wanted to call them one-by-one. My hopes for Yarn actually working were pretty low following NPM's spectacular performance. At least [installing Yarn](https://yarnpkg.com/lang/en/docs/install/) was quick and easy.

### CLI

```bash
$ cd path/to/1.18.4
$ rm -rf node_modules
$ rm -rf *.lock
$ ls -alh
total 76
drwxrwxr-x   4 cjharries cjharries  4096 Dec 12 04:34 .
drwxrwxrwt. 41 root      root       4096 Dec 12 04:33 ..
drwxr-xr-x   8 cjharries cjharries  4096 Dec 12 02:04 content
drwxr-xr-x   4 cjharries cjharries  4096 Dec 12 02:04 core
-rw-r--r--   1 cjharries cjharries 32178 Dec 12 02:04 Gruntfile.js
-rw-r--r--   1 cjharries cjharries  1403 Dec 12 02:04 index.js
-rw-r--r--   1 cjharries cjharries  1065 Dec 12 02:04 LICENSE
-rw-r--r--   1 cjharries cjharries   453 Dec 12 02:04 MigratorConfig.js
-rw-r--r--   1 cjharries cjharries  4199 Dec 12 02:04 package.json
-rw-r--r--   1 cjharries cjharries  2968 Dec 12 02:04 PRIVACY.md
-rw-r--r--   1 cjharries cjharries  3994 Dec 12 02:04 README.md
$ yarn install
yarn install v1.3.2
info No lockfile found.
[1/5] Validating package.json...
warning ghost@1.18.4: The engine "cli" appears to be invalid.
[2/5] Resolving packages...
warning brute-knex > knex > node-uuid@1.4.8: Use uuid module instead
warning nodemailer@0.7.1: All versions below 4.0.1 of Nodemailer are deprecated. See https://nodemailer.com/status/
warning nodemailer > mailcomposer > mimelib@0.2.19: This module is deprecated
warning sanitize-html > lodash.isarray@4.0.0: This package is deprecated. Use Array.isArray.
warning grunt > coffee-script@1.10.0: CoffeeScript on NPM has moved to "coffeescript" (no hyphen)
warning grunt-docker > grunt > coffee-script@1.3.3: CoffeeScript on NPM has moved to "coffeescript" (no hyphen)
warning grunt-docker > grunt > minimatch@0.2.14: Please update to minimatch 3.0.2 or higher to avoid a RegExp DoS issue
warning grunt-docker > grunt > glob > minimatch@0.2.14: Please update to minimatch 3.0.2 or higher to avoid a RegExp DoS issue
warning grunt-docker > grunt > glob > graceful-fs@1.2.3: please upgrade to graceful-fs 4 for compatibility with current and future versions of Node.js
warning grunt-docker > grunt > findup-sync > glob > minimatch@0.3.0: Please update to minimatch 3.0.2 or higher to avoid a RegExp DoS issue
warning grunt-docker > docker > pygmentize-bundled > through2 > xtend > object-keys@0.4.0:
[3/5] Fetching packages...
[4/5] Linking dependencies...
[5/5] Building fresh packages...
success Saved lockfile.
Done in 38.62s.
```

### Analysis

It worked. I'm not sure it needs more analysis than that.

### Memory Usage

Watch Yarn not get killed. Also, it doesn't seem to consume everything in reach. Dunno why; don't care; it works.

[![asciicast](https://asciinema.org/a/Vnpt0fIQkZrxeHE4Vp1khvrO0.png)](https://asciinema.org/a/Vnpt0fIQkZrxeHE4Vp1khvrO0)

## Side-By-Side

I actually recorded this first because I couldn't believe they were that dissimilar. If you watched the memory consumption above, there's nothing here you haven't seen.

[![asciicast](https://asciinema.org/a/HvikBkw4T50ZfN7OqkpPbFtkT.png)](https://asciinema.org/a/HvikBkw4T50ZfN7OqkpPbFtkT)

## Verdict

I'm moving to Yarn this week. Not only did it actually work in my environment, it worked much faster than NPM was killed. If you're always running on high-end hardware with lots of resources (e.g. your servers are running Google Chrome), NPM will probably do the job. If you're not made of money, Yarn's a better bet.
