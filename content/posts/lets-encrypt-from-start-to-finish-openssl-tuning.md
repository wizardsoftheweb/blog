---
title: "Let's Encrypt from Start to Finish: Tuning with OpenSSL"
slug: "lets-encrypt-from-start-to-finish-openssl-tuning"
date: "2018-01-01T18:00:00.000Z"
feature_image: "/images/2017/12/certbot-letsencrypt-nginx-apache.png"
author: "CJ Harries"
description: "This post sets up all the backend security logic (minus headers). I've tried to provide an explanation of each component and good values to use."
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

This is the third in a series of several posts on how to do way more than you really need to with Let's Encrypt, `certbot`, and a good server. I use all of these things regularly but I've never taken the time to take them apart, look at how they work, and spend hours in Google trying in vain to figure out how to put them back together. It was inspired by [a disturbing trend of ISP privacy violations](https://web.archive.org/web/20171214121709/http://forums.xfinity.com/t5/Customer-Service/Are-you-aware-Comcast-is-injecting-400-lines-of-JavaScript-into/td-p/3009551) and [the shocking regulatory capture of the US Federal Communications Commission](https://www.fcc.gov/document/fcc-takes-action-restore-internet-freedom).

This post sets up all the backend security logic (minus headers) to harden Nginx or Apache. I've tried to provide an explanation of each component and good values to use (or the means to create your own). If you don't have OpenSSL, most of this is meaningless.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#the-series-so-far)
- [Code](#code)
- [Note](#note)
- [Primary Security Reference](#primary-security-reference)
- [Primary Config File](#primary-config-file)
  - [Nginx](#nginx)
  - [Apache](#apache)
- [Specify Allowed TLS Versions](#specify-allowed-tls-versions)
  - [Nginx](#nginx-1)
  - [Apache](#apache-1)
- [Generate a List of Good Ciphers](#generate-a-list-of-good-ciphers)
  - [Nginx](#nginx-2)
  - [Apache](#apache-2)
- [Specify ECDHE Curve](#specify-ecdhe-curve)
  - [Nginx](#nginx-3)
  - [Apache](#apache-3)
- [Generate Diffie-Hellman Group](#generate-diffie-hellman-group)
  - [Nginx](#nginx-4)
  - [Apache](#apache-4)
- [Use Server Cipher Preference](#use-server-cipher-preference)
  - [Nginx](#nginx-5)
  - [Apache](#apache-5)
- [OCSP Stapling](#ocsp-stapling)
  - [Nginx](#nginx-6)
  - [Apache](#apache-6)
- [SSL Session](#ssl-session)
  - [Nginx](#nginx-7)
  - [Apache](#apache-7)
- [Primary Config File Redux](#primary-config-file-redux)
  - [Nginx](#nginx-8)
  - [Apache](#apache-8)
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

You can view the code related to this post [under the `post-03-openssl-tuning` tag](//github.com/wizardsoftheweb/lets-encrypt-from-start-to-finish/tree/post-03-openssl-tuning). If you're curious, you can also check out [my first draft](https://github.com/wizardsoftheweb/lets-encrypt-from-start-to-finish/blob/b425b6e601c9991c4918f569310e634ed5855afc/original-post.md).

## Note

I'm testing out some new tooling. This will be [`wotw-highlighter`'s shakedown run](https://github.com/wizardsoftheweb/wotw-highlighter). Let me know what you think about the syntax highlighting! I'm pretty excited because (no whammies) it should work well in AMP and normally.

I wrote the majority of the Apache examples with `httpd` in mind, i.e. from a RHEL perspective. If you instead use `apache2`, most of the stuff should still work, albeit maybe just a little bit different.

## Primary Security Reference

I'll be using [the Qualys suggested configuration](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices) to set this up. Most of this stuff is explained elsewhere on the internet. I wanted to grok the whole process, so I wrote it up.

If you're reading this more than, say, a month or two from its publication date, I'd strongly urge you to follow the documentation links to find the most current algorithms, best practices, and so on. Even if my minutae is current, you should always check sources when security is involved.

## Primary Config File

This creates a single file to hold the common config.

[As I said before](https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-first-steps/#reuselocation), I like `/etc/<server>/common/`, YMMV.

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo touch /etc/nginx/common/ssl.conf<br></pre></div>
</td></tr></table>

### Apache

So this probably won't work without some TLC. Apache differentiates global vs scoped config, and some of the things I mention only work in one or the other. [The official docs](https://httpd.apache.org/docs/2.4/mod/mod_ssl.html#sslprotocol) state scope per directive and I've tried to match that. However, I'm going to pretend like it will work without issue and hope no one says anything.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo touch /etc/httpd/common/ssl.conf<br></pre></div>
</td></tr></table>

You'll also need to ensure you've got the right modules installed and running. Depending [on your server's distro](https://askubuntu.com/a/600902) and the version of Apache you're running, installing and enabling modules is done differently.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> which a2enmod <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"apache2"</span> <span class="o" style="color:#f92672">||</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"httpd"</span><br><span class="go" style="color:#888">RHEL is usually httpd</span><br><span class="go" style="color:#888">Debian is usually apache2</span><br></pre></div>
</td></tr></table>

- If you're running `httpd`, enable them by editing `/etc/httpd/conf.modules.d/00-base.conf` (or another file there; you might have to `grep` them out).
- If you're running `apache2`, enable them via `a2enmod`.

You'll need these modules:

- `mod_rewrite`
- `mod_ssl`
- `mod_socache_shmcb` for any caching (sessions, stapling)

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> <span class="nb" style="color:#f8f8f2">eval</span> <span class="s2" style="color:#e6db74">"</span><span class="k" style="color:#66d9ef">$(</span>which apachectl <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nb" style="color:#f8f8f2">echo</span> apachectl <span class="o" style="color:#f92672">||</span> <span class="nb" style="color:#f8f8f2">echo</span> httpd<span class="k" style="color:#66d9ef">)</span><span class="s2" style="color:#e6db74"> -M"</span> <span class="p">|</span> grep -E <span class="s2" style="color:#e6db74">"rewrite|shmcb|ssl"</span><br><span class="go" style="color:#888"> rewrite_module (shared)</span><br><span class="go" style="color:#888"> socache_shmcb_module (shared)</span><br><span class="go" style="color:#888"> ssl_module (shared)</span><br></pre></div>
</td></tr></table>

You might actually have to install additional external packages depending on how you get Apache, e.g. `mod_ssl` on RHEL systems.

## Specify Allowed TLS Versions

Qualys says [`v1.2` is the only secure version](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices#22-use-secure-protocols). `v1.3` is [only a draft](https://tlswg.github.io/tls13-spec/), so including it might be odd. If you're truly desperate, `v1.1` isn't too bad. Don't forget that Qualys writes the benchmark, so if you ignore that advice, your rating will take a hit.

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">ssl_protocols</span> <span class="s" style="color:#e6db74">TLSv1.2</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

### Apache

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">SSLProtocol</span> -all +TLSv1.2<br></pre></div>
</td>
</tr></table>

## Generate a List of Good Ciphers

You might check [the current list](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices#23-use-secure-cipher-suites) to make sure this is up-to-date. You can also shorten this list; I was curious how it was built.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/save/the/qualys/list/somewhere</div></td>
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
18</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>ECDHE-ECDSA-AES128-GCM-SHA256<br>ECDHE-ECDSA-AES256-GCM-SHA384<br>ECDHE-ECDSA-AES128-SHA<br>ECDHE-ECDSA-AES256-SHA<br>ECDHE-ECDSA-AES128-SHA256<br>ECDHE-ECDSA-AES256-SHA384<br>ECDHE-RSA-AES128-GCM-SHA256<br>ECDHE-RSA-AES256-GCM-SHA384<br>ECDHE-RSA-AES128-SHA<br>ECDHE-RSA-AES256-SHA<br>ECDHE-RSA-AES128-SHA256<br>ECDHE-RSA-AES256-SHA384<br>DHE-RSA-AES128-GCM-SHA256<br>DHE-RSA-AES256-GCM-SHA384<br>DHE-RSA-AES128-SHA<br>DHE-RSA-AES256-SHA<br>DHE-RSA-AES128-SHA256<br>DHE-RSA-AES256-SHA256<br></pre></div>
</td>
</tr>
</table>

We can use `grep` to search with a pattern from a `-f`ile, composed of newline-separated `-F`ixed strings, where each pattern matches the entire line (`-x`). All we need is the available ciphers. `openssl ciphers` returns a colon-separated list, so we can pass it through `tr`anslate before searching it.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> openssl ciphers<br><span class="go" style="color:#888">ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:SRP-DSS-AES-256-CBC-SHA:SRP-RSA-AES-256-CBC-SHA:SRP-AES-256-CBC-SHA:DH-DSS-AES256-GCM-SHA384:DHE-DSS-AES256-GCM-SHA384:DH-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA256:DH-RSA-AES256-SHA256:DH-DSS-AES256-SHA256:DHE-RSA-AES256-SHA:DHE-DSS-AES256-SHA:DH-RSA-AES256-SHA:DH-DSS-AES256-SHA:DHE-RSA-CAMELLIA256-SHA:DHE-DSS-CAMELLIA256-SHA:DH-RSA-CAMELLIA256-SHA:DH-DSS-CAMELLIA256-SHA:ECDH-RSA-AES256-GCM-SHA384:ECDH-ECDSA-AES256-GCM-SHA384:ECDH-RSA-AES256-SHA384:ECDH-ECDSA-AES256-SHA384:ECDH-RSA-AES256-SHA:ECDH-ECDSA-AES256-SHA:AES256-GCM-SHA384:AES256-SHA256:AES256-SHA:CAMELLIA256-SHA:PSK-AES256-CBC-SHA:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:SRP-DSS-AES-128-CBC-SHA:SRP-RSA-AES-128-CBC-SHA:SRP-AES-128-CBC-SHA:DH-DSS-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:DH-RSA-AES128-GCM-SHA256:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES128-SHA256:DHE-DSS-AES128-SHA256:DH-RSA-AES128-SHA256:DH-DSS-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA:DH-RSA-AES128-SHA:DH-DSS-AES128-SHA:DHE-RSA-SEED-SHA:DHE-DSS-SEED-SHA:DH-RSA-SEED-SHA:DH-DSS-SEED-SHA:DHE-RSA-CAMELLIA128-SHA:DHE-DSS-CAMELLIA128-SHA:DH-RSA-CAMELLIA128-SHA:DH-DSS-CAMELLIA128-SHA:ECDH-RSA-AES128-GCM-SHA256:ECDH-ECDSA-AES128-GCM-SHA256:ECDH-RSA-AES128-SHA256:ECDH-ECDSA-AES128-SHA256:ECDH-RSA-AES128-SHA:ECDH-ECDSA-AES128-SHA:AES128-GCM-SHA256:AES128-SHA256:AES128-SHA:SEED-SHA:CAMELLIA128-SHA:PSK-AES128-CBC-SHA:ECDHE-RSA-RC4-SHA:ECDHE-ECDSA-RC4-SHA:ECDH-RSA-RC4-SHA:ECDH-ECDSA-RC4-SHA:RC4-SHA:RC4-MD5:PSK-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-ECDSA-DES-CBC3-SHA:SRP-DSS-3DES-EDE-CBC-SHA:SRP-RSA-3DES-EDE-CBC-SHA:SRP-3DES-EDE-CBC-SHA:EDH-RSA-DES-CBC3-SHA:EDH-DSS-DES-CBC3-SHA:DH-RSA-DES-CBC3-SHA:DH-DSS-DES-CBC3-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-ECDSA-DES-CBC3-SHA:DES-CBC3-SHA:PSK-3DES-EDE-CBC-SHA</span><br><span class="gp" style="color:#66d9ef">$</span> grep -Fx -f /save/the/qualys/list/somewhere &lt;<span class="o" style="color:#f92672">(</span> openssl ciphers <span class="p">|</span> tr <span class="s1" style="color:#e6db74">':'</span> <span class="s1" style="color:#e6db74">'\n'</span> <span class="o" style="color:#f92672">)</span><br><span class="go" style="color:#888">ECDHE-RSA-AES256-GCM-SHA384</span><br><span class="go" style="color:#888">ECDHE-ECDSA-AES256-GCM-SHA384</span><br><span class="go" style="color:#888">ECDHE-RSA-AES256-SHA384</span><br><span class="go" style="color:#888">ECDHE-ECDSA-AES256-SHA384</span><br><span class="go" style="color:#888">ECDHE-RSA-AES256-SHA</span><br><span class="go" style="color:#888">ECDHE-ECDSA-AES256-SHA</span><br><span class="go" style="color:#888">DHE-RSA-AES256-GCM-SHA384</span><br><span class="go" style="color:#888">DHE-RSA-AES256-SHA256</span><br><span class="go" style="color:#888">DHE-RSA-AES256-SHA</span><br><span class="go" style="color:#888">ECDHE-RSA-AES128-GCM-SHA256</span><br><span class="go" style="color:#888">ECDHE-ECDSA-AES128-GCM-SHA256</span><br><span class="go" style="color:#888">ECDHE-RSA-AES128-SHA256</span><br><span class="go" style="color:#888">ECDHE-ECDSA-AES128-SHA256</span><br><span class="go" style="color:#888">ECDHE-RSA-AES128-SHA</span><br><span class="go" style="color:#888">ECDHE-ECDSA-AES128-SHA</span><br><span class="go" style="color:#888">DHE-RSA-AES128-GCM-SHA256</span><br><span class="go" style="color:#888">DHE-RSA-AES128-SHA256</span><br><span class="go" style="color:#888">DHE-RSA-AES128-SHA</span><br></pre></div>
</td></tr></table>

If you didn't get any results, you should probably spend the few days necessary to move everything to a platform at least from the last decade. Or maybe `openssl` didn't get set up correctly.

Unfortunately, this doesn't retain the order Qualys uses, and I've yet to figure out a good way to maintain the original order. A standard `bash` approach would be to `comm`pare the two lists, but `comm` expects the lists to be sorted.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> comm -12 /save/the/qualys/list/somewhere &lt;<span class="o" style="color:#f92672">(</span> openssl ciphers <span class="p">|</span> tr <span class="s1" style="color:#e6db74">':'</span> <span class="s1" style="color:#e6db74">'\n'</span> <span class="o" style="color:#f92672">)</span><br><span class="go" style="color:#888">comm: file 1 is not in sorted order</span><br><span class="go" style="color:#888">ECDHE-RSA-AES256-GCM-SHA384</span><br><span class="go" style="color:#888">comm: file 2 is not in sorted order</span><br><span class="go" style="color:#888">ECDHE-RSA-AES256-SHA384</span><br><span class="gp" style="color:#66d9ef">$</span> comm --nocheck-order -12 /save/the/qualys/list/somewhere &lt;<span class="o" style="color:#f92672">(</span> openssl ciphers <span class="p">|</span> tr <span class="s1" style="color:#e6db74">':'</span> <span class="s1" style="color:#e6db74">'\n'</span> <span class="o" style="color:#f92672">)</span><br><span class="go" style="color:#888">ECDHE-RSA-AES256-GCM-SHA384</span><br><span class="go" style="color:#888">ECDHE-RSA-AES256-SHA384</span><br></pre></div>
</td></tr></table>

Brace expansion doesn't reduce the size by much, so I gave up after a few hours on that tangent. However, the important thing is that you now know what ciphers are available for you to use that also have the Qualys stamp of approval.

### Nginx

I don't think specifying all these is a great idea, but I actually have no idea.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">ssl_ciphers</span> <span class="s" style="color:#e6db74">ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES128-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA256</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

### Apache

I don't think specifying all these is a great idea, but I actually have no idea.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">SSLCipherSuite</span> <span class="s2" style="color:#e6db74">"ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES128-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA256"</span><br></pre></div>
</td>
</tr></table>

## Specify ECDHE Curve

Qualys suggests using a [specific elliptic curve for ECDHE](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices#26-use-strong-key-exchange). [Elliptic Curve Cryptography](https://wiki.openssl.org/index.php/Elliptic_Curve_Cryptography), like other algorithms, has both secure and insecure methods. Also like other algorithms, there are [a few common, widely used components](https://tools.ietf.org/html/rfc5480#section-2.1.1.1). Qualys recommends [`secp256r1` or `P-256`](https://tools.ietf.org/html/rfc5480#page-6). Coincidentally, that curve has [most likely been backdoored by government agencies for years](https://it.slashdot.org/story/13/09/11/1224252/are-the-nist-standard-elliptic-curves-back-doored) and has even been [put down by government agencies more recently](http://blog.bettercrypto.com/?p=1917).

I mention that because there's basically no way to protect yourself from actors with superior tech. No matter what you do, there's always someone with more money and decades of classified algebra and combinatorics to keep you grounded. However, unless some of that knowledge has been put to code and leaked recently, most of the cryptography mentioned here will probably prevent wardriving script kiddies from messing with you or your users for a few years.

If you'd like to use something a bit more secure, [check out SafeCurves](https://safecurves.cr.yp.to/). Like before, we'll need to check what's available to us with the installed version of OpenSSL.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> openssl ecparam -list_curves<br><span class="go" style="color:#888">secp112r1 : SECG/WTLS curve over a 112 bit prime field</span><br><span class="go" style="color:#888">...</span><br><span class="go" style="color:#888">secp521r1 : NIST/SECG curve over a 521 bit prime field</span><br><span class="go" style="color:#888">prime192v1: NIST/X9.62/SECG curve over a 192 bit prime field</span><br><span class="go" style="color:#888">...</span><br><span class="go" style="color:#888">prime256v1: X9.62/SECG curve over a 256 bit prime field</span><br><span class="go" style="color:#888">sect113r1 : SECG curve over a 113 bit binary field</span><br><span class="go" style="color:#888">...</span><br><span class="go" style="color:#888">sect571r1 : NIST/SECG curve over a 571 bit binary field</span><br><span class="go" style="color:#888">c2pnb163v1: X9.62 curve over a 163 bit binary field</span><br><span class="go" style="color:#888">...</span><br><span class="go" style="color:#888">c2tnb431r1: X9.62 curve over a 431 bit binary field</span><br><span class="go" style="color:#888">wap-wsg-idm-ecid-wtls1: WTLS curve over a 113 bit binary field</span><br><span class="go" style="color:#888">...</span><br><span class="go" style="color:#888">wap-wsg-idm-ecid-wtls12: WTLS curvs over a 224 bit prime field</span><br><span class="go" style="color:#888">brainpoolP160r1: RFC 5639 curve over a 160 bit prime field</span><br><span class="go" style="color:#888">...</span><br><span class="go" style="color:#888">brainpoolP512t1: RFC 5639 curve over a 512 bit prime field</span><br></pre></div>
</td></tr></table>

Comparing my list to SafeCurves yields zero safe curves. That's because OpenSSL has rolled [most of those into `v1.1`](https://www.openssl.org/news/openssl-1.1.0-notes.html), which isn't in stable channels yet (and probably won't ever make it to LTS channels).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> openssl version<br><span class="go" style="color:#888">OpenSSL 1.0.2g  1 Mar 2016</span><br></pre></div>
</td></tr></table>

That means we have two options:

1. Update OpenSSL manually and hope nothing system-critical actually needed the older version.
2. Pick the best from what we've got for now.

The first involves a ton of extra work (it's all fairly straightforward, just super involved), so I'm going to cover that in a later post, once I'm finished with the current slate. That leaves us with making due with what we've got. Mozilla recommends [`prime256v1`, `secp384r1`, and `secp521r1` for modern compatibility](https://wiki.mozilla.org/Security/Server_Side_TLS#Modern_compatibility) (actually for any compatibility).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> openssl ecparam -list_curves <span class="p">|</span> grep -E <span class="s2" style="color:#e6db74">"prime256v1|secp384r1|secp521r1"</span><br><span class="go" style="color:#888">secp384r1 : NIST/SECG curve over a 384 bit prime field</span><br><span class="go" style="color:#888">secp521r1 : NIST/SECG curve over a 521 bit prime field</span><br><span class="go" style="color:#888">prime256v1: X9.62/SECG curve over a 256 bit prime field</span><br></pre></div>
</td></tr></table>

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">ssl_ecdh_curve</span> <span class="s" style="color:#e6db74">secp521r1:secp384r1:prime256v1</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

### Apache

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">SSLOpenSSLConfCmd</span> Curves secp521r1:secp384r1:prime256v1<br></pre></div>
</td>
</tr></table>

## Generate Diffie-Hellman Group

Vanilla OpenSSL is susceptible to [Logjam](https://weakdh.org/) (among other things), so you'll want to create a new Diffie-Hellman group. Qualys [mentions this as well](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices#26-use-strong-key-exchange); basically, don't use defaults.

### Nginx

To generate,

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo mkdir -p /etc/nginx/tls<br><span class="gp" style="color:#66d9ef">$</span> sudo openssl dhparam -out /etc/nginx/tls/dhparams.pem <span class="m" style="color:#ae81ff">2048</span><br><span class="go" style="color:#888">Generating DH parameters, 2048 bit long safe prime, generator 2</span><br><span class="go" style="color:#888">This is going to take a long time</span><br><span class="go" style="color:#888">.+.+.+...........</span><br></pre></div>
</td></tr></table>

To use,

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">ssl_dhparam</span> <span class="s" style="color:#e6db74">/etc/nginx/tls/dhparams.pem</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

### Apache

To generate,

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo mkdir -p /etc/httpd/tls<br><span class="gp" style="color:#66d9ef">$</span> sudo openssl dhparam -out /etc/httpd/tls/dhparams.pem <span class="m" style="color:#ae81ff">2048</span><br><span class="go" style="color:#888">Generating DH parameters, 2048 bit long safe prime, generator 2</span><br><span class="go" style="color:#888">This is going to take a long time</span><br><span class="go" style="color:#888">.+.+.+...........</span><br></pre></div>
</td></tr></table>

To use,

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">SSLOpenSSLConfCmd</span> DHParameter <span class="s2" style="color:#e6db74">"/etc/httpd/tls/dhparams.pem"</span><br></pre></div>
</td>
</tr></table>

## Use Server Cipher Preference

Having done all of this work to actually set up cipher precedence and curves and lots of other things, it's important to actually specify we'd prefer it if clients would use our configuration instead of theirs. Assuming all methods are the same (which is actually a horrible assumption), we have more control with our configuration.

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">ssl_prefer_server_ciphers</span> <span class="no" style="color:#66d9ef">on</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

### Apache

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">SSLHonorCipherOrder</span> <span class="k" style="color:#66d9ef">on</span><br></pre></div>
</td>
</tr></table>

## OCSP Stapling

[OCSP Stapling](https://en.wikipedia.org/wiki/OCSP_stapling) makes things a little bit simpler for Let's Encrypt. To verify a cert's veracity, clients historically had to send a request to the CA, negotiate that, and then, knowing the cert was valid, hit the intended address. OCSP stapling allows your server to periodically timestamp its validity through the magic of digital signatures.

### Nginx

This config requires [also setting `ssl_trusted_certificate`](http://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_stapling_verify). This will be handled later, once we actually request a cert.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">ssl_stapling</span> <span class="no" style="color:#66d9ef">on</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">ssl_stapling_verify</span> <span class="no" style="color:#66d9ef">on</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

It's fairly common to see a `resolver` defined as well, and equally common to see it defined as Google.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">resolver</span> <span class="mi" style="color:#ae81ff">8</span><span class="s" style="color:#e6db74">.8.8.8</span> <span class="mi" style="color:#ae81ff">8</span><span class="s" style="color:#e6db74">.8.4.4</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

I'm not a huge fan of this because it routes everything to Google. If left out, the resolver defaults to your DNS. Theoretically, my DNS already knows a user is checking me out. Google doesn't need to be involved for the same reasons [OCSP stapling was created](https://en.wikipedia.org/wiki/Online_Certificate_Status_Protocol#Privacy_concerns).

### Apache

Apache doesn't [make it easy](https://httpd.apache.org/docs/trunk/ssl/ssl_howto.html#ocspstapling). Here's [a Stack Exchange thread](https://unix.stackexchange.com/a/394074) that seems to cover the important stuff. This is the first of many times [the new Apache cache](https://httpd.apache.org/docs/2.4/mod/mod_socache_shmcb.html) will pop up, and, every single time, it requires manual setup.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">SSLUseStapling</span> <span class="k" style="color:#66d9ef">On</span><br><span class="nb" style="color:#f8f8f2">SSLStaplingCache</span> <span class="s2" style="color:#e6db74">"shmcb:ssl_stapling(32768)"</span><br></pre></div>
</td>
</tr></table>

## SSL Session

As a fullstack dev who spends most of his time performing brute force data analysis and putting out fires, I honestly don't have a good baseline for what is or is not a safe config. Mozilla might have [abandoned open communication](https://wiki.mozilla.org/Media/EME) to court [the favor of big corporations](https://boingboing.net/2017/09/21/democracy-dies-in-dullness.html), but they still occasionally support the little dev (just not [the end user](https://blog.mozilla.org/firefox/update-looking-glass-add/)). [The Mozilla TLS Config Generator](https://mozilla.github.io/server-side-tls/ssl-config-generator/) is a fantastic tool to generate actually strong defaults. After reading several hundred posts about Nginx and Apache hardening for a couple of weekends, I've come to recognize the Mozilla standards pretty well. That was my long-winded way of saying this is section is total copypasta.

Due to [a security issue](https://wiki.mozilla.org/Security/Server_Side_TLS#TLS_tickets_.28RFC_5077.29), Mozilla doesn't recommend using [session tickets](https://tools.ietf.org/html/rfc5077). More recently, [at least one named vulnerability](https://filippo.io/Ticketbleed/) has popped up regarding session tickets, so use them at your own risk.

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">ssl_session_timeout</span> <span class="s" style="color:#e6db74">1d</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">ssl_session_cache</span> <span class="s" style="color:#e6db74">shared:SSL:50m</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">ssl_session_tickets</span> <span class="no" style="color:#66d9ef">off</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

### Apache

Apache again [makes this difficult](https://wiki.apache.org/httpd/SSLSessionCache). It does look like disabling tickets is easy, so they've got that going for them, which is nice.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">SSLSessionCache</span> <span class="s2" style="color:#e6db74">"shmcb:ssl_scache(512000)"</span><br><span class="nb" style="color:#f8f8f2">SSLOpenSSLConfCmd</span> Options -SessionTicket<br></pre></div>
</td>
</tr></table>

## Primary Config File Redux

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/nginx/common/ssl.conf</div></td>
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
12</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">ssl_protocols</span> <span class="s" style="color:#e6db74">TLSv1.2</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">ssl_ciphers</span> <span class="s" style="color:#e6db74">ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES128-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA256</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">ssl_ecdh_curve</span> <span class="s" style="color:#e6db74">secp521r1:secp384r1:prime256v1</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">ssl_dhparam</span> <span class="s" style="color:#e6db74">/etc/nginx/tls/dhparams.pem</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">ssl_prefer_server_ciphers</span> <span class="no" style="color:#66d9ef">on</span><span class="p">;</span><br><br><span class="k" style="color:#66d9ef">ssl_stapling</span> <span class="no" style="color:#66d9ef">on</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">ssl_stapling_verify</span> <span class="no" style="color:#66d9ef">on</span><span class="p">;</span><br><br><span class="k" style="color:#66d9ef">ssl_session_timeout</span> <span class="s" style="color:#e6db74">1d</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">ssl_session_cache</span> <span class="s" style="color:#e6db74">shared:SSL:50m</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">ssl_session_tickets</span> <span class="no" style="color:#66d9ef">off</span><span class="p">;</span><br></pre></div>
</td>
</tr>
</table>

### Apache

For the `n`th time, I'd like to reiterate that I haven't actually tested this config. I will. Eventually.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/httpd/common/ssl.conf</div></td>
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
12</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">SSLStaplingCache</span> <span class="s2" style="color:#e6db74">"shmcb:/path/to/ssl_stapling(32768)"</span><br><span class="nb" style="color:#f8f8f2">SSLSessionCache</span> <span class="s2" style="color:#e6db74">"shmcb:/path/to/ssl_scache(512000)"</span><br><br><span class="nt" style="color:#f92672">&lt;VirtualHost</span> <span class="s" style="color:#e6db74">*:443</span><span class="nt" style="color:#f92672">&gt;</span><br>    <span class="nb" style="color:#f8f8f2">SSLProtocol</span> -all +TLSv1.2<br>    <span class="nb" style="color:#f8f8f2">SSLCipherSuite</span> <span class="s2" style="color:#e6db74">"ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES128-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA256"</span><br>    <span class="nb" style="color:#f8f8f2">SSLOpenSSLConfCmd</span> Curves secp521r1:secp384r1:prime256v1<br>    <span class="nb" style="color:#f8f8f2">SSLOpenSSLConfCmd</span> DHParameter <span class="s2" style="color:#e6db74">"/etc/httpd/tls/dhparams.pem"</span><br>    <span class="nb" style="color:#f8f8f2">SSLHonorCipherOrder</span> <span class="k" style="color:#66d9ef">on</span><br>    <span class="nb" style="color:#f8f8f2">SSLUseStapling</span> <span class="k" style="color:#66d9ef">On</span><br>    <span class="nb" style="color:#f8f8f2">SSLOpenSSLConfCmd</span> Options -SessionTicket<br><span class="nt" style="color:#f92672">&lt;/VirtualHost&gt;</span><br></pre></div>
</td>
</tr>
</table>

## Before You Go

Let's Encrypt is a fantastic service. If you like what they do, i.e. appreciate how accessible they've made secure web traffic, [please donate](https://letsencrypt.org/donate/). [EFF's `certbot`](https://certbot.eff.org/) is what powers my site (and basically anything I work on these days); consider [buying them a beer](https://supporters.eff.org/donate/support-lets-encrypt) (it's really just a donate link but you catch my drift).

## Legal Stuff

I'm still pretty new to the whole CYA legal thing. I really like everything I've covered here, and I've done my best to respect individual legal policies. If I screwed something up, please send me an email ASAP so I can fix it.

- The Electronic Frontier Foundation and `certbot` are covered by [EFF's generous copyright](https://www.eff.org/copyright). As far as I know, it's all under [CC BY 3.0 US](http://creativecommons.org/licenses/by/3.0/us/). I made a few minor tweaks to build the banner image but tried to respect the trademark. I don't know who the `certbot` logo artist is but I really wish I did because it's a fantastic piece of art.
- Let's Encrypt [is trademarked](https://letsencrypt.org/trademarks/). Its logo uses [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). I made a few minor tweaks to build the banner image but tried to respect the trademark.
- I didn't find anything definitive (other than EULAs) covering Nginx, which doesn't mean it doesn't exist. Assets were taken [from its press page](https://www.nginx.com/press/).
- Apache content was sourced from [its press page](https://www.apache.org/foundation/press/kit/). It provides [a full trademark policy](http://www.apache.org/foundation/marks/).
