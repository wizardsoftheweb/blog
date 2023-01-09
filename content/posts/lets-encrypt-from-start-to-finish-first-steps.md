---
title: "Let's Encrypt From Start to Finish: First Steps"
slug: "lets-encrypt-from-start-to-finish-first-steps"
date: "2017-12-31T18:00:00.000Z"
feature_image: "/images/2017/12/certbot-letsencrypt-nginx-apache-3.png"
author: "CJ Harries"
description: "This post is a catch-all for many things: good resources, certbot installation, and my approach to reusing Let's Encrypt config."
tags:
  - Let's Encrypt from Start to Finish
  - certbot
  - Let's Encrypt
  - NGINX
  - Apache
  - security
  - EFF
  - HSTS
  - HTTPS
  - TLS
  - OpenSSL
---

This is the second in a series of several posts on how to do way more than you really need to with Let's Encrypt, `certbot`, and a good server. I use all of these things regularly but I've never taken the time to take them apart, look at how they work, and spend hours in Google trying in vain to figure out how to put them back together. It was inspired by [a disturbing trend of ISP privacy violations](https://web.archive.org/web/20171214121709/http://forums.xfinity.com/t5/Customer-Service/Are-you-aware-Comcast-is-injecting-400-lines-of-JavaScript-into/td-p/3009551) and [the shocking regulatory capture of the US Federal Communications Commission](https://www.fcc.gov/document/fcc-takes-action-restore-internet-freedom).

This post is a catch-all for items that aren't closely related to the other major tasks. It begins with a list of very useful resources that provided a foundation for my research, followed by a general dependency list. Using `certbot`'s docs, it presents two methods to get `certbot` up and running. It concludes with my approach to reusing Let's Encrypt and `certbot` config.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#the-series-so-far)
- [Code](#code)
- [Note](#note)
- [Prototypical Resources](#prototypical-resources)
- [Requirements](#requirements)
- [`certbot`](#certbot)
- [Common Let's Encrypt Elements](#common-lets-encrypt-elements)
  - [Group and Directory Creation](#group-and-directory-creation)
  - [Share and Test Access](#share-and-test-access)
  - [Reuse Location](#reuse-location)
    - [Nginx](#nginx)
    - [Apache](#apache)
- [Before You Go](#before-you-go)
- [Legal Stuff](#legal-stuff)

## The Series so Far

1. [Overview](https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-overview)
2. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-first-steps" target="_blank">First Steps</a>
3. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-openssl-tuning" target="_blank">Tuning with OpenSSL</a>
4. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-useful-headers" target="_blank">Useful Headers</a>
5. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-your-first-cert" target="_blank">Generating and Testing a Cert</a>
6. <!--<a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-automation" target="_blank">-->Automating Renewals<!--</a>-->

Things that are still planned but probably not soon:

- Updating OpenSSL
- CSP Playground
- Vagrant Examples (don't hold your breath)

## Code

You can view the code related to this post [under the `post-02-first-steps` tag](//github.com/wizardsoftheweb/lets-encrypt-from-start-to-finish/tree/post-02-first-steps). If you're curious, you can also check out [my first draft](https://github.com/wizardsoftheweb/lets-encrypt-from-start-to-finish/blob/b425b6e601c9991c4918f569310e634ed5855afc/original-post.md).

## Note

I'm testing out some new tooling. This will be [`wotw-highlighter`'s shakedown run](https://github.com/wizardsoftheweb/wotw-highlighter). Let me know what you think about the syntax highlighting! I'm pretty excited because (no whammies) it should work well in AMP and normally.

## Prototypical Resources

I've been shuffling around copypasta Let's Encrypt config since, I think, the middle of last year (the company's only 19 months old, so it couldn't have been much longer than that). I don't have VCS versions of any of that, so unfortunately I can't point to a single article or book that shaped this. This list deserves highlighting if for no other reason than I had the link saved and totally forgot where I was going to use it.

- [This Gist](https://gist.github.com/cecilemuller/a26737699a7e70a7093d4dc115915de8) is a great resource to snag a stable config you can put almost anywhere.
- [This Gist](https://gist.github.com/AndreiD/3d4b36c58fa59c8ec1ef98276eacb636) is another great resouce. I believe I've had portions of it in production at some point.
- [Qualys SSL Labs](https://www.ssllabs.com/) is the SSL gold standard. If you don't have a good Qualys rating, you don't have a good config.
- Mozilla provides [a great generator](https://mozilla.github.io/server-side-tls/ssl-config-generator/) that's probably responsible for a fair chunk of the articles out there now.

## Requirements

- [OpenSSL](https://www.openssl.org/): This entire series is written around `openssl` usage. As far as I know, it's necessary for any of the common webservers. If you can't get OpenSSL, there's a really good chance you shouldn't be serving from your machine.
- A web server:
  - [Nginx](https://www.nginx.com/): I'd recommend [at least `v1.12`](https://www.nginx.com/blog/nginx-1-12-1-13-released/) if possible. I can't point to specific sources, but I remember reading something about that at some point during my research this weekend. It is almost a year old by now.
  - [Apache](http://www.apache.org/): To follow a majority of the instructions I was able to find easily, you'll need at least `v2.4`  [to access `mod_socache_shmcb`](https://httpd.apache.org/docs/2.4/mod/mod_socache_shmcb.html). The alternatives I remember were somehow even more opaque than `shmcb`, so I avoided them.
  - You're on your own with something else. You can most likely figure out what you need to know with these examples, your server's docs, and Google.

## `certbot`

You can follow distro-specific instructions [via the official docs](https://certbot.eff.org/docs/install.html) for [almost everything](https://certbot.eff.org/docs/install.html#operating-system-packages). [The generic `wget` method](https://certbot.eff.org/docs/install.html#certbot-auto) usually provides the most current version; however, it's usually a better idea to wait for an official package.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> wget https://dl.eff.org/certbot-auto<br><span class="gp" style="color:#66d9ef">$</span> wget -N https://dl.eff.org/certbot-auto.asc<br><span class="gp" style="color:#66d9ef">$</span> gpg2 --recv-key A2CFB51FA275A7286234E7B24D17C995CD9775F2<br><span class="gp" style="color:#66d9ef">$</span> gpg2 --trusted-key 4D17C995CD9775F2 --verify certbot-auto.asc certbot-auto<br><span class="gp" style="color:#66d9ef">$</span> chmod a+x ./certbot-auto<br><span class="gp" style="color:#66d9ef">$</span> sudo mv ./certbot-auto /usr/bin/certbot-auto<br></pre></div>
</td></tr></table>

## Common Let's Encrypt Elements

Let's Encrypt works by creating challenges on the server and verifying them through an external request. To simplify things, it's a good idea to create a centralized location for everything. With one or two sites, it's not a huge deal; it's very nice the more sites your server supports.

### Group and Directory Creation

I prefer [the `/srv` directory](http://refspecs.linuxfoundation.org/FHS_2.3/fhs-2.3.html#SRVDATAFORSERVICESPROVIDEDBYSYSTEM) over [the `/var` directory](http://refspecs.linuxfoundation.org/FHS_2.3/fhs-2.3.html#THEVARHIERARCHY), YMMV. Also [`exa` isn't vanilla](https://the.exa.website/).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo groupadd letsencrypt<br><span class="gp" style="color:#66d9ef">$</span> sudo mkdir -p /srv/www/letsencrypt/.well-known/acme-challenge<br><span class="gp" style="color:#66d9ef">$</span> sudo chown -R :letsencrypt /srv/www/letsencrypt<br><span class="gp" style="color:#66d9ef">$</span> sudo chmod -R g+rwx /srv/www/letsencrypt<br><span class="gp" style="color:#66d9ef">$</span> exa --all --long --header --group-directories-first --group  --time-style long-iso --tree /srv<br><span class="go" style="color:#888">Permissions Size User Group       Date Modified    Name</span><br><span class="go" style="color:#888">drwxr-xr-x@    - root root        2017-12-24 01:06 /srv</span><br><span class="go" style="color:#888">drwxr-xr-x     - root root        2017-12-24 00:57 └── www</span><br><span class="go" style="color:#888">drwxrwxr-x     - root letsencrypt 2017-12-24 01:41    └── letsencrypt</span><br><span class="go" style="color:#888">drwxrwxr-x     - root letsencrypt 2017-12-24 01:37       └── .well-known</span><br><span class="go" style="color:#888">drwxrwxr-x     - root letsencrypt 2017-12-24 00:57          └── acme-challenge</span><br></pre></div>
</td></tr></table>

### Share and Test Access

You can then add your server's service account to the `letsencrypt` group.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo usermod -G letsencrypt nginx<br><span class="go" style="color:#888">or</span><br><span class="gp" style="color:#66d9ef">$</span> sudo usermod -G letsencrypt apache<br><span class="go" style="color:#888">or</span><br><span class="gp" style="color:#66d9ef">$</span> sudo usermod -G letsencrypt safer_single_purpose_named_service_account<br></pre></div>
</td></tr></table>

To make sure permissions work as intended, `touch` one of the new directories as the service account. You'll most likely need to specify a shell, as service accounts typically don't have login shells to limit outside access. If yours does expose a shell, you might think about changing that.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> getent passwd nginx <span class="p">|</span> cut -d <span class="s1" style="color:#e6db74">':'</span> -f <span class="m" style="color:#ae81ff">7</span><br><span class="go" style="color:#888">/sbin/nologin</span><br><span class="gp" style="color:#66d9ef">$</span> sudo su -s /bin/bash -c <span class="s2" style="color:#e6db74">"touch /srv/www/letsencrypt/.well-known"</span> good_service_account <span class="o" style="color:#f92672">||</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"whoops"</span><br><span class="gp" style="color:#66d9ef">$</span> sudo su -s /bin/bash -c <span class="s2" style="color:#e6db74">"touch /srv/www/letsencrypt/.well-known"</span> bad_service_account <span class="o" style="color:#f92672">||</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"whoops"</span><br><span class="go" style="color:#888">touch: setting times of '/srv/www/letsencrypt/.well-known/': Permission denied</span><br><span class="go" style="color:#888">whoops</span><br></pre></div>
</td></tr></table>

### Reuse Location

We'll also want to save a snippet exposing this structure.

I use `/etc/<server>/common/` for my shared config, YMMV.

#### Nginx

This is just a simple location block.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/nginx/common/letsencrypt.conf</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">location</span> <span class="s" style="color:#e6db74">^~</span> <span class="s" style="color:#e6db74">/.well-known/acme-challenge/</span> <span class="p">{</span><br>    <span class="kn" style="color:#f92672">default_type</span> <span class="s" style="color:#e6db74">"text/plain"</span><span class="p">;</span><br>    <span class="kn" style="color:#f92672">root</span> <span class="s" style="color:#e6db74">/srv/www/letsencrypt</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

I've got at least three servers running a variant of this right now.

#### Apache

From [the Let's Encrypt forums](https://community.letsencrypt.org/t/apache-multidomain-webroot/10663/2),

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/httpd/common/letsencrypt.conf</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6
7</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">Alias</span> /.well-known/acme-challenge/ <span class="sx" style="color:#e6db74">/srv/www/letsencrypt/.well-known/acme-challenge/</span><br><span class="nt" style="color:#f92672">&lt;Directory</span> <span class="s" style="color:#e6db74">"/srv/www/letsencrypt/.well-known/acme-challenge/"</span><span class="nt" style="color:#f92672">&gt;</span><br>    <span class="nb" style="color:#f8f8f2">Options</span> <span class="k" style="color:#66d9ef">None</span><br>    <span class="nb" style="color:#f8f8f2">AllowOverride</span> <span class="k" style="color:#66d9ef">None</span><br>    <span class="nb" style="color:#f8f8f2">ForceType</span> text/plain<br>    <span class="nb" style="color:#f8f8f2">RedirectMatch</span> <span class="m" style="color:#ae81ff">404</span> <span class="s2" style="color:#e6db74">"^(?!/\.well-known/acme-challenge/[\w-]{43}$)"</span><br><span class="nt" style="color:#f92672">&lt;/Directory&gt;</span><br></pre></div>
</td>
</tr>
</table>

I have not tested this.

## Before You Go

Let's Encrypt is a fantastic service. If you like what they do, i.e. appreciate how accessible they've made secure web traffic, [please donate](https://letsencrypt.org/donate/). [EFF's `certbot`](https://certbot.eff.org/) is what powers my site (and basically anything I work on these days); consider [buying them a beer](https://supporters.eff.org/donate/support-lets-encrypt) (it's really just a donate link but you catch my drift).

## Legal Stuff

I'm still pretty new to the whole CYA legal thing. I really like everything I've covered here, and I've done my best to respect individual legal policies. If I screwed something up, please send me an email ASAP so I can fix it.

- The Electronic Frontier Foundation and `certbot` are covered by [EFF's generous copyright](https://www.eff.org/copyright). As far as I know, it's all under [CC BY 3.0 US](http://creativecommons.org/licenses/by/3.0/us/). I made a few minor tweaks to build the banner image but tried to respect the trademark. I don't know who the `certbot` logo artist is but I really wish I did because it's a fantastic piece of art.
- Let's Encrypt [is trademarked](https://letsencrypt.org/trademarks/). Its logo uses [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). I made a few minor tweaks to build the banner image but tried to respect the trademark.
- I didn't find anything definitive (other than EULAs) covering Nginx, which doesn't mean it doesn't exist. Assets were taken [from its press page](https://www.nginx.com/press/).
- Apache content was sourced from [its press page](https://www.apache.org/foundation/press/kit/). It provides [a full trademark policy](http://www.apache.org/foundation/marks/).
