---
title: "Deconstructing Epom Ads for Personal Edification"
slug: "deconstructing-epom"
date: "2017-10-28T00:00:00.000Z"
author: "CJ Harries"
description: "Don't do anything dumb with this information. I've been sitting on this for awhile, so it might be valid anymore. I haven't checked. I am not and would never suggest you take advantage of anyone, even a company that makes its money taking advantage of you."
tags:
  - JavaScript
  - AutoHotkey
  - Epom
  - ad
---

<p class="nav-p"><a id="post-nav"></a></p>
<!-- MarkdownTOC -->

- [Completely unrelated setup](#completely-unrelated-setup)
- [Disclaimer](#disclaimer)
- [Curiousity](#curiousity)
- [DIY](#diy)
- [So what?](#so-what)
  - [Lock your `iframe`s](#lock-your-iframes)
  - [Never trust the client](#never-trust-the-client)

<!-- /MarkdownTOC -->

## Completely unrelated setup

I'm very interested in automating small, repetitive tasks that I don't want to do. I'm well known for this at work, and [AutoHotkey](https://autohotkey.com/) has come up a bunch recently because of a slew of new unskilled, repetitive computer tasks. My work environment is totally Linux and I've been playing through my "needed a better GPU" Steam backlog at home, so my AHK is a little rusty.

To fix that, I started a save in [Cave Heroes](http://www.kongregate.com/games/VSTGames/cave-heroes) (warning: Kongregate link). It has fairly straightforward mechanics and good visual clues to indicate state, so it's a great choice to take apart. [`ImageSearch`](https://autohotkey.com/docs/commands/ImageSearch.htm#ImageSearch), [Window Spy](https://www.autoitscript.com/autoit3/docs/intro/au3spy.htm), basic geometry, and lots of debugging are all you need to run the game without a player.

Like many games today, especially free ones, Cave Heroes gives you quality-of-life upgrades in exchange for interacting with advertising (videos, links, etc.). Whether or not that's a good thing is a topic for another day, because I was intrigued by their ad platform, [Epom](https://epom.com/). It serves a mix of clickbait, video ads, and landing pages. An ad will load, ask for interaction (e.g. click a link, watch a video), and, once done, send the game confirmation that it was completed.

## Disclaimer

Before I go any further, I want to clarify that [VST Games](http://www.vstgames.com/), the creators of Cave Heroes, are, as far as I know, not connected to Epom and probably chose the service via ad platform research. Any negative language here is directed at the ad codebase, not the hobby devs at VST trying to get some beer money.

The ad is constructed inside an element whose name begins with `epom`. It's actually served from `ultra-rv.com` with information gathered from an API at `adsrveys.com` and tracked via `atom-data.io`. All three are registered with privacy protection. The only real mention I could find anywhere of any of them was [this SEC document](https://www.sec.gov/Archives/edgar/data/1460329/000119312515400265/d82800dex101.htm). Based on [this documentation](https://epom.com/support/api/publisher-api/placement-api/placement-api-usage), I'd guess someone is running an Epom server and this isn't Epom direct. That being said, all the code I analyze is from API returns, which suggests Epom is the original author and the obfuscated servers are just a third-party host.

Don't do anything dumb with this information. I've been sitting on this for awhile, so it might not be valid anymore. I haven't checked. I am not and would never suggest you take advantage of anyone, even a company that makes its money taking advantage of you.

## Curiousity

Here's a selection of Epom ads:
![epom-popup-ad-one](/images/2017/09/epom-popup-ad-one.png)
![epom-popup-ad-two](/images/2017/09/epom-popup-ad-two.png)
![epom-popup-ad-three](/images/2017/09/epom-popup-ad-three.png)

As you can see, standard stuff. Normally I don't see any of that with [ABP](https://adblockplus.org/), but I do try to whitelist when the platform isn't too invasive. Servers aren't free. What originally caught my eye was that green "Continue" bar at the bottom of the last ad. Originally, it said to click a link to proceed (I tried to get another like it for a screenshot, but after six totally different ads, gave up). I didn't click anything, which means it's running on a timer. After some digging in dev tools, I found the [source](https://static.ultra-rv.com/rv-min-1_0_15.js) (I randomly got `15`, you might get `16`). It doesn't ship with a sourcemap, but you can pretty-print in your editor of choice. Neither it nor [its loader](https://static.ultra-rv.com/rv-min.js) ship with a license, and the CDN WHOIS is under a privacy protection service, so be careful.

The popup is actually an inserted [`iframe`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe) using the [HTML5 `sandbox`](https://www.w3.org/TR/2010/WD-html5-20100624/the-iframe-element.html#attr-iframe-sandbox) attribute. The `sandbox` sets `allow-forms`, `allow-pointer-lock`, `allow-popups`, `allow-same-origin`, and `allow-scripts`:

```javascript
"&lt;iframe id='epom-tag-container-iframe' width='" + t.data.containerWidth + "' height='" + t.data.containerHeight + "' frameborder='0' scrolling='no' sandbox='allow-forms allow-pointer-lock allow-popups allow-same-origin allow-scripts'>&lt;/iframe>"
```

Again, [pretty standard stuff](https://www.html5rocks.com/en/tutorials/security/sandboxed-iframes/). Because this `iframe` is using a [same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy), we can access its contents.

```javascript
let epomFrame = document.getElementById("epom-tag-container-iframe");
// https://developer.mozilla.org/en-US/docs/Web/API/HTMLIFrameElement/contentWindow
let epomWindow = epomFrame.contentWindow;
// https://developer.mozilla.org/en-US/docs/Web/API/HTMLIFrameElement/contentDocument
let epomDocument = epomFrame.contentDocument;
```

The content is inserted into the `iframe` with an [AJAX call](https://developer.mozilla.org/en-US/docs/AJAX/Getting_Started) to a generated link:

```javascript
"https://adsrveys.com/ads-api-v3?key=" + t.data.epomSiteId + "&format=JSONP&clientIp=" + t.data.ip + "&requestUrl=" + encodeURIComponent(t.data.pageURL) + "&" + d;
```

Each ad contains some generic setup in the `head`, a pixel representing the state, the ad itself, and something along these lines:

```javascript
var Common = {
  attrFired: false,
  rewardFired: false,
  loadFired: false,
  epomAdLoadedPixel: 'link',
  epomCompletePixel: 'link',
  epomRewardPixel: 'link',
  epomEncRewardPixel: 'link',
  epomRedirectToRewardEnc: 'link',
  epomRedirectToReward: 'link',
  epomPassbackPixel: 'link',
  epomClickPixel: 'link',
  epomClickRedirectPixel: 'link',
  onReward: function() {
    if (Common.rewardFired) return;
    Common.rewardFired = true;
    var pixel = document.createElement('img');
    pixel.src = Common.epomRewardPixel;
  },
  onAdLoaded: function(extraData) {
    if (Common.loadFired) return;
    Common.loadFired = true;

    // fire conv
    var pixel = document.createElement('img');
    pixel.src = Common.epomAdLoadedPixel;

    var bannerTxt = 'Click here to earn {REWARD}';
    var containerWidth = parseInt('$$CONTAINER_WIDTH$$') || '';
    var containerHeight = parseInt('$$CONTAINER_HEIGHT$$') || '';

    var data = {
      'isrv': true,
      'event': 'impression',
      'banner': 'id'
    };

    if (!!bannerTxt) {
      data['bannerTxt'] = bannerTxt;
    }

    if (!!containerWidth) {
      data['containerWidth'] = containerWidth;
    }

    if (!!containerHeight) {
      data['containerHeight'] = containerHeight;
    }

    // might sometime copy wrong settings if called with event data. FIX ME!
    if (extraData && extraData.rewardPixels) {
      for (var key in extraData) {
         if (extraData.hasOwnProperty(key)) {
            data[key] = extraData[key];
         }
      }
    }

    window.parent.postMessage(data, '*');

    if (window.webrv && window.webrv.onImpression) {
      window.webrv.onImpression();
    }
  },
  onComplete: function() {
    var pixel = document.createElement('img');
    pixel.src = Common.epomCompletePixel;
    // notify WebRV
    if (window.webrv && window.webrv.onComplete) {
      window.webrv.onComplete();
    }
    window.parent.postMessage({
      'isrv': true,
      'event': 'complete',
      'banner': 'id'
    }, '*');
  },
  onAttribution: function() {
    if (Common.attrFired) return;
    Common.attrFired = true;
    var pixel = document.createElement('img');
    pixel.src = Common.epomClickPixel;
  },
  // onPassback
  onError: function() {
    console.log("no fill");
    var passback = document.createElement('script');
    passback.src = Common.epomPassbackPixel;
    document.body.appendChild(passback);
    window.parent.postMessage({
      'isrv': true,
      'event': 'ad-passback',
      'banner': 'id'
    }, '*');
  },
  waitForReward: function(cb) {
    var rewardFunc = cb || Common.onReward;
    var rewardTime = parseInt('30') || 30;
    if (rewardTime && rewardTime > 0) {
      setTimeout(rewardFunc, rewardTime * 1000);
    } else {
      rewardFunc();
    }
  },
  // duplicate fir unruly
  onUnrulyEvent: function(e) {
    console.log(e);
    var data = e.data.split('#');
    if (data && data[0] == 'SR') {
      var evtName = data[1];
      if (evtName == 'AdPlay') {
        Common.onAttribution();
        Common.waitForReward();
      } else if (evtName == 'AdComplete') {
        Common.onComplete();
      }
    }
  },
  onAdvMessage: function(evt) {
      if (!evt || !evt.data || evt.data.int !== true) {
          return;
      }

      switch(evt.data.event) {
          case "load":
              Common.onAdLoaded();
              break;
          case "passback":
              Common.onError();
              break;
          case "conversion":
              Common.onAttribution();
              Common.onReward();
              break;
          case "complete":
              Common.onComplete();
              break;
      }
  }

};
```

(This isn't the only script type; I saw a couple of others occasionally that I didn't get a chance to analyze.)

I noticed this on first read:

```javascript
  waitForReward: function(cb) {
    var rewardFunc = cb || Common.onReward;
    var rewardTime = parseInt('30') || 30;
    if (rewardTime && rewardTime > 0) {
      setTimeout(rewardFunc, rewardTime * 1000);
    } else {
      rewardFunc();
    }
  },
```

There's the timer I saw with the ad, and, more importantly, here's a default reward action:

```javascript
  onReward: function() {
    if (Common.rewardFired) return;
    Common.rewardFired = true;
    var pixel = document.createElement('img');
    pixel.src = Common.epomRewardPixel;
  },
```

Here I put all of that to good use:
<video width="640" height="360" style="min-width: 100%" controls>
    <source src="https://giant.gfycat.com/ScarceCreamyKookaburra.mp4" type="video/mp4" />
    <source src="https://giant.gfycat.com/ScarceCreamyKookaburra.webm" type="video/webm" />
</video>
I clear and hide most of the console because the variables there probably provide enough information to track me down. You can verify all the steps yourself.

The last thing I know to check is whether or not it's actually being sent off to the server as a valid hit. Another obfuscated CDN, `atom-data.io`, receives responses that look like this:

```json
{
  "name": "impr_close_1",
  "msg": "msg",
  "user_id": "id",
  "app_name": "name",
  "app_key": "key,
  "device_id": "id",
  "session_id": "id",
  "impression_id": "id",
  "banner_id": "id",
  "sdk_version": "1.0.15a",
  "browser": "Browser",
  "os": "OS",
  "event_id": "id",
  "datetime": "2000-00-00 00:00:00"
}
```

Normal interaction sends off `"name": "pusher"`. Coincidentally, that's exactly what firing `Common.onReward` sends off. Aside from `impression_id`, `banner_id`, `event_id`, and `datetime`, the payloads are identical. There are a few other transactions and some messages that I was too lazy to chase down, but nothing a bit more time with the source wouldn't solve.

Outside of hitting the API, there's some intermingling inside the ad itself. If you were seriously thinking about breaking a system like this, you'd have to examine it as well.

## DIY

There are a few interesting things you could do with this information. Right off the bat, you've now got a way to get microtransaction rewards without the microtransactions. A nice bookmarklet, maybe along these lines, would work pretty well for common cases:

```javascript
javascript:( function() { document.getElementById("epom-tag-container-iframe").contentWindow.Common.onReward(); }() );
```

Of course the first thing Epom could do is change the names, which would break something like that. However, I've yet to see a variable name that couldn't be reverse-engineered from the source and [`regex`'d](https://regex101.com/). I'll leave that exercise up to the reader.

The great idea here is monetizing this. Because Epom gives you the tools to serve impressions and accidentally gives you the tools to validate and finalize impressions, you could, in theory, request and finalize impressions without your users ever seeing an ad. They'd still have to load the code, of course, and provide the details for the handshake, but you'd be getting paid for actually showing nothing. Many of the sites I saw building this followed pretty formulaic designs. Using some DOM-parsing, common names, and luck, you could even automate exposing fake personal information to provide some follow-through on your sudden massive rise in engagement. Throw in a little machine learning and you've got yourself a rad summer project. You might need to read their terms of service first; that might not be an okay thing to do.

## So what?

There are actually a couple of things to take away from this, outside the whole "ad impressions would be surprisingly easy to bot" thing.

### Lock your `iframe`s

I ran into a couple of ads that didn't `allow-same-origin`, and I had to go through the inconvenience of opening dev tools, selecting my context from a dropdown, and copypasting data like a barbarian. Still abusable thanks to modern browsers ([Chrome](https://developers.google.com/web/tools/chrome-devtools/console/#execution-context) and [Firefox](https://developer.mozilla.org/en-US/docs/Tools/Working_with_iframes); TIL the `Execution Context Selector` is not an upstream WebKit feature and just sorta showed up in the literature), but abuse of that complexity is going to filter out most of your everyday bad characters.

In general, `iframe`s on the same page should never interact directly, much in the same way that you should never use `root` as your primary user. If you made them and they have to interact, maybe they shouldn't be `iframe`s. If you didn't make them and they have to interact, use the [`window.postMessage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage) method, which was explicitly built for this. When you use `postMessage`, don't be like Epom:

```javascript
window.parent.postMessage(data, '*');
...
window.parent.postMessage({
  'isrv': true,
  'event': 'complete',
  'banner': 'id'
}, '*');
```

Always specify the `targetOrigin`. If you don't know where a message is going, don't waste the resources to send it. Always at least validate the `origin`. If you don't know where a message is coming from (or you're too lazy to specify), you probably shouldn't be listening for it. This is especially important in this context because, if they're not at least validating the source, you could sidestep the process entirely by parsing the request and `postMessage`(ing) the final state instead of actually sending the request. (Honestly, this could be another post by itself; `*` is a ridiculously dangerous origin that can be used for all sorts of hijinks.)

An even better idea for communication is to use an external, controllable, trusted source. This would, in theory, slim down the clientside code while also requiring an active connection. I don't think the connection is an issue, given the frequency the `ads-api-v3` updates. Running communication through not the client also means you can be more sure it wasn't doctored.

Finally, once you're done testing the solid `postMessage`/external API solution you make, don't forget to remove `allow-same-origin` like Epom did. If you do forget, some smartass like me is going to find it one day and air that dirty code.

### Never trust the client

I've got a nice little bruise on my jaw from when it hit the keyboard earlier. I was absolutely flabbergasted by how naive the entire `Common` set up is. All of the business logic is executed in the client, out in the real world, where people take things apart and figure out neat ways to make a buck or two. As the great physician House, M.D., is found of saying, "Everybody lies." Why would your externally-executed and unverified results be any different?

I could easily be missing out on a big-picture business reason for implicitly trusting everyone all the time because I only have limited experience with the ad industry. I'm willing to admit that. They could very well be only reporting impressions that have some sort of verifiable follow up, while not punishing the end user for issues. Epom doesn't care whether a user gets IAP or not; their goal is serving the ad.

I think the most puzzling thing here is that all of the logic for everything reward-related is publicly exposed in the `Common` object. There's absolutely no validation, just a collection of actions assumed to be fired when Epom intended. I'm not sure where code runs cleanly without error checks, but I wish I could live there.
