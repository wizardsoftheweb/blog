---
title: "TypeScript Decorators: Property Decorators"
slug: "typescript-decorators-property-decorators"
date: "2018-03-11T01:00:00.000Z"
feature_image: "/images/2018/03/header-8.png"
author: "CJ Harries"
description: "This post takes an in-depth look at property decorators. It examines their signature, provides sample usage, and exposes a common antipattern."
tags:
  - TypeScript
  - JavaScript
  - Node
  - decorators
  - OOP
  - compiler
  - properties
  - signature
  - antipattern
draft: true
---

This post takes an in-depth look at property decorators. It examines their signature, provides sample usage, and exposes a common antipattern. Reading the previous posts in the series is encouraged but not necessary.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#the-series-so-far)
- [Code](#code)
- [Overview](#overview)
- [Signature](#signature)
  - [`target: any`](#target-any)
  - [`propertyKey: string | symbol`](#propertykey-string--symbol)
- [Usage](#usage)
- [Antipattern](#antipattern)
  - [Example](#example)
  - [Solution](#solution)
- [Recap](#recap)
- [Legal](#legal)

## The Series so Far

1. [Decorator Introduction](https://blog.wizardsoftheweb.pro/typescript-decorators-introduction)
2. [JavaScript Foundation](https://blog.wizardsoftheweb.pro/typescript-decorators-javascript-foundation)
3. [Reflection](https://blog.wizardsoftheweb.pro/typescript-decorators-reflection)
4. [Parameter Decorators](https://blog.wizardsoftheweb.pro/typescript-decorators-parameter-decorators)
5. [Property Decorators](https://blog.wizardsoftheweb.pro/typescript-decorators-property-decorators)

These posts are planned but not written yet:

* Method Decorators
* Class Decorators

## Code

You can view the code related to this post [under the `post-05-property-decorators` tag](//github.com/thecjharries/posts-typescript-decorators/tree/post-05-property-decorators).

## Overview

Property decorators are very similar to [parameter decorators](https://blog.wizardsoftheweb.pro/typescript-decorators-parameter-decorators) in that they're only able to observe declarations (or rather, should only observe declarations). [The official docs](https://www.typescriptlang.org/docs/handbook/decorators.html#property-decorators) state

> a property decorator can only be used to observe that a property of a specific name has been declared for a class.

Property decorators ignore any return, underscoring their inability to affect the decorated properties. [Similar to parameter decorators](https://blog.wizardsoftheweb.pro/typescript-decorators-reflection/#examplevalidateaparameterrange), property decorators can be used in tandem with other decorators to define extra information about the property. By themselves, their effectiveness is limited. [Logging property data](https://blog.wizardsoftheweb.pro/typescript-decorators-javascript-foundation/#propertydecorators) seems to be the best use for a property decorator by itself.

A widely used antipattern is to update a property descriptor on `target` in a property decorator. This wreaks havoc on all sorts of things. Instead, property decorators should set metadata that can be consumed elsewhere. Don't use them to do too much.

## Signature

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">signature.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/properties/signature/signature.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nx">type</span> <span class="nx">PropertyDecoratorType</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br><span class="p">)</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="k" style="color:#66d9ef">void</span><span class="p">;</span><br></pre></div>
</td>
</tr>
</table>

This example is used to explain the signature.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">signature-example.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/properties/signature/signature-example.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
11</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">function</span> <span class="nx">DecoratedProperty</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// do nothing</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">TargetDemo</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">@DecoratedProperty</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"bar"</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

### `target: any`

`target` is the object that owns the decorated property. `target` in the example is `TargetDemo`.

### `propertyKey: string | symbol`

`propertyKey` is the name of the decorated property. It could also be [a `Symbol`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Symbol), depending on how the property is defined on the object. `propertyKey` in the example is `foo`.

## Usage

As property decorators do not affect the underlying object, their primary use is to create and attach metadata. Consuming said metadata involves other decorators, so it's skipped here. The example below illustrates an easy way to attach metadata to properties.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">arbitrary/constants.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/properties/usage/arbitrary/constants.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kr" style="color:#66d9ef">const</span> <span class="nx">PROPERTY_METADATA_KEY</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Symbol</span><span class="p">(</span><span class="s2" style="color:#e6db74">"propertyMetadata"</span><span class="p">);</span><br></pre></div>
</td>
</tr>
</table>

First we define the metadata key and `export` it for anything to `import`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">arbitrary/interfaces.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/properties/usage/arbitrary/interfaces.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kr" style="color:#66d9ef">interface</span> <span class="nx">ISinglePropertyMetadata</span> <span class="p">{</span><br>    <span class="nx">name?</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">;</span><br>    <span class="nx">description?</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">;</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kr" style="color:#66d9ef">interface</span> <span class="nx">IAllPropertyMetadata</span> <span class="p">{</span><br>    <span class="p">[</span><span class="nx">key</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">]</span><span class="o" style="color:#f92672">:</span> <span class="nx">ISinglePropertyMetadata</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

This defines `ISinglePropertyMetadata` and `IAllPropertyMetadata` to streamline manipulation. It's usually better to have types to rely on.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">arbitrary/PropertyMetadata.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/properties/usage/arbitrary/PropertyMetadata.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">PROPERTY_METADATA_KEY</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./constants"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">ISinglePropertyMetadata</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./interfaces"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">PropertyMetadata</span><span class="p">(</span><span class="nx">updates</span>: <span class="kt" style="color:#66d9ef">ISinglePropertyMetadata</span><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="p">(</span><span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span> <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">)</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// Pull the existing metadata or create an empty object</span><br>        <span class="kr" style="color:#66d9ef">const</span> <span class="nx">allMetadata</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>            <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><span class="nx">PROPERTY_METADATA_KEY</span><span class="p">,</span> <span class="nx">target</span><span class="p">)</span><br>            <span class="o" style="color:#f92672">||</span><br>            <span class="p">{}</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// Ensure allMetadata has propertyKey</span><br>        <span class="nx">allMetadata</span><span class="p">[</span><span class="nx">propertyKey</span><span class="p">]</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>            <span class="nx">allMetadata</span><span class="p">[</span><span class="nx">propertyKey</span><span class="p">]</span><br>            <span class="o" style="color:#f92672">||</span><br>            <span class="p">{}</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// Update the metadata with anything from updates</span><br>        <span class="c1" style="color:#75715e">// tslint:disable-next-line:forin</span><br>        <span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kr" style="color:#66d9ef">const</span> <span class="nx">key</span> <span class="nx">of</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">ownKeys</span><span class="p">(</span><span class="nx">updates</span><span class="p">))</span> <span class="p">{</span><br>            <span class="nx">allMetadata</span><span class="p">[</span><span class="nx">propertyKey</span><span class="p">][</span><span class="nx">key</span><span class="p">]</span> <span class="o" style="color:#f92672">=</span> <span class="nx">updates</span><span class="p">[</span><span class="nx">key</span><span class="p">];</span><br>        <span class="p">}</span><br>        <span class="c1" style="color:#75715e">// Update the metadata</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">defineMetadata</span><span class="p">(</span><br>            <span class="nx">PROPERTY_METADATA_KEY</span><span class="p">,</span><br>            <span class="nx">allMetadata</span><span class="p">,</span><br>            <span class="nx">target</span><span class="p">,</span><br>        <span class="p">);</span><br>    <span class="p">}</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

The `PropertyMetadata` decorator updates both a property's metadata name and description. It consumes an `ISinglePropertyMetadata` object to load the values.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">arbitrary/main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/properties/usage/arbitrary/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">PROPERTY_METADATA_KEY</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./constants"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">PropertyMetadata</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./PropertyMetadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">Demo</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">@PropertyMetadata</span><span class="p">({</span><br>        <span class="nx">name</span><span class="o" style="color:#f92672">:</span> <span class="s2" style="color:#e6db74">"foo"</span><span class="p">,</span><br>    <span class="p">})</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">;</span><br>    <span class="kd" style="color:#66d9ef">@PropertyMetadata</span><span class="p">({</span><br>        <span class="nx">description</span><span class="o" style="color:#f92672">:</span> <span class="s2" style="color:#e6db74">"property bar"</span><span class="p">,</span><br>    <span class="p">})</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">bar</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">;</span><br>    <span class="kd" style="color:#66d9ef">@PropertyMetadata</span><span class="p">({</span><br>        <span class="nx">name</span><span class="o" style="color:#f92672">:</span> <span class="s2" style="color:#e6db74">"baz"</span><span class="p">,</span><br>        <span class="nx">description</span><span class="o" style="color:#f92672">:</span> <span class="s2" style="color:#e6db74">"property baz"</span><span class="p">,</span><br>    <span class="p">})</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">baz</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">;</span><br><span class="p">}</span><br><br><span class="c1" style="color:#75715e">// The metadata is not defined on the class</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>    <span class="s2" style="color:#e6db74">"Class property metadata:"</span><span class="p">,</span><br>    <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><span class="nx">PROPERTY_METADATA_KEY</span><span class="p">,</span> <span class="nx">Demo</span><span class="p">),</span><br><span class="p">);</span><br><span class="c1" style="color:#75715e">// It's defined on an instance</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Demo</span><span class="p">();</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>    <span class="s2" style="color:#e6db74">"Instance property metadata:"</span><span class="p">,</span><br>    <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><span class="nx">PROPERTY_METADATA_KEY</span><span class="p">,</span> <span class="nx">demo</span><span class="p">),</span><br><span class="p">);</span><br></pre></div>
</td>
</tr>
</table>

Putting everything together, we can decorate at will.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ts-node arbitrary/main.ts<br><span class="go" style="color:#888">Class property metadata: undefined</span><br><span class="go" style="color:#888">Instance property metadata: { foo: { name: 'foo' },</span><br><span class="go" style="color:#888">  bar: { description: 'property bar' },</span><br><span class="go" style="color:#888">  baz: { name: 'baz', description: 'property baz' } }</span><br></pre></div>
</td></tr></table>

## Antipattern

Property decorators cannot modify the owning object as their return is ignored. Ergo any changes made on `target` are actually made globally. You might have seen [this common property decorator example](https://gist.github.com/remojansen/16c661a7afd68e22ac6e#file-property_decorator-ts); it defines a property on `target` using the decorator's scope to maintain state (note that example will not work in strict mode). However, for a single class, the decorator is only called once. This means any instance of the class reuses the same decorator scope, essentially changing an instance property into a static property that can be updated.

### Example

This will make more sense with an example. Rather than rehash the copypasta that [pops up everywhere](https://stackoverflow.com/q/45830878/2877698), I applied the logic to a (possibly?) common use-case. Many classes include numeric properties; many of those properties should not fall below a minimum value. We can erroneously solve this problem using something like the following.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">MinimumValue.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/properties/antipattern/MinimumValue.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">MinimumValue</span><span class="p">(</span><span class="nx">min</span>: <span class="kt" style="color:#66d9ef">number</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">)</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// Scope the value to be reused</span><br>    <span class="kd" style="color:#66d9ef">let</span> <span class="nx">value</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="p">(</span><span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span> <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">)</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// Store the definition result</span><br>        <span class="kr" style="color:#66d9ef">const</span> <span class="nx">update</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">defineProperty</span><span class="p">(</span><br>            <span class="nx">target</span><span class="p">,</span><br>            <span class="nx">propertyKey</span><span class="p">,</span><br>            <span class="p">{</span><br>                <span class="nx">configurable</span>: <span class="kt" style="color:#66d9ef">true</span><span class="p">,</span><br>                <span class="nx">enumerable</span>: <span class="kt" style="color:#66d9ef">true</span><span class="p">,</span><br>                <span class="nx">get</span><span class="o" style="color:#f92672">:</span> <span class="p">()</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>                    <span class="c1" style="color:#75715e">// Return the scoped value</span><br>                    <span class="k" style="color:#66d9ef">return</span> <span class="nx">value</span><span class="p">;</span><br>                <span class="p">},</span><br>                <span class="nx">set</span><span class="o" style="color:#f92672">:</span> <span class="p">(</span><span class="nx">newValue</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">)</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>                    <span class="c1" style="color:#75715e">// Update the scoped value with max(newValue, min)</span><br>                    <span class="nx">value</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>                        <span class="nx">newValue</span> <span class="o" style="color:#f92672">&gt;=</span> <span class="nx">min</span><br>                            <span class="o" style="color:#f92672">?</span> <span class="nx">newValue</span><br>                            : <span class="kt" style="color:#66d9ef">min</span><br>                    <span class="p">);</span><br>                <span class="p">}</span><br>            <span class="p">},</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// If the update failed, something went wrong</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="o" style="color:#f92672">!</span><span class="nx">update</span><span class="p">)</span> <span class="p">{</span><br>            <span class="c1" style="color:#75715e">// Kill everything</span><br>            <span class="k" style="color:#66d9ef">throw</span> <span class="k" style="color:#66d9ef">new</span> <span class="nb" style="color:#f8f8f2">Error</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Unable to update property"</span><span class="p">);</span><br>        <span class="p">}</span><br>    <span class="p">}</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

This factory defines `propertyKey` on `target` with the newly created property descriptor, using the scoped `value`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">HasDecoratedProperty.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/properties/antipattern/HasDecoratedProperty.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">MinimumValue</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./MinimumValue"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kr" style="color:#66d9ef">class</span> <span class="nx">HasDecoratedProperty</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">@MinimumValue</span><span class="p">(</span><span class="mi" style="color:#ae81ff">0</span><span class="p">)</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">currentValue</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

This class simply applies the decorator to its `currentValue` property.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/properties/antipattern/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
34</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">HasDecoratedProperty</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./HasDecoratedProperty"</span><span class="p">;</span><br><br><span class="c1" style="color:#75715e">// Pick a set of values</span><br><span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kr" style="color:#66d9ef">const</span> <span class="nx">newValue</span> <span class="nx">of</span> <span class="p">[</span><span class="o" style="color:#f92672">-</span><span class="mi" style="color:#ae81ff">10</span><span class="p">,</span> <span class="mi" style="color:#ae81ff">10</span><span class="p">,</span> <span class="mi" style="color:#ae81ff">20</span><span class="p">])</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// Create a new instance</span><br>    <span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">HasDecoratedProperty</span><span class="p">();</span><br>    <span class="c1" style="color:#75715e">// Add a basic linebreak</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">newValue</span> <span class="o" style="color:#f92672">&gt;</span> <span class="o" style="color:#f92672">-</span><span class="mi" style="color:#ae81ff">10</span><span class="p">)</span> <span class="p">{</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"---"</span><span class="p">);</span><br>    <span class="p">}</span><br>    <span class="c1" style="color:#75715e">// Log the current value</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Current value:"</span><span class="p">,</span> <span class="nx">demo</span><span class="p">.</span><span class="nx">currentValue</span><span class="p">);</span><br>    <span class="c1" style="color:#75715e">// Update the value</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="sb" style="color:#e6db74">`Attempting to set demo.currentValue = </span><span class="si" style="color:#e6db74">${</span><span class="nx">newValue</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">`</span><span class="p">);</span><br>    <span class="nx">demo</span><span class="p">.</span><span class="nx">currentValue</span> <span class="o" style="color:#f92672">=</span> <span class="nx">newValue</span><span class="p">;</span><br>    <span class="c1" style="color:#75715e">// Log the current value</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Current value:"</span><span class="p">,</span> <span class="nx">demo</span><span class="p">.</span><span class="nx">currentValue</span><span class="p">);</span><br><span class="p">}</span><br><span class="c1" style="color:#75715e">// Add a basic linebreak</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"---"</span><span class="p">);</span><br><span class="c1" style="color:#75715e">// Create a new instance</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo1</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">HasDecoratedProperty</span><span class="p">();</span><br><span class="c1" style="color:#75715e">// Update its value</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Setting demo1.currentValue = -10"</span><span class="p">);</span><br><span class="nx">demo1</span><span class="p">.</span><span class="nx">currentValue</span> <span class="o" style="color:#f92672">=</span> <span class="o" style="color:#f92672">-</span><span class="mi" style="color:#ae81ff">10</span><span class="p">;</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"demo1.currentValue:"</span><span class="p">,</span> <span class="nx">demo1</span><span class="p">.</span><span class="nx">currentValue</span><span class="p">);</span><br><span class="c1" style="color:#75715e">// Create a new instance</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo2</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">HasDecoratedProperty</span><span class="p">();</span><br><span class="c1" style="color:#75715e">// Update its value</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Setting demo2.currentValue = 20"</span><span class="p">);</span><br><span class="nx">demo2</span><span class="p">.</span><span class="nx">currentValue</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">20</span><span class="p">;</span><br><span class="c1" style="color:#75715e">// Compare the results</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"demo1.currentValue:"</span><span class="p">,</span> <span class="nx">demo1</span><span class="p">.</span><span class="nx">currentValue</span><span class="p">);</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"demo2.currentValue:"</span><span class="p">,</span> <span class="nx">demo2</span><span class="p">.</span><span class="nx">currentValue</span><span class="p">);</span><br></pre></div>
</td>
</tr>
</table>

Attempting to use the decorator will present several issues. The first, demonstrated in the `for` loop, is that `value` recycles state even though we've created a new object. This is because the decorator is only run once, the first time the class is loaded (I think; if I'm wrong I'd love to know). The second, demonstrated with `demo1` and `demo2`, shows that `value` is actually a singleton. Changing it in one instance changes it everywhere.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ts-node --project tsconfig.json main.ts<br><span class="go" style="color:#888">Current value: undefined</span><br><span class="go" style="color:#888">Attempting to set demo.currentValue = -10</span><br><span class="go" style="color:#888">Current value: 0</span><br><span class="go" style="color:#888">---</span><br><span class="go" style="color:#888">Current value: 0</span><br><span class="go" style="color:#888">Attempting to set demo.currentValue = 10</span><br><span class="go" style="color:#888">Current value: 10</span><br><span class="go" style="color:#888">---</span><br><span class="go" style="color:#888">Current value: 10</span><br><span class="go" style="color:#888">Attempting to set demo.currentValue = 20</span><br><span class="go" style="color:#888">Current value: 20</span><br><span class="go" style="color:#888">---</span><br><span class="go" style="color:#888">Setting demo1.currentValue = -10</span><br><span class="go" style="color:#888">demo1.currentValue: 0</span><br><span class="go" style="color:#888">Setting demo2.currentValue = 20</span><br><span class="go" style="color:#888">demo1.currentValue: 20</span><br><span class="go" style="color:#888">demo2.currentValue: 20</span><br></pre></div>
</td></tr></table>

### Solution

A full solution involves other decorators and is therefore outside the scope of this post (I'll add a link to the full example when I finish it). The gist of the solution is to combine class and property decorators, similar to combining parameter and method decorators. The property decorator sets metadata that the class decorator consumes.

## Recap

Property decorators are great at adding extra information about properties at runtime. They can't do a whole more. Property decorators are often used in combination with other decorators to perform new actions at runtime.

## Legal

The TS logo is a [modified `@typescript` avatar](https://www.npmjs.com/~typescript); I turned the PNG into a vector. I couldn't find the original and I didn't see any licensing on the other art, so it's most likely covered by [the TypeScript project's Apache 2.0 license](https://github.com/Microsoft/TypeScript/blob/master/LICENSE.txt). Any code from the TS project is similarly licensed.

If there's a problem with anything, my email's in the footer. Stay awesome.
