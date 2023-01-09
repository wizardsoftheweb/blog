---
title: "Let's Encrypt from Start to Finish: Useful Headers"
slug: "lets-encrypt-from-start-to-finish-useful-headers"
date: "2018-01-02T18:00:00.000Z"
feature_image: "/images/2017/12/certbot-letsencrypt-nginx-apache-5.png"
author: "CJ Harries"
description: "This post looks at common security headers. I've tried to explain what each one does, where it's helpful, and where it's not. I strongly recommend using HSTS."
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

This is the fourth in a series of several posts on how to do way more than you really need to with Let's Encrypt, `certbot`, and a good server. I use all of these things regularly but I've never taken the time to take them apart, look at how they work, and spend hours in Google trying in vain to figure out how to put them back together. It was inspired by [a disturbing trend of ISP privacy violations](https://web.archive.org/web/20171214121709/http://forums.xfinity.com/t5/Customer-Service/Are-you-aware-Comcast-is-injecting-400-lines-of-JavaScript-into/td-p/3009551) and [the shocking regulatory capture of the US Federal Communications Commission](https://www.fcc.gov/document/fcc-takes-action-restore-internet-freedom).

This post looks at a collection of useful security headers. I've tried to explain what each one does, where it can be helpful, and where it might bite you. None of these are absolutely necessary; if nothing else I strongly recommend using HSTS.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#the-series-so-far)
- [Code](#code)
- [Note](#note)
- [Primary Security Reference](#primary-security-reference)
- [Caveat](#caveat)
- [Primary Header Config](#primary-header-config)
  - [Nginx](#nginx)
  - [Apache](#apache)
- [Force Secure Communication](#force-secure-communication)
  - [Nginx](#nginx-1)
  - [Apache](#apache-1)
- [The Kitchen Sink](#the-kitchen-sink)
  - [Sources](#sources)
  - [Frames](#frames)
    - [I Made This](#i-made-this)
- [Prevent Clickjacking (Historical)](#prevent-clickjacking-historical)
  - [Nginx](#nginx-2)
  - [Apache](#apache-2)
- [Cross-Site Scripting](#cross-site-scripting)
  - [Nginx](#nginx-3)
  - [Apache](#apache-3)
- [Content Sniffing](#content-sniffing)
  - [Nginx](#nginx-4)
  - [Apache](#apache-4)
- [Referer](#referer)
- [Primary Header Config Redux](#primary-header-config-redux)
  - [Nginx](#nginx-5)
  - [Apache](#apache-5)
- [But What About](#but-what-about)
  - [Public Key Pinning](#public-key-pinning)
  - [Cross-Domain Policies](#cross-domain-policies)
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

You can view the code related to this post [under the `post-04-useful-headers` tag](//github.com/wizardsoftheweb/lets-encrypt-from-start-to-finish/tree/post-04-useful-headers). If you're curious, you can also check out [my first draft](https://github.com/wizardsoftheweb/lets-encrypt-from-start-to-finish/blob/b425b6e601c9991c4918f569310e634ed5855afc/original-post.md).

## Note

I'm testing out some new tooling. This will be [`wotw-highlighter`'s shakedown run](https://github.com/wizardsoftheweb/wotw-highlighter). Let me know what you think about the syntax highlighting! I'm pretty excited because (no whammies) it should work well in AMP and normally.

I wrote the majority of the Apache examples with `httpd` in mind, i.e. from a RHEL perspective. If you instead use `apache2`, most of the stuff should still work, albeit maybe just a little bit different.

## Primary Security Reference

Originally, this post was sourced from a collection of personal experience and interesting sources found during writing. However, once I split this post out, I wanted to find some best practices (my code, while certainly practice, isn't necessarily the best). The [Open Web Application Security Project](https://www.owasp.org/index.php/Main_Page) maintains [a list of useful headers](https://www.owasp.org/index.php/OWASP_Secure_Headers_Project#tab=Headers), which should all be covered here.

## Caveat

**EVERYTHING HERE CAN BE SIDESTEPPED**. Headers are sent [with a request/response](https://tools.ietf.org/html/rfc7540#section-8.1.2), which means they can be completely ignored. Headers do not prevent bad actors from doing malicious things. They do, however, force average users to do things as expected, which usually prevents bad actors from tricking average users into doing malicious things. This is a **very** important distinction.

## Primary Header Config

I like to split the crypto config and header config. I'm always going to want to use a good algorithm, but I might not always want to use, say, `X-Frame-Options`. YMMV.

[As I said before](https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-first-steps/#reuselocation), I like `/etc/<server>/common/`, YMMV.

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo touch /etc/nginx/common/ssl-headers.conf<br></pre></div>
</td></tr></table>

### Apache

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> sudo touch /etc/httpd/common/ssl-headers.conf<br></pre></div>
</td></tr></table>

## Force Secure Communication

As [previously mentioned](https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-overview/#hsts), HSTS ensures users use secure protocols. The HSTS header, `Strict-Transport-Security`, has three primary options:

- `max-age`: This specifies the maximum amount of time a user agent (browser) should cache the header. To make things easier, we'll give the cache a half-life of two years:

    ![63072000-origin-1](/images/2017/12/63072000-origin-1.png)

    Twitter uses [20 years](https://github.com/twitter/secureheaders#default-values). Most sites either use one or two years. Qualys wants to see [at least 120 days](https://blog.qualys.com/securitylabs/2016/03/28/the-importance-of-a-proper-http-strict-transport-security-implementation-on-your-web-server).

- `includeSubdomains`: Without including subdomains, there are apparently [some cookie attacks](https://www.owasp.org/index.php/HTTP_Strict_Transport_Security_Cheat_Sheet#Problems) that can still be run. However, if you explicitly cannot serve subdomain content securely, this will cause problems. Err on the side of caution but check you subdomains.

- `preload`: You can [submit your HSTS site](https://hstspreload.org/) to an external list. This is [a long-term commitment](https://hstspreload.org/#removal), so don't submit your site unless you're sure about config. I won't be using it here because of the extra steps, but I highly recommend it if you've got a stable setup.

HSTS will forcefully break your site if you don't have a proper TLS setup. Remember, it's cached by the user agent, not something you have control over. You [can nuke it](https://www.thesslstore.com/blog/clear-hsts-settings-chrome-firefox/) when necessary, but it is a hassle to do so.

### Nginx

Append `; preload` if [you're on the list](https://hstspreload.org/);

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">add_header</span> <span class="s" style="color:#e6db74">Strict-Transport-Security</span> <span class="s" style="color:#e6db74">"max-age=63072000</span><span class="p">;</span> <span class="k" style="color:#66d9ef">includeSubdomains"</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

### Apache

Append `; preload` if [you're on the list](https://hstspreload.org/);

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">Header</span> always set Strict-Transport-Security <span class="s2" style="color:#e6db74">"max-age=63072000; includeSubdomains"</span><br></pre></div>
</td>
</tr></table>

## The Kitchen Sink

[A `Content-Security-Policy` header](https://content-security-policy.com/) can handle a majority of the other topics here. In theory, CSP defines a secure execution contract. In the past, that was certainly true; [the recent spec addition of blackbox code](https://www.eff.org/deeplinks/2017/09/open-letter-w3c-director-ceo-team-and-membership) makes it much less secure (e.g. a media policy covers media, not blackbox code that must be run prior to actually running media). That's a personal soapbox, though.

Good CSPs are fairly rigid and explicitly define as much as possible. As such, you might not be able to share them across sites like some of the other headers (i.e. maybe define this per site instead of in `/etc/<server>/common/ssl-headers.conf`). For example, a website that serves all its own assets will have a different CSP than a website that uses assets from a CDN.

**WARNING:** CSPs might break everything if you don't know what you're doing (and if you do know what you're doing, change "might" to "most certainly will"). Luckily you can [test things via `Content-Security-Policy-Report`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/report-uri) until you're confident with the policy. CSPs are awesome but require much more work than the deprecated headers they, in part, replace.

### Sources

CSPs provide granular source definitions. The `default-src` directive is used for anything not specified, so it's a great place to start secure:
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span>default-src: 'self';<br></pre></div>
</td>
</tr></table>

Sources themselves have [lots of options](https://content-security-policy.com/#source_list).

- `*` allows anything, i.e. don't use this
- `'self'` allows content from the same origin
- `example.com` allows content from `example.com`
- `https:` allows anything over TLS
- `'unsafe-(inline|eval)'` allows inline and dynamic execution and styling

CSP [currently defines](https://content-security-policy.com/#directive) the following `-src` directives:

- catch-all: `default-src`
- JavaScript: `script-src`
- stylesheets: `style-src`
- images: `img-src`
- AJAX, sockets, and events: `connect-src`
- fonts: `font-src`
- plugins: `object-src`
- HTML5 media: `media-src`
- `iframe`s and web workers: `child-src`
- form actions: `form-action`

For example, suppose you're serving all your own content but need [a Google font](https://fonts.google.com/) to maintain consistent styling.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6
7</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span># Unless specified, everything must come from this origin<br>default-src: 'self';<br># Styles can come from here or Google (securely)<br># We might want to inline them, explicitly or with JavaScript<br>style-src: 'unsafe-inline' 'self' https://fonts.googleapis.com;<br># Fonts can come from here or Google (securely)<br>font-src: 'self' https://fonts.gstatic.com;<br></pre></div>
</td>
</tr></table>

In Nginx,

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">add_header</span> <span class="s" style="color:#e6db74">Content-Security-Policy</span> <span class="s" style="color:#e6db74">"default-src:</span> <span class="s" style="color:#e6db74">'self'</span><span class="p">;</span> <span class="k" style="color:#66d9ef">style-src:</span> <span class="s" style="color:#e6db74">'unsafe-inline'</span> <span class="s" style="color:#e6db74">'self'</span> <span class="s" style="color:#e6db74">https://fonts.googleapis.com</span><span class="p">;</span> <span class="k" style="color:#66d9ef">font-src:</span> <span class="s" style="color:#e6db74">'self'</span> <span class="s" style="color:#e6db74">https://fonts.gstatic.com</span><span class="p">;</span><span class="k" style="color:#66d9ef">"</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

In Apache,

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">Header</span> always set Content-Security-Policy <span class="s2" style="color:#e6db74">"default-src: 'self'; style-src: 'unsafe-inline' 'self' https://fonts.googleapis.com; font-src: 'self' https://fonts.gstatic.com;"</span><br></pre></div>
</td>
</tr></table>

If you're loading lots of external content, an explicit CSP might not be practical. It's always a good idea to specify as much as possible, though. For example, this allows anything over TLS with some caveats on not markup:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6
7
8</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span># Allow anything loaded securely<br>default-src: 'self' https:;<br># Allow images from anywhere<br>img-src: *;<br># Restrict scripts to cdnjs but block eval<br>script-src 'self' https://cdnjs.cloudflare.com;<br># Block plugins<br>object-src: 'none';<br></pre></div>
</td>
</tr></table>

### Frames

CSPs provide two directives that are useful for frames: `sandbox` and `frame-ancestors`. The first adds extra security when serving explicitly embedded content; the second adds extra security to all content.

I actually couldn't find any good examples of a CSP `sandbox` policy. All of the sources I found looked [like the MDN CSP `sandbox` page](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/sandbox), with a note about how the CSP `sandbox` mimics [the `iframe` `sandbox` attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#attr-sandbox) and a list of possible values. Without usage examples, my assumption is that it exists to provide an extra layer of `sandbox` security. Anyone can strip the `sandbox` tag from an `iframe` or change its values; by setting it in the header itself you can limit the options available to external consumers.

#### I Made This

I was trying to figure out how everything worked together, so I built [a small tool to play with everything together](https://csp.wizardsoftheweb.pro/). It's really interesting stuff, especially if you do the ad thing. I also [split off everything you need to ruin CSP](https://github.com/wizardsoftheweb/express-csp-demo) for a quick reference. You should just be able to clone and go.

## Prevent Clickjacking (Historical)

Note that this is [superceded by a solid `Content-Security-Policy`](https://www.w3.org/TR/CSP11/#frame-ancestors-and-frame-options).

`iframe`s make everything difficult. One of the simplest possible attacks is to drop your content into an `iframe` and snoop the interaction. It's not always malicious; some people always try to embed things (still, in 2017) so they can do their own thing. [The `X-Frame-Options` header](https://tools.ietf.org/html/rfc7034) gives you `iframe` control in user agents that support it.

The majority of websites don't want to be embedded and should probably use `deny`, which prevents user agents that respect the header from embedding it. Some sites embed their own content but do not want others to embed it, which is captured by `sameorigin`. Finally, you can allow a single external site to embed your content [via `allow-from example.com`](https://tools.ietf.org/html/rfc7034#section-2.1).

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">add_header</span> <span class="s" style="color:#e6db74">X-Frame-Options</span> <span class="s" style="color:#e6db74">"deny"</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

### Apache

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">Header</span> always set X-Frame-Options <span class="s2" style="color:#e6db74">"deny"</span><br></pre></div>
</td>
</tr></table>

## Cross-Site Scripting

XSS is a pretty neat little industry. I know a couple of guys that are still collecting income on exploits they found years ago. Creating exploits requires a lot of ingenuity and even more time.

Which means you should go out of your way to prevent it. No matter how clever you think you are, there's always someone smarter. More importantly, there's always a fresh cadre of new script kiddies that do things you've never thought of. As your codebase ages, [low-hanging fruit like XSS headers](https://www.veracode.com/blog/2014/03/guidelines-for-setting-security-headers) are more useful than you might think.

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">add_header</span> <span class="s" style="color:#e6db74">X-XSS-Protection</span> <span class="s" style="color:#e6db74">"1</span><span class="p">;</span> <span class="k" style="color:#66d9ef">mode=block"</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

### Apache

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">Header</span> always set X-XSS-Protection <span class="s2" style="color:#e6db74">"1; mode=block"</span><br></pre></div>
</td>
</tr></table>

## Content Sniffing

[Multipurpose Internet Mail Extension types](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) are really easy to pass around. They're fast to use and there are so many of them. However, they're equally easy to take advantage of.

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">add_header</span> <span class="s" style="color:#e6db74">X-Content-Type-Options</span> <span class="s" style="color:#e6db74">"nosniff"</span><span class="p">;</span><br></pre></div>
</td>
</tr></table>

### Apache

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">Header</span> always set X-Content-Type-Options <span class="s2" style="color:#e6db74">"nosniff"</span><br></pre></div>
</td>
</tr></table>

## Referer

This is [one of my favorite computer obstinacies](https://en.wikipedia.org/wiki/HTTP_referer#Etymology), close to [`\t` in Makefiles](https://stackoverflow.com/a/1765566/2877698). Typos aside, messing with the Referer header is both great and bad:

1. You should try to protect the privacy of your users as much as possible. You don't need to know where they came from and you don't need to tell anyone else when they leave.
2. Most of the internet works off the Referer header now. I've tried at various stages to get away from it without any luck. I might not want everything I do bought and sold by data firms and ad shops, but they don't really care and it's not going away any time soon.

You [can beef up the Referer](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy) if you'd like, but you should do some serious testing on your apps first to make sure you won't be shooting yourself in the foot.

## Primary Header Config Redux

I've left out things that could be problematic everywhere. You might need to consider tweaking `X-Frame-Options` if your content gets embedded.

### Nginx

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/nginx/common/ssl-headers.conf</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="k" style="color:#66d9ef">add_header</span> <span class="s" style="color:#e6db74">Strict-Transport-Security</span> <span class="s" style="color:#e6db74">"max-age=63072000</span><span class="p">;</span> <span class="k" style="color:#66d9ef">includeSubdomains"</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">add_header</span> <span class="s" style="color:#e6db74">X-Frame-Options</span> <span class="s" style="color:#e6db74">"deny"</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">add_header</span> <span class="s" style="color:#e6db74">X-XSS-Protection</span> <span class="s" style="color:#e6db74">"1</span><span class="p">;</span> <span class="k" style="color:#66d9ef">mode=block"</span><span class="p">;</span><br><span class="k" style="color:#66d9ef">add_header</span> <span class="s" style="color:#e6db74">X-Content-Type-Options</span> <span class="s" style="color:#e6db74">"nosniff"</span><span class="p">;</span><br></pre></div>
</td>
</tr>
</table>

### Apache

For the `n`th time, I'd like to reiterate that I haven't actually tested this config. I will. Eventually.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">/etc/httpd/common/ssl-headers.conf</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nb" style="color:#f8f8f2">Header</span> always set Strict-Transport-Security <span class="s2" style="color:#e6db74">"max-age=63072000; includeSubdomains"</span><br><span class="nb" style="color:#f8f8f2">Header</span> always set X-Frame-Options <span class="s2" style="color:#e6db74">"deny"</span><br><span class="nb" style="color:#f8f8f2">Header</span> always set X-XSS-Protection <span class="s2" style="color:#e6db74">"1; mode=block"</span><br><span class="nb" style="color:#f8f8f2">Header</span> always set X-Content-Type-Options <span class="s2" style="color:#e6db74">"nosniff"</span><br></pre></div>
</td>
</tr>
</table>

## But What About

### Public Key Pinning

I didn't include [HTTP Public Key Pinning](https://developer.mozilla.org/en-US/docs/Web/HTTP/Public_Key_Pinning) because it's pretty easy to screw up. As Let's Encrypt certs aren't necessarily as stable as commercial alternatives (i.e. may change more frequently without manual intervention), I want to do more research on this.

### Cross-Domain Policies

I spent thirty minutes trying to come up with a good reason [for a `crossdomain.xml` policy](https://www.perpetual-beta.org/weblog/security-headers.html#rule-8470-2-establish-a-cross-domain-meta-policy). If you're not doing anything big with Flash or PDFs, I just don't see why you'd bother, especially with a good CSP. Personally, I'd recommend either `none` or `master-only` if you need a policy at all.

## Before You Go

Let's Encrypt is a fantastic service. If you like what they do, i.e. appreciate how accessible they've made secure web traffic, [please donate](https://letsencrypt.org/donate/). [EFF's `certbot`](https://certbot.eff.org/) is what powers my site (and basically anything I work on these days); consider [buying them a beer](https://supporters.eff.org/donate/support-lets-encrypt) (it's really just a donate link but you catch my drift).

## Legal Stuff

I'm still pretty new to the whole CYA legal thing. I really like everything I've covered here, and I've done my best to respect individual legal policies. If I screwed something up, please send me an email ASAP so I can fix it.

- The Electronic Frontier Foundation and `certbot` are covered by [EFF's generous copyright](https://www.eff.org/copyright). As far as I know, it's all under [CC BY 3.0 US](http://creativecommons.org/licenses/by/3.0/us/). I made a few minor tweaks to build the banner image but tried to respect the trademark. I don't know who the `certbot` logo artist is but I really wish I did because it's a fantastic piece of art.
- Let's Encrypt [is trademarked](https://letsencrypt.org/trademarks/). Its logo uses [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). I made a few minor tweaks to build the banner image but tried to respect the trademark.
- I didn't find anything definitive (other than EULAs) covering Nginx, which doesn't mean it doesn't exist. Assets were taken [from its press page](https://www.nginx.com/press/).
- Apache content was sourced from [its press page](https://www.apache.org/foundation/press/kit/). It provides [a full trademark policy](http://www.apache.org/foundation/marks/).
