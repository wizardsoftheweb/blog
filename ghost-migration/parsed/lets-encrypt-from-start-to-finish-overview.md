---
title: "Let's Encrypt from Start to Finish: Overview"
slug: "lets-encrypt-from-start-to-finish-overview"
date: "2017-12-23T01:00:00.000Z"
feature_image: "/images/2017/12/certbot-letsencrypt-nginx-apache-1.png"
author: "CJ Harries"
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

This is the first in a series of several posts on how to do way more than you really need to with Let's Encrypt, `certbot`, and a good server. I use all of these things regularly but I've never taken the time to take them apart, look at how they work, and spend hours in Google trying in vain to figure out how to put them back together. It was inspired by [a disturbing trend of ISP privacy violations](https://web.archive.org/web/20171214121709/http://forums.xfinity.com/t5/Customer-Service/Are-you-aware-Comcast-is-injecting-400-lines-of-JavaScript-into/td-p/3009551) and [the shocking regulatory capture of the US Federal Communications Commission](https://www.fcc.gov/document/fcc-takes-action-restore-internet-freedom).

This post begins with the sad state of affairs that is the current US internet landscape but quickly moves on to more interesting topics like background information on HTTP, HTTPS, HSTS, Let's Encrypt, and `certbot`. It's intended as a gentle introduction and mainly served as a way for me to define what it was I was trying to accomplish.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#theseriessofar)
- [Code](#code)
- [The Status Quo](#thestatusquo)
- [Why Introduce This?](#whyintroducethis)
- [HTTP vs HTTPS](#httpvshttps)
- [HSTS](#hsts)
- [Let's Encrypt](#letsencrypt)
- [`certbot`](#certbot)
- [Before You Go](#beforeyougo)
- [Legal Stuff](#legalstuff)

## The Series so Far

1. [Overview](https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-overview)
2. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-first-steps" target="_blank">First Steps</a>
3. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-openssl-tuning" target="_blank">Tuning with OpenSSL</a>
4. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-useful-headers" target="_blank">Useful Headers</a>
5. <a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-your-first-cert" target="_blank">Generating and Testing a Cert</a>
6. <!--<a href="https://blog.wizardsoftheweb.pro/lets-encrypt-from-start-to-finish-automation" target="_blank">-->Automating Renewals<!--</a>-->

(This section should get updated as series progresses.)

## Code

You can view the code related to this post [under the `post-01-overview` tag](//github.com/wizardsoftheweb/lets-encrypt-from-start-to-finish/tree/post-01-overview).

## The Status Quo

2017's been a really scary year for the internet. Corporations strong-armed the W3C into [adding black box DRM to the HTML spec](https://www.eff.org/deeplinks/2017/09/open-letter-w3c-director-ceo-team-and-membership). WPA2 was [cracked](https://www.krackattacks.com/). IoT botnets, [while not making much of a splash this year](http://blog.netlab.360.com/iot_reaper-a-rappid-spreading-new-iot-botnet-en/), are now a regular threat. The US Federal Communications Commissions seems to be in [the final stages of regulatory capture](https://www.fcc.gov/document/fcc-takes-action-restore-internet-freedom).

The fight for US net neutrality has been center stage, at least everywhere I look, for the past month. So much so that I almost missed [this very interesting story about Comcast snooping unencrypted traffic](https://web.archive.org/web/20171214121709/http://forums.xfinity.com/t5/Customer-Service/Are-you-aware-Comcast-is-injecting-400-lines-of-JavaScript-into/td-p/3009551). Within a day or two of reading the original post, I stumbled on [this thread illustrating the same problem within Steam](https://www.reddit.com/r/gaming/comments/7ht8do/comcast_has_decided_to_start_injecting_popups/) (apparently [Steam never learned](http://store.steampowered.com/news/19852/)). Apparently [ISPs have been injecting code for years](https://www.infoworld.com/article/2925839/net-neutrality/code-injection-new-low-isps.html). That's not okay.

Sidestepping some of these issues takes a small investment of time up front, but is quickly automated afterward. The pernicious attitude that HTTPS isn't really necessary needs to go away, and this is a great place to start.

## Why Introduce This?

Before looking at how to build a strong configuration, it's worth some time to investigate the components involved. It's hard to understand why HTTPS is important without understanding what distinguishes it from HTTP. Without some historical perspective, Let's Encrypt seems like just the right thing and natural thing to do (it is) instead of the daring breakthrough it was and amazing disruptive business model it's become.

## HTTP vs HTTPS

The primary difference between [HTTP](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol) and [HTTPS](https://en.wikipedia.org/wiki/HTTPS) is encryption. The former is transmitted in the clear; the latter is encrypted prior to transmission. As web traffic flows through many nodes between source and destination, there are many opportunities for tampering or sniffing. HTTP neither has the ability to prevent attacks like this nor the hindsight to know they occurred. HTTPS defeats tampering and sniffing via [symmetric-key cryptography](https://en.wikipedia.org/wiki/Symmetric-key_algorithm) (assuming, of course, the attacker does not have access to sufficiently superior hardware).

However, HTTPS isn't just for people that need to pass secrets. It adds an extra layer of authenticity, giving your users some confidence they're actually communicating with you. To an extent, it keeps communication and activity private. HTTPS means the parties involved, and (theoretically) only the parties involved, will communicate.

Serving HTTP content is as simple as throwing something on a public address (well, with DNS and all that too, but I'm doing simple here). Serving HTTPS content requires more tooling. The box in question needs a digital identity (a cert) that will be used to establish secure pipelines. While you can technically [issue one yourself](http://www.selfsignedcertificate.com/), the internet usually expects [a third party](https://en.wikipedia.org/wiki/Certificate_authority) to be involved (and by "usually" I mean "self-signed certs are never accepted"). After obtaining digital ID, the content has to be served via encryption libraries (e.g. [the indomitable OpenSSL](https://www.openssl.org/)) and consumed by user agents capable of handling the encrypted tunnels (glossing over some refactoring that inevitably must be done to fix protocol-aware content). Modern webservers and browsers make the entire exchange fairly straightforward.

To make life easier, HTTPS content is usually served with additional HTTP pointers to the secure content, which cover user agents that don't try HTTPS by default. Nine times out of ten that means `http://example.com/page` gets a `301 Moved Permanently` that points to `https://example.com/page` (and I'm not sure what happens the other one time). HTTP and HTTPS are two very different protocols (rather, [application layer](https://en.wikipedia.org/wiki/Application_layer) v.s. [transport layer](https://en.wikipedia.org/wiki/Transport_layer)), so you can't serve HTTPS as HTTP. Instead, you instruct the user to resend the request using HTTPS.

## HSTS

HTTP Strict Transport Security (HSTS) is [a web standard](https://tools.ietf.org/html/rfc6797) that instructs user agents to use strict HTTPS. Its support is [pretty universal](https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security#Browser_support). The HSTS header automatically redirects HTTP traffic to HTTPS, adding another layer of enforcement. If it encounters an invalid HTTPS configuration (e.g. cert errors), HSTS prevents users from accessing the page entirely (e.g. [this intentional error page](https://subdomain.preloaded-hsts.badssl.com/)). It's cached by the browser, not the server, so an attacker can't just remove it from your content and redirect to a spoofed site.

HSTS can make sites a bit more complicated. It's recommended [to cover subdomains](https://blog.qualys.com/securitylabs/2016/03/28/the-importance-of-a-proper-http-strict-transport-security-implementation-on-your-web-server), but that can be complicated on larger sites. Wildcard certs and HSTS can actually [track everything ever](https://github.com/ben174/hsts-cookie), so you have to be aware of what you're loading externally. Finally, attackers aren't the only ones that can break HSTS. If your configuration breaks (e.g. forgot to renew the cert), users are locked out until you fix it.

At its core, HSTS is intended to snag some low-hanging fruit. By enforcing a site-wide HTTPS policy, shady third-party code can't hijack content (sort of). It's also much harder to execute a [man-in-the-middle attack](https://en.wikipedia.org/wiki/Man-in-the-middle_attack) of common varieties against a site with HSTS declared. More importantly, it forces users to switch to secure traffic (which probably could have been done years ago if certs weren't such a racket), all without making their eyes glaze over trying to figure out how to be safe. It just works.

## Let's Encrypt

From [its homepage](https://letsencrypt.org/),

> Let’s Encrypt is a free, automated, and open Certificate Authority.

No one should have to pay for secure communication. I don't want to say much more than that, because I've got some pretty strong opinions about predatory shared hosting providers and the pervasive desire to pull the wool over everyone's eyes that is central to the commercial SSL market.

Let's Encrypt provides a free alternative. As a solo dev (at least with my Wizards consulting), it's hard to describe just how much that changed my life. I can give local clients real security without even worrying about the cost (I mean, I do send them a few emails detailing both how much they're saving and how they can donate; pay it forward). I can throw up a prototype for the few dollars a month a cheap VPS costs and actually provide a secure service without diverting student loan payments.

## `certbot`

[The Electronic Frontier Foundation](https://www.eff.org/) has spearheaded [an amazing tool](https://certbot.eff.org) to set up and deploy Let's Encrypt certs anywhere (technically POSIX only but also technically you can make it work with a virtual machine and some elbow grease). They took an awesome idea and made it even more awesome. How neat is that?

## Before You Go

Let's Encrypt is a fantastic service. If you like what they do, i.e. appreciate how accessible they've made secure web traffic, [please donate](https://letsencrypt.org/donate/). [EFF's `certbot`](https://certbot.eff.org/) is what powers my site (and basically anything I work on these days); consider [buying them a beer](https://supporters.eff.org/donate/support-lets-encrypt) (it's really just a donate link but you catch my drift).

## Legal Stuff

I'm still pretty new to the whole CYA legal thing. I really like everything I've covered here, and I've done my best to respect individual legal policies. If I screwed something up, please send me an email ASAP so I can fix it.

* The Electronic Frontier Foundation and `certbot` are covered by [EFF's generous copyright](https://www.eff.org/copyright). As far as I know, it's all under [CC BY 3.0 US](http://creativecommons.org/licenses/by/3.0/us/). I made a few minor tweaks to build the banner image but tried to respect the trademark. I don't know who the `certbot` logo artist is but I really wish I did because it's a fantastic piece of art.
* Let's Encrypt [is trademarked](https://letsencrypt.org/trademarks/). Its logo uses [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). I made a few minor tweaks to build the banner image but tried to respect the trademark.
* I didn't find anything definitive (other than EULAs) covering Nginx, which doesn't mean it doesn't exist. Assets were taken [from its press page](https://www.nginx.com/press/).
* Apache content was sourced from [its press page](https://www.apache.org/foundation/press/kit/). It provides [a full trademark policy](http://www.apache.org/foundation/marks/).