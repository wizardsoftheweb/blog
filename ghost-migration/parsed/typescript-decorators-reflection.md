---
title: "TypeScript Decorators: Reflection"
slug: "typescript-decorators-reflection"
date: "2018-03-07T01:00:00.000Z"
feature_image: "/images/2018/03/header-6.png"
author: "CJ Harries"
description: "This post takes a cursory look at reflection with TypeScript. Its primary focus is how reflection can be used with TypeScript decorators."
tags: 
  - TypeScript
  - JavaScript
  - Node
  - decorators
  - patterns
  - OOP
  - compiler
draft: true
---

This post takes a cursory look at reflection with TypeScript. Its primary focus is how reflection can be used with TypeScript decorators.  It introduces `Reflect`, `reflect-metadata`, and some miscellaneous related components.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#theseriessofar)
- [Code](#code)
- [Overview](#overview)
  - [`Reflect`](#reflect)
  - [`emitDecoratorMetadata`](#emitdecoratormetadata)
  - [`reflect-metadata`](#reflectmetadata)
- [Example: Validate a Parameter Range](#examplevalidateaparameterrange)
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

You can view the code related to this post [under the `post-03-reflection` tag](//github.com/thecjharries/posts-typescript-decorators/tree/post-03-reflection).

## Overview

[Reflection](https://en.wikipedia.org/wiki/Reflection_(computer_programming)) is the capacity of code to inspect and modify itself while running. Reflection implies (typically) that the code has a secondary interface with which to access everything. [JavaScript's `eval` function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval) is a great example; an arbitrary string is converted (hopefully) into meaningful elements and executed.

### `Reflect`

ECMAScript 2015 added [the `Reflect` global](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Reflect). While might seem like [a rehashed `Object`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object), `Reflect` adds some very useful reflection functionality.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">ownKeys</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/overview/reflect-own-keys.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
33</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e">// This object will have prop = "cool"</span><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">RootObject</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">prop</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"cool"</span><span class="p">;</span><br><span class="p">}</span><br><br><span class="c1" style="color:#75715e">// Its prototype will have foo = "bar"</span><br><span class="nx">RootObject</span><span class="p">.</span><span class="nx">prototype</span> <span class="o" style="color:#f92672">=</span> <span class="p">{</span> <span class="nx">foo</span><span class="o" style="color:#f92672">:</span> <span class="s2" style="color:#e6db74">"bar"</span> <span class="p">}</span> <span class="kr" style="color:#66d9ef">as</span> <span class="nx">any</span><span class="p">;</span><br><br><span class="c1" style="color:#75715e">// Create an instance</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">root</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">RootObject</span><span class="p">();</span><br><br><span class="c1" style="color:#75715e">// for...in moves up the prototype chain</span><br><span class="c1" style="color:#75715e">// tslint:disable-next-line:forin</span><br><span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kr" style="color:#66d9ef">const</span> <span class="nx">key</span> <span class="k" style="color:#66d9ef">in</span> <span class="nx">root</span><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">key</span><span class="p">);</span><br><span class="p">}</span><br><span class="c1" style="color:#75715e">// prop</span><br><span class="c1" style="color:#75715e">// foo</span><br><br><span class="c1" style="color:#75715e">// hasOwnProperty will prevent this</span><br><span class="c1" style="color:#75715e">// but requires an extra conditional</span><br><span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kr" style="color:#66d9ef">const</span> <span class="nx">key</span> <span class="k" style="color:#66d9ef">in</span> <span class="nx">root</span><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">root</span><span class="p">.</span><span class="nx">hasOwnProperty</span><span class="p">(</span><span class="nx">key</span><span class="p">))</span> <span class="p">{</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">key</span><span class="p">);</span><br>    <span class="p">}</span><br><span class="p">}</span><br><span class="c1" style="color:#75715e">// prop</span><br><br><span class="c1" style="color:#75715e">// Reflect.ownKeys solves it in one line</span><br><span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kr" style="color:#66d9ef">const</span> <span class="nx">key</span> <span class="nx">of</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">ownKeys</span><span class="p">(</span><span class="nx">root</span><span class="p">))</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">key</span><span class="p">);</span><br><span class="p">}</span><br><span class="c1" style="color:#75715e">// prop</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">has</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/overview/reflect-has.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
18</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e">// The visibility compiles out but whatever</span><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">Demo</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo</span>: <span class="kt" style="color:#66d9ef">number</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">;</span><br>    <span class="kr" style="color:#66d9ef">protected</span> <span class="nx">bar</span>: <span class="kt" style="color:#66d9ef">number</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">2</span><span class="p">;</span><br>    <span class="kr" style="color:#66d9ef">private</span> <span class="nx">baz</span>: <span class="kt" style="color:#66d9ef">number</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">3</span><span class="p">;</span><br><span class="p">}</span><br><br><span class="c1" style="color:#75715e">// Create an instance</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Demo</span><span class="p">();</span><br><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">has</span><span class="p">(</span><span class="nx">demo</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"foo"</span><span class="p">));</span><br><span class="c1" style="color:#75715e">// true</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">has</span><span class="p">(</span><span class="nx">demo</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"bar"</span><span class="p">));</span><br><span class="c1" style="color:#75715e">// true</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">has</span><span class="p">(</span><span class="nx">demo</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"baz"</span><span class="p">));</span><br><span class="c1" style="color:#75715e">// true</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">has</span><span class="p">(</span><span class="nx">demo</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"qqq"</span><span class="p">));</span><br><span class="c1" style="color:#75715e">// false</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">deleteProperty</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/overview/reflect-delete-property.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
29</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="p">(()</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>    <span class="s2" style="color:#e6db74">"use strict"</span><span class="p">;</span><br>    <span class="kr" style="color:#66d9ef">const</span> <span class="nx">sampleDeleteObject</span> <span class="o" style="color:#f92672">=</span> <span class="p">{</span><br>        <span class="nx">one</span>: <span class="kt" style="color:#66d9ef">1</span><span class="p">,</span><br>        <span class="nx">three</span>: <span class="kt" style="color:#66d9ef">3</span><span class="p">,</span><br>        <span class="nx">two</span>: <span class="kt" style="color:#66d9ef">2</span><span class="p">,</span><br>    <span class="p">};</span><br><br>    <span class="c1" style="color:#75715e">// Delete a property with delete</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="k" style="color:#66d9ef">delete</span> <span class="nx">sampleDeleteObject</span><span class="p">.</span><span class="nx">one</span><span class="p">);</span><br>    <span class="c1" style="color:#75715e">// true</span><br>    <span class="c1" style="color:#75715e">// Delete a property with Reflect</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">deleteProperty</span><span class="p">(</span><span class="nx">sampleDeleteObject</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"two"</span><span class="p">));</span><br>    <span class="c1" style="color:#75715e">// true</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">sampleDeleteObject</span><span class="p">);</span><br>    <span class="c1" style="color:#75715e">// { three: 3 }</span><br>    <span class="c1" style="color:#75715e">// Accidentally try to delete an object</span><br>    <span class="k" style="color:#66d9ef">try</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// tslint:disable-next-line:no-eval</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nb" style="color:#f8f8f2">eval</span><span class="p">(</span><span class="s2" style="color:#e6db74">"delete sampleDeleteObject"</span><span class="p">));</span><br>    <span class="p">}</span> <span class="k" style="color:#66d9ef">catch</span> <span class="p">(</span><span class="nx">error</span><span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br>    <span class="c1" style="color:#75715e">// Accidentally try to delete an object</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">deleteProperty</span><span class="p">(</span><span class="nx">sampleDeleteObject</span><span class="p">));</span><br>    <span class="c1" style="color:#75715e">// true</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">sampleDeleteObject</span><span class="p">);</span><br>    <span class="c1" style="color:#75715e">// { three: 3 }</span><br><span class="p">})();</span><br></pre></div>
</td>
</tr>
</table>

### `emitDecoratorMetadata`

TypeScript comes with a few experimental reflection features. As before, you'll need to enable them first.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">tsconfig.json</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/experimental/tsconfig.json" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="p">{</span><br>  <span class="nt" style="color:#f92672">"compilerOptions"</span><span class="p">:</span> <span class="p">{</span><br>    <span class="nt" style="color:#f92672">"target"</span><span class="p">:</span> <span class="s2" style="color:#e6db74">"ESNext"</span><span class="p">,</span><br>    <span class="nt" style="color:#f92672">"experimentalDecorators"</span><span class="p">:</span> <span class="kc" style="color:#66d9ef">true</span><span class="p">,</span><br>    <span class="nt" style="color:#f92672">"emitDecoratorMetadata"</span><span class="p">:</span> <span class="kc" style="color:#66d9ef">true</span><br>  <span class="p">},</span><br>  <span class="nt" style="color:#f92672">"include"</span><span class="p">:</span> <span class="p">[</span><span class="s2" style="color:#e6db74">"./**/*.ts"</span><span class="p">]</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

To investigate the experimental metadata, we'll need to create a decorator. A logging method decorator was the first thing I typed out.

(Note: If you haven't seen [the previous post](https://blog.wizardsoftheweb.pro/typescript-decorators-javascript-foundation), you might benefit from a short skim.)

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/experimental/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
17</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">function</span> <span class="nx">LogMethod</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">descriptor</span>: <span class="kt" style="color:#66d9ef">PropertyDescriptor</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">target</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">propertyKey</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">descriptor</span><span class="p">);</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">Demo</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">@LogMethod</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo</span><span class="p">(</span><span class="nx">bar</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Demo</span><span class="p">();</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> tsc --project tsconfig.json<br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.js</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/experimental/main.js" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
26</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__decorate</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__decorate</span><span class="p">)</span> <span class="o" style="color:#f92672">||</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">)</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">var</span> <span class="nx">c</span> <span class="o" style="color:#f92672">=</span> <span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span><span class="p">,</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">target</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">===</span> <span class="kc" style="color:#66d9ef">null</span> <span class="o" style="color:#f92672">?</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">=</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">getOwnPropertyDescriptor</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span><span class="p">,</span> <span class="nx">d</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"object"</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"function"</span><span class="p">)</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span><span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">);</span><br>    <span class="k" style="color:#66d9ef">else</span> <span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">i</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">.</span><span class="nx">length</span> <span class="o" style="color:#f92672">-</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">;</span> <span class="nx">i</span> <span class="o" style="color:#f92672">&gt;=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">;</span> <span class="nx">i</span><span class="o" style="color:#f92672">--</span><span class="p">)</span> <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">d</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">[</span><span class="nx">i</span><span class="p">])</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">))</span> <span class="o" style="color:#f92672">||</span> <span class="nx">r</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nx">r</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">defineProperty</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">),</span> <span class="nx">r</span><span class="p">;</span><br><span class="p">};</span><br><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__metadata</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__metadata</span><span class="p">)</span> <span class="o" style="color:#f92672">||</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">k</span><span class="p">,</span> <span class="nx">v</span><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"object"</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">metadata</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"function"</span><span class="p">)</span> <span class="k" style="color:#66d9ef">return</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">metadata</span><span class="p">(</span><span class="nx">k</span><span class="p">,</span> <span class="nx">v</span><span class="p">);</span><br><span class="p">};</span><br><span class="kd" style="color:#66d9ef">function</span> <span class="nx">LogMethod</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">propertyKey</span><span class="p">,</span> <span class="nx">descriptor</span><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">target</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">propertyKey</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">descriptor</span><span class="p">);</span><br><span class="p">}</span><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">Demo</span> <span class="p">{</span><br>    <span class="nx">foo</span><span class="p">(</span><span class="nx">bar</span><span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><span class="nx">__decorate</span><span class="p">([</span><br>    <span class="nx">LogMethod</span><span class="p">,</span><br>    <span class="nx">__metadata</span><span class="p">(</span><span class="s2" style="color:#e6db74">"design:type"</span><span class="p">,</span> <span class="nb" style="color:#f8f8f2">Function</span><span class="p">),</span><br>    <span class="nx">__metadata</span><span class="p">(</span><span class="s2" style="color:#e6db74">"design:paramtypes"</span><span class="p">,</span> <span class="p">[</span><span class="nb" style="color:#f8f8f2">Number</span><span class="p">]),</span><br>    <span class="nx">__metadata</span><span class="p">(</span><span class="s2" style="color:#e6db74">"design:returntype"</span><span class="p">,</span> <span class="k" style="color:#66d9ef">void</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">)</span><br><span class="p">],</span> <span class="nx">Demo</span><span class="p">.</span><span class="nx">prototype</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"foo"</span><span class="p">,</span> <span class="kc" style="color:#66d9ef">null</span><span class="p">);</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Demo</span><span class="p">();</span><br></pre></div>
</td>
</tr>
</table>

The `__metadata` declaration is brand new. It looks similar to the `__decorate` and `__param` declarations that we've seen before. It too comes from [deep in the compiler](https://github.com/Microsoft/TypeScript/blob/v2.7.2/src/compiler/transformers/ts.ts#L3602).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">metadataHelper</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/Microsoft/TypeScript/blob/v2.7.2/src/compiler/transformers/ts.ts#L3602" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__metadata</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__metadata</span><span class="p">)</span> <span class="o" style="color:#f92672">||</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">k</span><span class="p">,</span> <span class="nx">v</span><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"object"</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">metadata</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"function"</span><span class="p">)</span> <span class="k" style="color:#66d9ef">return</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">metadata</span><span class="p">(</span><span class="nx">k</span><span class="p">,</span> <span class="nx">v</span><span class="p">);</span><br><span class="p">};</span><br></pre></div>
</td>
</tr>
</table>

`__metadata` attempts to create a `Reflect.metadata` factory (more on that soon). It passes `k`ey-`v`alue pairs to `Reflect.metadata`, which in turn stashes them away to be accessed later. By default, `emitDecoratorMetadata` exposes three new properties:

* `design:type`: the type of the object being decorated (here a `Function`)
* `design:paramtypes`: an array of types that match either the decorated item's signature or its constructor's signature (here `[Number]`)
* `design:returntype`: the return type of the object being decorated (here `void 0`)

At the bottom of the file in the `__decorate` call, you'll see the `__metadata` calls. Everything looks great. Except we're missing an important component.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ts-node --print <span class="s1" style="color:#e6db74">'Reflect &amp;&amp; Reflect.metadata || "whoops"'</span><br><span class="go" style="color:#888">whoops</span><br></pre></div>
</td></tr></table>

### `reflect-metadata`

[The `reflect-metadata` package](https://www.npmjs.com/package/reflect-metadata) aims to extend the available reflection capabilities. While it is an experimental package, it comes recommended in [the official docs](https://www.typescriptlang.org/docs/handbook/decorators.html#metadata) and sees quite a bit of play. It's also necessary to take advantage of the `emitDecoratorMetadata` compiler option, as we've just discovered.

Defining new metadata is very easy. `reflect-metadata` provides both imperative commands and a decorator factory. The decorator factory stores the metadata key-value pair and passes control through.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">basic-usage.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/reflect-metadata/basic-usage.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
24</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">BasicUsage</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">constructor</span><span class="p">()</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// Explicitly define some metadata</span><br>        <span class="c1" style="color:#75715e">// key, value, target, propertyKey</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">defineMetadata</span><span class="p">(</span><span class="s2" style="color:#e6db74">"foo1"</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"bar1"</span><span class="p">,</span> <span class="k" style="color:#66d9ef">this</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"baz"</span><span class="p">);</span><br>    <span class="p">}</span><br><br>    <span class="c1" style="color:#75715e">// Define metadata via a decorator</span><br>    <span class="c1" style="color:#75715e">// key, value</span><br>    <span class="kd" style="color:#66d9ef">@Reflect</span><span class="p">.</span><span class="nx">metadata</span><span class="p">(</span><span class="s2" style="color:#e6db74">"foo2"</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"bar2"</span><span class="p">)</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">baz() {</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoBasicUsage</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">BasicUsage</span><span class="p">();</span><br><br><span class="c1" style="color:#75715e">// key, target, propertyKey</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><span class="s2" style="color:#e6db74">"foo1"</span><span class="p">,</span> <span class="nx">basicUsageDemo</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"baz"</span><span class="p">));</span><br><span class="c1" style="color:#75715e">// bar1</span><br><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><span class="s2" style="color:#e6db74">"foo2"</span><span class="p">,</span> <span class="nx">basicUsageDemo</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"baz"</span><span class="p">));</span><br><span class="c1" style="color:#75715e">// bar2</span><br></pre></div>
</td>
</tr>
</table>

Accessing the data is also very easy. We can now grab the `emitDecoratorMetadata` metadata that we've been trying to get to.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">decorator-metadata.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/reflect-metadata/decorator-metadata.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
25</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kd" style="color:#66d9ef">function</span> <span class="nx">LogMethod</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">descriptor</span>: <span class="kt" style="color:#66d9ef">PropertyDescriptor</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// Checks the type of the decorated object</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><span class="s2" style="color:#e6db74">"design:type"</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">propertyKey</span><span class="p">));</span><br>    <span class="c1" style="color:#75715e">// [Function: Function]</span><br>    <span class="c1" style="color:#75715e">// Checks the types of all params</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><span class="s2" style="color:#e6db74">"design:paramtypes"</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">propertyKey</span><span class="p">));</span><br>    <span class="c1" style="color:#75715e">// [[Function: Number]]</span><br>    <span class="c1" style="color:#75715e">// Checks the return type</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><span class="s2" style="color:#e6db74">"design:returntype"</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">propertyKey</span><span class="p">));</span><br>    <span class="c1" style="color:#75715e">// undefined</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">Demo</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">@LogMethod</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo</span><span class="p">(</span><span class="nx">bar</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Demo</span><span class="p">();</span><br></pre></div>
</td>
</tr>
</table>

## Example: Validate a Parameter Range

This group of files adds the ability to ensure specific parameters fall within a certain range. `RANGE_KEY` is shared across files so everything can access the stashed ranges.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">constants.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/usage/constants.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kr" style="color:#66d9ef">const</span> <span class="nx">RANGE_KEY</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Symbol</span><span class="p">(</span><span class="s2" style="color:#e6db74">"validateRange"</span><span class="p">);</span><br></pre></div>
</td>
</tr>
</table>

When a parameter is decorated, add the range to the owning method's metadata.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">RangeParameter.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/usage/RangeParameter.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
25</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">RANGE_KEY</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./constants"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">RangeParameter</span><span class="p">(</span><br>    <span class="nx">min</span>: <span class="kt" style="color:#66d9ef">number</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">,</span><br>    <span class="nx">max</span>: <span class="kt" style="color:#66d9ef">number</span> <span class="o" style="color:#f92672">=</span> <span class="mi" style="color:#ae81ff">100</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="p">(</span><br>        <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>        <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>        <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br>    <span class="p">)</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// Pull existing metadata (if any)</span><br>        <span class="kr" style="color:#66d9ef">const</span> <span class="nx">existingRanges</span><span class="o" style="color:#f92672">:</span> <span class="p">{</span> <span class="p">[</span><span class="nx">key</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">]</span><span class="o" style="color:#f92672">:</span> <span class="kt" style="color:#66d9ef">number</span><span class="p">[]</span> <span class="p">}</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>            <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getMetadata</span><span class="p">(</span><span class="nx">RANGE_KEY</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">propertyKey</span><span class="p">)</span><br>            <span class="o" style="color:#f92672">||</span><br>            <span class="p">{}</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// Add new value</span><br>        <span class="nx">existingRanges</span><span class="p">[</span><span class="nx">parameterIndex</span><span class="p">]</span> <span class="o" style="color:#f92672">=</span> <span class="p">[</span><span class="nx">min</span><span class="p">,</span> <span class="nx">max</span><span class="p">];</span><br>        <span class="c1" style="color:#75715e">// Store metadata</span><br>        <span class="nx">Reflect</span><span class="p">.</span><span class="nx">defineMetadata</span><span class="p">(</span><span class="nx">RANGE_KEY</span><span class="p">,</span> <span class="nx">existingRanges</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">propertyKey</span><span class="p">);</span><br>    <span class="p">};</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

This decorates the method that owns the decorated range. When called, it checks for any active ranges. Each watched parameter is checked against the range's endpoints. An error is thrown if the value is out of the range.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">ValidateRange.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/usage/ValidateRange.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
37</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">RANGE_KEY</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./constants"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">ValidateRange</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">descriptor</span>: <span class="kt" style="color:#66d9ef">PropertyDescriptor</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// Store the original value</span><br>    <span class="kr" style="color:#66d9ef">const</span> <span class="nx">savedValue</span> <span class="o" style="color:#f92672">=</span> <span class="nx">descriptor</span><span class="p">.</span><span class="nx">value</span><span class="p">;</span><br>    <span class="c1" style="color:#75715e">// Attach validation logic</span><br>    <span class="nx">descriptor</span><span class="p">.</span><span class="nx">value</span> <span class="o" style="color:#f92672">=</span> <span class="p">(...</span><span class="nx">args</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">[])</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// Pull the active ranges (if any)</span><br>        <span class="kr" style="color:#66d9ef">const</span> <span class="nx">monitoredRanges</span><span class="o" style="color:#f92672">:</span> <span class="p">{</span> <span class="p">[</span><span class="nx">key</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">]</span><span class="o" style="color:#f92672">:</span> <span class="kt" style="color:#66d9ef">number</span><span class="p">[]</span> <span class="p">}</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>            <span class="nx">Reflect</span><span class="p">.</span><span class="nx">getOwnMetadata</span><span class="p">(</span><br>                <span class="nx">RANGE_KEY</span><span class="p">,</span><br>                <span class="nx">target</span><span class="p">,</span><br>                <span class="nx">propertyKey</span><span class="p">,</span><br>            <span class="p">)</span><br>            <span class="o" style="color:#f92672">||</span><br>            <span class="p">{}</span><br>        <span class="p">);</span><br>        <span class="c1" style="color:#75715e">// Check all monitored ranges</span><br>        <span class="c1" style="color:#75715e">// tslint:disable-next-line:forin</span><br>        <span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kr" style="color:#66d9ef">const</span> <span class="nx">key</span> <span class="k" style="color:#66d9ef">in</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">ownKeys</span><span class="p">(</span><span class="nx">monitoredRanges</span><span class="p">))</span> <span class="p">{</span><br>            <span class="kr" style="color:#66d9ef">const</span> <span class="nx">range</span> <span class="o" style="color:#f92672">=</span> <span class="nx">monitoredRanges</span><span class="p">[</span><span class="nx">key</span><span class="p">];</span><br>            <span class="kr" style="color:#66d9ef">const</span> <span class="nx">value</span> <span class="o" style="color:#f92672">=</span> <span class="nx">args</span><span class="p">[</span><span class="nx">key</span><span class="p">];</span><br>            <span class="c1" style="color:#75715e">// Throw error if outside range</span><br>            <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">value</span> <span class="o" style="color:#f92672">&lt;</span> <span class="nx">range</span><span class="p">[</span><span class="mi" style="color:#ae81ff">0</span><span class="p">]</span> <span class="o" style="color:#f92672">||</span> <span class="nx">value</span> <span class="o" style="color:#f92672">&gt;</span> <span class="nx">range</span><span class="p">[</span><span class="mi" style="color:#ae81ff">1</span><span class="p">])</span> <span class="p">{</span><br>                <span class="k" style="color:#66d9ef">throw</span> <span class="k" style="color:#66d9ef">new</span> <span class="nb" style="color:#f8f8f2">Error</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Value outside of range"</span><span class="p">);</span><br>            <span class="p">}</span><br>        <span class="p">}</span><br>        <span class="c1" style="color:#75715e">// Actually call the function</span><br>        <span class="k" style="color:#66d9ef">return</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">apply</span><span class="p">(</span><span class="nx">savedValue</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">args</span><span class="p">);</span><br>    <span class="p">};</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

This puts everything together in a simple class.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">Sample.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/usage/Sample.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
16</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">RangeParameter</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./RangeParameter"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">ValidateRange</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./ValidateRange"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">export</span> <span class="kr" style="color:#66d9ef">class</span> <span class="nx">Sample</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// Validate the input ranges</span><br>    <span class="kd" style="color:#66d9ef">@ValidateRange</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">updatePercentage</span><span class="p">(</span><br>        <span class="c1" style="color:#75715e">// Define a min,max of 0,100</span><br>        <span class="kd" style="color:#66d9ef">@RangeParameter</span><span class="p">(</span><span class="mi" style="color:#ae81ff">0</span><span class="p">,</span> <span class="mi" style="color:#ae81ff">100</span><span class="p">)</span><br>        <span class="nx">newValue</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br>        <span class="c1" style="color:#75715e">// Does nothing</span><br>        <span class="nx">negative</span>: <span class="kt" style="color:#66d9ef">boolean</span> <span class="o" style="color:#f92672">=</span> <span class="kc" style="color:#66d9ef">false</span><span class="p">,</span><br>    <span class="p">)</span> <span class="p">{</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">newValue</span><span class="p">);</span><br>    <span class="p">}</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

This runs everything, illustrating how a successful update works and catching a failed update.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/reflection/usage/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
15</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="s2" style="color:#e6db74">"reflect-metadata"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">RANGE_KEY</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./constants"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">Sample</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./Sample"</span><span class="p">;</span><br><br><span class="c1" style="color:#75715e">// Initialize</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoSample</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Sample</span><span class="p">();</span><br><span class="c1" style="color:#75715e">// Working value</span><br><span class="nx">demoSample</span><span class="p">.</span><span class="nx">updatePercentage</span><span class="p">(</span><span class="mi" style="color:#ae81ff">10</span><span class="p">);</span><br><span class="c1" style="color:#75715e">// Bad value</span><br><span class="k" style="color:#66d9ef">try</span> <span class="p">{</span><br>    <span class="nx">demoSample</span><span class="p">.</span><span class="nx">updatePercentage</span><span class="p">(</span><span class="mi" style="color:#ae81ff">200</span><span class="p">);</span><br><span class="p">}</span> <span class="k" style="color:#66d9ef">catch</span> <span class="p">(</span><span class="nx">error</span><span class="p">)</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// do nothing</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

## Recap

Make sure to skim [metadata coverage in the official docs](https://www.typescriptlang.org/docs/handbook/decorators.html#metadata). Reflection tweaks active code. `Reflect` is a robust tool with applications outside this context. `emitDecoratorMetadata` emits object type, param type, and return type, when `reflect-metadata` is loaded. `reflect-metadata` can easily link disparate portions of your app together via straightfoward key-value matching.

## Legal

The TS logo is a [modified `@typescript` avatar](https://www.npmjs.com/~typescript); I turned the PNG into a vector. I couldn't find the original and I didn't see any licensing on the other art, so it's most likely covered by [the TypeScript project's Apache 2.0 license](https://github.com/Microsoft/TypeScript/blob/master/LICENSE.txt). Any code from the TS project is similarly licensed.

If there's a problem with anything, my email's in the footer. Stay awesome.