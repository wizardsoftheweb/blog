---
title: "Let's Encrypt from Start to Finish: Automating Renewals"
slug: "lets-encrypt-from-start-to-finish-automating-renewals"
date: "2018-01-05T00:00:00.000Z"
feature_image: "/images/2017/12/certbot-letsencrypt-nginx-apache-7.png"
author: "CJ Harries"
description: "This post looks at several different ways to automate cert renewal, including cron and systemd options. You'll want to be able to send email from your server."
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
<!-- markdownlint-disable MD037 -->

This is the sixth in a series of several posts on how to do way more than you really need to with Let's Encrypt, `certbot`, and a good server. I use all of these things regularly but I've never taken the time to take them apart, look at how they work, and spend hours in Google trying in vain to figure out how to put them back together. It was inspired by [a disturbing trend of ISP privacy violations](https://web.archive.org/web/20171214121709/http://forums.xfinity.com/t5/Customer-Service/Are-you-aware-Comcast-is-injecting-400-lines-of-JavaScript-into/td-p/3009551) and [the shocking regulatory capture of the US Federal Communications Commission](https://www.fcc.gov/document/fcc-takes-action-restore-internet-freedom).

This post looks at several different ways to automate cert renewal. I tried to cater to everyone by including `cron` and `systemd` options. If you don't have your server set up to send emails, you might want to do that first.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#the-series-so-far)
- [Code](#code)
- [Note](#note)
- [Automating Renewals](#automating-renewals)
- [Hooks](#hooks)
  - [Nginx](#nginx)
  - [Apache](#apache)
- [Scripting a Renewal](#scripting-a-renewal)
  - [`at`](#at)
    - [Block Scheduling](#block-scheduling)
    - [Random Scheduling](#random-scheduling)
- [Scheduling the Renewal](#scheduling-the-renewal)
  - [`cron`](#cron)
  - [`systemd`](#systemd)
- [Before You Go](#before-you-go)
- [Legal Stuff](#legal-stuff)

## The Series so Far

1. [Overview](https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-overview)
2. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-first-steps" target="_blank">First Steps</a>
3. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-openssl-tuning" target="_blank">Tuning with OpenSSL</a>
4. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-useful-headers" target="_blank">Useful Headers</a>
5. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-your-first-cert" target="_blank">Generating and Testing a Cert</a>
6. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-automation" target="_blank">Automating Renewals</a>

Things that are still planned but probably not soon:

- Updating OpenSSL
- CSP Playground
- Vagrant Examples (don't hold your breath)

## Code

You can view the code related to this post [under the `post-06-automation` tag](//github.com/wizardsoftheweb/lets-encrypt-from-start-to-finish/tree/post-06-automation). If you're curious, you can also check out [my first draft](https://github.com/wizardsoftheweb/lets-encrypt-from-start-to-finish/blob/b425b6e601c9991c4918f569310e634ed5855afc/original-post.md).

## Note

I'm testing out some new tooling. This will be [`wotw-highlighter`'s shakedown run](https://github.com/wizardsoftheweb/wotw-highlighter). Let me know what you think about the syntax highlighting! I'm pretty excited because (no whammies) it should work well in AMP and normally.

I wrote the majority of the Apache examples with `httpd` in mind, i.e. from a RHEL perspective. If you instead use `apache2`, most of the stuff should still work, albeit maybe just a little bit different.

## Automating Renewals

Now that everything's installed and in place, we've got to think about keeping the cert current. Let's Encrypt certs have [a 90-day lifetime](https://letsencrypt.org/2015/11/09/why-90-days.html), which is substantially shorter than a typical commercial cert. `certbot` is built to handle automated renewals and can update everything in place without any intervention on your part.

If you try running `certbot renew` right now, you'll probably get something like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo certbot renew<br><span class="go" style="color:#888">Saving debug log to /var/log/letsencrypt/letsencrypt.log</span><br><br><span class="go" style="color:#888">-------------------------------------------------------------------------------</span><br><span class="go" style="color:#888">Processing /etc/letsencrypt/renewal/example.com.conf</span><br><span class="go" style="color:#888">-------------------------------------------------------------------------------</span><br><span class="go" style="color:#888">Cert not yet due for renewal</span><br><br><span class="go" style="color:#888">-------------------------------------------------------------------------------</span><br><br><span class="go" style="color:#888">The following certs are not due for renewal yet:</span><br><span class="go" style="color:#888">  /etc/letsencrypt/live/example.com.pro/fullchain.pem (skipped)</span><br><span class="go" style="color:#888">No renewals were attempted.</span><br><span class="go" style="color:#888">-------------------------------------------------------------------------------</span><br></pre></div>
</td></tr></table>

While the cert isn't due for renewal, we can actually test the renewal process like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> certbot renew --dry-run<br><span class="go" style="color:#888">Saving debug log to /var/log/letsencrypt/letsencrypt.log</span><br><br><span class="go" style="color:#888">-------------------------------------------------------------------------------</span><br><span class="go" style="color:#888">Processing /etc/letsencrypt/renewal/example.com.conf</span><br><span class="go" style="color:#888">-------------------------------------------------------------------------------</span><br><span class="go" style="color:#888">Cert not due for renewal, but simulating renewal for dry run</span><br><span class="go" style="color:#888">Plugins selected: Authenticator webroot, Installer None</span><br><span class="go" style="color:#888">Starting new HTTPS connection (1): acme-staging.api.letsencrypt.org</span><br><span class="go" style="color:#888">Renewing an existing certificate</span><br><span class="go" style="color:#888">Performing the following challenges:</span><br><span class="go" style="color:#888">http-01 challenge for example.com</span><br><span class="go" style="color:#888">http-01 challenge for www.example.com</span><br><span class="go" style="color:#888">Waiting for verification...</span><br><span class="go" style="color:#888">Cleaning up challenges</span><br><span class="go" style="color:#888">Dry run: skipping deploy hook command</span><br><br><span class="go" style="color:#888">-------------------------------------------------------------------------------</span><br><span class="go" style="color:#888">new certificate deployed without reload, fullchain is</span><br><span class="go" style="color:#888">/etc/letsencrypt/live/example.com/fullchain.pem</span><br><span class="go" style="color:#888">-------------------------------------------------------------------------------</span><br><br><span class="go" style="color:#888">-------------------------------------------------------------------------------</span><br><span class="go" style="color:#888">** DRY RUN: simulating 'certbot renew' close to cert expiry</span><br><span class="go" style="color:#888">**          (The test certificates below have not been saved.)</span><br><br><span class="go" style="color:#888">Congratulations, all renewals succeeded. The following certs have been renewed:</span><br><span class="go" style="color:#888">  /etc/letsencrypt/live/example.com/fullchain.pem (success)</span><br><span class="go" style="color:#888">** DRY RUN: simulating 'certbot renew' close to cert expiry</span><br><span class="go" style="color:#888">**          (The test certificates above have not been saved.)</span><br><span class="go" style="color:#888">-------------------------------------------------------------------------------</span><br></pre></div>
</td></tr></table>

This is useful to make sure everything's in place for automation.

## Hooks

You might have noticed the `Dry run: skipping deploy hook command` line in the output. `certbot` can run commands or scripts at several stages in its lifecycle. You can either add hooks via flags every time you `renew`, or you can offload them to executable scripts in `/etc/letsencrypt/renewal-hooks`.

For this example, all I'd like to do is restart the server process following successful renewals. Assuming we've got a local script capable of that called `server-reboot`, this should add it to `certbot`'s pipeline.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo cp ./server-reboot /var/letsencrypt/renewal-hooks/deploy<br><span class="gp" style="color:#66d9ef">$</span> sudo chmod +x /var/letsencrypt/renewal-hooks/deploy<br></pre></div>
</td></tr></table>

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/var/letsencrypt/renewal-hooks/deploy/server-reboot</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><br>nginx -t <span class="o" style="color:#f92672">&amp;&amp;</span> systemctl restart nginx<br></pre></div>
</td>
</tr>
</table>

### Apache

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/var/letsencrypt/renewal-hooks/deploy/server-reboot</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><br>apachectl -t <span class="o" style="color:#f92672">&amp;&amp;</span> systemctl restart apachectl<br></pre></div>
</td>
</tr>
</table>

## Scripting a Renewal

The official documentation suggests running an automated renewal task at least twice a day (e.g. [the CentOS instructions](https://certbot.eff.org/#centosrhel7-nginx); scroll down). `certbot` also asks that you run it at a random minute. To make things easier later, let's isolate our renew command:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/sbin/certbot-renew-everything</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><br><span class="c1" style="color:#75715e"># Create a temporary file for STDERR</span><br><span class="nv" style="color:#f8f8f2">ERROR_LOG</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span>mktemp<span class="k" style="color:#66d9ef">)</span><br><br><span class="c1" style="color:#75715e"># Renew, ignoring STDOUT and piping STDERR to the temp file</span><br>/usr/bin/certbot renew &gt; /dev/null <span class="m" style="color:#ae81ff">2</span>&gt; <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$ERROR_LOG</span><span class="s2" style="color:#e6db74">"</span><br><br><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> -s <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$ERROR_LOG</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    mail -s <span class="s2" style="color:#e6db74">"certbot Renewal Issue"</span> your@email.address &lt; <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$ERROR_LOG</span><span class="s2" style="color:#e6db74">"</span><br><span class="k" style="color:#66d9ef">fi</span><br><br>rm -rf <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$ERROR_LOG</span><span class="s2" style="color:#e6db74">"</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo chmod <span class="s1" style="color:#e6db74">'u=rwx,go='</span> /sbin/certbot-renew-everything<br></pre></div>
</td></tr></table>

Adding extra flags is straightforward. `renew` only exits [with a nonzero code if the renewal failed](https://github.com/certbot/certbot/blob/v0.20.0/docs/using.rst#modifying-the-renewal-configuration-file) (paragraph right above the link), meaning the skipped renewals we saw earlier don't generate any traffic. They do, however, send many things to `STDOUT`, which is enough to trigger `cron`'s mail action. The `quiet` flag suppresses `STDOUT`, so you won't get multiple emails a day letting you know `certbot` did nothing. If you're into that you don't have to use it.

Most of the solutions I've seen for the randomness do some cool stuff with advanced PRNG and then pass the result to `sleep`. There's nothing wrong with `sleep` if [you're pausing tasks that don't actually need to run](http://man7.org/linux/man-pages/man3/sleep.3.html). Anything that kills the thread kills the task.

### `at`

`at` provides a much better solution because, [via `man at`](http://man7.org/linux/man-pages/man1/at.1p.html),

> The `at` utility shall read commands from standard input and group them together as an `at-job`, to be executed at a later time.

In other words, `at` is a single-execution `cron`. It manages an `at` queue, most likely accessible via `atq`, which means random power failure or accidentally nuking a remote session won't kill the delayed task. Of course that means some setup is required:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo yum install -y at<br><span class="gp" style="color:#66d9ef">$</span> sudo pkill -f atd<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl <span class="nb" style="color:#f8f8f2">enable</span> atd<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl start atd<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl status atd<br><span class="go" style="color:#888">● atd.service - Job spooling tools</span><br><span class="go" style="color:#888">   Loaded: loaded (/usr/lib/systemd/system/atd.service; enabled; vendor preset: enabled)</span><br><span class="go" style="color:#888">   Active: active (running) since Sun 2017-12-17 11:17:15 UTC; 4s ago</span><br><span class="go" style="color:#888"> Main PID: 47 (atd)</span><br><span class="go" style="color:#888">   CGroup: /system.slice/atd.service</span><br><span class="go" style="color:#888">           4747 /usr/sbin/atd -f</span><br><br><span class="go" style="color:#888">Dec 17 11:17:15 examplehost systemd[1]: Started Job spooling tools.</span><br><span class="go" style="color:#888">Dec 17 11:17:15 examplehost systemd[1]: Starting Job spooling tools...</span><br></pre></div>
</td></tr></table>

- `at` is the command itself
- `atd` is the `at` daemon
- `atq` is an alias for listing `at` jobs
- `atrm` is an alias for removing `at` jobs

#### Block Scheduling

The simplest `at` solution triggers a script like this `NUMBER_OF_DAILY_RUNS` times per day.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/sbin/certbot-renew-everything</div></td>
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
24</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><br><span class="nv" style="color:#f8f8f2">TASK_FILE</span><span class="o" style="color:#f92672">=</span>/sbin/certbot-renew-everything<br><br><span class="c1" style="color:#75715e"># This assumes you've got some control over the machine's at queues</span><br><span class="nv" style="color:#f8f8f2">AT_QUEUE</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"z"</span><br><br><span class="c1" style="color:#75715e"># The number of times we want the script to run in 24 hours</span><br><span class="nv" style="color:#f8f8f2">NUMBER_OF_DAILY_RUNS</span><span class="o" style="color:#f92672">=</span><span class="m" style="color:#ae81ff">2</span><br><br><span class="c1" style="color:#75715e"># The calculated maximum number of minutes per block</span><br><span class="nv" style="color:#f8f8f2">MAX_MINUTES</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$((</span> <span class="m" style="color:#ae81ff">60</span> <span class="o" style="color:#f92672">*</span> <span class="m" style="color:#ae81ff">24</span> <span class="o" style="color:#f92672">/</span> <span class="nv" style="color:#f8f8f2">$NUMBER_OF_DAILY_RUNS</span> <span class="k" style="color:#66d9ef">))</span><br><br><span class="c1" style="color:#75715e"># Create 7 pseudorandom bytes, output as hex</span><br><span class="nv" style="color:#f8f8f2">PRN_HEX</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span>openssl rand -hex <span class="m" style="color:#ae81ff">7</span><span class="k" style="color:#66d9ef">)</span><br><span class="c1" style="color:#75715e"># The hex is converted to base 10</span><br><span class="nv" style="color:#f8f8f2">PRN_TEN</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$((</span> <span class="m" style="color:#ae81ff">16#</span><span class="nv" style="color:#f8f8f2">$PRN_HEX</span> <span class="k" style="color:#66d9ef">))</span><br><span class="c1" style="color:#75715e"># Finally, PRN_TEN is taken mod MAX_MINUTES to fit the domain</span><br><span class="nv" style="color:#f8f8f2">PRN_MIN</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$((</span> <span class="nv" style="color:#f8f8f2">$PRN_TEN</span> <span class="o" style="color:#f92672">%</span> <span class="nv" style="color:#f8f8f2">$MAX_MINUTES</span> <span class="k" style="color:#66d9ef">))</span><br><br><span class="c1" style="color:#75715e"># Only execute if this queue is empty</span><br><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> -z <span class="s2" style="color:#e6db74">"</span><span class="k" style="color:#66d9ef">$(</span> atq -q <span class="nv" style="color:#f8f8f2">$AT_QUEUE</span> <span class="k" style="color:#66d9ef">)</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    at <span class="s2" style="color:#e6db74">"now +</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">PRN_MIN</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74"> min"</span> -q <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$AT_QUEUE</span><span class="s2" style="color:#e6db74">"</span> -f <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$TASK_FILE</span><span class="s2" style="color:#e6db74">"</span><br><span class="k" style="color:#66d9ef">fi</span><br></pre></div>
</td>
</tr>
</table>

#### Random Scheduling

A slightly more involved `at` script calls both the task and itself.

Update 2019/05: Mischa Fiala (@mikfiala) pointed out my original script didn't work. This updated version should.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/sbin/at-random-renewal</div></td>
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
76</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="ch" style="color:#75715e">#!/bin/bash</span><br><br><span class="c1" style="color:#75715e"># Store original noclobber</span><br><span class="nv" style="color:#f8f8f2">ORIGINAL_NOCLOBBER</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span> <span class="nb" style="color:#f8f8f2">set</span> +o <span class="p">|</span> grep noclobber <span class="k" style="color:#66d9ef">)</span><br><span class="nb" style="color:#f8f8f2">set</span> +o noclobber<br><br><span class="c1" style="color:#75715e"># Pull out the PRNG into a function</span><br><span class="k" style="color:#66d9ef">function</span> openssl_prng <span class="o" style="color:#f92672">{</span><br>    <span class="nv" style="color:#f8f8f2">MAX</span><span class="o" style="color:#f92672">=</span><span class="nv" style="color:#f8f8f2">$1</span><br>    <span class="c1" style="color:#75715e"># Create 7 pseudorandom bytes, output as hex</span><br>    <span class="nv" style="color:#f8f8f2">PRN_HEX</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span>openssl rand -hex <span class="m" style="color:#ae81ff">7</span><span class="k" style="color:#66d9ef">)</span><br>    <span class="c1" style="color:#75715e"># The hex is converted to base 10</span><br>    <span class="nv" style="color:#f8f8f2">PRN_TEN</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$((</span> <span class="m" style="color:#ae81ff">16#</span><span class="nv" style="color:#f8f8f2">$PRN_HEX</span> <span class="k" style="color:#66d9ef">))</span><br>    <span class="c1" style="color:#75715e"># Finally, PRN_TEN is taken mod MAX to fit the domain</span><br>    <span class="nv" style="color:#f8f8f2">PRN_MIN</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$((</span> <span class="nv" style="color:#f8f8f2">$PRN_TEN</span> <span class="o" style="color:#f92672">%</span> <span class="nv" style="color:#f8f8f2">$MAX</span> <span class="k" style="color:#66d9ef">))</span><br>    <span class="k" style="color:#66d9ef">echo</span> <span class="nv" style="color:#f8f8f2">$PRN_MIN</span><br><span class="o" style="color:#f92672">}</span><br><br><span class="c1" style="color:#75715e"># Path to renew task</span><br><span class="nv" style="color:#f8f8f2">TASK_FILE</span><span class="o" style="color:#f92672">=</span>/sbin/certbot-renew-everything<br><br><span class="c1" style="color:#75715e"># This assumes you've got some control over the machine's at queues</span><br><span class="nv" style="color:#f8f8f2">SCRIPT_QUEUE</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"y"</span><br><span class="nv" style="color:#f8f8f2">TASK_QUEUE</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"z"</span><br><br><span class="c1" style="color:#75715e"># A hard cap on run count to account for unpleasant randomness</span><br><span class="nv" style="color:#f8f8f2">ABSOLUTE_RUN_COUNT_MAX</span><span class="o" style="color:#f92672">=</span><span class="m" style="color:#ae81ff">10</span><br><br><span class="c1" style="color:#75715e"># The number of minutes in 24 hours</span><br><span class="nv" style="color:#f8f8f2">MINUTES_IN_TWENTY_FOUR_HOURS</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$((</span> <span class="m" style="color:#ae81ff">24</span> <span class="o" style="color:#f92672">*</span> <span class="m" style="color:#ae81ff">60</span> <span class="k" style="color:#66d9ef">))</span><br><br><span class="c1" style="color:#75715e"># When to schedule the next renew run</span><br><span class="nv" style="color:#f8f8f2">TASK_SLEEP_MINS</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span> openssl_prng <span class="nv" style="color:#f8f8f2">$MINUTES_IN_TWENTY_FOUR_HOURS</span> <span class="k" style="color:#66d9ef">)</span><br><span class="c1" style="color:#75715e"># Delay scheduling the next self run by an arbitrary amount</span><br><span class="nv" style="color:#f8f8f2">SCRIPT_SLEEP_MINS</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$((</span> <span class="nv" style="color:#f8f8f2">$TASK_SLEEP_MINS</span> <span class="o" style="color:#f92672">+</span> <span class="m" style="color:#ae81ff">30</span> <span class="k" style="color:#66d9ef">))</span><br><br><span class="c1" style="color:#75715e"># Directory to hold active files</span><br><span class="nv" style="color:#f8f8f2">RUN_DIR</span><span class="o" style="color:#f92672">=</span>/var/run/certbot-renew<br>mkdir -p <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$RUN_DIR</span><span class="s2" style="color:#e6db74">"</span><br><span class="c1" style="color:#75715e"># File to store current date and run count</span><br><span class="nv" style="color:#f8f8f2">RUN_COUNT_FILE</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$RUN_DIR</span><span class="s2" style="color:#e6db74">/count"</span><br>touch <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$RUN_COUNT_FILE</span><span class="s2" style="color:#e6db74">"</span><br><span class="c1" style="color:#75715e"># Using awk, load the file</span><br><span class="c1" style="color:#75715e">#   * If the dates match, use the loaded run count</span><br><span class="c1" style="color:#75715e">#   * If not, reset the count</span><br><span class="nv" style="color:#f8f8f2">RUN_COUNT</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span> awk <span class="s1" style="color:#e6db74">'{ if ($1 == strftime("%F")) { print $2; } else { print 0; } }'</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$RUN_COUNT_FILE</span><span class="s2" style="color:#e6db74">"</span> <span class="k" style="color:#66d9ef">)</span><br><br><span class="c1" style="color:#75715e"># Get the absolute path to this file</span><br><span class="nv" style="color:#f8f8f2">RUN_SCRIPT_PATH_FILE</span><span class="o" style="color:#f92672">=</span><span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$RUN_DIR</span><span class="s2" style="color:#e6db74">/path"</span><br>touch <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$RUN_SCRIPT_PATH_FILE</span><span class="s2" style="color:#e6db74">"</span><br><span class="nv" style="color:#f8f8f2">THIS_SCRIPT</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$(</span> <span class="o" style="color:#f92672">[[</span> -s <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$RUN_SCRIPT_PATH_FILE</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span> <span class="o" style="color:#f92672">&amp;&amp;</span> cat <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$RUN_SCRIPT_PATH_FILE</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">||</span> readlink -m <span class="nv" style="color:#f8f8f2">$0</span><span class="k" style="color:#66d9ef">)</span><br>rm -rf <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$RUN_SCRIPT_PATH_FILE</span><span class="s2" style="color:#e6db74">"</span><br><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> -e <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$THIS_SCRIPT</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$THIS_SCRIPT</span><span class="s2" style="color:#e6db74">"</span> &gt;<span class="p">|</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$RUN_SCRIPT_PATH_FILE</span><span class="s2" style="color:#e6db74">"</span><br><span class="k" style="color:#66d9ef">else</span><br>    <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"Unable to find self-reference"</span> <span class="p">|</span> systemd-cat -t certbot-renew-everything<br>    <span class="nb" style="color:#f8f8f2">eval</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$ORIGINAL_NOCLOBBER</span><span class="s2" style="color:#e6db74">"</span><br>    <span class="nb" style="color:#f8f8f2">exit</span> <span class="m" style="color:#ae81ff">1</span><br><span class="k" style="color:#66d9ef">fi</span><br><br><span class="c1" style="color:#75715e"># Check that RUN_COUNT is low enough and TASK_QUEUE is empty</span><br><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$RUN_COUNT</span><span class="s2" style="color:#e6db74">"</span> -lt <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$ABSOLUTE_RUN_COUNT_MAX</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="o" style="color:#f92672">[[</span> -z <span class="s2" style="color:#e6db74">"</span><span class="k" style="color:#66d9ef">$(</span> atq -q <span class="nv" style="color:#f8f8f2">$TASK_QUEUE</span> <span class="k" style="color:#66d9ef">)</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    <span class="c1" style="color:#75715e"># Increment RUN_COUNT</span><br>    <span class="nv" style="color:#f8f8f2">RUN_COUNT</span><span class="o" style="color:#f92672">=</span><span class="k" style="color:#66d9ef">$((</span> <span class="nv" style="color:#f8f8f2">$RUN_COUNT</span> <span class="o" style="color:#f92672">+</span> <span class="m" style="color:#ae81ff">1</span> <span class="k" style="color:#66d9ef">))</span><br>    <span class="c1" style="color:#75715e"># Schedule a renew and run count update</span><br>    <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"source </span><span class="nv" style="color:#f8f8f2">$TASK_FILE</span><span class="s2" style="color:#e6db74"> &amp;&amp; (date \"+%F </span><span class="nv" style="color:#f8f8f2">$RUN_COUNT</span><span class="s2" style="color:#e6db74">\" &gt;| </span><span class="nv" style="color:#f8f8f2">$RUN_COUNT_FILE</span><span class="s2" style="color:#e6db74">)"</span> <span class="p">|</span> at <span class="s2" style="color:#e6db74">"now +</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">TASK_SLEEP_MINS</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74"> min"</span> -q <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$TASK_QUEUE</span><span class="s2" style="color:#e6db74">"</span><br><span class="k" style="color:#66d9ef">fi</span><br><br><span class="c1" style="color:#75715e"># Check that SCRIPT_QUEUE is empty</span><br><span class="k" style="color:#66d9ef">if</span> <span class="o" style="color:#f92672">[[</span> -z <span class="s2" style="color:#e6db74">"</span><span class="k" style="color:#66d9ef">$(</span> atq -q <span class="nv" style="color:#f8f8f2">$SCRIPT_QUEUE</span> <span class="k" style="color:#66d9ef">)</span><span class="s2" style="color:#e6db74">"</span> <span class="o" style="color:#f92672">]]</span><span class="p">;</span> <span class="k" style="color:#66d9ef">then</span><br>    <span class="c1" style="color:#75715e"># Schedule a new self run</span><br>    at <span class="s2" style="color:#e6db74">"now +</span><span class="si" style="color:#e6db74">${</span><span class="nv" style="color:#f8f8f2">SCRIPT_SLEEP_MINS</span><span class="si" style="color:#e6db74">}</span><span class="s2" style="color:#e6db74"> min"</span> -q <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$SCRIPT_QUEUE</span><span class="s2" style="color:#e6db74">"</span> -f <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$THIS_SCRIPT</span><span class="s2" style="color:#e6db74">"</span><br><span class="k" style="color:#66d9ef">fi</span><br><br><span class="c1" style="color:#75715e"># Revert to original noclobber</span><br><span class="nb" style="color:#f8f8f2">eval</span> <span class="s2" style="color:#e6db74">"</span><span class="nv" style="color:#f8f8f2">$ORIGINAL_NOCLOBBER</span><span class="s2" style="color:#e6db74">"</span><br></pre></div>
</td>
</tr>
</table>

## Scheduling the Renewal

With or without `at`, you've got to ensure the task is actually being run.

### `cron`

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo crontab -e<br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">crontab -e</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6
7
8</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e"># Add a `MAILTO` that looks like this:</span><br><span class="nv" style="color:#f8f8f2">MAILTO</span><span class="o" style="color:#f92672">=</span>your@email.address<br><span class="c1" style="color:#75715e"># Add one of the following, depending on how you set it up:</span><br><span class="m" style="color:#ae81ff">0</span> <span class="m" style="color:#ae81ff">0</span>,12 * * * /full/path/to/certbot renew --quiet<br><span class="c1" style="color:#75715e"># or</span><br><span class="m" style="color:#ae81ff">0</span> <span class="m" style="color:#ae81ff">0</span>,12 * * * /sbin/certbot-renew-everything<br><span class="c1" style="color:#75715e"># or</span><br><span class="m" style="color:#ae81ff">0</span> <span class="m" style="color:#ae81ff">0</span>,12 * * * /sbin/at-random-renewal<br></pre></div>
</td>
</tr>
</table>

If you're not changing the time in the script itself, you probably don't want to use `0 0,12`. This launches the task at `00:00` and `12:00` every day. If launching means `at` assigns a random time, or checks to see if it's running, those times aren't a problem. If you're actually hitting Let's Encrypt every day at that time, that's not a great idea.

### `systemd`

(Note: my `systemd` knowledge is still pretty rudimentary. I'm using to userspace `cron`. If you see anything I can improve, I'd love to know about it!)

We're going to define a [oneshot unit](https://www.freedesktop.org/software/systemd/man/systemd.service.html#Type=) ([example #2](https://www.freedesktop.org/software/systemd/man/systemd.service.html#Examples)):

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/systemd/system/certbot-renew.service</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6
7
8</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="o" style="color:#f92672">[</span>Unit<span class="o" style="color:#f92672">]</span><br><span class="nv" style="color:#f8f8f2">Description</span><span class="o" style="color:#f92672">=</span>Attempts to renew all certbot certs<br><br><span class="o" style="color:#f92672">[</span>Service<span class="o" style="color:#f92672">]</span><br><span class="nv" style="color:#f8f8f2">Type</span><span class="o" style="color:#f92672">=</span>oneshot<br><span class="nv" style="color:#f8f8f2">ExecStart</span><span class="o" style="color:#f92672">=</span>/full/path/to/at/runner<br><span class="c1" style="color:#75715e"># ExecStart=/sbin/certbot-renew-everything</span><br><span class="c1" style="color:#75715e"># ExecStart=/full/path/to/certbot renew --quiet</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo chmod <span class="s1" style="color:#e6db74">'ugo=r,u+w'</span> /etc/systemd/system/certbot-renew.service<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl daemon-reload<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl <span class="nb" style="color:#f8f8f2">enable</span> certbot-renew.service<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl start certbot-renew.service<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl status certbot-renew.service<br><br><span class="go" style="color:#888">● certbot-renew.service - Attempts to renew all certbot certs</span><br><span class="go" style="color:#888">   Loaded: loaded (/etc/systemd/system/certbot-renew.service; static; vendor preset: disabled)</span><br><span class="go" style="color:#888">   Active: inactive (dead)</span><br><br><span class="go" style="color:#888">Dec 17 14:50:31 wizardsoftheweb1 systemd[1]: Starting Attempts to renew all certbot certs...</span><br><span class="go" style="color:#888">Dec 17 14:50:31 wizardsoftheweb1 systemd[1]: Started Attempts to renew all certbot certs.</span><br></pre></div>
</td></tr></table>

To run it regularly, we also create [a timer](https://www.freedesktop.org/software/systemd/man/systemd.timer.html):
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/systemd/system/certbot-renew.timer</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="o" style="color:#f92672">[</span>Unit<span class="o" style="color:#f92672">]</span><br><span class="nv" style="color:#f8f8f2">Description</span><span class="o" style="color:#f92672">=</span>Run certbot-renew.service every day at <span class="m" style="color:#ae81ff">00</span>:00 and <span class="m" style="color:#ae81ff">12</span>:00<br><br><span class="o" style="color:#f92672">[</span>Timer<span class="o" style="color:#f92672">]</span><br><span class="nv" style="color:#f8f8f2">OnCalendar</span><span class="o" style="color:#f92672">=</span>*-*-* <span class="m" style="color:#ae81ff">00</span>/12:00<br><span class="nv" style="color:#f8f8f2">Unit</span><span class="o" style="color:#f92672">=</span>certbot-renew.service<br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo chmod <span class="s1" style="color:#e6db74">'ugo=r,u+w'</span> /etc/systemd/system/certbot-renew.service<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl daemon-reload<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl <span class="nb" style="color:#f8f8f2">enable</span> certbot-renew.service<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl start certbot-renew.service<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl status certbot-renew.service<br><br><span class="go" style="color:#888">● certbot-renew.service - Attempts to renew all certbot certs</span><br><span class="go" style="color:#888">   Loaded: loaded (/etc/systemd/system/certbot-renew.service; static; vendor preset: disabled)</span><br><span class="go" style="color:#888">   Active: inactive (dead)</span><br><br><span class="go" style="color:#888">Dec 17 14:50:31 wizardsoftheweb1 systemd[1]: Starting Attempts to renew all certbot certs...</span><br><span class="go" style="color:#888">Dec 17 14:50:31 wizardsoftheweb1 systemd[1]: Started Attempts to renew all certbot certs.</span><br><br><span class="gp" style="color:#66d9ef">$</span> sudo chmod <span class="s1" style="color:#e6db74">'ugo=r,u+w'</span> /etc/systemd/system/certbot-renew.timer<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl daemon-reload<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl <span class="nb" style="color:#f8f8f2">enable</span> certbot-renew.timer<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl start certbot-renew.timer<br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl status certbot-renew.timer<br><br><span class="go" style="color:#888">● certbot-renew.timer - Run certbot-renew.service every day at 00:00 and 12:00.</span><br><span class="go" style="color:#888">   Loaded: loaded (/etc/systemd/system/certbot-renew.timer; static; vendor preset: disabled)</span><br><span class="go" style="color:#888">   Active: active (waiting) since Sun 2017-12-17 15:03:21 UTC; 4min 3s ago</span><br><br><span class="go" style="color:#888">Dec 17 15:03:21 wizardsoftheweb1 systemd[1]: Started Run certbot-renew.service every day at 00:00 and 12:00.</span><br><span class="go" style="color:#888">Dec 17 15:03:21 wizardsoftheweb1 systemd[1]: Starting Run certbot-renew.service every day at 00:00 and 12:00.</span><br><br><span class="gp" style="color:#66d9ef">$</span> sudo systemctl list-timers certbot*<br><br><span class="go" style="color:#888">NEXT                         LEFT    LAST PASSED UNIT                ACTIVATES</span><br><span class="go" style="color:#888">Mon 2017-12-18 00:00:00 UTC  8h left n/a  n/a    certbot-renew.timer certbot-renew.service</span><br><br><span class="go" style="color:#888">1 timers listed.</span><br><span class="go" style="color:#888">Pass --all to see loaded but inactive timers, too.</span><br></pre></div>
</td></tr></table>

## Before You Go

Let's Encrypt is a fantastic service. If you like what they do, i.e. appreciate how accessible they've made secure web traffic, [please donate](https://letsencrypt.org/donate/). [EFF's `certbot`](https://certbot.eff.org/) is what powers my site (and basically anything I work on these days); consider [buying them a beer](https://supporters.eff.org/donate/support-lets-encrypt) (it's really just a donate link but you catch my drift).

## Legal Stuff

I'm still pretty new to the whole CYA legal thing. I really like everything I've covered here, and I've done my best to respect individual legal policies. If I screwed something up, please send me an email ASAP so I can fix it.

- The Electronic Frontier Foundation and `certbot` are covered by [EFF's generous copyright](https://www.eff.org/copyright). As far as I know, it's all under [CC BY 3.0 US](http://creativecommons.org/licenses/by/3.0/us/). I made a few minor tweaks to build the banner image but tried to respect the trademark. I don't know who the `certbot` logo artist is but I really wish I did because it's a fantastic piece of art.
- Let's Encrypt [is trademarked](https://letsencrypt.org/trademarks/). Its logo uses [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). I made a few minor tweaks to build the banner image but tried to respect the trademark.
- I didn't find anything definitive (other than EULAs) covering Nginx, which doesn't mean it doesn't exist. Assets were taken [from its press page](https://www.nginx.com/press/).
- Apache content was sourced from [its press page](https://www.apache.org/foundation/press/kit/). It provides [a full trademark policy](http://www.apache.org/foundation/marks/).
