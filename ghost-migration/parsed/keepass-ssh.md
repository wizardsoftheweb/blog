---
title: "KeePass + ssh"
slug: "keepass-ssh"
date: "2017-09-09T11:00:00.000Z"
feature_image: "/images/2017/09/post-markdown.png"
author: "CJ Harries"
description: "I've begun building a collection of keys for everything. It's annoying to re-enter all those passphrases more than once. With KeePass, I don't have to."
tags: 
  - KeePass
  - CLI
  - Linux
  - ssh
  - Windows
draft: true
---

I've been using [KeePass Professional Edition](https://keepass.info) for a few months now, and I'm always discovering new things to do with it. For example, I've got HQ photos of my driver's license so that I can go to the gym without carrying my full wallet (if that's illegal I totally don't do that). I've got a couple of shared databases that sync off my main personal database that I can share with family and friends, which means I change update my accounts without the old hassle of texting everyone the new credentials. I keep all of my work identities in KeePass, both for personal and employer accounts (with different databases, of course).

Today I was messing around in my gaming environment (which, until I take the time to set up another SSD with a real OS, is also my dev environment) and finally got sick of re-entering my `ssh` credentials on reloading `bash`. I've begun taking my online identity a bit more seriously and I'm building a collection of keys for everything. It's safe, but it's insanely annoying to have to re-enter all those passphrases more than once, say, a month.

<p class="nav-p"><a id="post-nav"></a></p>
<!-- MarkdownTOC -->

- [Background](#background)
- [Software](#software)
- [Adding keys](#addingkeys)
- [Running KeePass as an `ssh-agent`](#runningkeepassasansshagent)
    - [The basics](#thebasics)
    - [`systemd`](#systemd)
    - [Windows](#windows)
        - [Using `msys`/`cygwin`](#usingmsyscygwin)
        - [Using `python`](#usingpython)
- [KeePass Auto-Type](#keepassautotype)

<!-- /MarkdownTOC -->
## Background

Typically on Linux, [`ssh-agent`](http://blog.joncairns.com/2013/12/understanding-ssh-agent-and-ssh-add/) persists [with the session](https://superuser.com/questions/1238486/windows-10-linux-subsystem-ssh-agent-not-persisting-added-identities). Also typically on Linux, bouncing a machine is pretty rare. I can't remember the last time I logged out to log out, because I usually just lock the machine.

On Windows, however, closing all active `bash` shells kills off the processes. Microsoft says [this a feature](https://superuser.com/a/1173513), while the internet [hates it](https://wpdev.uservoice.com/forums/266908-command-prompt-console-bash-on-ubuntu-on-windo). For someone like me running `ssh-add` more than once in my [`.zpreztorc`](https://github.com/sorin-ionescu/prezto/blob/master/runcoms/zpreztorc), it's horrible and I hate it.

This is where KeePass steps in...
* **as an `ssh-agent`**: [KeeAgent](https://github.com/dlech/KeeAgent) is a fantastic crossplatform tool that functions as an `ssh-agent` capable of reading keys directly from your database.
* **as a typist**: For situations where you aren't able to [foward the agent](https://developer.github.com/v3/guides/using-ssh-agent-forwarding/) or aren't starting from a configured instance of KeePass, [Auto-Type](http://keepass.info/help/base/autotype.html) has you covered.

By always forwarding your agent (e.g. `ssh -A ...`), you can handle all of the keys via KeePass on your machine, instead of managing different keys on each machine.

## Software
* KeePass 2 (`~2`)
    * [Windows](http://keepass.info/download.html)
    * [Mac OS X](http://keepass.info/download.html) `cmd+f` "Contributed/Unofficial KeePass Packages"
    * [Some Linux package managers](http://keepass.info/download.html) `ctrl+f` "Contributed/Unofficial KeePass Packages"
    * [Everything else](http://keepass.info/help/v2/setup.html#mono)
* [KeeAgent](https://github.com/dlech/KeeAgent)
* (optional) [KPEntryTemplates](https://github.com/mitchcapper/KPEntryTemplates/releases) (makes it easier to manage templates)

## Adding keys
The [official docs for KeeAgent](https://lechnology.com/software/keeagent/usage/quick-start/) are awesome and have way more screenshots than I want to take. Basically, make your key like normal, use KeePass to generate the passphrase, and attach both the private and public files.

If, like me, you plan on building as many keys as you have passwords, you should uncheck the "Add key to agent when database is opened/unlocked" and instead manage it through KeeAgent.
![keeagent-dont-auto-add](/images/2017/09/keeagent-dont-auto-add.png)
The agent works by [forwarding as many keys as possible](https://serverfault.com/a/820048), so you can lock yourself out of a server if you load too many keys at once.

## Running KeePass as an `ssh-agent`
### The basics
Set up KeeAgent as the Agent and export a socket:
![keepass-linux-agent](/images/2017/09/keepass-linux-agent.png)
I use `ssh-keeagent.sock` instead of `ssh-agent.sock` to keep origin explicit.

You'll need to add the socket to your `.{whatever}rc` file:
<pre class="line-numbers"><code class="language-bash">
export SSH_AUTH_SOCK=/tmp/user/ssh-keeagent.sock
</code></pre>
Finally, [add keys](#addingkeys) and test the connection with some server:
<pre class="line-numbers"><code class="language-bash">
ssh -T git@github.com
</code></pre>
### `systemd`
(Note: I'm lazy and prefer to just run KeeAgent as the `ssh-agent`, so I didn't test this)

[This article](https://www.schmengler-se.de/en/2017/03/set-up-keepass-with-keeagent-on-linux/) by [Fabian Schmengler](https://www.schmengler-se.de/en/author/fabian-schmengler/) provides an excellent `systemd` setup. I'm pulling out the steps just in case:

Add `SSH_AGENT_SOCK` to your `.{whatever}rc` file ([source](https://www.schmengler-se.de/en/2017/03/set-up-keepass-with-keeagent-on-linux/#highlighter_499877)):
<pre class="line-numbers"><code class="language-bash">
export SSH_AUTH_SOCK="$XDG_RUNTIME_DIR/ssh-agent.socket"
</code></pre>

Add a user service, `~/.config/systemd/user/ssh-agent.service` ([source](https://www.schmengler-se.de/en/2017/03/set-up-keepass-with-keeagent-on-linux/#highlighter_868016)):
<pre class="line-numbers"><code class="language-bash">
[Unit]
Description=SSH key agent
Wants=environment.target
Before=environment.target
IgnoreOnIsolate=true

[Service]
Type=forking
Environment=SSH_AUTH_SOCK=%t/ssh-agent.socket
ExecStart=/usr/bin/ssh-agent -a $SSH_AUTH_SOCK
ExecStartPost=/bin/sh -c "/usr/bin/ps --no-headers -o pid -C ssh-agent | sed 's/^ /export SSH_AGENT_PID=/' > ~/ssh-agent.properties"
ExecStartPost=/bin/sh -c "echo export SSH_AUTH_SOCK=$SSH_AUTH_SOCK >> ~/ssh-agent.properties"
ExecStartPost=/usr/bin/systemctl --user set-environment SSH_AUTH_SOCK=${SSH_AUTH_SOCK}
ExecStopPost=/bin/rm ${SSH_AUTH_SOCK}

[Install]
WantedBy=default.target
</code></pre>
This step is really smart. Like the author, I've had trouble with `SSH_AGENT_PID` in the past. The service throws the generated config into a local file, removing the headache of exporting the variables.

Start and enable the service ([source](https://www.schmengler-se.de/en/2017/03/set-up-keepass-with-keeagent-on-linux/#highlighter_300270)):
<pre class="line-numbers"><code class="language-bash">
systemctl --user enable ~/.config/systemd/user/ssh-agent.service
systemctl --user start ssh-agent
</code></pre>

Guard `keepass` with `~/ssh-agent.properties` ([source](https://www.schmengler-se.de/en/2017/03/set-up-keepass-with-keeagent-on-linux/#highlighter_9794)):
<pre class="line-numbers"><code class="language-bash">
source ~/ssh-agent.properties && keepass
</code></pre>
You'll have to change the command wherever it's being called (e.g. update the path in your menu editor)
### Windows
[mendhak](https://github.com/mendhak) wrote a wonderful article about [connecting KeeAgent to Cygwin/MsysGit](http://code.mendhak.com/keepass-and-keeagent-setup/). However, with Windows 10, I'd like to integrate with WSL. At the moment, full integration [doesn't exist](https://github.com/dlech/KeeAgent/issues/159), but there are several solutions to get around it.
#### Using `msys`/`cygwin`
You can read from a [`msysgit`](https://github.com/msysgit/msysgit) (or possibly [`cygwin`](https://www.cygwin.com/)) socket via [`socat`](http://www.dest-unreach.org/socat/doc/socat.html). Find or install `socat`,
<pre class="line-numbers"><code class="language-bash">
which socat || sudo apt-get -y install socat
</code></pre>
then update your `.{whatever}rc` file ([source](https://github.com/dlech/KeeAgent/issues/159#issue-165437587)):
<pre class="line-numbers"><code class="language-bash">
 # If MSYSGIT socket in keeagent is set as c:\Users/foo/Documents/ssh_auth_msysgit
SSH_AUTH_KEEAGENT_SOCK=/mnt/c/Users/foo/Documents/ssh_auth_msysgit
SSH_AUTH_KEEAGENT_PORT=`sed -r 's/!<socket >([0-9]*\b).*/\1/' ${SSH_AUTH_KEEAGENT_SOCK}`

 # use socket filename structure similar to ssh-agent
ssh_auth_tmpdir=`mktemp --tmpdir --directory keeagent-ssh.XXXXXXXXXX`
SSH_AUTH_SOCK="${ssh_auth_tmpdir}/agent.$$"

socat UNIX-LISTEN:${SSH_AUTH_SOCK},mode=0600,fork,shut-down TCP:127.0.0.1:${SSH_AUTH_KEEAGENT_PORT},connect-timeout=2 2>&1 > /dev/null &
</code></pre>
I had to modify this a bit to get it to work with my `prezto` setup. Placing it in my `.zshrc` meant it was running in every new `bash.exe`, so I `ps | awk` to find the proper `SSH_AUTH_SOCK` if it's already running.
<pre class="line-numbers"><code class="language-bash">
 # Attempt to find the current process
SSH_AUTH_SOCK=$(ps -C socat -o command | awk '{ match($2, /\/tmp.*keeagent[^,]*/, a) }END{ print a[0] }')
 # Check if variable is empty
if [[ -z $SSH_AUTH_SOCK ]]; then
    # Clean all old tmp files
    rm -rf /tmp/user/keeagent*
    # If msys doesn't work, try cyg
    SSH_AUTH_KEEAGENT_SOCK=/mnt/c/Users/path/to/msyslock
    SSH_AUTH_KEEAGENT_PORT=`sed -r 's/!<socket >([0-9]*\b).*/\1/' ${SSH_AUTH_KEEAGENT_SOCK}`

    # use socket filename structure similar to ssh-agent
    ssh_auth_tmpdir=`mktemp --tmpdir --directory keeagent-ssh.XXXXXXXXXX`
    SSH_AUTH_SOCK="${ssh_auth_tmpdir}/agent.$$"

    socat UNIX-LISTEN:${SSH_AUTH_SOCK},mode=0600,fork,shut-down TCP:127.0.0.1:${SSH_AUTH_KEEAGENT_PORT},connect-timeout=2 2>&1 > /dev/null &
fi
export SSH_AUTH_SOCK=$SSH_AUTH_SOCK
</code></pre>
Breakdown of the initial command:
* `ps -C socat -o command`
    - `-C socat` searches the `COMMAND` column for `socat`
    - `-o command` returns only the `COMMAND` column
* `awk '{ match($2, /\/tmp.*keeagent[^,]*/, a) }END{ print a[0] }'`:
    - `match($2, /\/tmp.*keeagent[^,]*/, a)` searches the second column (see the space between `socat` and `UNIX`?) for a `/tmp` path containing `keeagent` and stores it in `a`.
    - `print a[0]` sends off the matched string, if any.
#### Using `python`
With [`python`](http://timmyreilly.azurewebsites.net/python-with-ubuntu-on-windows/) you can directly convert the socket ([gist](https://gist.github.com/FlorinAsavoaie/8c2b6cb00f786c2caab65b1a51f4e847) | [fork with additional features](https://gist.github.com/kevinvalk/3ccd5b360fd568862b4a397a9df9ed26)) instead of using `socat`. I haven't tried this, but it seems pretty solid. I might eventually run it in a VM at work.
## KeePass Auto-Type
If you, for whatever reason, [aren't forwarding/can't forward your agent](https://developer.github.com/v3/guides/using-ssh-agent-forwarding/), KeePass is still insanely useful. I use for server-specific users whose config I don't want to leave the server (if it doesn't leave the server, I know it's insecure when I see it in the wild). I make a template per user and reference things everywhere. Here's a breakdown of a sample user:

![keepass-add-entry](/images/2017/09/keepass-add-entry.png)

I'm abusing `URL` as `hostname`, and the password is actually the key's passphrase.

![keepass-add-advanced](/images/2017/09/keepass-add-advanced.png)

I include a string field for each of the CLI options (sure, specifying options and a config file is overkill, but you get the point).

![keepass-add-auto-type](/images/2017/09/keepass-add-auto-type.png)
```
ssh -i {S:SSH Key Path} -F {S:SSH Config File} -p {S:SSH Port} {USERNAME}@{URL}{ENTER}{DELAY 1000}{PASSWORD}{ENTER}
```
This is where the magic happens. I've beefed up the autotype to include all of the variables. I could actually use `URL:Port` instead of a custom variable, but I like having a custom variable because I can create a default template with port 22 and not worry about always appending `:22` to the `URL`.



