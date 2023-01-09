---
title: "NPM Lifecycle Stages: A Study in Stream Editors"
slug: "npm-lifecycle-stages-a-study"
date: "2017-10-09T04:33:55.000Z"
feature_image: "/images/2017/10/npm-cycle-1.png"
author: "CJ Harries"
description: "NPM's lifecycle stages provide a discrete set of events to track state. Getting programmatic access to them all was a fun challenge."
tags:
  - NPM
  - awk
  - Node
  - TypeScript
  - JavaScript
  - package
draft: true
---

A majority of my work, both business and pleasure, is done in Node. I support a fairly large codebase which always needs maintenance. As I get new ideas or learn new techniques, the codebase grows. No matter how organized I try to be, every project seems to spawn half a dozen new projects. New projects means new config and packages and builds and instead of doing things the right way, I've just been shuffling a few master files around.

This weekend I sat down to break off a chunk of that. I've been using way too much copypasta config recently. It hasn't broken yet, and it probably won't break in the future, but it bothers me that I have to copy and paste scripts between projects. I'd much rather find or write a library to coordinate the process. My goal was to to streamline some of my [`npm` lifecycle scripts](https://docs.npmjs.com/misc/scripts).

<p class="nav-p"><a id="post-nav"></a></p>
<!-- MarkdownTOC -->

- [Quick Note](#quick-note)
- [NPM Scripts](#npm-scripts)
- [Code](#code)
- [Distinguished Stages](#distinguished-stages)
- [Programmatic Access](#programmatic-access)
  - [TypeScript](#typescript)
  - [NPM](#npm)
    - [`npm-lifecycle`](#npm-lifecycle)
    - [`npm_lifecycle_event`](#npm_lifecycle_event)
    - [`run-script`](#run-script)
    - [`npm-lifecycle` Usage](#npm-lifecycle-usage)
  - [Stream Editors to the Rescue](#stream-editors-to-the-rescue)
- [Solutions Compiled](#solutions-compiled)
  - [Examples](#examples)
- [Final Thoughts](#final-thoughts)

<!-- /MarkdownTOC -->

## Quick Note

I haven't taken the time to set up a solid AMP template yet, so if you're viewing this on an AMP CDN, the code won't be as pretty as it could be. You might notice a leading newline with some blocks. There are also some longer blocks in AMP that I shrank on my website via CSS. You win some, you lose some.

I assume a lot of things about your shell, mainly that it's not PowerShell or `cmd.exe`. There's a chance I've used some `zsh`isms; if the code isn't working in your shell let me know and I'll find a fix. I think all of the tools I use here are installed by default, or at least easily accessible via your package manager.

For posterity, here's a list of possibly important versions:

```bash
$ lsb_release -a
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 16.04.2 LTS
Release:        16.04
Codename:       xenial
$ awk --version
GNU Awk 4.1.3, API: 1.1 (GNU MPFR 3.1.4, GNU MP 6.1.0)
$ find --version
find (GNU findutils) 4.7.0-git
$ git --version
git version 2.7.4
$ grep --version
grep (GNU grep) 2.25
$ node -v
v8.4.0
$ npm -v
5.4.2
```

All of this was done on some Windows 10 Insider build at least capable of [running edge Docker for Windows](https://blog.wizardsoftheweb.pro/docker-in-wsl/#bespokerequirements).

## NPM Scripts

NPM has created a solid set of discrete stages that describe every state a package might be in. Each stage typically has three components: `prestage`, `stage`, and `poststage`. The components are made up of shell commands passed to `sh` (or whatever the value of [`script-shell` option](https://docs.npmjs.com/misc/config#script-shell) is). Stages are initiated by running

```bash
$ npm run stage
# e.g.
$ npm run lint
```

or, if the stage is a valid lifecycle stage with a command,

```bash
$ npm stage
# e.g.
$ npm install
```

The `run` command attempts to fire `prestage`. If successful, or if `prestage` doesn't have a command, it continues to `stage`. Again, if successful, or if `stage` is empty, it continues to `poststage`. Finally, if `poststage` is successful, or if it's empty, `npm` exits with code `0`. `npm` will halt and throw failures if any of the stages exit with nonzero status.

## Code

Before we get too far, it might be a good idea to check out an actual package. I'll be poking around [`npm` (latest)](https://github.com/npm/npm) later, so it's a great place to start.

```bash
git clone https://github.com/npm/npm.git
cd npm
npm install
```

## Distinguished Stages

NPM differentiates between lifecycle scripts and user-created scripts. You can see the difference with `npm run`:

```bash
$ basename $PWD
npm
$ npm run
Lifecycle scripts included in npm:
  preversion
    bash scripts/update-authors.sh && git add AUTHORS && git commit -m "update AUTHORS" || true
  test
    standard && npm run test-tap

available via `npm run-script`:
  dumpconf
    env | grep npm | sort | uniq
  prepare
    node bin/npm-cli.js --no-timing prune --prefix=. --no-global && rimraf test/*/*/node_modules && make -j4 doc
  tap
    tap --timeout 300
  tap-cover
    tap --nyc-arg='--cache' --coverage --timeout 600
  test-coverage
    npm run tap-cover -- "test/tap/*.js" "test/network/*.js" "test/broken-under-*/*.js"
  test-tap
    npm run tap -- "test/tap/*.js" "test/network/*.js" "test/broken-under-*/*.js"
  test-node
    tap --timeout 240 "test/tap/*.js" "test/network/*.js" "test/broken-under-nyc*/*.js"
```

Finding a list of lifecycle scripts online is [pretty easy](https://docs.npmjs.com/misc/scripts#description). For the most part, you can assume that an NPM command that alters your package will trigger a lifecycle event.

The [`version` command](https://docs.npmjs.com/cli/version#description) is a great example with some really useful scripts.

```json
"scripts": {
  "preversion": "npm test",
  "version": "npm run build && git add -A dist",
  "postversion": "git push && git push --tags && rm -rf build/temp"
}
```

Let's break down what happens (I'm just going to focus on the `version` stages and ignore the other lifecycles present):

```bash
npm version patch
```

1. NPM looks for `preversion`
    1. NPM finds `preversion` (instead of skipping the stage)
    2. NPM executes the command

        ```bash
        npm test
        ```

    3. NPM checks the exit status of `npm test`
        - `0` means everything is okay; continue
        - not zero means something went wrong; throw an error and kill the process
2. NPM looks for `version`
    1. NPM finds `version` (instead of skipping the stage)
    2. NPM executes the command

        ```bash
        npm run build && git add -A dist
        ```

    3. NPM checks the exit status of `npm run build && git add -A dist`&mdash;note that, with the guard, each individual command must exit with `0`
        - `0` means everything is okay; continue
        - not zero means something went wrong; throw an error and kill the process
3. NPM looks for `postversion`
    1. NPM finds `postversion` (instead of skipping the stage)
    2. NPM executes the command

        ```bash
        git push && git push --tags && rm -rf build/temp
        ```

    3. NPM checks the exit status of `git push && git push --tags && rm -rf build/temp`&mdash;more guards means more potential points of failure (which isn't a bad thing)
        - `0` means everything is okay; continue
        - not zero means something went wrong; throw an error and kill the process

Putting it all together, NPM won't increase the version unless
    1. the tests pass,
    2. the package builds successfully and is added to VCS,
    3. and the repo + tags are pushed followed by the removal of temp files.
Because the commands are fired as NPM moves through its own internal process, you're guaranteed execution at the proper time. You can even chain lifecycle events, making package maintenance easily automatable.

## Programmatic Access

The first step in managing lifecycle scripts is validating the stage. [The docs](https://docs.npmjs.com/misc/scripts#description) are great for human perusal, but they're not as nice for code. You can't expect every user to periodically `curl` NPM's website for updates.

### TypeScript

I mostly use TypeScript, so I started [with `npm`'s `package.json`](https://github.com/npm/npm/blob/latest/package.json). The TS handbook says to [bundle whenever possible](http://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html), which makes a ton of sense:

```bash
$ grep -P "typ(e|ing)s" package.json || echo "not found"
not found
```

Not a big deal. [DefinitelyTyped](https://github.com/DefinitelyTyped/DefinitelyTyped) (`@types`) usually has semi-recent pulls.

```bash
$ npm install --save-dev @types/npm
+ @types/npm@2.0.29
added 2 packages in 3.457s
```

I've often found that the `@types` package semver varies wildly from its upstream, so `npm@2` might not be too worrisome.

```bash
$ cat node_modules/@types/npm/index.d.ts
// Type definitions for npm 2.0.0
// Project: https://github.com/npm/npm
// Definitions by: Maxime LUCE <https://github.com/SomaticIT>
// Definitions: https://github.com/DefinitelyTyped/DefinitelyTyped
...
```

As it turns out, [most of the file](https://github.com/DefinitelyTyped/DefinitelyTyped/blame/master/types/npm/index.d.ts) is from several years ago. The semver actually matches. Unfortunately, that means TypeScript is a bust.

```bash
git reset --hard
```

### NPM

NPM might not be exporting a interface or enum, but there has to be a central repository of events, right? How else would the docs get made?

#### `npm-lifecycle`

`npm` depends on [the aptly named `npm-lifecycle`](https://github.com/npm/lifecycle), which
> is a standalone library for executing packages' lifecycle scripts. It is extracted from npm itself and intended to be fully compatible with the way npm executes individual scripts.

```bash
$ npm install --save-dev npm-lifecycle
npm notice save npm-lifecycle is being moved from dependencies to devDependencies
npm WARN npm@5.5.1 Non-dependency in bundleDependencies: npm-lifecycle

+ npm-lifecycle@1.0.3
updated 1 package in 3.473s
$ grep -R "post" node_modules/npm-lifecycle
node_modules/npm-lifecycle/package.json:    "postrelease": "npm publish && git push --follow-tags",
$ grep -R "shrink" node_modules/npm-lifecycle || echo "not found"
not found
```

Honestly, that's confusing. I can understand a generic `lifecycle` package not validating events against a master list, but this is the official `npm` package.

```bash
git reset --hard
```

#### `npm_lifecycle_event`

The docs mention [the current stage is stored in `env.npm_lifecycle_event`](https://docs.npmjs.com/misc/scripts#current-lifecycle-event), which seems like a decent term to search next:

```bash
$ grep -R "npm_lifecycle_event"
doc/misc/npm-scripts.md:Lastly, the `npm_lifecycle_event` environment variable is set to
doc/misc/npm-scripts.md:be wise in this case to look at the `npm_lifecycle_event` environment
html/doc/misc/npm-scripts.html:<p>Lastly, the <code>npm_lifecycle_event</code> environment variable is set to
html/doc/misc/npm-scripts.html:be wise in this case to look at the <code>npm_lifecycle_event</code> environment
man/man7/npm-scripts.7:Lastly, the \fBnpm_lifecycle_event\fP environment variable is set to
man/man7/npm-scripts.7:be wise in this case to look at the \fBnpm_lifecycle_event\fP environment
node_modules/npm-lifecycle/index.js:      env.npm_lifecycle_event = stage
node_modules/npm-lifecycle/index.js:  var stage = env.npm_lifecycle_event
node_modules/npm-lifecycle/index.js:  var stage = env.npm_lifecycle_event
```

Unfortunately, that leads us right back to `npm-lifecycle`. Because `npm-lifecycle` is a solid package, it's [very DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself). `stage` is passed in and `npm_lifecycle_event` is only set in a single location. The NPM devs have done a great job trimming the fat. You can't really complain about that one.

#### `run-script`

I originally started this morning with [the `run-script` command](https://github.com/npm/npm/blob/latest/lib/run-script.js). At first glance, that `cmdList` [looks pretty awesome](https://github.com/npm/npm/blob/latest/lib/run-script.js#L67). Loading it in the REPL kills some of that joy:

```bash
$ node
> const runScript = require("./lib/run-script")
undefined
> runScript
{ [Function: runScript]
  usage: 'npm run-script <command> [-- <args>...]\n\naliases: run, rum',
  completion: [Function] }
```

The important function, `list`, isn't accessible from the outside. We could modify the file itself, but that would involve messing with an API that wasn't exposed. It's more of a nothing-else-worked option than anything else. We might come back to it.

#### `npm-lifecycle` Usage

Because `npm-lifecycle` is the official package, it has to be used. There's a chance its implementation will highlight the stages. To reduce extraneous results (e.g. the static docs), we can shrink the input to only important directories. Based on some of my earlier `grep`ping, it looks like [`lib` directory](https://github.com/npm/npm/tree/latest/lib) and [`node_modules` directory](https://github.com/npm/npm/tree/latest/node_modules) are the only ones that contain active lifecycle code.

```bash
$ grep -R "lifecycle" node_modules --exclude-dir='npm-lifecycle'
node_modules/cacache/node_modules/lru-cache/node_modules/pseudomap/map.js:    process.env.npm_lifecycle_script === 'test')
node_modules/libnpx/index.js:      // we take a bit of extra time to pick up npm's full lifecycle script
node_modules/lru-cache/node_modules/pseudomap/map.js:    process.env.npm_lifecycle_script === 'test')
node_modules/npm-registry-couchapp/node_modules/couchapp/boiler/attachments/sammy/plugins/sammy.cache.js:  // Sammy.Cache provides helpers for caching data within the lifecycle of a
node_modules/npm-registry-couchapp/node_modules/couchapp/boiler/attachments/sammy/plugins/sammy.storage.js:  // Sammy.Cache provides helpers for caching data within the lifecycle of a
node_modules/npm-registry-couchapp/node_modules/couchapp/boiler/attachments/sammy/sammy.js:    // application during its lifecycle
node_modules/npm-registry-couchapp/node_modules/couchapp/boiler/attachments/sammy/sammy.js:    // Actually starts the application's lifecycle. `run()` should be invoked
node_modules/npm-registry-couchapp/node_modules/couchapp/node_modules/nano/node_modules/follow/node_modules/request/node_modules/hawk/test/browser.js:            it('goes through the full lifecycle', function (done) {
node_modules/npm-registry-couchapp/www/attachments/sammy/plugins/sammy.cache.js:  // Sammy.Cache provides helpers for caching data within the lifecycle of a
node_modules/npm-registry-couchapp/www/attachments/sammy/plugins/sammy.storage.js:  // Sammy.Cache provides helpers for caching data within the lifecycle of a
node_modules/npm-registry-couchapp/www/attachments/sammy/sammy.js:    // application during its lifecycle
node_modules/npm-registry-couchapp/www/attachments/sammy/sammy.js:    // Actually starts the application's lifecycle. `run()` should be invoked
node_modules/standard/node_modules/eslint-plugin-react/CHANGELOG.md:* Fix missing `getChildContext` lifecycle method in `prefer-stateless-function` ([#492][])
node_modules/standard/node_modules/eslint-plugin-react/CHANGELOG.md:* Add `state` in lifecycle methods for `sort-comp` rule ([#197][] @mathieudutour)
node_modules/standard/node_modules/eslint-plugin-react/CHANGELOG.md:* Allow `this.getState` references (not calls) in lifecycle methods ([#22][] @benmosher)
node_modules/standard/node_modules/eslint-plugin-react/lib/rules/sort-comp.js:      'lifecycle',
node_modules/standard/node_modules/eslint-plugin-react/lib/rules/sort-comp.js:      lifecycle: [
node_modules/tap/node_modules/coveralls/node_modules/request/node_modules/hawk/test/browser.js:            it('goes through the full lifecycle', function (done) {
node_modules/tap/node_modules/nyc/node_modules/center-align/utils.js: * point in the lifecycle of the application, whilst also
node_modules/tap/node_modules/nyc/node_modules/pseudomap/map.js:    process.env.npm_lifecycle_script === 'test')
```

`node_modules` didn't turn up anything all that useful.

```bash
$ grep -R "lifecycle" lib
lib/build.js:var lifecycle = require('./utils/lifecycle.js')
lib/build.js:        !didPre && [lifecycle, pkg, 'preinstall', folder],
lib/build.js:        didPre !== build.&lowbar;noLC && [lifecycle, pkg, 'install', folder],
lib/build.js:        didPre !== build.&lowbar;noLC && [lifecycle, pkg, 'postinstall', folder]
lib/config/lifecycle.js:module.exports = lifecycleOpts
lib/config/lifecycle.js:function lifecycleOpts (moreOpts) {
lib/install/action/install.js:var lifecycle = require('../../utils/lifecycle.js')
lib/install/action/install.js:  lifecycle(pkg.package, 'install', pkg.path, next)
lib/install/action/move.js:var lifecycle = require('../../utils/lifecycle.js')
lib/install/action/move.js:    [lifecycle, pkg.package, 'preuninstall', pkg.fromPath, { failOk: true }],
lib/install/action/move.js:    [lifecycle, pkg.package, 'uninstall', pkg.fromPath, { failOk: true }],
lib/install/action/move.js:    [lifecycle, pkg.package, 'postuninstall', pkg.fromPath, { failOk: true }],
lib/install/action/move.js:    [lifecycle, pkg.package, 'preinstall', pkg.path, { failOk: true }],
lib/install/action/postinstall.js:var lifecycle = require('../../utils/lifecycle.js')
lib/install/action/postinstall.js:  lifecycle(pkg.package, 'postinstall', pkg.path, next)
lib/install/action/preinstall.js:var lifecycle = require('../../utils/lifecycle.js')
lib/install/action/preinstall.js:  lifecycle(pkg.package, 'preinstall', pkg.path, next)
lib/install/action/prepare.js:var lifecycle = require('../../utils/lifecycle.js')
lib/install/action/prepare.js:      [lifecycle, pkg.package, 'prepublish', buildpath],
lib/install/action/prepare.js:      [lifecycle, pkg.package, 'prepare', buildpath]
lib/install/action/unbuild.js:var lifecycle = Bluebird.promisify(require('../../utils/lifecycle.js'))
lib/install/action/unbuild.js:  return lifecycle(pkg.package, 'preuninstall', pkg.path, { failOk: true }).then(() => {
lib/install/action/unbuild.js:    return lifecycle(pkg.package, 'uninstall', pkg.path, { failOk: true })
lib/install/action/unbuild.js:    return lifecycle(pkg.package, 'postuninstall', pkg.path, { failOk: true })
lib/install.js:  var trackLifecycle = cg.newGroup('lifecycle')
lib/pack.js:const lifecycle = BB.promisify(require('./utils/lifecycle'))
lib/pack.js:        return lifecycle(pkg, 'prepare', dir).then(() => pkg)
lib/pack.js:        return lifecycle(pkg, 'prepublish', dir).then(() => {
lib/pack.js:          return lifecycle(pkg, 'prepare', dir)
lib/pack.js:    return lifecycle(pkg, 'prepack', dir)
lib/pack.js:        .then(() => lifecycle(pkg, 'postpack', dir))
lib/publish.js:const lifecycle = BB.promisify(require('./utils/lifecycle.js'))
lib/publish.js:    return lifecycle(pkg, 'prepublishOnly', arg)
lib/publish.js:    return lifecycle(pkg, 'publish', arg)
lib/publish.js:    return lifecycle(pkg, 'postpublish', arg)
lib/restart.js:module.exports = require('./utils/lifecycle-cmd.js')('restart')
lib/run-script.js:var lifecycle = require('./utils/lifecycle.js')
lib/run-script.js:    return [lifecycle, pkg, c, wd, { unsafePerm: true }]
lib/shrinkwrap.js:const lifecycle = require('./utils/lifecycle.js')
lib/shrinkwrap.js:  lifecycle(tree.package, 'preshrinkwrap', tree.path, function () {
lib/shrinkwrap.js:      [lifecycle, tree.package, 'shrinkwrap', tree.path],
lib/shrinkwrap.js:      [lifecycle, tree.package, 'postshrinkwrap', tree.path]
lib/start.js:module.exports = require('./utils/lifecycle-cmd.js')('start')
lib/stop.js:module.exports = require('./utils/lifecycle-cmd.js')('stop')
lib/test.js:const testCmd = require('./utils/lifecycle-cmd.js')('test')
lib/unbuild.js:var lifecycle = require('./utils/lifecycle.js')
lib/unbuild.js:          [lifecycle, pkg, 'preuninstall', folder, { failOk: true }],
lib/unbuild.js:          [lifecycle, pkg, 'uninstall', folder, { failOk: true }],
lib/unbuild.js:          [lifecycle, pkg, 'postuninstall', folder, { failOk: true }],
lib/uninstall.js:  // no top level lifecycles on rm
lib/utils/lifecycle.js:const lifecycleOpts = require('../config/lifecycle')
lib/utils/lifecycle.js:const lifecycle = require('npm-lifecycle')
lib/utils/lifecycle.js:  const opts = lifecycleOpts(moreOpts)
lib/utils/lifecycle.js:  lifecycle(pkg, stage, wd, opts).then(cb, cb)
lib/version.js:const lifecycle = require('./utils/lifecycle.js')
lib/version.js:  var lifecycleData = Object.create(data)
lib/version.js:  lifecycleData.&lowbar;id = data.name + '@' + newVersion
lib/version.js:    [lifecycle, lifecycleData, 'preversion', where],
lib/version.js:    [lifecycle, lifecycleData, 'version', where],
lib/version.js:    [lifecycle, lifecycleData, 'postversion', where]
```

But `lib`, on the other hand, hit the jackpot. `npm-lifecycle` exports a [`lifecycle` function](https://github.com/npm/lifecycle/blob/latest/index.js#L32) whose signature is

- `pkg`: the calling package
- `stage`: the lifecycle stage
- `wd`: the working directory for the stage
- `opts`: any passed-in options to apply to the stage

The odd `[lifecycle, something, stage, something, something]` ([example](https://github.com/npm/npm/blob/latest/lib/unbuild.js#L39)) comes from [the package `slide`](https://github.com/npm/slide-flow-control/blob/master/lib/chain.js); `chain` is doing exactly what you think it is&mdash;sequentially calling `lifecycle` with the rest of the array bound as parameters.

For the most part, `lifecycle` is called via the `chain` syntax. But not always. It wouldn't be an open-source project if tons of people didn't contribute, and that means different files do things different ways. [The direct calls](https://github.com/npm/npm/blob/latest/lib/install/action/postinstall.js#L7) are pretty close to the `chain` calls, and the [out-of-left-field](https://github.com/npm/npm/blob/latest/lib/start.js#L1) calls match just enough of the other two that regex should work.

```bash
$ grep -RP "(?:lifecycle[\s\S]*?[,\(]\s*['\"])(\w[^\'\"\s\-]*?)[\'\"]" lib
lib/build.js:        !didPre && [lifecycle, pkg, 'preinstall', folder],
lib/build.js:        didPre !== build._noLC && [lifecycle, pkg, 'install', folder],
lib/build.js:        didPre !== build._noLC && [lifecycle, pkg, 'postinstall', folder]
lib/install/action/install.js:  lifecycle(pkg.package, 'install', pkg.path, next)
lib/install/action/move.js:    [lifecycle, pkg.package, 'preuninstall', pkg.fromPath, { failOk: true }],
lib/install/action/move.js:    [lifecycle, pkg.package, 'uninstall', pkg.fromPath, { failOk: true }],
lib/install/action/move.js:    [lifecycle, pkg.package, 'postuninstall', pkg.fromPath, { failOk: true }],
lib/install/action/move.js:    [lifecycle, pkg.package, 'preinstall', pkg.path, { failOk: true }],
lib/install/action/postinstall.js:  lifecycle(pkg.package, 'postinstall', pkg.path, next)
lib/install/action/preinstall.js:  lifecycle(pkg.package, 'preinstall', pkg.path, next)
lib/install/action/prepare.js:      [lifecycle, pkg.package, 'prepublish', buildpath],
lib/install/action/prepare.js:      [lifecycle, pkg.package, 'prepare', buildpath]
lib/install/action/unbuild.js:  return lifecycle(pkg.package, 'preuninstall', pkg.path, { failOk: true }).then(() => {
lib/install/action/unbuild.js:    return lifecycle(pkg.package, 'uninstall', pkg.path, { failOk: true })
lib/install/action/unbuild.js:    return lifecycle(pkg.package, 'postuninstall', pkg.path, { failOk: true })
lib/pack.js:        return lifecycle(pkg, 'prepare', dir).then(() => pkg)
lib/pack.js:        return lifecycle(pkg, 'prepublish', dir).then(() => {
lib/pack.js:          return lifecycle(pkg, 'prepare', dir)
lib/pack.js:    return lifecycle(pkg, 'prepack', dir)
lib/pack.js:        .then(() => lifecycle(pkg, 'postpack', dir))
lib/publish.js:    return lifecycle(pkg, 'prepublishOnly', arg)
lib/publish.js:    return lifecycle(pkg, 'publish', arg)
lib/publish.js:    return lifecycle(pkg, 'postpublish', arg)
lib/shrinkwrap.js:  lifecycle(tree.package, 'preshrinkwrap', tree.path, function () {
lib/shrinkwrap.js:      [lifecycle, tree.package, 'shrinkwrap', tree.path],
lib/shrinkwrap.js:      [lifecycle, tree.package, 'postshrinkwrap', tree.path]
lib/unbuild.js:          [lifecycle, pkg, 'preuninstall', folder, { failOk: true }],
lib/unbuild.js:          [lifecycle, pkg, 'uninstall', folder, { failOk: true }],
lib/unbuild.js:          [lifecycle, pkg, 'postuninstall', folder, { failOk: true }],
lib/version.js:    [lifecycle, lifecycleData, 'preversion', where],
lib/version.js:    [lifecycle, lifecycleData, 'version', where],
lib/version.js:    [lifecycle, lifecycleData, 'postversion', where]
```

### Stream Editors to the Rescue

Now that we have a pretty good idea how everything works, we can leverage external tools to find the stages:

```bash
$ find . -type f -exec awk '\
    match($0, /lifecycle.*?[,\(]\s*['\''"]([a-zA-Z.]+)['\''"]/, a){\
        match(a[1], /(pre|post)*(.+)/, b);\
        gsub(/pare/, "prepare", b[2]);\
        gsub(/publishOnly/, "prepublishOnly", b[2]);\
        print b[2];\
    }' {} \+ | sort | uniq

install
pack
prepare
prepublishOnly
publish
restart
shrinkwrap
start
stop
test
uninstall
version
```

`(g)awk`'s regex is much more opaque that the stuff I'm used to.

- `find ... -exec awk`: standard stuff
- `match($0, /lifecycle.*?[,\(]\s*['\''"]([a-zA-Z.]+)['\''"]/, a)`: We're only interested in lines that meet our pattern, `lifecycle< stuff >,|(< whitespace >?['"]word['"]`.
- `match(a[1], /(pre|post)*(.+)/, b)`: Once we have those lines, we want to strip `pre|post` from the beginning
- `gsub(/pare/, "prepare", b[2]);`: We stripped `pre` from `prepare`; without lookaheads, I don't know how to do this in a single pass
- `gsub(/publishOnly/, "prepublishOnly", b[2]);`: same deal
- `print b[2];`: spits out the word in quotes
- `{} \+`: append each filename, i.e. run the command once (escape the `+` to be safe) ([man link](http://man7.org/linux/man-pages/man1/find.1.html) or `man --pager="less -p '-exec\s+command\s+\{\}\s+\+'" find`)
- `sort`: sorts the output
- `uniq`: strips duplicates

To check, we can parse `lib/run-script` ([the file](#run-script) I said we should stay away from earlier):

```bash
$ awk '\
    BEGIN{ RS="\n\n+"; }\
    match($0, /cmdList[^=]*=[^\[]*\[([^\]]*)\]/, a) {\
        $0 = a[1];\
        while (match($0, /\w+/)) {\
            print substr($0, RSTART, RLENGTH);\
            $0 = substr($0, RSTART + RLENGTH);\
        }\
    }' lib/run-script.js | sort

install
publish
restart
start
stop
test
uninstall
version
```

- `awk`: scary stuff
- `BEGIN{ RS="\n\n+"; }`: change the `R`ecord `S`eparator to multiple newlines
- `match($0, /cmdList[^=]*=[^\[]*\[([^\]]*)\]/, a)`: coaxing `(g)awk`'s regex to select as little as possible is not an easy task; I had to grab `[^<character>]*` to make things work
- `while (match($0, /\w+/))`: We're assigning in a conditional because there isn't really a better way
- `print substr($0, RSTART, RLENGTH);`: the pattern selected just the text; this prints it
- `$0 = substr($0, RSTART + RLENGTH);`: this moves the starting character, meaning we won't refind old stuff
- `lib/run-script.js`: as far as I know, the commands aren't anywhere else
- `sort`: same as before; sorts for easy reading

Let's compare the outputs (just because [we can](https://unix.stackexchange.com/a/27335)):

```bash
$ diff <(find . -type f -exec awk 'match($0, /lifecycle.*?[,\(]\s*['\''"]([a-zA-Z.]+)['\''"]/, a){ match(a[1], /(pre|post)*(.+)/, b); gsub(/pare/, "prepare", b[2]); gsub(/publishOnly/, "prepublishOnly", b[2]); print b[2]; }' {} \+ | sort | uniq) <(awk 'BEGIN{ RS="\n\n+"; } match($0, /cmdList[^=]*=[^\[]*\[([^\]]*)\]/, a) { $0 = a[1]; while (match($0, /\w+/)) { print substr($0, RSTART, RLENGTH); $0 = substr($0, RSTART + RLENGTH); } }' lib/run-script.js | sort)
2,4d1
< pack
< prepare
< prepublishOnly
7d3
< shrinkwrap
```

It looks like the `find ... awk` solution found more stages than `run-script` knows about, which is a good feeling.

We've got one last place we can check for stages, `docs/misc/npm-scripts.md`:

```bash
$ awk '\
    BEGIN{ RS="\n\n\n+"; }\
    match($0, /## DESCRIPTION[^\#]*/, a) {\
        $0 = a[0];\
        while(match($0, /\n\*([^\:]*)/, b)) {\
            split(b[1], c, ",");\
            for (i in c) {\
                gsub(/(pre|post)/, "", c[i]);\
                gsub(/pare/, "prepare", c[i]);\
                gsub(/publishOnly/, "prepublishOnly", c[i]);\
                gsub(/ /, "", c[i]); print c[i];\
            }\
            $0 = substr($0, RSTART + RLENGTH);\
        }\
    }' doc/misc/npm-scripts.md | sort | uniq

install
pack
prepare
prepublishOnly
publish
restart
shrinkwrap
start
stop
test
uninstall
version
```

- `awk`: scary stuff
- `BEGIN{ RS="\n\n\n+"; }`: change the `R`ecord `S`eparator to multiple newlines
- `match($0, /## DESCRIPTION[^\#]*/, a)`: Only select the first block of text
- `while(match($0, /\n\*([^\:]*)/, b))`: Pull out lines starting with `*`
- `split(b[1], c, ",");`: split the string along commas
- `for (i in c)`: loop over the elements of the exploded string
- `gsub(/(pre|post)/, "", c[i]);`: strip prefix
- `gsub(/pare/, "prepare", c[i]);`: fix `prepare`
- `gsub(/publishOnly/, "prepublishOnly", c[i]);`: fix `prepublishOnly`
- `gsub(/ /, "", c[i]);`: strip spaces
- `print c[i];`: print the cleaned stage
- `$0 = substr($0, RSTART + RLENGTH);`: increment the loop
- `doc/misc/npm-scripts.md`: Only doc location I could find with everything
- `sort`: same as before; sorts for easy reading
- `uniq`: same as before; strip duplicates

It looks like that doc file does contain all the stages. That's awesome, because it means we walked away with two solutions. That means we can both guess the lifecycles and check our guess against another source.

## Solutions Compiled

When I started down this path early this morning, I thought that finding the lifecycle stages would take an hour tops. I thought I'd read some docs, look at the repo, find a well-defined and accessible list, and go do other stuff. I've logged the better part of a day on this problem now (granted, plenty of that was spent playing with `awk`), and I'd be remiss if I didn't leave the environment better for the next person with a similar question.

I've compiled this stuff (specifically the `find ... awk` and `awk ... doc` solutions) into a super tiny package ([GitHub](https://github.com/wizardsoftheweb/npm-lifecycle-stages#readme) | [NPM](https://www.npmjs.com/package/@wizardsoftheweb/npm-lifecycle-stages)). It exposes all the lifecycle stages as both an array and an enum whose keys are initialized with themselves. It has no dependencies, its version should match `npm`, it's got fairly autonomous logic, and, eventually, I'll get around to building historical versions.

```bash
npm install --save @wizardsoftheweb/npm-lifecycle-stages
```

### Examples

```TypeScript
import { ENpmLifecycleStages } from "@wizardsoftheweb/npm-lifecycle-stages";

const stage = "somestage";
if (typeof ENpmLifecycleStages[stage as any] !== "undefined") {
    console.log("It's lifecycle stage!");
} else {
    console.log("You'll have to run this one yourself");
}
```

```TypeScript
import { NpmLifecycleStages } from "@wizardsoftheweb/npm-lifecycle-stages";

const allPostStages = NpmLifecycleStages.filter((current: string): boolean => {
    return current.match(/^post/);
});
console.log(`All the 'post' stages are ${allPostStages.join(", ").replace(/, (\w+)$/, ", and $1")});
```

## Final Thoughts

If you know of a better way to access the lifecycle stages, I'd love to hear about it. As much fun as I had with `awk`, it requires so much extra setup that it's not a good, long-term solution.

Sometime later this week I'll be trying to add some older versions to the package to support older `npm` versions. I don't know how volatile the lifecycle stages have been, so I'm not sure how far I'll get.

If you end up using the package, I'd love to see what you do with it. If it's missing something, make a PR or fork it. My email is in the `package.json` (and below).
