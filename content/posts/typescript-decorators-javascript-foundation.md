---
title: "TypeScript Decorators: JavaScript Foundation"
slug: "typescript-decorators-javascript-foundation"
date: "2018-03-06T01:00:00.000Z"
feature_image: "/images/2018/03/header.png"
author: "CJ Harries"
description: "This post looks at how TypeScript compiles decorators, breaks down the raw JavaScript from the compiler, and analyzes the JavaScript output from several examples."
tags:
  - TypeScript
  - JavaScript
  - Node
  - decorators
  - patterns
  - OOP
  - compiler
---

This post looks at how TypeScript compiles decorators. It pulls the raw JavaScript from the compiler and breaks down the result. It has basic decorator examples of each type to examine the JavaScript output.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#the-series-so-far)
- [Code](#code)
- [Why Look at the JavaScript?](#why-look-at-the-javascript)
- [Configuration](#configuration)
- [From the Source](#from-the-source)
  - [Raw](#raw)
  - [Prettified and Polished](#prettified-and-polished)
- [Analysis](#analysis)
  - [Parameter Decorators](#parameter-decorators)
  - [Property Decorators](#property-decorators)
  - [Method Decorators](#method-decorators)
  - [Class Decorators](#class-decorators)
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

- Where Decorators Work
- Decorating Instance Elements vs. Static Elements
- Examples
  - Pairing Parameter Decorators with Method Decorators
  - Pairing Property Decorators with Class Decorators

## Code

You can view the code related to this post [under the `post-02-javascript-foundation` tag](//github.com/thecjharries/posts-typescript-decorators/tree/post-02-javascript-foundation).

## Why Look at the JavaScript?

A little bit of perspective is never a bad thing. I often forget that JavaScript is somewhere in the toolchain because `ts-node` keeps me so far removed. Looking at how the compiler handles decorators will shed some light on the process and make debugging the inevitable issues easier.

## Configuration

I'll be using this `tsconfig.json` throughout the post.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">tsconfig.json</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/tsconfig.json" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="p">{</span><br>  <span class="nt" style="color:#f92672">"compilerOptions"</span><span class="p">:</span> <span class="p">{</span><br>    <span class="nt" style="color:#f92672">"target"</span><span class="p">:</span> <span class="s2" style="color:#e6db74">"ESNext"</span><span class="p">,</span><br>    <span class="nt" style="color:#f92672">"experimentalDecorators"</span><span class="p">:</span> <span class="kc" style="color:#66d9ef">true</span><span class="p">,</span><br>    <span class="nt" style="color:#f92672">"emitDecoratorMetadata"</span><span class="p">:</span> <span class="kc" style="color:#66d9ef">false</span><br>  <span class="p">},</span><br>  <span class="nt" style="color:#f92672">"include"</span><span class="p">:</span> <span class="p">[</span><span class="s2" style="color:#e6db74">"./**/*.ts"</span><span class="p">]</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

## From the Source

Decorators begin with stored, prebuilt JavaScript. [The `decorateHelper`](https://github.com/Microsoft/TypeScript/blob/v2.7.2/src/compiler/transformers/ts.ts#L3577), deep in the compiler, exports the `__decorate` function wherever it needs to go. The same function is used for all decorator types.

### Raw

[As of `v2.7.2`](https://github.com/Microsoft/TypeScript/blob/v2.7.2/src/compiler/transformers/ts.ts#L3577), `decorateHelper` generates this JavaScript.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">decorateHelper</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/Microsoft/TypeScript/blob/v2.7.2/src/compiler/transformers/ts.ts#L3577" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__decorate</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__decorate</span><span class="p">)</span> <span class="o" style="color:#f92672">||</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">)</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">var</span> <span class="nx">c</span> <span class="o" style="color:#f92672">=</span> <span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span><span class="p">,</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">target</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">===</span> <span class="kc" style="color:#66d9ef">null</span> <span class="o" style="color:#f92672">?</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">=</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">getOwnPropertyDescriptor</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span><span class="p">,</span> <span class="nx">d</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"object"</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"function"</span><span class="p">)</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span><span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">);</span><br>    <span class="k" style="color:#66d9ef">else</span> <span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">i</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">.</span><span class="nx">length</span> <span class="o" style="color:#f92672">-</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">;</span> <span class="nx">i</span> <span class="o" style="color:#f92672">&gt;=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">;</span> <span class="nx">i</span><span class="o" style="color:#f92672">--</span><span class="p">)</span> <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">d</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">[</span><span class="nx">i</span><span class="p">])</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">))</span> <span class="o" style="color:#f92672">||</span> <span class="nx">r</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nx">r</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">defineProperty</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">),</span> <span class="nx">r</span><span class="p">;</span><br><span class="p">};</span><br></pre></div>
</td>
</tr>
</table>

To verify, we can create a simple class, decorate it, and see how TypeScript compiles it.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/raw/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">function</span> <span class="nx">Enumerable</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">descriptor</span>: <span class="kt" style="color:#66d9ef">PropertyDescriptor</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">descriptor</span><span class="p">.</span><span class="nx">enumerable</span> <span class="o" style="color:#f92672">=</span> <span class="kc" style="color:#66d9ef">true</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="nx">descriptor</span><span class="p">;</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">Demo</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">@Enumerable</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo() {</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Demo</span><span class="p">();</span><br></pre></div>
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
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/raw/main.js" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
19</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__decorate</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__decorate</span><span class="p">)</span> <span class="o" style="color:#f92672">||</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">)</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">var</span> <span class="nx">c</span> <span class="o" style="color:#f92672">=</span> <span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span><span class="p">,</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">target</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">===</span> <span class="kc" style="color:#66d9ef">null</span> <span class="o" style="color:#f92672">?</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">=</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">getOwnPropertyDescriptor</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span><span class="p">,</span> <span class="nx">d</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"object"</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"function"</span><span class="p">)</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span><span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">);</span><br>    <span class="k" style="color:#66d9ef">else</span> <span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">i</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">.</span><span class="nx">length</span> <span class="o" style="color:#f92672">-</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">;</span> <span class="nx">i</span> <span class="o" style="color:#f92672">&gt;=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">;</span> <span class="nx">i</span><span class="o" style="color:#f92672">--</span><span class="p">)</span> <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">d</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">[</span><span class="nx">i</span><span class="p">])</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">))</span> <span class="o" style="color:#f92672">||</span> <span class="nx">r</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nx">r</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">defineProperty</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">),</span> <span class="nx">r</span><span class="p">;</span><br><span class="p">};</span><br><span class="kd" style="color:#66d9ef">function</span> <span class="nx">Enumerable</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">propertyKey</span><span class="p">,</span> <span class="nx">descriptor</span><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">descriptor</span><span class="p">.</span><span class="nx">enumerable</span> <span class="o" style="color:#f92672">=</span> <span class="kc" style="color:#66d9ef">true</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="nx">descriptor</span><span class="p">;</span><br><span class="p">}</span><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">Demo</span> <span class="p">{</span><br>    <span class="nx">foo</span><span class="p">()</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><span class="nx">__decorate</span><span class="p">([</span><br>    <span class="nx">Enumerable</span><br><span class="p">],</span> <span class="nx">Demo</span><span class="p">.</span><span class="nx">prototype</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"foo"</span><span class="p">,</span> <span class="kc" style="color:#66d9ef">null</span><span class="p">);</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Demo</span><span class="p">();</span><br></pre></div>
</td>
</tr>
</table>

The `__decorate` blob is defined at the top and consumed at the bottom with `foo` as an input. If you need more examples, either keep reading or compile more things.

### Prettified and Polished

As it stands, `__decorate` isn't easy to grok. Let's clean it up a bit to see how it works.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">decorate.js</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/pretty/decorate.js" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
53</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e">// Pulled from https://github.com/Microsoft/TypeScript/blob/v2.7.2/src/compiler/transformers/ts.ts#L3577</span><br><span class="c1" style="color:#75715e">// Punctuation and spacing added to improve readability</span><br><span class="c1" style="color:#75715e">// Original licensed under https://github.com/Microsoft/TypeScript/blob/master/LICENSE.txt</span><br><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__decorate</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>    <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__decorate</span><span class="p">)</span><br>    <span class="o" style="color:#f92672">||</span><br>    <span class="kd" style="color:#66d9ef">function</span><span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">)</span> <span class="p">{</span><br>        <span class="kd" style="color:#66d9ef">var</span> <span class="nx">c</span> <span class="o" style="color:#f92672">=</span> <span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span><span class="p">,</span><br>            <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>                <span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span><br>                    <span class="o" style="color:#f92672">?</span> <span class="nx">target</span><br>                    <span class="o" style="color:#f92672">:</span> <span class="p">(</span><br>                        <span class="nx">desc</span> <span class="o" style="color:#f92672">===</span> <span class="kc" style="color:#66d9ef">null</span><br>                            <span class="o" style="color:#f92672">?</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">=</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">getOwnPropertyDescriptor</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">)</span><br>                            <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span><br>                    <span class="p">)</span><br>            <span class="p">),</span><br>            <span class="nx">d</span><span class="p">;</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><br>            <span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"object"</span><br>            <span class="o" style="color:#f92672">&amp;&amp;</span><br>            <span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"function"</span><br>        <span class="p">)</span> <span class="p">{</span><br>            <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span><span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">);</span><br>        <span class="p">}</span> <span class="k" style="color:#66d9ef">else</span> <span class="p">{</span><br>            <span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">i</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">.</span><span class="nx">length</span> <span class="o" style="color:#f92672">-</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">;</span> <span class="nx">i</span> <span class="o" style="color:#f92672">&gt;=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">;</span> <span class="nx">i</span><span class="o" style="color:#f92672">--</span><span class="p">)</span> <span class="p">{</span><br>                <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">d</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">[</span><span class="nx">i</span><span class="p">])</span> <span class="p">{</span><br>                    <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><br>                        <span class="p">(</span><br>                            <span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span><br>                                <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">r</span><span class="p">)</span><br>                                <span class="o" style="color:#f92672">:</span> <span class="p">(</span><br>                                    <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span><br>                                        <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">)</span><br>                                        <span class="o" style="color:#f92672">:</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">)</span><br>                                <span class="p">)</span><br>                        <span class="p">)</span><br>                        <span class="o" style="color:#f92672">||</span><br>                        <span class="nx">r</span><br>                    <span class="p">);</span><br>                <span class="p">}</span><br>            <span class="p">}</span><br>        <span class="p">}</span><br>        <span class="k" style="color:#66d9ef">return</span> <span class="p">(</span><br>            <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span><br>            <span class="o" style="color:#f92672">&amp;&amp;</span><br>            <span class="nx">r</span><br>            <span class="o" style="color:#f92672">&amp;&amp;</span><br>            <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">defineProperty</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">),</span><br>            <span class="nx">r</span><br>        <span class="p">);</span><br>    <span class="p">}</span><br><span class="p">);</span><br></pre></div>
</td>
</tr>
</table>

- [Line 5](https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/pretty/decorate.js#L5) is a guarded assignment; it reuses an existing `__decorate` or builds it from scratch.
- [Line 8](https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/pretty/decorate.js#L8) counts the call's arguments. Remember the arguments have typically been

    1. `target`: base object
    2. `propertyKey`: name or symbol of the active object
    3. `descriptor`: the active [property descriptor](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty#Description)

    We can reasonably infer having all three is important.

- [Lines 10-16](https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/pretty/decorate.js#L10) set the initial item that will decorated.

  - If there are fewer than three arguments, the item is the `target`, which should be the class.
  - If there are three (or more) arguments, the item is the property descriptor for `target[propertyKey]`.

- [Lines 19-24](https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/pretty/decorate.js#L19) search [the Reflect object](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Reflect) for a `decorate` method. I scratched my head over this for a few minutes, then discovered [a great SO answer](https://stackoverflow.com/a/46499259/2877698). It's future planning for the day when `Reflect.decorate` does exist.

- [Lines 26-42](https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/pretty/decorate.js#L42) loop over the passed-in decorators and attempt to evaluate them.

  - Once again, three arguments is important. If there are fewer than three, the decorator is called with `r`, which as we learned above, should be `target`.
  - With more than three arguments, the decorator is called with `r` as the property descriptor (in addition to `target` and `propertyKey`)
  - If there are three exactly, the decorator is called without anything to connect it to the current state (just `target` and `propertyKey`).

- [The `return`](https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/pretty/decorate.js#L44) checks to see if the descriptor has been updated. If there are more than three arguments, the decorator was called with `r`, so it might have changed. If `r` is defined and the `target` is able to define `propertyKey` with the `r`-descriptor, the object will be updated. `r` is always returned.

## Analysis

To keep with the JavaScript theme, I'm going to look at each kind of decorator and the JS it generates. This is just a cursory overview; when I wrap back around with posts about the individual decorators I'll go deeper with more examples and more complicated setups.

Because I didn't do anything complicated with these decorators, I ended 3/4 with a fairly pessimistic assessment. I assure you that will change once I bring factories and fancy config back into the mix. Vanilla decorators are fantastic at monitoring state and not much else.

### Parameter Decorators

To explore parameter decorators, let's build an uncomplicated logger.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/parameter/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
20</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">function</span> <span class="nx">LogParameter</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">target</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">propertyKey</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">parameterIndex</span><span class="p">);</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">ParameterExample</span> <span class="p">{</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">logThis</span><span class="p">(</span><br>        <span class="nx">first</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">""</span><span class="p">,</span><br>        <span class="kd" style="color:#66d9ef">@LogParameter</span> <span class="nx">greeting</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"Hello, world"</span><span class="p">,</span><br>    <span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoParameter</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">ParameterExample</span><span class="p">();</span><br></pre></div>
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
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/parameter/main.js" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__decorate</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__decorate</span><span class="p">)</span> <span class="o" style="color:#f92672">||</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">)</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">var</span> <span class="nx">c</span> <span class="o" style="color:#f92672">=</span> <span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span><span class="p">,</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">target</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">===</span> <span class="kc" style="color:#66d9ef">null</span> <span class="o" style="color:#f92672">?</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">=</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">getOwnPropertyDescriptor</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span><span class="p">,</span> <span class="nx">d</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"object"</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"function"</span><span class="p">)</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span><span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">);</span><br>    <span class="k" style="color:#66d9ef">else</span> <span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">i</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">.</span><span class="nx">length</span> <span class="o" style="color:#f92672">-</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">;</span> <span class="nx">i</span> <span class="o" style="color:#f92672">&gt;=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">;</span> <span class="nx">i</span><span class="o" style="color:#f92672">--</span><span class="p">)</span> <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">d</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">[</span><span class="nx">i</span><span class="p">])</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">))</span> <span class="o" style="color:#f92672">||</span> <span class="nx">r</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nx">r</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">defineProperty</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">),</span> <span class="nx">r</span><span class="p">;</span><br><span class="p">};</span><br><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__param</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__param</span><span class="p">)</span> <span class="o" style="color:#f92672">||</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">paramIndex</span><span class="p">,</span> <span class="nx">decorator</span><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">)</span> <span class="p">{</span> <span class="nx">decorator</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">paramIndex</span><span class="p">);</span> <span class="p">}</span><br><span class="p">};</span><br><span class="kd" style="color:#66d9ef">function</span> <span class="nx">LogParameter</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">propertyKey</span><span class="p">,</span> <span class="nx">parameterIndex</span><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">target</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">propertyKey</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">parameterIndex</span><span class="p">);</span><br><span class="p">}</span><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">ParameterExample</span> <span class="p">{</span><br>    <span class="nx">logThis</span><span class="p">(</span><span class="nx">first</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">""</span><span class="p">,</span> <span class="nx">greeting</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"Hello, world"</span><span class="p">)</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><span class="nx">__decorate</span><span class="p">([</span><br>    <span class="nx">__param</span><span class="p">(</span><span class="mi" style="color:#ae81ff">1</span><span class="p">,</span> <span class="nx">LogParameter</span><span class="p">)</span><br><span class="p">],</span> <span class="nx">ParameterExample</span><span class="p">.</span><span class="nx">prototype</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"logThis"</span><span class="p">,</span> <span class="kc" style="color:#66d9ef">null</span><span class="p">);</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoParameter</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">ParameterExample</span><span class="p">();</span><br></pre></div>
</td>
</tr>
</table>

The `__decorate` call is full of `__param` calls. That's a new function. Like `__decorate`, `__param` is [stored deep in the compiler](https://github.com/Microsoft/TypeScript/blob/v2.7.2/src/compiler/transformers/ts.ts#L3627).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">paramHelper</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/Microsoft/TypeScript/blob/v2.7.2/src/compiler/transformers/ts.ts#L3627" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__param</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__param</span><span class="p">)</span> <span class="o" style="color:#f92672">||</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">paramIndex</span><span class="p">,</span> <span class="nx">decorator</span><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">)</span> <span class="p">{</span> <span class="nx">decorator</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">paramIndex</span><span class="p">);</span> <span class="p">}</span><br><span class="p">};</span><br></pre></div>
</td>
</tr>
</table>

`__param` is [only used by parameter decorators](https://github.com/Microsoft/TypeScript/blob/v2.7.2/src/compiler/transformers/ts.ts#L1609), unlike `__decorate`, which is used by all. Like `__decorate`, `__param`'s assignment is guarded. When created, `__param` becomes a factory that takes `target` and `propertyKey` as input with fixed `decorator` and `paramIndex`.

Returning to [line 10](https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/parameter/main.js#L10), after the `__decorate` and `__param` declarations, we see a tidier `LogParameter` and `ParameterExample`. All of the TS syntactic sugar has been removed for a faster, vanilla JS experience.

We're mainly interested in the `__decorate` call itself. [On line 21](https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/parameter/main.js#L21), the `decorators` array has been filled with `__param` calls. This converts the unique signature of parameter decorators into the standard `(target, propertyKey, descriptor)` format, albeit without a descriptor. Similarly, the decoration is happening on `logThis` (which owns the parameter) without a descriptor.

All of this together means parameter decorators really don't do much for us. We can verify a parameter has been used. We don't have access to the value it was used with. Returns from parameter decorators [are ignored](https://www.typescriptlang.org/docs/handbook/decorators.html#parameter-decorators) which means any changes we attempt will persist beyond this decorator. All that being said, there are some very good uses for the limited access we have, which will be explored more in the Parameter Decorator post (TODO!).

### Property Decorators

Once again, building a simple, logging decorator is a good way to explore.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/property/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">function</span> <span class="nx">LogProperty</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">target</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">propertyKey</span><span class="p">);</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">PropertyExample</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">@LogProperty</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">greeting</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">;</span><br><br>    <span class="kr" style="color:#66d9ef">constructor</span><span class="p">()</span> <span class="p">{</span><br>        <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">greeting</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"Hello, world"</span><span class="p">;</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoExample</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">PropertyExample</span><span class="p">();</span><br></pre></div>
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
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/property/main.js" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
19</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__decorate</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__decorate</span><span class="p">)</span> <span class="o" style="color:#f92672">||</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">)</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">var</span> <span class="nx">c</span> <span class="o" style="color:#f92672">=</span> <span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span><span class="p">,</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">target</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">===</span> <span class="kc" style="color:#66d9ef">null</span> <span class="o" style="color:#f92672">?</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">=</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">getOwnPropertyDescriptor</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span><span class="p">,</span> <span class="nx">d</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"object"</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"function"</span><span class="p">)</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span><span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">);</span><br>    <span class="k" style="color:#66d9ef">else</span> <span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">i</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">.</span><span class="nx">length</span> <span class="o" style="color:#f92672">-</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">;</span> <span class="nx">i</span> <span class="o" style="color:#f92672">&gt;=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">;</span> <span class="nx">i</span><span class="o" style="color:#f92672">--</span><span class="p">)</span> <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">d</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">[</span><span class="nx">i</span><span class="p">])</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">))</span> <span class="o" style="color:#f92672">||</span> <span class="nx">r</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nx">r</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">defineProperty</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">),</span> <span class="nx">r</span><span class="p">;</span><br><span class="p">};</span><br><span class="kd" style="color:#66d9ef">function</span> <span class="nx">LogProperty</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">propertyKey</span><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">target</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">propertyKey</span><span class="p">);</span><br><span class="p">}</span><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">PropertyExample</span> <span class="p">{</span><br>    <span class="nx">constructor</span><span class="p">()</span> <span class="p">{</span><br>        <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">greeting</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"Hello, world"</span><span class="p">;</span><br>    <span class="p">}</span><br><span class="p">}</span><br><span class="nx">__decorate</span><span class="p">([</span><br>    <span class="nx">LogProperty</span><br><span class="p">],</span> <span class="nx">PropertyExample</span><span class="p">.</span><span class="nx">prototype</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"greeting"</span><span class="p">,</span> <span class="k" style="color:#66d9ef">void</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">);</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoExample</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">PropertyExample</span><span class="p">();</span><br></pre></div>
</td>
</tr>
</table>

Below `__decorate`'s declaration and the simplified core logic, `__decorate`'s call cements how limited the property decorator appears. `LogProperty` isn't called with a property descriptor so any modifications it makes will persist beyond the decorator. `__decorate`'s final argument, `void 0`, reiterates that. Once again, `__decorate` has left us with solid observation options.

### Method Decorators

Logging decorators are very easy to write.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/method/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">function</span> <span class="nx">LogMethod</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">descriptor</span>: <span class="kt" style="color:#66d9ef">PropertyDescriptor</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">target</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">propertyKey</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">descriptor</span><span class="p">);</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">MethodExample</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">@LogMethod</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo() {</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoMethod</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">MethodExample</span><span class="p">();</span><br></pre></div>
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
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/method/main.js" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
20</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__decorate</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__decorate</span><span class="p">)</span> <span class="o" style="color:#f92672">||</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">)</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">var</span> <span class="nx">c</span> <span class="o" style="color:#f92672">=</span> <span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span><span class="p">,</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">target</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">===</span> <span class="kc" style="color:#66d9ef">null</span> <span class="o" style="color:#f92672">?</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">=</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">getOwnPropertyDescriptor</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span><span class="p">,</span> <span class="nx">d</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"object"</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"function"</span><span class="p">)</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span><span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">);</span><br>    <span class="k" style="color:#66d9ef">else</span> <span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">i</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">.</span><span class="nx">length</span> <span class="o" style="color:#f92672">-</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">;</span> <span class="nx">i</span> <span class="o" style="color:#f92672">&gt;=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">;</span> <span class="nx">i</span><span class="o" style="color:#f92672">--</span><span class="p">)</span> <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">d</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">[</span><span class="nx">i</span><span class="p">])</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">))</span> <span class="o" style="color:#f92672">||</span> <span class="nx">r</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nx">r</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">defineProperty</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">),</span> <span class="nx">r</span><span class="p">;</span><br><span class="p">};</span><br><span class="kd" style="color:#66d9ef">function</span> <span class="nx">LogMethod</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">propertyKey</span><span class="p">,</span> <span class="nx">descriptor</span><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">target</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">propertyKey</span><span class="p">);</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">descriptor</span><span class="p">);</span><br><span class="p">}</span><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">MethodExample</span> <span class="p">{</span><br>    <span class="nx">foo</span><span class="p">()</span> <span class="p">{</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><span class="nx">__decorate</span><span class="p">([</span><br>    <span class="nx">LogMethod</span><br><span class="p">],</span> <span class="nx">MethodExample</span><span class="p">.</span><span class="nx">prototype</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"foo"</span><span class="p">,</span> <span class="kc" style="color:#66d9ef">null</span><span class="p">);</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoMethod</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">MethodExample</span><span class="p">();</span><br></pre></div>
</td>
</tr>
</table>

Now we're getting somewhere. Method decorators provide a descriptor and update `target[propertyKey]` with changes made to `descriptor` that are returned. While the `__decorate` call ends with a `null`, as we saw above, `__decorate` should pull the proper property descriptor with a `null` tail.

To be fair, there's not a whole lot we can streamline with access to the property descriptor. Any changes made on anything but the descriptor will persist. We do, as always, have some fantastic observation options via `__decorate`, and the code is getting easier to read.

### Class Decorators

There's not much to logging a class name.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/class/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
10</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">function</span> <span class="nx">LogClass</span><span class="p">(</span><span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">target</span><span class="p">.</span><span class="kr" style="color:#66d9ef">constructor</span><span class="p">.</span><span class="nx">name</span><span class="p">);</span><br><span class="p">}</span><br><br><span class="kd" style="color:#66d9ef">@LogClass</span><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">ClassExample</span> <span class="p">{</span><br>    <span class="c1" style="color:#75715e">// do nothing</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoClass</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">ClassExample</span><span class="p">();</span><br></pre></div>
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
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/foundation/class/main.js" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">__decorate</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="k" style="color:#66d9ef">this</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">__decorate</span><span class="p">)</span> <span class="o" style="color:#f92672">||</span> <span class="kd" style="color:#66d9ef">function</span> <span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">)</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">var</span> <span class="nx">c</span> <span class="o" style="color:#f92672">=</span> <span class="nx">arguments</span><span class="p">.</span><span class="nx">length</span><span class="p">,</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">target</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">===</span> <span class="kc" style="color:#66d9ef">null</span> <span class="o" style="color:#f92672">?</span> <span class="nx">desc</span> <span class="o" style="color:#f92672">=</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">getOwnPropertyDescriptor</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">desc</span><span class="p">,</span> <span class="nx">d</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"object"</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="k" style="color:#66d9ef">typeof</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span> <span class="o" style="color:#f92672">===</span> <span class="s2" style="color:#e6db74">"function"</span><span class="p">)</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="nx">Reflect</span><span class="p">.</span><span class="nx">decorate</span><span class="p">(</span><span class="nx">decorators</span><span class="p">,</span> <span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">desc</span><span class="p">);</span><br>    <span class="k" style="color:#66d9ef">else</span> <span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kd" style="color:#66d9ef">var</span> <span class="nx">i</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">.</span><span class="nx">length</span> <span class="o" style="color:#f92672">-</span> <span class="mi" style="color:#ae81ff">1</span><span class="p">;</span> <span class="nx">i</span> <span class="o" style="color:#f92672">&gt;=</span> <span class="mi" style="color:#ae81ff">0</span><span class="p">;</span> <span class="nx">i</span><span class="o" style="color:#f92672">--</span><span class="p">)</span> <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">d</span> <span class="o" style="color:#f92672">=</span> <span class="nx">decorators</span><span class="p">[</span><span class="nx">i</span><span class="p">])</span> <span class="nx">r</span> <span class="o" style="color:#f92672">=</span> <span class="p">(</span><span class="nx">c</span> <span class="o" style="color:#f92672">&lt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">?</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">)</span> <span class="o" style="color:#f92672">:</span> <span class="nx">d</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">))</span> <span class="o" style="color:#f92672">||</span> <span class="nx">r</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="nx">c</span> <span class="o" style="color:#f92672">&gt;</span> <span class="mi" style="color:#ae81ff">3</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nx">r</span> <span class="o" style="color:#f92672">&amp;&amp;</span> <span class="nb" style="color:#f8f8f2">Object</span><span class="p">.</span><span class="nx">defineProperty</span><span class="p">(</span><span class="nx">target</span><span class="p">,</span> <span class="nx">key</span><span class="p">,</span> <span class="nx">r</span><span class="p">),</span> <span class="nx">r</span><span class="p">;</span><br><span class="p">};</span><br><span class="kd" style="color:#66d9ef">function</span> <span class="nx">LogClass</span><span class="p">(</span><span class="nx">target</span><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">target</span><span class="p">.</span><span class="nx">constructor</span><span class="p">.</span><span class="nx">name</span><span class="p">);</span><br><span class="p">}</span><br><span class="kd" style="color:#66d9ef">let</span> <span class="nx">ClassExample</span> <span class="o" style="color:#f92672">=</span> <span class="kr" style="color:#66d9ef">class</span> <span class="nx">ClassExample</span> <span class="p">{</span><br><span class="p">};</span><br><span class="nx">ClassExample</span> <span class="o" style="color:#f92672">=</span> <span class="nx">__decorate</span><span class="p">([</span><br>    <span class="nx">LogClass</span><br><span class="p">],</span> <span class="nx">ClassExample</span><span class="p">);</span><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoClass</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">ClassExample</span><span class="p">();</span><br></pre></div>
</td>
</tr>
</table>

Class decorators can directly affect the classes they decorate by modifying their return, so you won't hear me complaining about this one. The compiled result is the simplest to read, which is an added bonus.

## Recap

TypeScript builds all the decorators from the stored `__decorate` code. `__decorate` is used by the all the decorators; `__param` pops up with parameter decorators to transform their odd signature into something useful. Logging decorators are very easy to code. Without frills, parameter and property decorators are useful to monitor application flow. Method and class decorators can make simple changes without too much trouble.

## Legal

The TS logo is a [modified `@typescript` avatar](https://www.npmjs.com/~typescript); I turned the PNG into a vector. I couldn't find the original and I didn't see any licensing on the other art, so it's most likely covered by [the TypeScript project's Apache 2.0 license](https://github.com/Microsoft/TypeScript/blob/master/LICENSE.txt). Any code from the TS project is similarly licensed.

If there's a problem with anything, my email's in the footer. Stay awesome.
