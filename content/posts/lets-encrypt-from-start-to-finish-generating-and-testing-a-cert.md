---
title: "Let's Encrypt from Start to Finish: Generating and Testing a Cert"
slug: "lets-encrypt-from-start-to-finish-generating-and-testing-a-cert"
date: "2018-01-04T00:00:00.000Z"
feature_image: "/images/2017/12/certbot-letsencrypt-nginx-apache-6.png"
author: "CJ Harries"
description: "This post wraps up the server config and puts it to use. It covers my approach to generating a cert, and provides some useful `openssl` commands for verification."
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
draft: true
---

This is the fifth in a series of several posts on how to do way more than you really need to with Let's Encrypt, `certbot`, and a good server. I use all of these things regularly but I've never taken the time to take them apart, look at how they work, and spend hours in Google trying in vain to figure out how to put them back together. It was inspired by [a disturbing trend of ISP privacy violations](https://web.archive.org/web/20171214121709/http://forums.xfinity.com/t5/Customer-Service/Are-you-aware-Comcast-is-injecting-400-lines-of-JavaScript-into/td-p/3009551) and [the shocking regulatory capture of the US Federal Communications Commission](https://www.fcc.gov/document/fcc-takes-action-restore-internet-freedom).

This post wraps up (most of) the server config and puts it to use. It covers my approach to generating a cert, and provides some useful `openssl` commands for verification. Most of the work here is simply shuffling files around.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#the-series-so-far)
- [Code](#code)
- [Note](#note)
- [Prepare the Site](#prepare-the-site)
  - [Nginx](#nginx)
  - [Apache](#apache)
- [Providing the User Challenge Access](#providing-the-user-challenge-access)
- [Include the Challenge Config](#include-the-challenge-config)
  - [Nginx](#nginx-1)
  - [Apache](#apache-1)
- [Generate the Cert](#generate-the-cert)
- [Wiring up the Cert](#wiring-up-the-cert)
  - [Nginx](#nginx-2)
  - [Apache](#apache-2)
- [Restart the Server](#restart-the-server)
  - [Nginx](#nginx-3)
  - [Apache](#apache-3)
- [Testing with OpenSSL](#testing-with-openssl)
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

You can view the code related to this post [under the `post-05-your-first-cert` tag](//github.com/wizardsoftheweb/lets-encrypt-from-start-to-finish/tree/post-05-your-first-cert). If you're curious, you can also check out [my first draft](https://github.com/wizardsoftheweb/lets-encrypt-from-start-to-finish/blob/b425b6e601c9991c4918f569310e634ed5855afc/original-post.md).

## Note

I'm testing out some new tooling. This will be [`wotw-highlighter`'s shakedown run](https://github.com/wizardsoftheweb/wotw-highlighter). Let me know what you think about the syntax highlighting! I'm pretty excited because (no whammies) it should work well in AMP and normally.

I wrote the majority of the Apache examples with `httpd` in mind, i.e. from a RHEL perspective. If you instead use `apache2`, most of the stuff should still work, albeit maybe just a little bit different.

I'll be using [Mozilla's config generator](https://mozilla.github.io/server-side-tls/ssl-config-generator/) again for simplicity.

## Prepare the Site

Let's assume we start with examples like these:

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/nginx/conf.d/example.com.conf</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">server</span> <span class="p">{</span><br>    <span class="kn" style="color:#f92672">listen</span> <span class="mi" style="color:#ae81ff">80</span> <span class="s" style="color:#e6db74">default_server</span><span class="p">;</span><br>    <span class="kn" style="color:#f92672">listen</span> <span class="s" style="color:#e6db74">[::]:80</span> <span class="s" style="color:#e6db74">default_server</span> <span class="s" style="color:#e6db74">ipv6only=on</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">server_name</span> <span class="s" style="color:#e6db74">example.com</span> <span class="s" style="color:#e6db74">www.example.com</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">root</span> <span class="s" style="color:#e6db74">/srv/www/example.com</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

### Apache

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/httpd/vhosts.d/example.com.conf</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">Listen</span> <span class="m" style="color:#ae81ff">80</span><br><span class="nt" style="color:#f92672">&lt;VirtualHost</span> <span class="s" style="color:#e6db74">*:80</span><span class="nt" style="color:#f92672">&gt;</span><br>    <span class="nb" style="color:#f8f8f2">DocumentRoot</span> <span class="s2" style="color:#e6db74">"/srv/www/example.com"</span><br>    <span class="nb" style="color:#f8f8f2">ServerName</span> example.com www.example.com<br><span class="nt" style="color:#f92672">&lt;/VirtualHost&gt;</span><br></pre></div>
</td>
</tr>
</table>

## Providing the User Challenge Access

The reason we built [the group and external folder previously](https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-first-steps#groupanddirectorycreation) was so that it would be easy to access later. Simply add the website user to the `letsencrypt` group.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo usermod -G letsencrypt nginx<br><span class="go" style="color:#888">or, if you're being careful</span><br><span class="gp" style="color:#66d9ef">$</span> sudo usermod -G letsencrypt siteserviceaccount<br></pre></div>
</td></tr></table>

## Include the Challenge Config

We set up [a challenge directory earlier](https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-first-steps#reuselocation)

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/nginx/conf.d/example.com.conf</div></td>
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
10</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">server</span> <span class="p">{</span><br>    <span class="kn" style="color:#f92672">listen</span> <span class="mi" style="color:#ae81ff">80</span> <span class="s" style="color:#e6db74">default_server</span><span class="p">;</span><br>    <span class="kn" style="color:#f92672">listen</span> <span class="s" style="color:#e6db74">[::]:80</span> <span class="s" style="color:#e6db74">default_server</span> <span class="s" style="color:#e6db74">ipv6only=on</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">server_name</span> <span class="s" style="color:#e6db74">example.com</span> <span class="s" style="color:#e6db74">www.example.com</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">include</span> <span class="s" style="color:#e6db74">/etc/nginx/common/letsencrypt.conf</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">root</span> <span class="s" style="color:#e6db74">/srv/www/example.com</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

### Apache

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/httpd/vhosts.d/example.com.conf</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">Listen</span> <span class="m" style="color:#ae81ff">80</span><br><span class="nt" style="color:#f92672">&lt;VirtualHost</span> <span class="s" style="color:#e6db74">*:80</span><span class="nt" style="color:#f92672">&gt;</span><br>    <span class="nb" style="color:#f8f8f2">DocumentRoot</span> <span class="s2" style="color:#e6db74">"/srv/www/example.com"</span><br>    <span class="nb" style="color:#f8f8f2">ServerName</span> example.com www.example.com<br>    <span class="nb" style="color:#f8f8f2">Include</span> <span class="sx" style="color:#e6db74">/etc/httpd/common/letsencrypt.conf</span><br><span class="nt" style="color:#f92672">&lt;/VirtualHost&gt;</span><br></pre></div>
</td>
</tr>
</table>

## Generate the Cert

With everything in place, we can finally create a cert. All of this manual configuration was done to give us some flexibility over the final product. We're going to pass `certbot` a ton of options to handle this

- We only want a cert, not an installation
- We're going to agree to [the TOS](https://letsencrypt.org/repository/)
- We're going to register an email for important contacts
- We're going to skip joining [the EFF email list](https://www.eff.org/effector)
- We're going to specify the webroot (i.e. the directory to place the challenges)
- We're going to specify all the domains AND subdomains on the cert

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> certbot                       <span class="se" style="color:#ae81ff">\</span><br>    certonly                    <span class="se" style="color:#ae81ff">\</span><br>    --agree-tos                 <span class="se" style="color:#ae81ff">\</span><br>    --email your@email.address  <span class="se" style="color:#ae81ff">\</span><br>    --no-eff-email              <span class="se" style="color:#ae81ff">\</span><br>    --webroot                   <span class="se" style="color:#ae81ff">\</span><br>    -w /srv/www/letsencrypt     <span class="se" style="color:#ae81ff">\</span><br>    -d example.com              <span class="se" style="color:#ae81ff">\</span><br>    -d www.example.com          <span class="se" style="color:#ae81ff">\</span><br>    -d anotherone.example.com<br></pre></div>
</td></tr></table>

Depending on how things ran, you might have an issue or two to fix. If it worked, you'll get a confirmation notice.

You can verify the files were properly created by checking the Let's Encrypt directory.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> cat /etc/letsencrypt/live/example.com/README<br><span class="go" style="color:#888">This directory contains your keys and certificates.</span><br><br><span class="go" style="color:#888">`privkey.pem`  : the private key for your certificate.</span><br><span class="go" style="color:#888">`fullchain.pem`: the certificate file used in most server software.</span><br><span class="go" style="color:#888">`chain.pem`    : used for OCSP stapling in Nginx &gt;=1.3.7.</span><br><span class="go" style="color:#888">`cert.pem`     : will break many server configurations, and should not be used</span><br><span class="go" style="color:#888">                 without reading further documentation (see link below).</span><br><br><span class="go" style="color:#888">We recommend not moving these files. For more information, see the Certbot</span><br><span class="go" style="color:#888">User Guide at https://certbot.eff.org/docs/using.html#where-are-my-certificates.</span><br></pre></div>
</td></tr></table>

## Wiring up the Cert

### Nginx

We paused with a config like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/nginx/conf.d/example.com.conf</div></td>
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
10</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">server</span> <span class="p">{</span><br>    <span class="kn" style="color:#f92672">listen</span> <span class="mi" style="color:#ae81ff">80</span> <span class="s" style="color:#e6db74">default_server</span><span class="p">;</span><br>    <span class="kn" style="color:#f92672">listen</span> <span class="s" style="color:#e6db74">[::]:80</span> <span class="s" style="color:#e6db74">default_server</span> <span class="s" style="color:#e6db74">ipv6only=on</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">server_name</span> <span class="s" style="color:#e6db74">example.com</span> <span class="s" style="color:#e6db74">www.example.com</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">include</span> <span class="s" style="color:#e6db74">/etc/nginx/common/letsencrypt.conf</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">root</span> <span class="s" style="color:#e6db74">/srv/www/example.com</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

We can replace it with something like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/nginx/conf.d/example.com.conf</div></td>
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
27</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">server</span> <span class="p">{</span><br>    <span class="kn" style="color:#f92672">listen</span> <span class="mi" style="color:#ae81ff">80</span> <span class="s" style="color:#e6db74">default_server</span><span class="p">;</span><br>    <span class="kn" style="color:#f92672">listen</span> <span class="s" style="color:#e6db74">[::]:80</span> <span class="s" style="color:#e6db74">default_server</span> <span class="s" style="color:#e6db74">ipv6only=on</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">server_name</span> <span class="s" style="color:#e6db74">example.com</span> <span class="s" style="color:#e6db74">www.example.com</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">include</span> <span class="s" style="color:#e6db74">/etc/nginx/common/letsencrypt.conf</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">return</span> <span class="mi" style="color:#ae81ff">301</span> <span class="s" style="color:#e6db74">https://</span><span class="nv" style="color:#f8f8f2">$host$request_uri</span><span class="p">;</span><br><span class="p">}</span><br><span class="k" style="color:#66d9ef">server</span> <span class="p">{</span><br>    <span class="kn" style="color:#f92672">listen</span> <span class="mi" style="color:#ae81ff">443</span> <span class="s" style="color:#e6db74">ssl</span> <span class="s" style="color:#e6db74">http2</span><span class="p">;</span><br>    <span class="kn" style="color:#f92672">listen</span> <span class="s" style="color:#e6db74">[::]:443</span> <span class="s" style="color:#e6db74">ssl</span> <span class="s" style="color:#e6db74">http2</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">server_name</span> <span class="s" style="color:#e6db74">example.com</span> <span class="s" style="color:#e6db74">www.example.com</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">include</span> <span class="s" style="color:#e6db74">/etc/nginx/common/ssl.conf</span><span class="p">;</span><br><br>    <span class="c1" style="color:#75715e"># Normal cert</span><br>    <span class="kn" style="color:#f92672">ssl_certificate</span> <span class="s" style="color:#e6db74">/etc/letsencrypt/live/example.com/fullchain.pem</span><span class="p">;</span><br>    <span class="c1" style="color:#75715e"># Private key</span><br>    <span class="kn" style="color:#f92672">ssl_certificate_key</span> <span class="s" style="color:#e6db74">/etc/letsencrypt/live/example.com/privkey.pem</span><span class="p">;</span><br>    <span class="c1" style="color:#75715e"># OCSP stapling cert</span><br>    <span class="kn" style="color:#f92672">ssl_trusted_certificate</span> <span class="s" style="color:#e6db74">/etc/letsencrypt/live/example.com/chain.pem</span><span class="p">;</span><br><br>    <span class="kn" style="color:#f92672">root</span> <span class="s" style="color:#e6db74">/srv/www/example.com</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

### Apache

We paused with a config like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/httpd/vhosts.d/example.com.conf</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">Listen</span> <span class="m" style="color:#ae81ff">80</span><br><span class="nt" style="color:#f92672">&lt;VirtualHost</span> <span class="s" style="color:#e6db74">*:80</span><span class="nt" style="color:#f92672">&gt;</span><br>    <span class="nb" style="color:#f8f8f2">DocumentRoot</span> <span class="s2" style="color:#e6db74">"/srv/www/example.com"</span><br>    <span class="nb" style="color:#f8f8f2">ServerName</span> example.com www.example.com<br>    <span class="nb" style="color:#f8f8f2">Include</span> <span class="sx" style="color:#e6db74">/etc/httpd/common/letsencrypt.conf</span><br><span class="nt" style="color:#f92672">&lt;/VirtualHost&gt;</span><br></pre></div>
</td>
</tr>
</table>

We can replace it with something like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/httpd/vhosts.d/example.com.conf</div></td>
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
23</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">Listen</span> <span class="m" style="color:#ae81ff">80</span><br><span class="nb" style="color:#f8f8f2">Listen</span> <span class="m" style="color:#ae81ff">443</span><br><span class="nt" style="color:#f92672">&lt;VirtualHost</span> <span class="s" style="color:#e6db74">*:80</span><span class="nt" style="color:#f92672">&gt;</span><br>    <span class="nb" style="color:#f8f8f2">DocumentRoot</span> <span class="s2" style="color:#e6db74">"/srv/www/example.com"</span><br>    <span class="nb" style="color:#f8f8f2">ServerName</span> example.com www.example.com<br>    <span class="nb" style="color:#f8f8f2">Include</span> <span class="sx" style="color:#e6db74">/etc/httpd/common/letsencrypt.conf</span><br>    <span class="c" style="color:#75715e"># https://serverfault.com/a/739128/446829</span><br>    <span class="nb" style="color:#f8f8f2">RewriteEngine</span> <span class="k" style="color:#66d9ef">On</span><br>    <span class="nb" style="color:#f8f8f2">RewriteCond</span> %{HTTPS} <span class="k" style="color:#66d9ef">off</span><br>    <span class="nb" style="color:#f8f8f2">RewriteCond</span> %{REQUEST_URI} !^/\.well\-known/acme\-challenge/<br>    <span class="nb" style="color:#f8f8f2">RewriteRule</span> (.*) https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]<br><span class="nt" style="color:#f92672">&lt;/VirtualHost&gt;</span><br><span class="nt" style="color:#f92672">&lt;VirtualHost</span> <span class="s" style="color:#e6db74">*:443</span><span class="nt" style="color:#f92672">&gt;</span><br>    <span class="nb" style="color:#f8f8f2">DocumentRoot</span> <span class="s2" style="color:#e6db74">"/srv/www/example.com"</span><br>    <span class="nb" style="color:#f8f8f2">ServerName</span> example.com www.example.com<br><br>    <span class="c" style="color:#75715e"># Include scoped config</span><br><br>    <span class="nb" style="color:#f8f8f2">SSLEngine</span> <span class="k" style="color:#66d9ef">on</span><br>    <span class="nb" style="color:#f8f8f2">SSLCertificateFile</span> <span class="sx" style="color:#e6db74">/etc/letsencrypt/live/example.com/fullchain.pem</span><br>    <span class="nb" style="color:#f8f8f2">SSLCertificateKeyFile</span> <span class="sx" style="color:#e6db74">/etc/letsencrypt/live/example.com/privkey.pem</span><br><span class="nt" style="color:#f92672">&lt;/VirtualHost&gt;</span><br><span class="c" style="color:#75715e"># Include global config</span><br></pre></div>
</td>
</tr>
</table>

As before, I haven't tested the Apache config. At all. It might fail spectatularly.

## Restart the Server

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo nginx -t <span class="o" style="color:#f92672">&amp;&amp;</span> sudo systemctl restart nginx <span class="o" style="color:#f92672">||</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"whoops"</span><br></pre></div>
</td></tr></table>

### Apache

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo httpd -t <span class="o" style="color:#f92672">&amp;&amp;</span> sudo systemctl restart httpd <span class="o" style="color:#f92672">||</span> <span class="nb" style="color:#f8f8f2">echo</span> <span class="s2" style="color:#e6db74">"whoops"</span><br></pre></div>
</td></tr></table>

## Testing with OpenSSL

You can quickly verify your settings with `openssl`. If there are any errors and you just restarted the server process, wait a few minutes and try again. The OCSP stapling especially takes more than a few seconds to propagate.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> openssl s_client              <span class="se" style="color:#ae81ff">\</span><br>    -connect example.com:443    <span class="se" style="color:#ae81ff">\</span><br>    -servername example.com     <span class="se" style="color:#ae81ff">\</span><br>    -tls1_2                     <span class="se" style="color:#ae81ff">\</span><br>    -status<br><br><span class="go" style="color:#888">CONNECTED(00000003)</span><br><span class="go" style="color:#888">depth=2 O = Digital Signature Trust Co., CN = DST Root CA X3</span><br><span class="go" style="color:#888">verify return:1</span><br><span class="go" style="color:#888">depth=1 C = US, O = Let's Encrypt, CN = Let's Encrypt Authority X3</span><br><span class="go" style="color:#888">verify return:1</span><br><span class="go" style="color:#888">depth=0 CN = example.com</span><br><span class="go" style="color:#888">verify return:1</span><br><span class="go" style="color:#888">OCSP response:</span><br><span class="go" style="color:#888">======================================</span><br><span class="go" style="color:#888">OCSP Response Data:</span><br><span class="go" style="color:#888">    OCSP Response Status: successful (0x0)</span><br><span class="go" style="color:#888">    Response Type: Basic OCSP Response</span><br><span class="go" style="color:#888">    Version: 1 (0x0)</span><br><span class="go" style="color:#888">    Responder Id: C = US, O = Let's Encrypt, CN = Let's Encrypt Authority X3</span><br><span class="go" style="color:#888">    ...</span><br><span class="go" style="color:#888">======================================</span><br><span class="go" style="color:#888">---</span><br><span class="go" style="color:#888">Certificate chain</span><br><span class="go" style="color:#888"> 0 s:/CN=example.com</span><br><span class="go" style="color:#888">   i:/C=US/O=Let's Encrypt/CN=Let's Encrypt Authority X3</span><br><span class="go" style="color:#888"> 1 s:/C=US/O=Let's Encrypt/CN=Let's Encrypt Authority X3</span><br><span class="go" style="color:#888">   i:/O=Digital Signature Trust Co./CN=DST Root CA X3</span><br><span class="go" style="color:#888">---</span><br><span class="go" style="color:#888">Server certificate</span><br><span class="go" style="color:#888">-----BEGIN CERTIFICATE-----</span><br><span class="go" style="color:#888">...</span><br><span class="go" style="color:#888">-----END CERTIFICATE-----</span><br><span class="go" style="color:#888">subject=/CN=example.com</span><br><span class="go" style="color:#888">issuer=/C=US/O=Let's Encrypt/CN=Let's Encrypt Authority X3</span><br><span class="go" style="color:#888">...</span><br><span class="go" style="color:#888">SSL-Session:</span><br><span class="go" style="color:#888">    Protocol  : TLSv1.2</span><br><span class="go" style="color:#888">    Cipher    : ECDHE-RSA-AES256-GCM-SHA384</span><br><span class="go" style="color:#888">    ...</span><br><span class="go" style="color:#888">---</span><br></pre></div>
</td></tr></table>

To make sure your content is coming through as intended, you can make [actual HTTP request](https://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html). I've illustrated below with my website. Note that there are two newlines to finish the request.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> openssl s_client                      <span class="se" style="color:#ae81ff">\</span><br>    -connect wizardsoftheweb.pro:443    <span class="se" style="color:#ae81ff">\</span><br>    -servername wizardsoftheweb.pro     <span class="se" style="color:#ae81ff">\</span><br>    -tls1_2 -status -quiet<br><span class="go" style="color:#888">depth=2 O = Digital Signature Trust Co., CN = DST Root CA X3</span><br><span class="go" style="color:#888">verify return:1</span><br><span class="go" style="color:#888">depth=1 C = US, O = Let's Encrypt, CN = Let's Encrypt Authority X3</span><br><span class="go" style="color:#888">verify return:1</span><br><span class="go" style="color:#888">depth=0 CN = wizardsoftheweb.pro</span><br><span class="go" style="color:#888">verify return:1</span><br><span class="go" style="color:#888">GET / HTTP/1.1</span><br><span class="go" style="color:#888">HOST: wizardsoftheweb.pro</span><br><br><span class="go" style="color:#888">HTTP/1.1 200 OK</span><br><span class="go" style="color:#888">Server: nginx/1.10.2</span><br><span class="go" style="color:#888">Date: Sun, 17 Dec 2017 03:04:46 GMT</span><br><span class="go" style="color:#888">Content-Type: text/html</span><br><span class="go" style="color:#888">Content-Length: 722</span><br><span class="go" style="color:#888">Last-Modified: Sun, 28 May 2017 11:02:56 GMT</span><br><span class="go" style="color:#888">Connection: keep-alive</span><br><span class="go" style="color:#888">Strict-Transport-Security: max-age=63072000; includeSubdomains</span><br><span class="go" style="color:#888">X-Frame-Options: DENY</span><br><span class="go" style="color:#888">X-Content-Type-Options: nosniff</span><br><span class="go" style="color:#888">Accept-Ranges: bytes</span><br><br><span class="go" style="color:#888">&lt;!DOCTYPE html&gt;</span><br><span class="go" style="color:#888">...</span><br></pre></div>
</td></tr></table>

Along those lines, we can also test the redirect.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> telnet wizardsoftheweb.pro <span class="m" style="color:#ae81ff">80</span><br><span class="go" style="color:#888">Trying 198.199.79.185...</span><br><span class="go" style="color:#888">Connected to wizardsoftheweb.pro.</span><br><span class="go" style="color:#888">Escape character is '^]'.</span><br><span class="go" style="color:#888">GET / HTTP/1.1</span><br><span class="go" style="color:#888">HOST: wizardsoftheweb.pro</span><br><br><span class="go" style="color:#888">HTTP/1.1 301 Moved Permanently</span><br><span class="go" style="color:#888">Server: nginx/1.10.2</span><br><span class="go" style="color:#888">Date: Sun, 17 Dec 2017 03:12:55 GMT</span><br><span class="go" style="color:#888">Content-Type: text/html</span><br><span class="go" style="color:#888">Content-Length: 185</span><br><span class="go" style="color:#888">Connection: keep-alive</span><br><span class="go" style="color:#888">Location: https://www.wizardsoftheweb.pro/</span><br><br><span class="go" style="color:#888">&lt;html&gt;</span><br><span class="go" style="color:#888">&lt;head&gt;&lt;title&gt;301 Moved Permanently&lt;/title&gt;&lt;/head&gt;</span><br><span class="go" style="color:#888">&lt;body bgcolor="white"&gt;</span><br><span class="go" style="color:#888">&lt;center&gt;&lt;h1&gt;301 Moved Permanently&lt;/h1&gt;&lt;/center&gt;</span><br><span class="go" style="color:#888">&lt;hr&gt;&lt;center&gt;nginx/1.10.2&lt;/center&gt;</span><br><span class="go" style="color:#888">&lt;/body&gt;</span><br><span class="go" style="color:#888">&lt;/html&gt;</span><br></pre></div>
</td></tr></table>

## Before You Go

Let's Encrypt is a fantastic service. If you like what they do, i.e. appreciate how accessible they've made secure web traffic, [please donate](https://letsencrypt.org/donate/). [EFF's `certbot`](https://certbot.eff.org/) is what powers my site (and basically anything I work on these days); consider [buying them a beer](https://supporters.eff.org/donate/support-lets-encrypt) (it's really just a donate link but you catch my drift).

## Legal Stuff

I'm still pretty new to the whole CYA legal thing. I really like everything I've covered here, and I've done my best to respect individual legal policies. If I screwed something up, please send me an email ASAP so I can fix it.

- The Electronic Frontier Foundation and `certbot` are covered by [EFF's generous copyright](https://www.eff.org/copyright). As far as I know, it's all under [CC BY 3.0 US](http://creativecommons.org/licenses/by/3.0/us/). I made a few minor tweaks to build the banner image but tried to respect the trademark. I don't know who the `certbot` logo artist is but I really wish I did because it's a fantastic piece of art.
- Let's Encrypt [is trademarked](https://letsencrypt.org/trademarks/). Its logo uses [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). I made a few minor tweaks to build the banner image but tried to respect the trademark.
- I didn't find anything definitive (other than EULAs) covering Nginx, which doesn't mean it doesn't exist. Assets were taken [from its press page](https://www.nginx.com/press/).
- Apache content was sourced from [its press page](https://www.apache.org/foundation/press/kit/). It provides [a full trademark policy](http://www.apache.org/foundation/marks/).
