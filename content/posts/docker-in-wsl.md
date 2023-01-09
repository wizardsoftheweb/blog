---
title: "Docker in WSL"
slug: "docker-in-wsl"
date: "2017-10-03T23:00:00.000Z"
feature_image: "/images/2017/10/dockerwin_nt.png"
author: "CJ Harries"
description: "Being able to run a Docker host natively in Windows would be awesome. Being able to interact with it via WSL would be even more awesome."
tags:
  - Windows
  - WSL
  - Docker
  - LinuxKit
draft: true
---

Being able to run a Docker host natively in Windows would be awesome. Being able to interact with it via WSL would be even more awesome.

I've pieced together both a native and bespoke solution. The native solution comes mostly from Docker and Windows docs. The bespoke solution is wired up using the preview version of [LinuxKit](https://github.com/friism/linuxkit/).

<p class="nav-p"><a id="post-nav"></a></p>
<!-- MarkdownTOC -->

- [Code Note](#code-note)
- [Native Solution](#native-solution)
  - [Native Requirements](#native-requirements)
  - [Inside Windows](#inside-windows)
    - [IMPORTANT](#important)
    - [`dockerd` From Docker](#dockerd-from-docker)
    - [Aside: Things That Didn't Work Initially](#aside-things-that-didnt-work-initially)
    - [Settings](#settings)
  - [Inside WSL](#inside-wsl)
    - [Configure `python`](#configure-python)
    - [Install `pip`](#install-pip)
    - [Install `docker-compose`](#install-docker-compose)
    - [Environment](#environment)
- [Just Kidding](#just-kidding)
  - [Mostly](#mostly)
- [Bespoke Solution](#bespoke-solution)
  - [Bespoke Requirements](#bespoke-requirements)
  - [A Word of Caution](#a-word-of-caution)
  - [Inside Windows](#inside-windows-1)
    - [Installation](#installation)
    - [Bootstrapping](#bootstrapping)
    - [Lifecycle](#lifecycle)
  - [Inside WSL](#inside-wsl-1)
- [Final Notes](#final-notes)

<!-- /MarkdownTOC -->

## Code Note

I use both PowerShell and Bash throughout this post. I tried to distinguish between the shells using symbols from their default values:

```bash
$ bash
> powershell
```

If you're thoroughly confused, you can always check the source. Each block is labelled.

I'd also like to apologize in advance for my PowerShell style. I don't have much experience with the shell, so my knowledge of conventions is pretty limited. I've tried to maintain consistent usage throughout, but it's all just my interpretation of what I was sourcing so it could be totally wrong.

## Native Solution

### Native Requirements

You'll need these things before getting started:

- Windows 10 [in Developer mode](https://docs.microsoft.com/en-us/windows/uwp/get-started/enable-your-device-for-development)
- [Ubuntu on Windows](https://blogs.windows.com/buildingapps/2016/03/30/run-bash-on-ubuntu-on-windows/): some of the info here is Debian-specific, so if you're using [a different flavor](https://blogs.msdn.microsoft.com/commandline/2017/05/11/new-distros-coming-to-bashwsl-via-windows-store/), you might need to Google some stuff.

### Inside Windows

You can install Docker and the Docker Engine via your normal choice of package installation. If you're installing Docker on your production server to work with WSL, stop what you're doing, take the time you need to figure out PowerShell, and remove WSL from your production server. Since you're not, and you're setting it up for a dev environment, I recommend installing from [prebuilt](https://docs.docker.com/docker-for-windows/install/).

#### IMPORTANT

1. Search "Turn Windows features on or off" and open the Control Panel GUI result.
2. Make sure the following are enabled (requires reboot):

    - Hyper-V
    - Containers

A generic install from a stable package followed by toggling [Switch to Windows Containers](https://docs.microsoft.com/en-us/virtualization/windowscontainers/quick-start/quick-start-windows-10#2-switch-to-windows-containers) will achieve the same results. Because I like to tell myself I know what I'm doing, I started out with the more advanced installs and missed that.

#### `dockerd` From Docker

I did notice that the provided `PATH` addition, `$env:ProgramFiles\Docker\Docker\Resources\bin` doesn't include `dockerd`. The file, `dockerd.exe` is actually a directory above in `Resources`. To confirm,

```powershell
> Get-ChildItem -Path $env:ProgramFiles\Docker -Filter dockerd.exe -Recurse -ErrorAction SilentlyContinue -Force


    Directory: C:\Program Files\Docker\Docker\resources


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        10/1/2017  12:06 PM       35451239 dockerd.exe
```

You can either add `$env:ProgramFiles\Docker\Docker\Resources` to your `PATH` or symlink into `bin`.

```powershell
> [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path",[System.EnvironmentVariableTarget]::Machine) + ";$env:ProgramFiles\Docker", [EnvironmentVariableTarget]::Machine)
```

This is actually much easier in the GUI. Search "environment variables". It used to involve way more menus.

```powershell
> New-Item -ItemType SymbolicLink -Path $env:ProgramFiles\Docker\Docker\Resources\bin\dockerd.exe -Target $env:ProgramFiles\Docker\Docker\Resources\dockerd.exe
```

I recommend going with the symlink because it's a bit more secure. Adding an unknown directory that you don't have control over to your path is, at best, a recipe for spending more time debugging than coding. Docker didn't expose the directory, which means Docker might update the directory with some executables that conflict with the normal path. If you symlink the executable, you're forced to review changes when updates break the symlink. I've checked as much of the source as I can; while Docker didn't expose `dockerd`, it is used heavily through the documentation, so you can safely export it knowing that your code will break if Docker changes it.

#### Aside: Things That Didn't Work Initially

I started with

```powershell
> choco install docker-for-windows
```

but its installation matched almost zero documentation I found. It kept yelling at me when I tried to change `hosts` and wouldn't load an externally created config (both of which, I later discovered, were actual features of the edge version not covered the now outdated Microsoft docs).

I next tried the official Microsoft docs [on manual installation](https://docs.microsoft.com/en-us/virtualization/windowscontainers/manage-docker/configure-docker-daemon#install-docker):

```powershell
 # Select release to download
$version = (Invoke-WebRequest -UseBasicParsing https://raw.githubusercontent.com/docker/docker/master/VERSION).Content.Trim()
Invoke-WebRequest "https://master.dockerproject.org/windows/x86_64/docker-$($version).zip" -OutFile "$env:TEMP\docker.zip" -UseBasicParsing
 # Extract to Program Files
Expand-Archive -Path "$env:TEMP\docker.zip" -DestinationPath $env:ProgramFiles
 # Add path to this PowerShell session immediately
$env:path += ";$env:ProgramFiles\Docker"
 # For persistent use after a reboot
$existingMachinePath = [Environment]::GetEnvironmentVariable("Path",[System.EnvironmentVariableTarget]::Machine)
[Environment]::SetEnvironmentVariable("Path", $existingMachinePath + ";$env:ProgramFiles\Docker", [EnvironmentVariableTarget]::Machine)
 # Register the service
dockerd --register-service
 # Start the service
Start-Service Docker
```

This puts `docker.exe` and `dockerd.exe` into `$env:ProgramFiles\Docker`, creates `$env:ProgramData\docker`, and successfully registers a service via `dockerd --register-service`. However, I kept getting this error (and completely missed the whole `ensure...` note):

```powershell
> dockerd --run-service
Error starting daemon: a required service is not installed, ensure the Containers feature is installed: failed to open service hns: The specified service does not exist as an installed service.
```

In hindsight, I think the key was actually installing Docker for Windows through an official source and following the tutorial to the letter first. After getting very frustrated with the `choco` and manual installations, I followed the MS install guide and was notified Containers would be turned on. I assumed that it had been enabled when `docker-for-windows` enabled Hyper-V, but I think I was wrong about that assumption. So, if you want to use either one of these options, you should probably start by enabling the features.

#### Settings

Once Docker is up and running, access its settings via the toolbar. You'll need to expose the daemon. You can use the defaults (pictured below) or use secure settings.
![docker-expose-daemon](/images/2017/10/docker-expose-daemon.png)
This poses a potential security risk, so be careful. [WSL can be attacked](http://www.zdnet.com/article/windows-10s-subsystem-for-linux-heres-how-hackers-could-use-it-to-hide-malware/). I'd highly recommend you change and secure the port instead ([source](https://docs.microsoft.com/en-us/virtualization/windowscontainers/manage-docker/configure-docker-daemon#configure-docker-with-configuration-file)):

```json
{
    "hosts": ["tcp://0.0.0.0:2376", "npipe://"],
    "tlsverify": true,
    "tlscacert": "C:\\ProgramData\\docker\\certs.d\\ca.pem",
    "tlscert": "C:\\ProgramData\\docker\\certs.d\\server-cert.pem",
    "tlskey": "C:\\ProgramData\\docker\\certs.d\\server-key.pem",
}
```

### Inside WSL

You can use the stable Ubuntu packages if you want. However, the repositories are one major [Composer file version](https://docs.docker.com/compose/compose-file/compose-versioning/#compatibility-matrix) behind. Since that might not always be the case, you can check versions like this:

```bash
$ lsb_release -a
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 16.04.2 LTS
Release:        16.04
Codename:       xenial
$ apt search '^docker(-\w+)?$'
Sorting... Done
Full Text Search... Done
docker/xenial,now 1.5-1 amd64 [installed]
  System tray for KDE3/GNOME2 docklet applications

docker-compose/xenial-updates 1.8.0-2~16.04.1 all
  Punctual, lightweight development environments using Docker

docker-doc/xenial-updates 1.12.6-0ubuntu1~16.04.1 all
  Linux container runtime -- documentation

docker-registry/xenial 2.3.0~ds1-1 amd64
  Docker toolset to pack, ship, store, and deliver content
```

If you're happy with `2`, you can skip to [Environment](#environment).

#### Configure `python`

I used the vanilla `python` install with Ubuntu on Windows.

```bash
$ python --version
Python 2.7.12
```

If you've got other versions floating around, you probably already know how to handle dependencies. Docker recommends running a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) (bonus: [enforce `virtualenv` usage with `pip`](http://docs.python-guide.org/en/latest/dev/pip-virtualenv/)) to install its scripts. I have no interest in messing with that many environments, so everything after this assumes a global install via [`sudo -H`](https://www.sudo.ws/man/1.8.3/sudo.man.html#H).

#### Install `pip`

If you don't have `pip`, you'll need to get that first. From [the official repo](https://github.com/pypa/get-pip#usage),

```bash
curl https://bootstrap.pypa.io/get-pip.py | sudo -H python
```

#### Install `docker-compose`

Installing `docker-compose` by itself should resolve its dependences. If not, you can [install as a container](https://docs.docker.com/compose/install/#install-using-as-a-container).

```bash
sudo -H pip install docker-compose
```

#### Environment

Because the daemon is running on Windows, not via `bash.exe`, `docker(-compose)` won't be able to do things that require a Docker host.

```bash
$ docker version
Client:
 Version:      1.12.6
 API version:  1.24
 Go version:   go1.6.2
 Git commit:   78d1802
 Built:        Tue Jan 31 23:35:14 2017
 OS/Arch:      linux/amd64
Cannot connect to the Docker daemon. Is the docker daemon running on this host?
```

You can either specify the host every time, e.g.

```bash
$ docker -H 'tcp://0.0.0.0:2375' version
Client:
 Version:      1.12.6
 API version:  1.24
 Go version:   go1.6.2
 Git commit:   78d1802
 Built:        Tue Jan 31 23:35:14 2017
 OS/Arch:      linux/amd64

Server:
 Version:      17.06.2-ce
 API version:  1.30
 Go version:   go1.8.3
 Git commit:   cec0b72
 Built:        Tue Sep  5 19:59:47 2017
 OS/Arch:      windows/amd64
 Experimental: true
```

or you can export `DOCKER_HOST` because no one wants to type that much

```bash
$ DOCKER_HOST='tcp://0.0.0.0:2375' docker version
 # same as above
```

If you went the smart route and secured your installation, you can export the value from [the config file](https://docs.microsoft.com/en-us/virtualization/windowscontainers/manage-docker/configure-docker-daemon#configure-docker-with-configuration-file) in your `.whateverrc`. Otherwise you can just export the default:

```bash
$EDITOR ~/.whateverrc
```

```bash
export DOCKER_HOST='tcp://0.0.0.0.0:2375'
 # Better option
export DOCKER_HOST='tcp://not.default.value.from:docs'
```

Unfortunately, once it's in the config, you aren't going to get it back out programmatically.

```bash
$ ls -l /mnt/c/ProgramData/Docker/config
total 225
---------- 1 root root 196 Oct  1 13:45 daemon.json
-r-xr-xr-x 1 root root 244 Oct  1 13:00 key.json
```

```powershell
> dir $env:ProgramData\Docker\config

    Directory: C:\ProgramData\Docker\config


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        10/1/2017   1:45 PM            196 daemon.json
-a----        10/1/2017   1:00 PM            244 key.json
```

That means you'll have to update it in two places when it changes.

## Just Kidding

So far, I haven't been able to find a single image whose manifest includes the proper architecture. For example,

```bash
$ docker pull pick-a-common-Linux-distro
Using default tag: latest
latest: Pulling from library/pick-a-common-Linux-distro
no matching manifest for windows/amd64 in the manifest list entries

$ echo "FROM scratch" | docker build -
Sending build context to Docker daemon 2.048 kB
Step 1/1 : FROM scratch
Windows does not support FROM scratch
```

Basically, like many current WSL features, Docker support is just a really cool idea that doesn't work. Years of [embrace and extend](https://en.wikipedia.org/wiki/Embrace,_extend,_and_extinguish) have completely butchered generally accepted higher APIs (I dare you to `find` in PowerShell), so outside devs porting the containerization at a lower level can't have an easy job. Microsoft is actively embracing containerization, and they're working hard to extend it via Windows Containers using their own proprietary stack. Either you see where this is going or you like Microsoft.

Granted, it's getting a ton of attention and dev focus, so it will probably be implemented sooner than, say, `cron` support.

### Mostly

Right now, running Linux containers on Docker for Windows does work. However, the Windows configuration file is severely limited. Or, rather, Docker for Windows [cannot use `hosts`](https://github.com/docker/for-win/issues/453#issuecomment-276583573), which I find severely limiting. Barring some Windows voodoo that I don't know about, your only option for WSL access is to expose a widely-documented default port without TLS authentication. This really concerns me for a few reasons:

- WSL touches [the Windows kernel](https://blogs.msdn.microsoft.com/wsl/2016/04/22/windows-subsystem-for-linux-overview/)
- WSL runs [with Windows permissions](https://msdn.microsoft.com/en-us/commandline/wsl/user_support#permissions)
- `dockerd` elevates [to superuser/administrator](https://docs.docker.com/engine/security/security/#docker-daemon-attack-surface)
- Any attacker that knows [how to pivot](https://security.stackexchange.com/a/104265) is also, in my opinion, intelligent enough to probe widely published and unchangeable defaults

In my dev world, I often reformat and try a new environment. Rebuilding wouldn't be a big deal. However, I also keep basically all config ever in dev, because, unsurprisingly, that's where I develop it. It's already hard enough to stay safe in a Windows world without worrying about exposing myself in brand new ways (in all fairness, Windows Defender does a good job and I don't often leave trusted domains like Steam, GitHub, StackExchange, etc.)

In any production world, that's so dumb it doesn't even merit a detailed rebuttal. If you're running Docker for Windows in production, use PowerShell.

If you don't think any of these issues are a big deal (e.g. dev exists on an air-gapped network that also contains carefully vetted private registries updated via thumbdrive), expose the port. Honestly, the chances of you being attacked are at least as low as a credit reporting agency's database being compromised.

## Bespoke Solution

First, I want to point out how awesome the LinuxKit devs are. They're suffering through the pain of figuring out how to do this in Windows so we don't have to. Second, this is only bespoke right now, a few weeks after all the announcements. In two or three years, it might be default.

The [LinuxKit preview announcement](https://blog.docker.com/2017/09/preview-linux-containers-on-windows/) came with [the Linux Containers announcement](https://blogs.technet.microsoft.com/windowsserver/2017/09/13/sneak-peek-3-windows-server-version-1709-for-developers/). With minimal tooling, you can get it set up to run with more recent Windows Insider builds.

### Bespoke Requirements

- [Native Requirements](#native-requirements)
- [Windows Insider](https://insider.windows.com/en-us/): whatever the settings you choose, you'll need at least Windows 10 Insider Preview RC16281. I set content to "Active..." and was able to get RC16299 with pace "Slow". I was also able to manually check for updates instead of waiting for a build. Downloading and installing it was slow, though.

### A Word of Caution

Enabling Windows Insider changes a few things about your installation of Windows.

- You will send data to Microsoft. There's no option to opt out. If you're concerned about privacy (protip: you should be), you should take the time to read [the entire Program Agreement](https://insider.windows.com/en-us/program-agreement/).
- You will be forced to interact with ads while doing normal things like writing code. Again, there's no option to opt out. Because Windows Insider provides a fresh evaluation license, you don't even get to insist that you shouldn't be served ads because you paid for the copy of Windows you installed Windows Insider on. (Note I'm loosely grouping "free focus group" questions i.e. Feedback, one of which just popped over my editor, in with the normal Windows 10 ads for bloatware like Skype.)

### Inside Windows

#### Installation

I took the code from [the announcement](https://blog.docker.com/2017/09/preview-linux-containers-on-windows/) and tried to expand on it just a little bit.

```powershell
$progressPreference = "silentlyContinue";
 # Create directory for LinuxKit
mkdir $env:ProgramFiles\'Linux Containers';
 # Download and extract LinuxKit
Invoke-WebRequest -UseBasicParsing -OutFile linuxkit.zip https://github.com/friism/linuxkit/releases/download/preview-1/linuxkit.zip;
Expand-Archive linuxkit.zip -DestinationPath $env:ProgramFiles\'Linux Containers'\.;
rm linuxkit.zip;
 # Create a directory for the preview docker
mkdir $env:ProgramFiles\'Docker Preview';
 # Download (and change the name to remove path conflicts)
Invoke-WebRequest -UseBasicParsing -OutFile $env:ProgramFiles\'Docker Preview'\dockerd-preview.exe https://master.dockerproject.org/windows/x86_64/dockerd.exe;
 # Add the preview location to the user path
[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path',[System.EnvironmentVariableTarget]::User) + "$env:ProgramFiles\'Docker Preview';", [EnvironmentVariableTarget]::User);
```

If you're using an edge version (e.g. from [master](https://master.dockerproject.org)) of Docker for Windows, I'd hazard a guess that you don't need to run separate `dockerd`s and can see the features by setting `$env:LCOW_SUPPORTED`. I prefer discrete copies with distinct names for readability and maintenance reasons; your mileage may vary.

#### Bootstrapping

There's plenty that could be added to that script, but I didn't want to spend a Sunday off beating my head against my keyboard over Windows configuration (TypeScript issues, sure, but not Windows config). I started reading the docs on building a service out of commands and my eyes glazed over. Something like this in whichever of the million PowerShell profiles there are could do the trick instead:

```powershell
 # Define the LCOW environment variable
[Environment]::SetEnvironmentVariable('LCOW_SUPPORTED', 1, [EnvironmentVariableTarget]::User);
 # No one will ever guess the default port reversed
 & "$env:ProgramFiles\Docker Preview\dockerd-preview.exe" -D --experimental -H 'tcp://0.0.0.0:5732' --data-root C:\lcow
```

- I changed the host from a named pipe to TCP; I couldn't get WSL to recognize it. I've skimmed this issue [before](https://blog.wizardsoftheweb.pro/keepass-ssh/#usingmsyscygwin). I wouldn't be surprised if I had to read [this entire wall of docs](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365590.aspx) just to learn somewhere at the end that I can install a third-party application that will automatically configure them properly for me.
- `$env:LCOW_SUPPORTED` is vital. Without it, `dockerd-preview` will function exactly like `dockerd`, i.e. only works as a Linux host with scary defaults. Ideally, you should only have it set before and during `dockerd-preview` execution, and unset it afterward. I don't think the two systems (`dockerd` and `dockerd-preview`) conflict with each other, but, if this ordeal has taught me anything, it's better to not make assumptions about Windows applications.

#### Lifecycle

Unless you create a service, you'll have to be conscious of the lifecycle of both shells. I feel like an app capable of running each Windows shell will make your life much easier (I like [ConEmu](https://conemu.github.io/)). WSL [doesn't run in the background](https://wpdev.uservoice.com/forums/266908-command-prompt-console-bash-on-ubuntu-on-windo/suggestions/13653522-consider-enabling-cron-jobs-daemons-and-background), but you [can detach PowerShell](https://docs.microsoft.com/en-us/powershell/module/Microsoft.PowerShell.Management/Start-Process?view=powershell-5.1).

Another option I spent some time investigating is creating a [task](https://technet.microsoft.com/en-us/library/cc721871%28v%3Dws.11%29.aspx) triggered by [an event](https://technet.microsoft.com/en-us/library/cc766042%28v%3Dws.11%29.aspx) related [to the Docker service](https://blogs.technet.microsoft.com/askds/2011/09/26/advanced-xml-filtering-in-the-windows-event-viewer/). I was able to find a launch event when I bounced the service, but I haven't been able to find anything else. I'm personally wary of just running off the odd launch event, which was fired in my userspace while logged in, so I didn't pursue that.

A dependent service seems to be the best solution. I work with some rad dudes that grok Windows voodoo. If they have any suggestions this week, I'll add some updates (which means if you're still seeing this explanation I don't have updates).

### Inside WSL

Everything from [the native solution](#inside-wsl) thankfully still applies. If you set up a decent PowerShell script and read the host from another file (preferably one that won't get locked by Windows permissions when `dockerd-preview` starts), you can even read it directly in your `.whateverrc` instead of maintaining the same constant in two locations.

## Final Notes

I wouldn't use either of these solutions in a production environment. If Docker for Windows can safely run not-Windows images in PowerShell, that's a great solution for a ton of business applications, like easily running dev/test builds on a mandated-Windows office network. Natively connecting Docker to WSL is still (probably) a couple of years away. Plus there's the whole WSL malware exploit to address first. Adding a bespoke layer, no matter how awesome the devs are, makes the stack much too untenable. A better title for this post would have been "Why Docker for Windows is Scary Outside of PowerShell."

I'm currently running the bespoke solution on my personal dev box. I don't touch this machine very much outside of the weekends, so it might be some time before I really run it through the wringer. I was originally curious about adding some `Dockerfile`s to a repo for easy testing/demos. 12+ hours later, I've decided that I really need to spend the hour or so it will take me to finally install Linux on another drive for dev.

If you took something away from this, please take the time to pay it forward. The next time you discover an solution after reading a few threads that didn't have a good/non-deprecated solution, go back and share it in one or two them.
