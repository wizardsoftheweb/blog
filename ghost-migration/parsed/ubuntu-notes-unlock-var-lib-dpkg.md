---
title: "Ubuntu Notes: Unlocking /var/lib/dpkg"
slug: "ubuntu-notes-unlock-var-lib-dpkg"
date: "2017-11-26T22:00:00.000Z"
feature_image: "/images/2017/11/systemd-xenial.png"
author: "CJ Harries"
description: "I ran into some issues this morning setting up a Xenial box via Vagrant. On boot, /var/lib/dpkg was totally locked."
tags: 
  - Vagrant
  - CLI
  - Linux
  - awk
  - Ubuntu
  - bash
  - systemd
draft: true
---

I ran into some issues this morning setting up a Xenial box via Vagrant. On boot, `/var/lib/dpkg` was totally locked with nothing I knew to link it to in `ps aux`. I've created a fairly novel solution; my point today was to learn about something new.

You should have a basic familiarity with the Linux CLI. If you don't know what `systemd` is, that's not a big deal. Skip to my take on [a full solution](#fullscript) if you'd like, but make sure to read [the disclaimer](#disclaimer) first.

<!-- MarkdownTOC -->

- [Windows](#windows)
- [`/var/lib/dpkg/` Locked](#varlibdpkglocked)
- [`apt-daily.service` and `apt-daily.timer`](#apt-dailyserviceandapt-dailytimer)
- [Broken Down](#brokendown)
- [Disclaimer](#disclaimer)
- [Full Script](#fullscript)

<!-- /MarkdownTOC -->

## Windows

The first issue, unsurprisingly, had to do with Windows. There are no officially supported [Hyper-V Xenial Images](https://app.vagrantup.com/ubuntu/boxes/xenial64) and I'm still too lazy to [create a custom boot config](https://blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-overview/#windows). I suppose I could make an image myself, but today is not that day. Instead, I went with [this solid box, `kmm/ubuntu-xenial64`](https://app.vagrantup.com/kmm/boxes/ubuntu-xenial64) (there are [plenty of others too](https://app.vagrantup.com/boxes/search?utf8=%E2%9C%93&sort=downloads&provider=hyperv&q=xenial64)).

## `/var/lib/dpkg/` Locked

Everything after that was just `systemd` being helpful. I think. I don't know much about the Debian ecosystem, and my RH knowledge is only barely better.

```powershell
$ vagrant init kmm/ubuntu-hyperv
... confirmation
$ vagrant up --provider=hyperv
... options and things
==> default: Get:1 http://security.ubuntu.com/ubuntu xenial-security InRelease [102 kB]
==> default: Hit:2 http://at.archive.ubuntu.com/ubuntu xenial InRelease
==> default: Hit:3 http://at.archive.ubuntu.com/ubuntu xenial-updates InRelease
==> default: Hit:4 http://at.archive.ubuntu.com/ubuntu xenial-backports InRelease
==> default: Fetched 102 kB in 1s (57.4 kB/s)
==> default: E: Could not get lock /var/lib/dpkg/lock - open (11: Resource temporarily unavailable)
```

I genuinely had no idea what that was, because I'm not used to things getting locked on boot. I don't know if I'm spoiled or naive; either way I should have at least been prepared for that, given the host OS I'm running. I don't want to admit how many times I `halt`ed and `destroy`ed the image trying to figure out what I had done to screw it up.

## `apt-daily.service` and `apt-daily.timer`

Turns out [Ubuntu enabled](https://launchpad.net/ubuntu/+source/apt/+changelog) an `apt-daily` service (ctrl+f the changelogs; they're pretty neat), linked to [a `systemd` condition, `ConditionACPower`](https://www.freedesktop.org/software/systemd/man/systemd.unit.html#ConditionArchitecture=).  I didn't start there; I began around [this SE thread](https://unix.stackexchange.com/questions/315502/how-to-disable-apt-daily-service-on-ubuntu-cloud-vm-image/315517#315517), whose solution seemed a bit extreme:

```bash
#!/bin/bash
# https://unix.stackexchange.com/a/315517

systemctl stop apt-daily.service
systemctl kill --kill-who=all apt-daily.service

# wait until `apt-get updated` has been killed
while ! (systemctl list-units --all apt-daily.service | fgrep -q dead)
do
  sleep 1;
done

# now proceed with own APT tasks
apt-get update
```

Apparently, with OP's cloud setup, `apt.systemd.daily` was firing a ton of actions. `kmm/ubuntu-xenial64` doesn't seem to have that feature, so the fix was a bit easier.

## Broken Down

```bash
$ systemctl list-unit-files apt* --all
UNIT FILE         STATE
apt-daily.service static
apt-daily.timer   enabled

2 unit files listed.
```

I know about `enabled` and `disabled`; I thought `active` and `inactive` were there too. [Those are actually unit states](https://www.freedesktop.org/software/systemd/man/systemctl.html#id-1.7.3.2.15.2.4), whereas `static` and `enabled` are [enablement states](https://www.freedesktop.org/software/systemd/man/systemctl.html#id-1.7.4.2.7.2.2). I have yet to see `static`, but I typically only touch `systemd` when something is `running`/`failed`. [`static` services](https://www.freedesktop.org/software/systemd/man/systemctl.html#is-enabled%20NAME%E2%80%A6) are those whose unit file isn't enabled and doesn't have an `[Install]` section. They're not going to get touched unless something calls them or [you go out of your way to mess with them](https://bbs.archlinux.org/viewtopic.php?pid=1193091#p1193091).

```bash
$ systemctl stop apt*
Warning: Stopping apt-daily.service, but it can still be activated by:
    apt-daily.timer
$ systemctl list-unit-files apt* --all
UNIT FILE         STATE
apt-daily.service static
apt-daily.timer   enabled

2 unit files listed.
```

It doesn't look like we've done much. However, the `lock` should be gone.

```bash
$ systemctl disable apt-daily.timer
Removed symlink /etc/systemd/system/timers.target.wants/apt-daily.timer.
$ systemctl disable apt-daily.service
$ systemctl list-unit-files apt* --all
UNIT FILE         STATE
apt-daily.service static
apt-daily.timer   disabled

2 unit files listed.
```

Notice how the first one logged about removing a symlink, but the second logged nothing? Without an installation target, there's nothing to `disable` with `apt-daily.service`. I basically wasted those key strokes. It was for a good cause.

```bash
$ systemctl mask apt-daily.service
Created symlink from /etc/systemd/system/apt-daily.service to /dev/null.
$ systemctl mask apt-daily.timer
Created symlink from /etc/systemd/system/apt-daily.timer to /dev/null.
$ systemctl list-unit-files apt* --all
UNIT FILE              STATE
apt-daily.service      masked
apt-daily.timer        masked

2 unit files listed.
```

As the output explains, the files are now linked to `/dev/null`, so they're not doing anything ([sort of](https://www.freedesktop.org/software/systemd/man/systemctl.html#mask%20NAME%E2%80%A6); there are some special cases).

```bash
$ date
Sun Nov 26 16:24:46 CET 2017
$ systemctl status apt-daily.timer
● apt-daily.timer
   Loaded: masked (/dev/null; bad)
   Active: inactive (dead)

Nov 26 16:13:15 ubuntu systemd[1]: apt-daily.timer: Adding 8h 14min 32.547236s random time.
Nov 26 16:13:22 ubuntu systemd[1]: apt-daily.timer: Adding 11h 9min 6.467456s random time.
Nov 26 16:13:20 ubuntu systemd[1]: apt-daily.timer: Adding 8h 17min 18.264787s random time.
Nov 26 16:13:27 ubuntu systemd[1]: apt-daily.timer: Adding 31min 22.064766s random time.
Nov 26 16:13:25 ubuntu systemd[1]: apt-daily.timer: Adding 8h 3min 17.916537s random time.
Nov 26 16:13:32 ubuntu systemd[1]: apt-daily.timer: Adding 6h 29min 41.757720s random time.
Nov 26 16:13:30 ubuntu systemd[1]: apt-daily.timer: Adding 9h 51min 26.987812s random time.
Nov 26 16:13:37 ubuntu systemd[1]: apt-daily.timer: Adding 4h 48min 58.662526s random time.
Nov 26 16:13:35 ubuntu systemd[1]: apt-daily.timer: Adding 5h 56min 26.259868s random time.
Nov 26 16:13:36 ubuntu systemd[1]: Stopped Daily apt activities.
```

## Disclaimer

You'll notice I'm basically piping a totally unknown result directly into `systemctl` commands below. Someone that actually knows what all of this stuff does could easily take my fun diversion and have even more fun with it. Meanwhile, I'm still struggling with the whole "which quote does what in which shell" question.

Don't be dumb and use that on sensitive machines. It works great on machines you're going to completely annihilate every ten minutes because you royally screwed up an Ansible permissions play. It doesn't work so well on machines you might actually need tomorrow.

## Full Script

I have two versions for you. You're going to hate me for both of them.

```bash
$ systemctl list-unit-files --all | awk '/apt/{ print $1; }' | xargs -t -I % sh -c "$(echo 'systemctl '{stop,disable,mask,'list-unit-files --all'}' %;')"
sh -c systemctl stop apt-daily.service; systemctl disable apt-daily.service; systemctl mask apt-daily.service; systemctl list-unit-files --all apt-daily.service;
UNIT FILE         STATE
apt-daily.service masked

1 unit files listed.
sh -c systemctl stop apt-daily.timer; systemctl disable apt-daily.timer; systemctl mask apt-daily.timer; systemctl list-unit-files --all apt-daily.timer;
UNIT FILE       STATE
apt-daily.timer masked

1 unit files listed.
```

```bash
systemctl list-unit-files --all | awk '/apt/{ printf "%s ", $1; }' | xargs -t -I % sh -c "$(echo 'systemctl '{stop,disable,mask,'list-unit-files --all'}' %;')"
sh -c systemctl stop apt-daily.service apt-daily.timer ; systemctl disable apt-daily.service apt-daily.timer ; systemctl mask apt-daily.service apt-daily.timer ; systemctl list-unit-files --all apt-daily.service apt-daily.timer ;
UNIT FILE         STATE
apt-daily.service masked
apt-daily.timer   masked

2 unit files listed.
```

1. `systemctl` drops all units into `stdout`
2. `awk` picks up any line containing `apt`.

    * The first prints it as a new line, meaning the final chain gets hit twice. This uses basic `awk` `print`ing. It looks like this:

    ```
    apt-daily.service
    apt-daily.timer
    ```

    * The second uses `printf` to [skip the `ORS`](https://www.gnu.org/software/gawk/manual/html_node/Output-Separators.html) entirely. It looks like this:

    ```
    apt-daily.service apt-daily.timer
    ```

3. Two things are happening here:
    * First, the command substitution (`"$(this stuff here)"`) is [expanding the braces](`https://www.gnu.org/software/bash/manual/html_node/Brace-Expansion.html`) via `echo` to create this string:

    ```
    systemctl stop %; systemctl disable %; systemctl mask %; systemctl list-unit-files --all %;
    ```

    * `xargs` then applies `stdin` (via the pipe) to the full `sh` command. It runs verbosely with `-t`, which is why you see a couple of calls. The replace flag (`-I`) specifies a placeholder (`%`) in the command that follows.

4. I told you you were going to hate me. I'm not smart enough yet to bum it down even more. #lyfgoals


Oh, and you can also wait for `apt-daily` to finish. I suppose you could just manually run all those commands, or even use a `bash` script like this

```bash
#!/bin/bash

for unit do
    echo "Checking systemd for $unit"
    systemctl list-unit-files "$unit" | grep "$unit" || exit 1
    echo "Stopping $unit..."
    systemctl stop "$unit"
    echo "Disabling $unit..."
    systemctl disable "$unit"
    echo "Masking $unit..."
    systemctl mask "$unit"
    systemctl list-unit-files "$unit"
done
```
Which is clearly the most boring way to do this task ever.
