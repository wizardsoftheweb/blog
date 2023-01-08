---
title: "The certbot Hook API"
slug: "certbot-hook-api"
date: "2017-12-17T05:00:00.000Z"
feature_image: "/images/2017/12/certbot-hooks.png"
author: "CJ Harries"
description: "I spent some time ripping the code apart to see how hooks actually work. I've broken down where the hooks are defined, their configuration, and how you can modify them."
tags: 
  - certbot
  - Let's Encrypt
  - security
  - NGINX
  - Apache
  - EFF
draft: true
---

Hopefully this is useful to someone else. I got confused by the language change from `renew` to `deploy` hooks and spent some time ripping the code apart to see how the hooks actually work. I've broken down where the hooks are defined, their configuration, and how you can modify them.

<p class="nav-p"><a id="post-nav"></a></p>
<!-- MarkdownTOC -->

- [Notes](#notes)
- [Overview](#overview)
- [Initial Change](#initialchange)
    - [CLI](#cli)
    - [Hook Definitions](#hookdefinitions)
    - [Execution](#execution)
- [Current API](#currentapi)
    - [CLI](#cli1)
    - [External Hooks](#externalhooks)
    - [Hook Definitions](#hookdefinitions1)
    - [Execution](#execution1)
- [So What?](#sowhat)
    - [Expect Change](#expectchange)
    - [Manually Run Hooks After Initial Creation](#manuallyrunhooksafterinitialcreation)
    - [Create a Generic Server Restart Hook](#createagenericserverrestarthook)
        - [Nginx](#nginx)
        - [Apache](#apache)
    - [Pre- and Post-Hooks are Always Run](#pre-andpost-hooksarealwaysrun)
- [Final Note](#finalnote)

<!-- /MarkdownTOC -->

## Notes

When I started this, `certbot` was on `0.19`. There's a really good chance it's been updated when you're reading this, especially if you're trying to update older usage. I've tried to mention the versions when talking about things, and I've linked the version-tagged files instead of the files from the default branch.

`certbot` is solid, organic FOSS written by many capable devs, each with different ideas about how to structure a Python repo. I don't have a solid grasp on Python yet. I haven't yet encountered useful tools to break code down and trace execution, so my breakdowns exclusively use the source. My interpretation of the source might be horribly wrong.

When I generalize "hooks" in this post, I'm referring to `renew_hook`s and `deploy_hook`s. There are also `pre_hook`s and `post_hook`s that probably shouldn't get lumped in. For example, when I say "all the hooks are `renew_hook`s", I'm not including `(pre|post)_hook`s. I explicitly mention them when they're pertinent.

Finally, I'm releasing this without all the code I wanted to write. It's been on the backburner for a couple of weekends. I had originally planned to do a more detailed execution analysis with examples, but I need some of this info in a post I'm working on now. I'm still planning on (eventually) doing that, so stay tuned.

## Overview

I had some SSL issues several weekends ago. Something apparently went wrong with my `cron` job, and, while trying to verify everything, I realized the CLI flags were different. I was running this command (with absolute paths to mimic `cron`):

```bash
$ /usr/bin/certbot renew --quiet --renew-hook "systemctl restart nginx"
```

However, I couldn't find it mentioned in the docs:

```bash
$ /usr/bin/certbot --help renew | grep -- --renew-hook || (state=$? && echo "whoops" && $(exit $state))
whoops
```

I did notice `--deploy-hook` after reading the entire output:

```bash
$ /usr/bin/certbot --help renew | awk 'BEGIN { inside_desired_block = 0; }; /^\s*--deploy-hook/{ inside_desired_block = 1; }; (/^\s*--/ && !/^\s*--deploy-hook/){ inside_desired_block = 0; }; inside_desired_block { print; }'
  --deploy-hook DEPLOY_HOOK
                        Command to be run in a shell once for each
                        successfully issued certificate. For this command, the
                        shell variable $RENEWED_LINEAGE will point to the
                        config live subdirectory (for example,
                        "/etc/letsencrypt/live/example.com") containing the
                        new certificates and keys; the shell variable
                        $RENEWED_DOMAINS will contain a space-delimited list
                        of renewed certificate domains (for example,
                        "example.com www.example.com" (default: None)
```

That sounded exactly like what I remembered reading about `--renew-hook`.

## Initial Change

[As of `0.17`](https://github.com/certbot/certbot/blob/master/CHANGELOG.md#0170---2017-08-02),
>The `--renew-hook` flag has been hidden in favor of `--deploy-hook`.

`renew_hook` was, essentially, hidden behind an adapter, `deploy_hook`. My best guess for reasoning is that the functions involved are actually triggered whenever a cert is successfully built, which happens on `run`, `certonly`, and `renew`.  Anything passed as a `deploy_hook` was duplicated as a `renew_hook`, which the major difference being, quite literally, the function called to access them.

(Note: nailing down the precise design pattern used here requires more pedantry than I'm willing to invest right now. `deploy_hook`, at inception, was an adapter/wrapper/convenience method that calls `renew_hook` when a `renew_hook` is called a `deploy_hook` instead of a `renew_hook`.)

### CLI

* `--renew-hook` was [suppressed in `cli.py`](https://github.com/certbot/certbot/blob/v0.17.0/certbot/cli.py#L1094). It's still parsed, just not exposed in the help.
* In its place, `--deploy-hook` was [added](https://github.com/certbot/certbot/blob/v0.17.0/certbot/cli.py#L1096).
* At this point, [a `deploy_hook` is a `renew_hook`](https://github.com/certbot/certbot/blob/v0.17.0/certbot/cli.py#L1381) or [everything is a `renew_hook`](https://github.com/certbot/certbot/blob/v0.17.0/certbot/cli.py#L1392).

### Hook Definitions

* `renew_hook` was unchanged in `hooks.py` (aside from [some output language](https://github.com/certbot/certbot/blame/v0.17.0/certbot/hooks.py#L112)).
* `deploy_hook` was created [as an adapter to `renew_hook`](https://github.com/certbot/certbot/blob/v0.17.0/certbot/hooks.py#L99). The conditional is deceptive; `config.deploy_hook == config.renew_hook` so there's no reason to not just explicitly call `renew_hook`.

### Execution

When a cert is installed for any reason (`renew|certonly|run`),

1. [execute `pre_hook`](https://github.com/certbot/certbot/blob/v0.17.0/certbot/main.py#L71)
2. 	* if the cert already exists and was changed, [execute `renew_hook`](https://github.com/certbot/certbot/blob/v0.17.0/certbot/renewal.py#L310) by [calling `renewal.renew_cert`](https://github.com/certbot/certbot/blob/v0.17.0/certbot/main.py#L77)
	* if the cert is new and was successfully created, [execute `deploy_hook`](https://github.com/certbot/certbot/blob/v0.17.0/certbot/main.py#L86)
3. [execute `post_hook`](https://github.com/certbot/certbot/blob/v0.17.0/certbot/main.py#L88)

## Current API

This section uses [tag `v0.19.0`](https://github.com/certbot/certbot/tree/v0.19.0/), which was current when I wrote this.

<h3 id="cli1">CLI</h3>

There weren't many changes from `0.17` in the CLI setup.

* `--renew-hook` is [suppressed in `cli.py`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/cli.py#L1147). It's still parsed, just not exposed in the help
* `--deploy-hook` [masks `--renew-hook`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/cli.py#L1150)
* Either [all the `deploy_hook`s are duplicated as `renew_hook`s](https://github.com/certbot/certbot/blob/v0.19.0/certbot/cli.py#L1461) or [there are only `renew_hook`s](https://github.com/certbot/certbot/blob/v0.19.0/certbot/cli.py#L1472)

<h3 id="externalhooks1">External Hooks</h3>

`certbot` can pick up hooks from [its configuration file](https://github.com/certbot/certbot/blob/v0.19.0/docs/using.rst#modifying-the-renewal-configuration-file). I can't find actual documentation of this feature (e.g. [ctrl+f `renew_hook`](https://certbot.eff.org/docs/using.html)), but it's [built by `renewal`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/renewal.py#L30). Specifically, you can create something like this:

```init
...
[renewalparams]
renew_hook = echo 'do stuff'
...
```

This will be loaded as a `renew_hook` after bootstrapping, so, in theory, it will only be executed by `renew_hook` (unlike CLI-created `deploy_hook`s, for example), but I haven't tested that. They're loaded by [`restore_required_config_elements`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/renewal.py#L158), [via `_reconstitute`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/renewal.py#L78), [via `handle_renewal_request`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/renewal.py#L401), which [seems to only appear](https://github.com/certbot/certbot/search?utf8=%E2%9C%93&q=handle_renewal_request&type=) in `main`, where it's [called by `renew`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/main.py#L794).

Similarly, you can [define global hooks](https://github.com/certbot/certbot/blob/v0.19.0/docs/using.rst#renewing-certificates), placed in (most likely) `/etc/letsencrypt/renewal-hooks/deploy`. As explained below, these are not executed by `deploy_hook` but rather by `renew_hook`, i.e. they're only going to run with `renew`. You can possibly trigger them by explicitly setting a `deploy_hook` via the CLI, to force creation of the `renew_hook` attribute, but I haven't tested this.

### Hook Definitions

The hooks have been extensively refactored (which kinda happens often at major version `0`). `deploy_hook` is similar in name to the primary runner, `_run_deploy_hook`. However, the `deploy_hook` function is much slimmer than `renew_hook`, implying a continued reliance on `renew_hook`.

* `_run_deploy_hook` is [a straight-forward runner](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L199). I'd argue its primary purpose is to collect command logging and state logic, which it does admirably.
* `deploy_hook` is [a simple conditional](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L153) that executes any defined hooks.
* `renew_hook` is [a bit larger](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L167). It begins by loading, caching, and executing [any hooks in `renewal_deploy_hooks_dir`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L185). The directory is [created in `configuration`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/configuration.py#L124) as a join on `config_dir` (which is likely [this default](https://github.com/certbot/certbot/blob/v0.19.0/certbot/constants.py#L83)), [the `RENEWAL_HOOKS_DIR` constant](https://github.com/certbot/certbot/blob/v0.19.0/certbot/constants.py#L180), and  [the `RENEWAL_DEPLOY_HOOKS_DIR` constant](https://github.com/certbot/certbot/blob/v0.19.0/certbot/constants.py#L186). Once finished, it [executes any `renew_hook` that wasn't included in `renewal_deploy_hooks_dir`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L190).

### Execution

This breakdown is a bit messier than before, with a few more branches to trace. When a cert is installed for any reason (`renew|certonly|run`),

1. [execute `pre_hook`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/main.py#L74):
    * if renewing and the external `pre_hook`s directory exists, [run the global `pre_hook`s](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L71).
    * run any [defined `pre_hook`s](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L75) (if they weren't already run) 
2. 	* if the cert already exists and was changed, [execute `renew_hook`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/renewal.py#L310) by [calling `renewal.renew_cert`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/main.py#L80)
        * if the external `deploy_hook`s directory exists and contains hooks, [run them](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L185)
        * if a `renew_hook` exists and was not run, [run it](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L190)
	* if the cert is new and was successfully created, [execute `deploy_hook`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/main.py#L89), which [skips the external `deploy_hook` directory](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L162)
3. [execute `post_hook`](https://github.com/certbot/certbot/blob/v0.19.0/certbot/main.py#L91):
    * if renewing and the external `post_hook`s directory exists, [run the global `post_hook`s](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L119).
    * run any [defined `post_hook`s](https://github.com/certbot/certbot/blob/v0.19.0/certbot/hooks.py#L128) (if they weren't already run)

## So What?

### Expect Change

In the couple of weekends it took me to get back to this post, `v0.20` was released. I haven't had a chance to look at it yet. This is great, active FOSS. Don't expect the minutae to work as intended for awhile yet. To quote [semver](https://semver.org/),

> Major version zero (`0.y.z`) is for initial development. Anything may change at any time. The public API should not be considered stable.

### Manually Run Hooks After Initial Creation

For some reason there's a disconnect between `deploy_hook` and `renew_hook` on installation ([confirmed in `v0.20`](https://github.com/certbot/certbot/blob/v0.20.0/certbot/hooks.py#L162)). If you've built an external hook in `/etc/letsencrypt/renewal-hooks/deploy` that, say, restarts your webserver, it's not going to get triggered with a brand new cert. However, it will get run every time you `renew` afterward.

### Create a Generic Server Restart Hook

Something like this in `/etc/letsencrypt/renewal-hooks/deploy` will successfully reload any new configuration on any of your new sites (assuming they're all run by the same webserver). It's only going to get triggered on a successful update, so it shouldn't run wild.

#### Nginx

```bash
#!/bin/bash

nginx -t && systemctl restart nginx
```

#### Apache

Might have to use `apache2ctl` or `httpd`.

```bash
#!/bin/bash

apachectl -t && systemctl restart apachectl
```

### Pre- and Post-Hooks are Always Run

No matter what, `certbot` starts with `pre_hook`s and finishes with `post_hook`s. I don't have a good use for either, so I'm a bit short on examples. However, know the hooks are there and can be used.

## Final Note

Let's Encrypt is a fantastic service. If you like what they do, i.e. appreciate how accessible they've made secure web traffic, [please donate](https://letsencrypt.org/donate/). [EFF's `certbot`](https://certbot.eff.org/) is what powers my site (and basically anything I work on these days); consider [buying them a beer](https://supporters.eff.org/donate/support-lets-encrypt) (it's really just a donate link but you catch my drift).