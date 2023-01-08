---
title: "TypeScript Decorators: Parameter Decorators"
slug: "typescript-decorators-parameter-decorators"
date: "2018-03-10T23:00:00.000Z"
feature_image: "/images/2018/03/header-7.png"
author: "CJ Harries"
description: "This post takes an in-depth look at parameter decorators. It examines their signature and provides a couple of useful examples."
tags: 
  - TypeScript
  - JavaScript
  - Node
  - decorators
  - OOP
  - parameter
  - signature
  - compiler
draft: true
---

This post takes an in-depth look at parameter decorators. It examines their signature and provides a couple of useful examples. Reading the previous posts in the series is encouraged but not necessary.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#theseriessofar)
- [Code](#code)
- [Overview](#overview)
  - [Class Method vs Global Function](#classmethodvsglobalfunction)
- [Signature](#signature)
  - [`target: any`](#targetany)
  - [`propertyKey: string | symbol`](#propertykeystringsymbol)
  - [`parameterIndex: number`](#parameterindexnumber)
- [Usage](#usage)
  - [`required`](#required)
  - [Arbitrary Metadata](#arbitrarymetadata)
- [Recap](#recap)
- [Legal](#legal)

## The Series so Far

1. [Decorator Introduction](https://blog.wizardsoftheweb.pro/typescript-decorators-introduction)
2. [JavaScript Foundation](https://blog.wizardsoftheweb.pro/typescript-decorators-javascript-foundation)
3. [Reflection](https://blog.wizardsoftheweb.pro/typescript-decorators-reflection)
4. [Parameter Decorators](https://blog.wizardsoftheweb.pro/typescript-decorators-parameter-decorators)
5. Property Decorators
6. Method Decorators
7. Class Decorators

Eventual Topics:

* Where Decorators Work
* Decorating Instance Elements vs. Static Elements
* Examples
    * Pairing Parameter Decorators with Method Decorators
    * Pairing Property Decorators with Class Decorators

## Code

You can view the code related to this post [under the `post-04-parameter-decorators` tag](//github.com/thecjharries/posts-typescript-decorators/tree/post-04-parameter-decorators).

## Overview

Parameter decorators are the most restricted decorators. [The official docs](https://www.typescriptlang.org/docs/handbook/decorators.html#parameter-decorators) state

> [a] parameter decorator can only be used to observe that a parameter has been declared on a method.

Parameter decorators ignore any return, underscoring their inability to affect the decorated parameters. [As we saw previously](https://blog.wizardsoftheweb.pro/typescript-decorators-reflection/#examplevalidateaparameterrange), parameter decorators can be used in tandem with other decorators to define extra information about the parameter. By themselves, their effectiveness is limited. [Logging parameter data](https://blog.wizardsoftheweb.pro/typescript-decorators-javascript-foundation/#parameterdecorators) seems to be the best use for a parameter decorator by itself.

(If you've got a different or novel use for parameter decorators, I'd love to hear about it. Seriously. I'm really curious to see how other devs are using these. My email's in the footer.)

### Class Method vs Global Function

An interesting side-effect of decorators is that they (apparently) must be defined on class elements. You can't decorate globals unattached to a class.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">class-only.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/overview/class-only.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">function</span> <span class="nx">DecoratedParameter</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">target</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">propertyKey</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">parameterIndex</span><span class="p">);</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">TargetDemo</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo1</span><span class="p">(</span><span class="nx">baz</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span> <span class="kd" style="color:#66d9ef">@DecoratedParameter</span> <span class="nx">bar</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">)</span> <span class="p">{</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Class method foo"</span><span class="p">);</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="kd" style="color:#66d9ef">function</span> <span class="nx">foo2</span><span class="p">(</span><span class="nx">baz</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span> <span class="kd" style="color:#66d9ef">@DecoratedParameter</span> <span class="nx">bar</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Global function foo"</span><span class="p">);</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">test</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">TargetDemo</span><span class="p">();</span><br><span class="nx">test</span><span class="p">.</span><span class="nx">foo1</span><span class="p">(</span><span class="s2" style="color:#e6db74">"class baz"</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"class bar"</span><span class="p">);</span><br><span class="nx">foo2</span><span class="p">(</span><span class="s2" style="color:#e6db74">"function baz"</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"function bar"</span><span class="p">);</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ts-node class-only.ts<br><span class="go" style="color:#888">TargetDemo { foo1: [Function] }</span><br><span class="go" style="color:#888">foo1</span><br><span class="go" style="color:#888">1</span><br><span class="go" style="color:#888">Class method foo</span><br><span class="go" style="color:#888">Global function foo</span><br></pre></div>
</td></tr></table>

Even though we've attempted to decorate the global function `foo`, it doesn't work. Notice how the decorated logging is only called once, not twice, and only with `foo1`. I suspect this is related to how all of these things are defined, and I plan to investigate this more in another post.

## Signature

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">signature.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/signature/signature.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nx">type</span> <span class="nx">ParameterDecoratorType</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br><span class="p">)</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="k" style="color:#66d9ef">void</span><span class="p">;</span><br></pre></div>
</td>
</tr>
</table>

This example is used to explain the signature.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">signature-example.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/signature/signature-example.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">function</span> <span class="nx">DecoratedParameter</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// do nothing</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">TargetDemo</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo</span><span class="p">(</span><span class="nx">baz</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span> <span class="kd" style="color:#66d9ef">@DecoratedParameter</span> <span class="nx">bar</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

### `target: any`

`target` is the object (not method) that owns the method whose parameter has been decorated. `target` in the example is `TargetDemo`, not `foo`.

### `propertyKey: string | symbol`

`propertyKey` is the method name (not object name) whose signature has been decorated. It could also be [a `Symbol`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Symbol), depending on how the method is defined on the object. `propertyKey` in the example is `foo`, not `TargetDemo`.

### `parameterIndex: number`

`parameterIndex` is the index of the decorated parameter in the signature of the calling method. `parameterIndex` in the example is `1`.

## Usage

I spent last week trying to figure out an interesting or useful parameter decorator that functions in a vacuum, i.e. one not used with other decorators (well, not the whole week, just when I wanted to work on a really difficult problem that doesn't seem to have a good solution). I still have nothing. Parameter decorators are triggered when the parameter is declared, but they don't affect anything. We can't observe the parameter's value, because that's attached long after the parameter is decorated. We can't change the state, because that's also not created until long after the parameter is decorated. Long story short, we can define metadata and that's about it.

If you haven't read [the reflection post](https://blog.wizardsoftheweb.pro/typescript-decorators-reflection/), give it a quick skim. We'll either have to build our own metadata interface in vanilla TypeScript or use [the `reflect-metadata` package](https://www.npmjs.com/package/reflect-metadata). One requires a bunch of extra work totally unrelated to the code we're writing and the other is a simple import.

Once again (I'm getting tired of reiterating this), parameter decorators are observers. We can define metadata, but we're not really able to consume any. Parameter decorators are executed [before anything else](https://www.typescriptlang.org/docs/handbook/decorators.html#decorator-evaluation), so I suppose you could consume other parameter metadata but that's just silly (I'd wager that execution order isn't well-defined across platforms, modules, and standards).

### `required`

[The official docs](https://www.typescriptlang.org/docs/handbook/decorators.html#parameter-decorators) give a very useful example. One of the features TypeScript adds is required arguments, e.g. if I define `function foo(bar: string)`, I can't compile `foo()`. However, the underlying JavaScript doesn't respect those restrictions. Anything downstream that uses the JavaScript instead of the TypeScript could easily sidestep those restriction (accidentally or not), and there are plenty of ways around them in TypeScript itself.

Using decorators, we can at least note that parameter is required or not. Whether or not something is done with that metadata is outside the scope of parameter decorators, so I'm skipping that here. This is one way to tag them. It's loosely based on [the official docs](https://www.typescriptlang.org/docs/handbook/decorators.html#parameter-decorators) but approaches things differently enough that I'm comfortable calling this my own. Honestly there are only so many way to create an array, add values, and pass it on.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">required/constants.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/usage/required/constants.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kr" style="color:#66d9ef">const</span> <span class="nx">REQUIRED_KEY</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Symbol</span><span class="p">(</span><span class="s2" style="color:#e6db74">"requiredParameter"</span><span class="p">);</span><br></pre></div>
</td>
</tr>
</table>

By `export`ing the `Symbol` we can use it anywhere we `import` it (and ensure it's the same everywhere).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">required/Required.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/usage/required/Required.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
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
31</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">REQUIRED_KEY</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./constants"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">Required</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// Pull existing parameters for this method or create an empty array</span><br>    <span class="kr" style="color:#66d9ef">const</span> <span class="nx">requiredParameters</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getOwnMetadata</span><span class="p">(</span><br>            <span class="nx">REQUIRED_KEY</span><span class="p">,</span><br>            <span class="nx">target</span><span class="p">,</span><br>            <span class="nx">propertyKey</span><span class="p">,</span><br>        <span class="p">)</span><br>        <span class="o" style="color:#f92672">||</span><br>        <span class="p">[]</span><br>    <span class="p">);</span><br>    <span class="c1" style="color:#75715e">// Add this parameter</span><br>    <span class="nx">requiredParameters</span><span class="p">.</span><span class="nx">push</span><span class="p">(</span><span class="nx">parameterIndex</span><span class="p">);</span><br>    <span class="c1" style="color:#75715e">// Ensure regular order</span><br>    <span class="nx">requiredParameters</span><span class="p">.</span><span class="nx">sort</span><span class="p">();</span><br>    <span class="c1" style="color:#75715e">// Update the required parameters for this method</span><br>    <span class="nx">Reflect</span><span class="p">.</span><span class="nx">defineMetadata</span><span class="p">(</span><br>        <span class="nx">REQUIRED_KEY</span><span class="p">,</span><br>        <span class="nx">requiredParameters</span><span class="p">,</span><br>        <span class="nx">target</span><span class="p">,</span><br>        <span class="nx">propertyKey</span><span class="p">,</span><br>    <span class="p">);</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

You don't actually have to `sort` the array, but the order might not be what you expect (it was reversed the one time I ran it). If you're consuming it via [a `for...of` loop](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for...of), you really don't have to `sort` it.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">required/main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/usage/required/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
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
32</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">REQUIRED_KEY</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./constants"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">Required</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./Required"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">Demo</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo</span><span class="p">(</span><br>        <span class="kd" style="color:#66d9ef">@Required</span> <span class="nx">bar1</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>        <span class="nx">bar2</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>        <span class="kd" style="color:#66d9ef">@Required</span> <span class="nx">bar3</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="c1" style="color:#75715e">// Not defined on the class itself</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><br>    <span class="nx">REQUIRED_KEY</span><span class="p">,</span><br>    <span class="nx">Demo</span><span class="p">,</span><br>    <span class="s2" style="color:#e6db74">"foo"</span><span class="p">,</span><br><span class="p">));</span><br><span class="c1" style="color:#75715e">// undefined</span><br><br><span class="c1" style="color:#75715e">// Create an instance</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Demo</span><span class="p">();</span><br><span class="c1" style="color:#75715e">// Defined on instances of the class</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><br>    <span class="nx">REQUIRED_KEY</span><span class="p">,</span><br>    <span class="nx">demo</span><span class="p">,</span><br>    <span class="s2" style="color:#e6db74">"foo"</span><span class="p">,</span><br><span class="p">));</span><br><span class="c1" style="color:#75715e">// [ 0, 2 ]</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ts-node required/main.ts<br><span class="go" style="color:#888">undefined</span><br><span class="go" style="color:#888">[ 0, 2 ]</span><br></pre></div>
</td></tr></table>

### Arbitrary Metadata

I've already written [an example adding some validation metadata](https://blog.wizardsoftheweb.pro/typescript-decorators-reflection/#examplevalidateaparameterrange). The official docs cover [pulling existing metadata](https://www.typescriptlang.org/docs/handbook/decorators.html#metadata). You can basically add anything you'd like.

The example below illustrates two different approaches to add specific parameter metadata. You can either create a decorator that takes everything (`ParameterMetadata`) or chain individual decorators (`Name`, `Description`) to attach only the desired information (of course you could tweak `ParameterMetadata`'s signature to request an object and pull `name` and `description` out of that instead).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">arbitrary/constants.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/usage/arbitrary/constants.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kr" style="color:#66d9ef">const</span> <span class="nx">PARAMETER_NAME_KEY</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Symbol</span><span class="p">(</span><span class="s2" style="color:#e6db74">"parameterName"</span><span class="p">);</span><br><span class="kr" style="color:#66d9ef">export</span> <span class="kr" style="color:#66d9ef">const</span> <span class="nx">PARAMETER_DESCRIPTION_KEY</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Symbol</span><span class="p">(</span><span class="s2" style="color:#e6db74">"parameterDescription"</span><span class="p">);</span><br><span class="kr" style="color:#66d9ef">export</span> <span class="kr" style="color:#66d9ef">const</span> <span class="nx">PARAMETER_METADATA_KEY</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Symbol</span><span class="p">(</span><span class="s2" style="color:#e6db74">"parameterMetadata"</span><span class="p">);</span><br></pre></div>
</td>
</tr>
</table>

First we define the metadata keys and `export` them for anything to `import`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">arbitrary/interfaces.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/usage/arbitrary/interfaces.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kr" style="color:#66d9ef">interface</span> <span class="nx">IParameterMetadata</span> <span class="p">{</span><br>    <span class="nx">name</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">;</span><br>    <span class="nx">description</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">;</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="nx">type</span> <span class="nx">SignatureMetadataType</span> <span class="o" style="color:#f92672">=</span> <span class="nx">IParameterMetadata</span><span class="p">[];</span><br></pre></div>
</td>
</tr>
</table>

This defines `IParameterMetadata` and aliases an array of `IParameterMetadata` as `SignatureMetadataType` to streamline manipulation. It's usually better to have types to rely on.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">arbitrary/Name.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/usage/arbitrary/Name.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
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
76
77
78
79</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">PARAMETER_METADATA_KEY</span><span class="p">,</span> <span class="nx">PARAMETER_NAME_KEY</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./constants"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">SignatureMetadataType</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./interfaces"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">updateParameterNames</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br>    <span class="nx">name</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// Pull the array of parameter names</span><br>    <span class="kr" style="color:#66d9ef">const</span> <span class="nx">parameterNames</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getOwnMetadata</span><span class="p">(</span><br>            <span class="nx">PARAMETER_NAME_KEY</span><span class="p">,</span><br>            <span class="nx">target</span><span class="p">,</span><br>            <span class="nx">propertyKey</span><span class="p">,</span><br>        <span class="p">)</span><br>        <span class="o" style="color:#f92672">||</span><br>        <span class="p">[]</span><br>    <span class="p">);</span><br>    <span class="c1" style="color:#75715e">// Add the current parameter name</span><br>    <span class="nx">parameterNames</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">]</span> <span class="o" style="color:#f92672">=</span> <span class="nx">name</span><span class="p">;</span><br>    <span class="c1" style="color:#75715e">// Update the parameter names</span><br>    <span class="nx">Reflect</span><span class="p">.</span><span class="nx">defineMetadata</span><span class="p">(</span><br>        <span class="nx">PARAMETER_NAME_KEY</span><span class="p">,</span><br>        <span class="nx">parameterNames</span><span class="p">,</span><br>        <span class="nx">target</span><span class="p">,</span><br>        <span class="nx">propertyKey</span><span class="p">,</span><br>    <span class="p">);</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">Name</span><span class="p">(</span><span class="nx">name</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="p">(</span><br>        <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>        <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>        <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br>    <span class="p">)</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// Update the parameter name metadata</span><br>        <span class="nx">updateParameterNames</span><span class="p">(</span><br>            <span class="nx">target</span><span class="p">,</span><br>            <span class="nx">propertyKey</span><span class="p">,</span><br>            <span class="nx">parameterIndex</span><span class="p">,</span><br>            <span class="nx">name</span><span class="p">,</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// Pull the signature's metadata</span><br>        <span class="kr" style="color:#66d9ef">const</span> <span class="nx">parameterMetadata</span>: <span class="kt" style="color:#66d9ef">SignatureMetadataType</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>            <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getOwnMetadata</span><span class="p">(</span><br>                <span class="nx">PARAMETER_METADATA_KEY</span><span class="p">,</span><br>                <span class="nx">target</span><span class="p">,</span><br>                <span class="nx">propertyKey</span><span class="p">,</span><br>            <span class="p">)</span><br>            <span class="o" style="color:#f92672">||</span><br>            <span class="p">[]</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// Either</span><br>        <span class="c1" style="color:#75715e">// * update an entry that has a description, or</span><br>        <span class="c1" style="color:#75715e">// * create a new entry with an empty description</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><br>            <span class="nx">parameterMetadata</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">]</span><br>            <span class="o" style="color:#f92672">&amp;&amp;</span><br>            <span class="nx">parameterMetadata</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">].</span><span class="nx">description</span><br>        <span class="p">)</span> <span class="p">{</span><br>            <span class="nx">parameterMetadata</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">].</span><span class="nx">name</span> <span class="o" style="color:#f92672">=</span> <span class="nx">name</span><span class="p">;</span><br>        <span class="p">}</span> <span class="k" style="color:#66d9ef">else</span> <span class="p">{</span><br>            <span class="nx">parameterMetadata</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">]</span> <span class="o" style="color:#f92672">=</span> <span class="p">{</span><br>                <span class="nx">description</span><span class="o" style="color:#f92672">:</span> <span class="s2" style="color:#e6db74">""</span><span class="p">,</span><br>                <span class="nx">name</span><span class="p">,</span><br>            <span class="p">};</span><br>        <span class="p">}</span><br>        <span class="c1" style="color:#75715e">// Update the signature metadata</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">defineMetadata</span><span class="p">(</span><br>            <span class="nx">PARAMETER_METADATA_KEY</span><span class="p">,</span><br>            <span class="nx">parameterMetadata</span><span class="p">,</span><br>            <span class="nx">target</span><span class="p">,</span><br>            <span class="nx">propertyKey</span><span class="p">,</span><br>        <span class="p">);</span><br>    <span class="p">};</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

The `Name` decorator updates the list of parameter names and also updates the list of signature metadata, since I decided to make things complicated.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">arbitrary/Description.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/usage/arbitrary/Description.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
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
76
77
78
79</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">PARAMETER_DESCRIPTION_KEY</span><span class="p">,</span> <span class="nx">PARAMETER_METADATA_KEY</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./constants"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">SignatureMetadataType</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./interfaces"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">updateParameterDescriptions</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br>    <span class="nx">description</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// Pull the array of parameter names</span><br>    <span class="kr" style="color:#66d9ef">const</span> <span class="nx">parameterDescriptions</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getOwnMetadata</span><span class="p">(</span><br>            <span class="nx">PARAMETER_DESCRIPTION_KEY</span><span class="p">,</span><br>            <span class="nx">target</span><span class="p">,</span><br>            <span class="nx">propertyKey</span><span class="p">,</span><br>        <span class="p">)</span><br>        <span class="o" style="color:#f92672">||</span><br>        <span class="p">[]</span><br>    <span class="p">);</span><br>    <span class="c1" style="color:#75715e">// Add the current parameter name</span><br>    <span class="nx">parameterDescriptions</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">]</span> <span class="o" style="color:#f92672">=</span> <span class="nx">description</span><span class="p">;</span><br>    <span class="c1" style="color:#75715e">// Update the parameter descriptions</span><br>    <span class="nx">Reflect</span><span class="p">.</span><span class="nx">defineMetadata</span><span class="p">(</span><br>        <span class="nx">PARAMETER_DESCRIPTION_KEY</span><span class="p">,</span><br>        <span class="nx">parameterDescriptions</span><span class="p">,</span><br>        <span class="nx">target</span><span class="p">,</span><br>        <span class="nx">propertyKey</span><span class="p">,</span><br>    <span class="p">);</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">Description</span><span class="p">(</span><span class="nx">description</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="p">(</span><br>        <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>        <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>        <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br>    <span class="p">)</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// Update the parameter description metadata</span><br>        <span class="nx">updateParameterDescriptions</span><span class="p">(</span><br>            <span class="nx">target</span><span class="p">,</span><br>            <span class="nx">propertyKey</span><span class="p">,</span><br>            <span class="nx">parameterIndex</span><span class="p">,</span><br>            <span class="nx">description</span><span class="p">,</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// Pull the signature's metadata</span><br>        <span class="kr" style="color:#66d9ef">const</span> <span class="nx">parameterMetadata</span>: <span class="kt" style="color:#66d9ef">SignatureMetadataType</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>            <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getOwnMetadata</span><span class="p">(</span><br>                <span class="nx">PARAMETER_METADATA_KEY</span><span class="p">,</span><br>                <span class="nx">target</span><span class="p">,</span><br>                <span class="nx">propertyKey</span><span class="p">,</span><br>            <span class="p">)</span><br>            <span class="o" style="color:#f92672">||</span><br>            <span class="p">[]</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// Either</span><br>        <span class="c1" style="color:#75715e">// * update an entry that has a name, or</span><br>        <span class="c1" style="color:#75715e">// * create a new entry with an empty name</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><br>            <span class="nx">parameterMetadata</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">]</span><br>            <span class="o" style="color:#f92672">&amp;&amp;</span><br>            <span class="nx">parameterMetadata</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">].</span><span class="nx">name</span><br>        <span class="p">)</span> <span class="p">{</span><br>            <span class="nx">parameterMetadata</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">].</span><span class="nx">description</span> <span class="o" style="color:#f92672">=</span> <span class="nx">description</span><span class="p">;</span><br>        <span class="p">}</span> <span class="k" style="color:#66d9ef">else</span> <span class="p">{</span><br>            <span class="nx">parameterMetadata</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">]</span> <span class="o" style="color:#f92672">=</span> <span class="p">{</span><br>                <span class="nx">description</span><span class="p">,</span><br>                <span class="nx">name</span><span class="o" style="color:#f92672">:</span> <span class="s2" style="color:#e6db74">""</span><span class="p">,</span><br>            <span class="p">};</span><br>        <span class="p">}</span><br>        <span class="c1" style="color:#75715e">// Update the signature metadata</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">defineMetadata</span><span class="p">(</span><br>            <span class="nx">PARAMETER_METADATA_KEY</span><span class="p">,</span><br>            <span class="nx">parameterMetadata</span><span class="p">,</span><br>            <span class="nx">target</span><span class="p">,</span><br>            <span class="nx">propertyKey</span><span class="p">,</span><br>        <span class="p">);</span><br>    <span class="p">};</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

The `Description` decorator is almost identical to `Name`. It, rather unsurprisingly, updates descriptions instead of names.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">arbitrary/ParameterMetadata.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/usage/arbitrary/ParameterMetadata.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
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
52</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">PARAMETER_METADATA_KEY</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./constants"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">SignatureMetadataType</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./interfaces"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">updateParameterDescriptions</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./Description"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">updateParameterNames</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./Name"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">ParameterMetadata</span><span class="p">(</span><span class="nx">name</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">,</span> <span class="nx">description</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="p">(</span><br>        <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>        <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>        <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br>    <span class="p">)</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// Update the parameter name metadata</span><br>        <span class="nx">updateParameterNames</span><span class="p">(</span><br>            <span class="nx">target</span><span class="p">,</span><br>            <span class="nx">propertyKey</span><span class="p">,</span><br>            <span class="nx">parameterIndex</span><span class="p">,</span><br>            <span class="nx">name</span><span class="p">,</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// Update the parameter description metadata</span><br>        <span class="nx">updateParameterDescriptions</span><span class="p">(</span><br>            <span class="nx">target</span><span class="p">,</span><br>            <span class="nx">propertyKey</span><span class="p">,</span><br>            <span class="nx">parameterIndex</span><span class="p">,</span><br>            <span class="nx">description</span><span class="p">,</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// Pull the signature's metadata</span><br>        <span class="kr" style="color:#66d9ef">const</span> <span class="nx">parameterMetadata</span>: <span class="kt" style="color:#66d9ef">SignatureMetadataType</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>            <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getOwnMetadata</span><span class="p">(</span><br>                <span class="nx">PARAMETER_METADATA_KEY</span><span class="p">,</span><br>                <span class="nx">target</span><span class="p">,</span><br>                <span class="nx">propertyKey</span><span class="p">,</span><br>            <span class="p">)</span><br>            <span class="o" style="color:#f92672">||</span><br>            <span class="p">[]</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// Define or overwrite the metadata for this parameter</span><br>        <span class="nx">parameterMetadata</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">]</span> <span class="o" style="color:#f92672">=</span> <span class="p">{</span><br>            <span class="nx">description</span><span class="p">,</span><br>            <span class="nx">name</span><span class="p">,</span><br>        <span class="p">};</span><br>        <span class="c1" style="color:#75715e">// Update the signature metadata</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">defineMetadata</span><span class="p">(</span><br>            <span class="nx">PARAMETER_METADATA_KEY</span><span class="p">,</span><br>            <span class="nx">parameterMetadata</span><span class="p">,</span><br>            <span class="nx">target</span><span class="p">,</span><br>            <span class="nx">propertyKey</span><span class="p">,</span><br>        <span class="p">);</span><br>    <span class="p">};</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

The `ParameterMetadata` decorator updates both names and descriptions as well as signature metadata. As I mentioned earlier, it would be fairly straightforward to update its signature to request an `IParameterMetadata` object (instead of `[string, string]`), but I didn't think of that until I started annotating the example so I didn't do that.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">arbitrary/main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/parameters/usage/arbitrary/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">  1
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
 76
 77
 78
 79
 80
 81
 82
 83
 84
 85
 86
 87
 88
 89
 90
 91
 92
 93
 94
 95
 96
 97
 98
 99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span><br>    <span class="nx">PARAMETER_DESCRIPTION_KEY</span><span class="p">,</span><br>    <span class="nx">PARAMETER_METADATA_KEY</span><span class="p">,</span><br>    <span class="nx">PARAMETER_NAME_KEY</span><span class="p">,</span><br><span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./constants"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">Description</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./Description"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">Name</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./Name"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">ParameterMetadata</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./ParameterMetadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">ArbitraryMetadata</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">nameOnly</span><span class="p">(</span><br>        <span class="kd" style="color:#66d9ef">@Name</span><span class="p">(</span><span class="s2" style="color:#e6db74">"propertyWithNameOnly"</span><span class="p">)</span><br>        <span class="nx">propertyWithNameOnly</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">descriptionOnly</span><span class="p">(</span><br>        <span class="kd" style="color:#66d9ef">@Description</span><span class="p">(</span><span class="s2" style="color:#e6db74">"decorated with Description"</span><span class="p">)</span><br>        <span class="nx">propertyWithDescriptionOnly</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">usingParameterMetadata</span><span class="p">(</span><br>        <span class="kd" style="color:#66d9ef">@ParameterMetadata</span><span class="p">(</span><br>            <span class="s2" style="color:#e6db74">"decoratedWithParameterMetadata"</span><span class="p">,</span><br>            <span class="s2" style="color:#e6db74">"decorated with ParameterMetadata"</span><span class="p">,</span><br>        <span class="p">)</span><br>        <span class="nx">decoratedWithParameterMetadata</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">chainingDecorators</span><span class="p">(</span><br>        <span class="kd" style="color:#66d9ef">@Name</span><span class="p">(</span><span class="s2" style="color:#e6db74">"decoratedViaChain"</span><span class="p">)</span><br>        <span class="kd" style="color:#66d9ef">@Description</span><span class="p">(</span><span class="s2" style="color:#e6db74">"decorated with Name and Description"</span><span class="p">)</span><br>        <span class="nx">decoratedViaChain</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="c1" style="color:#75715e">// These are not defined on the class</span><br><span class="c1" style="color:#75715e">// names</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>    <span class="s2" style="color:#e6db74">"ArbitraryMetadata names:"</span><span class="p">,</span><br>    <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><br>        <span class="nx">PARAMETER_NAME_KEY</span><span class="p">,</span><br>        <span class="nx">ArbitraryMetadata</span><span class="p">,</span><br>    <span class="p">),</span><br><span class="p">);</span><br><span class="c1" style="color:#75715e">// descriptions</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>    <span class="s2" style="color:#e6db74">"ArbitraryMetadata descriptions:"</span><span class="p">,</span><br>    <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><br>        <span class="nx">PARAMETER_DESCRIPTION_KEY</span><span class="p">,</span><br>        <span class="nx">ArbitraryMetadata</span><span class="p">,</span><br>    <span class="p">),</span><br><span class="p">);</span><br><span class="c1" style="color:#75715e">// signature metadata</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>    <span class="s2" style="color:#e6db74">"metadata from ArbitraryMetadata signatures:"</span><span class="p">,</span><br>    <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><br>        <span class="nx">PARAMETER_METADATA_KEY</span><span class="p">,</span><br>        <span class="nx">ArbitraryMetadata</span><span class="p">,</span><br>    <span class="p">),</span><br><span class="p">);</span><br><span class="c1" style="color:#75715e">// They're defined on an instance</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoArbitraryMetadata</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">ArbitraryMetadata</span><span class="p">();</span><br><br><span class="c1" style="color:#75715e">// This could be created via decorators</span><br><span class="c1" style="color:#75715e">// Since it requires more than parameter decorators, it's hardcoded</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">METHODS</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><br>    <span class="s2" style="color:#e6db74">"nameOnly"</span><span class="p">,</span><br>    <span class="s2" style="color:#e6db74">"descriptionOnly"</span><span class="p">,</span><br>    <span class="s2" style="color:#e6db74">"usingParameterMetadata"</span><span class="p">,</span><br>    <span class="s2" style="color:#e6db74">"chainingDecorators"</span><span class="p">,</span><br><span class="p">];</span><br><br><span class="c1" style="color:#75715e">// Loop over each method</span><br><span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kr" style="color:#66d9ef">const</span> <span class="nx">method</span> <span class="nx">of</span> <span class="nx">METHODS</span><span class="p">)</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// Line break to make things easier to read</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"---"</span><span class="p">);</span><br>    <span class="c1" style="color:#75715e">// Log the parameter names</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>        <span class="sb" style="color:#e6db74">`</span><span class="si" style="color:#e6db74">${</span><span class="nx">method</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74"> names:`</span><span class="p">,</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><br>            <span class="nx">PARAMETER_NAME_KEY</span><span class="p">,</span><br>            <span class="nx">demoArbitraryMetadata</span><span class="p">,</span><br>            <span class="nx">method</span><span class="p">,</span><br>        <span class="p">),</span><br>    <span class="p">);</span><br>    <span class="c1" style="color:#75715e">// Log the parameter descriptions</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>        <span class="sb" style="color:#e6db74">`</span><span class="si" style="color:#e6db74">${</span><span class="nx">method</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74"> descriptions:`</span><span class="p">,</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><br>            <span class="nx">PARAMETER_DESCRIPTION_KEY</span><span class="p">,</span><br>            <span class="nx">demoArbitraryMetadata</span><span class="p">,</span><br>            <span class="nx">method</span><span class="p">,</span><br>        <span class="p">),</span><br>    <span class="p">);</span><br>    <span class="c1" style="color:#75715e">// Log the full signature metadata</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>        <span class="sb" style="color:#e6db74">`</span><span class="si" style="color:#e6db74">${</span><span class="nx">method</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74"> signature metadata:`</span><span class="p">,</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><br>            <span class="nx">PARAMETER_METADATA_KEY</span><span class="p">,</span><br>            <span class="nx">demoArbitraryMetadata</span><span class="p">,</span><br>            <span class="nx">method</span><span class="p">,</span><br>        <span class="p">),</span><br>    <span class="p">);</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

Putting everything together, we can use any of the decorators we'd like. We could chain any combination we'd like, but it's important to remember [how decorator chaining works](https://blog.wizardsoftheweb.pro/typescript-decorators-introduction/#composition); essentially the outermost (first, top, whatever) decorator will overwrite anything set by inner decorators.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ts-node arbitrary/main.ts<br><span class="go" style="color:#888">ArbitraryMetadata names: undefined</span><br><span class="go" style="color:#888">ArbitraryMetadata descriptions: undefined</span><br><span class="go" style="color:#888">metadata from ArbitraryMetadata signatures: undefined</span><br><span class="go" style="color:#888">---</span><br><span class="go" style="color:#888">nameOnly names: [ 'propertyWithNameOnly' ]</span><br><span class="go" style="color:#888">nameOnly descriptions: undefined</span><br><span class="go" style="color:#888">nameOnly signature metadata: [ { description: '', name: 'propertyWithNameOnly' } ]</span><br><span class="go" style="color:#888">---</span><br><span class="go" style="color:#888">descriptionOnly names: undefined</span><br><span class="go" style="color:#888">descriptionOnly descriptions: [ 'decorated with Description' ]</span><br><span class="go" style="color:#888">descriptionOnly signature metadata: [ { description: 'decorated with Description', name: '' } ]</span><br><span class="go" style="color:#888">---</span><br><span class="go" style="color:#888">usingParameterMetadata names: [ 'decoratedWithParameterMetadata' ]</span><br><span class="go" style="color:#888">usingParameterMetadata descriptions: [ 'decorated with ParameterMetadata' ]</span><br><span class="go" style="color:#888">usingParameterMetadata signature metadata: [ { description: 'decorated with ParameterMetadata', name: 'decoratedWithParameterMetadata' } ]</span><br><span class="go" style="color:#888">---</span><br><span class="go" style="color:#888">chainingDecorators names: [ 'decoratedViaChain' ]</span><br><span class="go" style="color:#888">chainingDecorators descriptions: [ 'decorated with Name and Description' ]</span><br><span class="go" style="color:#888">chainingDecorators signature metadata: [ { description: 'decorated with Name and Description', name: 'decoratedViaChain' } ]</span><br></pre></div>
</td></tr></table>

## Recap

Parameter decorators are great at adding extra information about parameters at runtime. They can't do a whole lot more. Parameter decorators are often used in combination with other decorators to perform new actions at runtime.

## Legal

The TS logo is a [modified `@typescript` avatar](https://www.npmjs.com/~typescript); I turned the PNG into a vector. I couldn't find the original and I didn't see any licensing on the other art, so it's most likely covered by [the TypeScript project's Apache 2.0 license](https://github.com/Microsoft/TypeScript/blob/master/LICENSE.txt). Any code from the TS project is similarly licensed.

If there's a problem with anything, my email's in the footer. Stay awesome.