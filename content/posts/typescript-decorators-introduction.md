---
title: "TypeScript Decorators: Introduction"
slug: "typescript-decorators-introduction"
date: "2018-03-04T19:00:00.000Z"
feature_image: "/images/2018/03/header-4.png"
author: "CJ Harries"
description: "This is an introduction to TypeScript decorators. It looks at the basics, factories, and composition. You should have some familiarity with TypeScript and OOP."
tags:
  - TypeScript
  - JavaScript
  - Node
  - decorators
  - patterns
  - composition
  - OOP
---

This post serves as introduction to TypeScript decorators. It looks at basic decorators, decorator factories, and decorator composition. You should have some familiarity with TypeScript and some object-oriented programming experience.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#the-series-so-far)
- [Code](#code)
- [Decorators](#decorators)
- [Configuration](#configuration)
- [Simple Example](#simple-example)
- [Decorator Factories](#decorator-factories)
- [Composition](#composition)
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

You can view the code related to this post [under the `post-01-decorator-intro` tag](//github.com/thecjharries/posts-typescript-decorators/tree/post-01-decorator-intro).

## Decorators

[The decorator pattern](https://sourcemaking.com/design_patterns/decorator) modifies instances of existing objects without affecting the root object or siblings. Typically the pattern extends a base interface by toggling features, setting attributes, or defining roles. Instances of the object being decorated should usually be able to interact, but they don't have to have identical interfaces. Like many foundational patterns, [no one agrees about the Platonic decorator](http://wiki.c2.com/?DecoratorPattern).

TypeScript provides [experimental decorator support](https://www.typescriptlang.org/docs/handbook/decorators.html). [The ECMAScript decorator proposal](https://github.com/tc39/proposal-decorators) has reached [stage 2](https://tc39.github.io/process-document/), so we could see them in vanilla JS eventually. TypeScript provides class, method, parameter, and property decorators. Each can be used to observe the decorated objects (mentioned heavily in the docs). All but the parameter decorator can be used to modify the root object.

TypeScript decorators also provide some [mixin support](https://en.wikipedia.org/wiki/Mixin). Without true [multiple inheritance](https://en.wikipedia.org/wiki/Multiple_inheritance) in JavaScript, combining features can lead to obscenely long prototype chains. TypeScript decorators alleviate that issue by adding behavior at runtime on top of normal inheritance.

## Configuration

To gain decorator functionality, you'll have to pass a few new options to the TypeScript compiler.

- `target`: The docs mention [some issues below `ES5`](https://www.typescriptlang.org/docs/handbook/decorators.html) (ctrl+f `ES5`). I tend to run `ESNext` while developing.
- `experimentalDecorators`: This is what enables the functionality.
- `emitDecoratorMetadata`: This is another expermental feature that [provides decorator metadata](https://www.typescriptlang.org/docs/handbook/decorators.html#metadata).

You can either include the options by hand every time

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> tsc --target <span class="s1" style="color:#e6db74">'ESNext'</span> --experimentalDecorators --emitDecoratorMetadata<br></pre></div>
</td></tr></table>

or you can add them to your `tsconfig.json` once.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">tsconfig.json</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/tsconfig.json" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6
7</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="p">{</span><br>  <span class="nt" style="color:#f92672">"compilerOptions"</span><span class="p">:</span> <span class="p">{</span><br>    <span class="nt" style="color:#f92672">"target"</span><span class="p">:</span> <span class="s2" style="color:#e6db74">"ESNext"</span><span class="p">,</span><br>    <span class="nt" style="color:#f92672">"experimentalDecorators"</span><span class="p">:</span> <span class="kc" style="color:#66d9ef">true</span><span class="p">,</span><br>    <span class="nt" style="color:#f92672">"emitDecoratorMetadata"</span><span class="p">:</span> <span class="kc" style="color:#66d9ef">true</span><br>  <span class="p">}</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

## Simple Example

First we need to define several decorators. Each signature was taken from [the official docs](https://www.typescriptlang.org/docs/handbook/decorators.html) and will be explained more later (but maybe not this post).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">decorators/ClassDecorator.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/intro/decorators/ClassDecorator.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">ClassDecorator</span><span class="p">(</span><br>    <span class="kr" style="color:#66d9ef">constructor</span><span class="o" style="color:#f92672">:</span> <span class="p">(...</span><span class="nx">args</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">[])</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="nx">any</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="sb" style="color:#e6db74">`Decorating </span><span class="si" style="color:#e6db74">${</span><span class="kr" style="color:#66d9ef">constructor</span><span class="p">.</span><span class="nx">name</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">`</span><span class="p">);</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">decorators/MethodDecorator.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/intro/decorators/MethodDecorator.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">MethodDecorator</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">descriptor</span>: <span class="kt" style="color:#66d9ef">PropertyDescriptor</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>        <span class="sb" style="color:#e6db74">`Decorating method </span><span class="si" style="color:#e6db74">${</span><span class="nx">propertyKey</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">`</span> <span class="o" style="color:#f92672">+</span><br>        <span class="sb" style="color:#e6db74">` from </span><span class="si" style="color:#e6db74">${</span><span class="nx">target</span><span class="p">.</span><span class="kr" style="color:#66d9ef">constructor</span><span class="p">.</span><span class="nx">name</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">`</span><span class="p">,</span><br>    <span class="p">);</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">decorators/ParameterDecorator.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/intro/decorators/ParameterDecorator.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">ParameterDecorator</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>    <span class="nx">parameterIndex</span>: <span class="kt" style="color:#66d9ef">number</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>        <span class="sb" style="color:#e6db74">`Decorating parameter </span><span class="si" style="color:#e6db74">${</span><span class="nx">propertyKey</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">`</span> <span class="o" style="color:#f92672">+</span><br>        <span class="sb" style="color:#e6db74">` (index </span><span class="si" style="color:#e6db74">${</span><span class="nx">parameterIndex</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">)`</span> <span class="o" style="color:#f92672">+</span><br>        <span class="sb" style="color:#e6db74">` from </span><span class="si" style="color:#e6db74">${</span><span class="nx">target</span><span class="p">.</span><span class="kr" style="color:#66d9ef">constructor</span><span class="p">.</span><span class="nx">name</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">`</span><span class="p">,</span><br>    <span class="p">);</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">decorators/PropertyDecorator.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/intro/decorators/PropertyDecorator.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
8
9</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">PropertyDecorator</span><span class="p">(</span><br>    <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>    <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>        <span class="sb" style="color:#e6db74">`Decorating property </span><span class="si" style="color:#e6db74">${</span><span class="nx">propertyKey</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">`</span> <span class="o" style="color:#f92672">+</span><br>        <span class="sb" style="color:#e6db74">` from </span><span class="si" style="color:#e6db74">${</span><span class="nx">target</span><span class="p">.</span><span class="kr" style="color:#66d9ef">constructor</span><span class="p">.</span><span class="nx">name</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">`</span><span class="p">,</span><br>    <span class="p">);</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

Next we'll need to consume the decorators. The decorators are placed before the object they modify, e.g. `@ClassDecorator class Foo {}`. You could use any of the decorators on any object, but you probably won't see great results unless you hit something like their intended targets. Do note that method decorators are used to modify both normal methods and `(g|s)etter` methods.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/intro/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">ClassDecorator</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./decorators/ClassDecorator"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">MethodDecorator</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./decorators/MethodDecorator"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">ParameterDecorator</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./decorators/ParameterDecorator"</span><span class="p">;</span><br><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">PropertyDecorator</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./decorators/PropertyDecorator"</span><span class="p">;</span><br><br><span class="kd" style="color:#66d9ef">@ClassDecorator</span><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">Demo</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">@PropertyDecorator</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"foo"</span><span class="p">;</span><br><br>    <span class="kr" style="color:#66d9ef">constructor</span><span class="p">()</span> <span class="p">{</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Simple class initialized"</span><span class="p">);</span><br>        <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">writeGreeting</span><span class="p">();</span><br>    <span class="p">}</span><br><br>    <span class="kd" style="color:#66d9ef">@MethodDecorator</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">get</span> <span class="nx">bar() {</span><br>        <span class="k" style="color:#66d9ef">return</span> <span class="s2" style="color:#e6db74">"bar"</span><span class="p">;</span><br>    <span class="p">}</span><br><br>    <span class="kd" style="color:#66d9ef">@MethodDecorator</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">writeGreeting</span><span class="p">(</span><br>        <span class="kd" style="color:#66d9ef">@ParameterDecorator</span> <span class="kr" style="color:#66d9ef">public</span> <span class="nx">greeting</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"Hello, world"</span><span class="p">,</span><br>    <span class="p">)</span> <span class="p">{</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">greeting</span><span class="p">);</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Demo</span><span class="p">();</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ts-node main.ts<br><span class="go" style="color:#888">Decorating property foo from Demo</span><br><span class="go" style="color:#888">Decorating method bar from Demo</span><br><span class="go" style="color:#888">Decorating parameter writeGreeting (index 0) from Demo</span><br><span class="go" style="color:#888">Decorating method writeGreeting from Demo</span><br><span class="go" style="color:#888">Decorating Demo</span><br><span class="go" style="color:#888">Simple class initialized</span><br><span class="go" style="color:#888">Hello, world</span><br></pre></div>
</td></tr></table>

The execution order is [explained in the docs](https://www.typescriptlang.org/docs/handbook/decorators.html#decorator-evaluation); to summarize,

1. instance parameter, method, and property decorators;
2. static parameter, method, and property decorators;
3. constructor parameter decorators; and
4. class decorators.

## Decorator Factories

Decorators have well-defined signatures without room for extension. To pass new information into the decorators, we can use [the factory pattern](https://sourcemaking.com/design_patterns/factory_method). A factory provides a uniform creation interface whose details are delegated to and managed by children.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">decorators/Decorator.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/factories/decorators/Decorator.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
</td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">Decorator</span><span class="p">(</span><span class="nx">type</span>: <span class="kt" style="color:#66d9ef">string</span><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="p">(...</span><span class="nx">args</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">[])</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">type</span><span class="p">,</span> <span class="nx">args</span><span class="p">);</span><br>    <span class="p">};</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

In this example, `Decorator` takes a string as input and creates a `Function`. Changing the input will create a new `Function`, but all of the `Function`s log the original input string followed by an array containing the args that the child was called with.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ts-node<br><span class="gp" style="color:#66d9ef">&gt;</span> import <span class="o" style="color:#f92672">{</span> Decorator <span class="o" style="color:#f92672">}</span> from <span class="s2" style="color:#e6db74">"./typescript/factories/decorators/Decorator.ts"</span><span class="p">;</span><br><span class="go" style="color:#888">{}</span><br><span class="gp" style="color:#66d9ef">&gt;</span> const <span class="nv" style="color:#f8f8f2">foo</span> <span class="o" style="color:#f92672">=</span> Decorator<span class="o" style="color:#f92672">(</span><span class="s2" style="color:#e6db74">"foo"</span><span class="o" style="color:#f92672">)</span><br><span class="go" style="color:#888">undefined</span><br><span class="gp" style="color:#66d9ef">&gt;</span> foo<span class="o" style="color:#f92672">(</span><span class="m" style="color:#ae81ff">1</span>, <span class="m" style="color:#ae81ff">2</span>, <span class="m" style="color:#ae81ff">3</span><span class="o" style="color:#f92672">)</span><br><span class="go" style="color:#888">foo [ 1, 2, 3 ]</span><br><span class="go" style="color:#888">undefined</span><br><span class="gp" style="color:#66d9ef">&gt;</span> const <span class="nv" style="color:#f8f8f2">bar</span> <span class="o" style="color:#f92672">=</span> Decorator<span class="o" style="color:#f92672">(</span><span class="s2" style="color:#e6db74">"bar"</span><span class="o" style="color:#f92672">)</span><br><span class="go" style="color:#888">undefined</span><br><span class="gp" style="color:#66d9ef">&gt;</span> bar<span class="o" style="color:#f92672">(</span>true, <span class="nb" style="color:#f8f8f2">false</span><span class="o" style="color:#f92672">)</span><br><span class="go" style="color:#888">bar [ true, false ]</span><br><span class="go" style="color:#888">undefined</span><br></pre></div>
</td></tr></table>

We can use this decorator everywhere thanks to [rest parameters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/rest_parameters).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/factories/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">Decorator</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./decorators/Decorator"</span><span class="p">;</span><br><br><span class="kd" style="color:#66d9ef">@Decorator</span><span class="p">(</span><span class="s2" style="color:#e6db74">"class"</span><span class="p">)</span><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">Demo</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">@Decorator</span><span class="p">(</span><span class="s2" style="color:#e6db74">"property"</span><span class="p">)</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"foo"</span><span class="p">;</span><br><br>    <span class="kr" style="color:#66d9ef">constructor</span><span class="p">()</span> <span class="p">{</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"Simple class initialized"</span><span class="p">);</span><br>        <span class="k" style="color:#66d9ef">this</span><span class="p">.</span><span class="nx">writeGreeting</span><span class="p">();</span><br>    <span class="p">}</span><br><br>    <span class="kd" style="color:#66d9ef">@Decorator</span><span class="p">(</span><span class="s2" style="color:#e6db74">"accessor"</span><span class="p">)</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">get</span> <span class="nx">bar() {</span><br>        <span class="k" style="color:#66d9ef">return</span> <span class="s2" style="color:#e6db74">"bar"</span><span class="p">;</span><br>    <span class="p">}</span><br><br>    <span class="kd" style="color:#66d9ef">@Decorator</span><span class="p">(</span><span class="s2" style="color:#e6db74">"method"</span><span class="p">)</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">writeGreeting</span><span class="p">(</span><br>        <span class="kd" style="color:#66d9ef">@Decorator</span><span class="p">(</span><span class="s2" style="color:#e6db74">"parameter"</span><span class="p">)</span> <span class="kr" style="color:#66d9ef">public</span> <span class="nx">greeting</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">=</span> <span class="s2" style="color:#e6db74">"Hello, world"</span><span class="p">,</span><br>    <span class="p">)</span> <span class="p">{</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">greeting</span><span class="p">);</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Demo</span><span class="p">();</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ts-node main.ts<br><span class="go" style="color:#888">property [ Demo {}, 'foo', undefined ]</span><br><span class="go" style="color:#888">accessor [ Demo {},</span><br><span class="go" style="color:#888">  'bar',</span><br><span class="go" style="color:#888">  { get: [Function: get bar],</span><br><span class="go" style="color:#888">    set: undefined,</span><br><span class="go" style="color:#888">    enumerable: false,</span><br><span class="go" style="color:#888">    configurable: true } ]</span><br><span class="go" style="color:#888">parameter [ Demo {}, 'writeGreeting', 0 ]</span><br><span class="go" style="color:#888">method [ Demo {},</span><br><span class="go" style="color:#888">  'writeGreeting',</span><br><span class="go" style="color:#888">  { value: [Function: writeGreeting],</span><br><span class="go" style="color:#888">    writable: true,</span><br><span class="go" style="color:#888">    enumerable: false,</span><br><span class="go" style="color:#888">    configurable: true } ]</span><br><span class="go" style="color:#888">class [ [Function: Demo] ]</span><br><span class="go" style="color:#888">Simple class initialized</span><br><span class="go" style="color:#888">Hello, world</span><br></pre></div>
</td></tr></table>

While this example was fairly simple, decorator factories are capable of much more. Anything you pass to the factory can be used to assemble the decorator. As the decorator's return is used by everything except for parameter decorators, you can customize the instance using anything in the scope. Decorators aren't limited to building up; they can also tear down.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">decorators/MaskMethod.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/factories/decorators/MaskMethod.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
14</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">MaskMethod</span><span class="p">(</span><span class="nx">hide</span>: <span class="kt" style="color:#66d9ef">boolean</span><span class="p">)</span> <span class="p">{</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="p">(</span><br>        <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>        <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>        <span class="nx">descriptor</span>: <span class="kt" style="color:#66d9ef">PropertyDescriptor</span><span class="p">,</span><br>    <span class="p">)</span> <span class="o" style="color:#f92672">=&gt;</span> <span class="p">{</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="nx">hide</span><span class="p">)</span> <span class="p">{</span><br>            <span class="k" style="color:#66d9ef">return</span> <span class="p">{</span><br>                <span class="nx">get</span>: <span class="kt" style="color:#66d9ef">undefined</span><span class="p">,</span><br>            <span class="p">};</span><br>        <span class="p">}</span><br>        <span class="k" style="color:#66d9ef">return</span> <span class="nx">descriptor</span><span class="p">;</span><br>    <span class="p">};</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

This decorator can hide methods at run time by tweaking [the property descriptor](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty#Description) for the method.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">other-main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/factories/other-main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">MaskMethod</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./decorators/MaskMethod"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">MaskableMethods</span> <span class="p">{</span><br>    <span class="kd" style="color:#66d9ef">@MaskMethod</span><span class="p">(</span><span class="kc" style="color:#66d9ef">true</span><span class="p">)</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">foo() {</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"foo"</span><span class="p">);</span><br>    <span class="p">}</span><br><br>    <span class="kd" style="color:#66d9ef">@MaskMethod</span><span class="p">(</span><span class="kc" style="color:#66d9ef">false</span><span class="p">)</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">bar() {</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2" style="color:#e6db74">"bar"</span><span class="p">);</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demoMaskableMethods</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">MaskableMethods</span><span class="p">();</span><br><br><span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kr" style="color:#66d9ef">const</span> <span class="nx">key</span> <span class="nx">of</span> <span class="p">[</span><span class="s2" style="color:#e6db74">"foo"</span><span class="p">,</span> <span class="s2" style="color:#e6db74">"bar"</span><span class="p">])</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">key</span><span class="p">,</span> <span class="nx">demo</span><span class="p">[</span><span class="nx">key</span><span class="p">]);</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ts-node other-main.ts<br><span class="go" style="color:#888">foo undefined</span><br><span class="go" style="color:#888">bar bar() {</span><br><span class="go" style="color:#888">        console.log("bar");</span><br><span class="go" style="color:#888">    }</span><br></pre></div>
</td></tr></table>

## Composition

[Function composition](https://en.wikipedia.org/wiki/Function_composition) is a very useful tool. It requires two functions, `f: A → B` and `g: C → D`, with some conditions on their domains and ranges. To compose `f` with `g`, i.e. `f(g(x))`, `D` must be a subset of `A`, i.e. the input of `f` must contain the output of `g`.

This is much simpler in code. For the most part, we can compose `f` with `g` when `g`'s return value is identical to `f`'s input (completely ignoring containment because that gets messy). As we've seen, decorators seem to return a single object while they consume an array of arguments. That would suggest they cannot be composed. However, decorators aren't actually being called and run on the stack by themselves. TypeScript surrounds the decorator calls with several other things behind the scenes, which, rather magically, means decorators can be composed with other decorators.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">decorators/Enumerable.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/composition/decorators/Enumerable.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">export</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">Enumerable</span><span class="p">(</span><span class="nx">enumerable</span>: <span class="kt" style="color:#66d9ef">boolean</span> <span class="o" style="color:#f92672">=</span> <span class="kc" style="color:#66d9ef">true</span><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>        <span class="sb" style="color:#e6db74">`Creating </span><span class="si" style="color:#e6db74">${</span><span class="nx">enumerable</span> <span class="o" style="color:#f92672">?</span> <span class="s2" style="color:#e6db74">""</span> <span class="o" style="color:#f92672">:</span> <span class="s2" style="color:#e6db74">"non-"</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">`</span> <span class="o" style="color:#f92672">+</span><br>        <span class="sb" style="color:#e6db74">`enumerable property factory`</span><span class="p">,</span><br>    <span class="p">);</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="kd" style="color:#66d9ef">function</span> <span class="nx">decorator</span><span class="p">(</span><br>        <span class="nx">target</span>: <span class="kt" style="color:#66d9ef">any</span><span class="p">,</span><br>        <span class="nx">propertyKey</span>: <span class="kt" style="color:#66d9ef">string</span> <span class="o" style="color:#f92672">|</span> <span class="nx">symbol</span><span class="p">,</span><br>        <span class="nx">descriptor</span>: <span class="kt" style="color:#66d9ef">PropertyDescriptor</span><span class="p">,</span><br>    <span class="p">)</span> <span class="p">{</span><br>        <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><br>            <span class="sb" style="color:#e6db74">`Making </span><span class="si" style="color:#e6db74">${</span><span class="nx">propertyKey</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">`</span> <span class="o" style="color:#f92672">+</span><br>            <span class="sb" style="color:#e6db74">` </span><span class="si" style="color:#e6db74">${</span><span class="nx">enumerable</span> <span class="o" style="color:#f92672">?</span> <span class="s2" style="color:#e6db74">""</span> <span class="o" style="color:#f92672">:</span> <span class="s2" style="color:#e6db74">"non-"</span><span class="si" style="color:#e6db74">}</span><span class="sb" style="color:#e6db74">enumerable`</span><span class="p">,</span><br>        <span class="p">);</span><br>        <span class="nx">descriptor</span><span class="p">.</span><span class="nx">enumerable</span> <span class="o" style="color:#f92672">=</span> <span class="nx">enumerable</span><span class="p">;</span><br>        <span class="k" style="color:#66d9ef">return</span> <span class="nx">descriptor</span><span class="p">;</span><br>    <span class="p">};</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

This decorator updates the `enumerable` property of methods, showing/hiding them when iterating over the object. To illustrate how it works, this class has two methods that are only decorated once. To illustrate composition, another two are decorated twice.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40">
<div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">main.ts</div>
<div class="code-tab" style="color:#57584f; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px" height="35"><a target="_blank" href="https://github.com/thecjharries/posts-typescript-decorators/blob/master/typescript/composition/main.ts" style="color:inherit; display:block; position:relative; text-decoration:none">view source <i class="fa fa-external-link" style="color:inherit; height:35px; line-height:35px" height="35"></i></a></div>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="kr" style="color:#66d9ef">import</span> <span class="p">{</span> <span class="nx">Enumerable</span> <span class="p">}</span> <span class="nx">from</span> <span class="s2" style="color:#e6db74">"./decorators/Enumerable"</span><span class="p">;</span><br><br><span class="kr" style="color:#66d9ef">class</span> <span class="nx">Demo</span> <span class="p">{</span><br><br>    <span class="kd" style="color:#66d9ef">@Enumerable</span><span class="p">(</span><span class="kc" style="color:#66d9ef">true</span><span class="p">)</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">isEnumerable() {</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><br>    <span class="kd" style="color:#66d9ef">@Enumerable</span><span class="p">(</span><span class="kc" style="color:#66d9ef">true</span><span class="p">)</span><br>    <span class="kd" style="color:#66d9ef">@Enumerable</span><span class="p">(</span><span class="kc" style="color:#66d9ef">false</span><span class="p">)</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">resultIsEnumerable() {</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><br>    <span class="kd" style="color:#66d9ef">@Enumerable</span><span class="p">(</span><span class="kc" style="color:#66d9ef">false</span><span class="p">)</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">isNotEnumerable() {</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><br>    <span class="kd" style="color:#66d9ef">@Enumerable</span><span class="p">(</span><span class="kc" style="color:#66d9ef">false</span><span class="p">)</span><br>    <span class="kd" style="color:#66d9ef">@Enumerable</span><span class="p">(</span><span class="kc" style="color:#66d9ef">true</span><span class="p">)</span><br>    <span class="kr" style="color:#66d9ef">public</span> <span class="nx">resultIsNotEnumerable() {</span><br>        <span class="c1" style="color:#75715e">// do nothing</span><br>    <span class="p">}</span><br><span class="p">}</span><br><br><span class="kr" style="color:#66d9ef">const</span> <span class="nx">demo</span> <span class="o" style="color:#f92672">=</span> <span class="k" style="color:#66d9ef">new</span> <span class="nx">Demo</span><span class="p">();</span><br><br><span class="c1" style="color:#75715e">// tslint:disable-next-line:forin</span><br><span class="k" style="color:#66d9ef">for</span> <span class="p">(</span><span class="kr" style="color:#66d9ef">const</span> <span class="nx">key</span> <span class="k" style="color:#66d9ef">in</span> <span class="nx">demo</span><span class="p">)</span> <span class="p">{</span><br>    <span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="nx">key</span><span class="p">);</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ts-node main.ts<br><span class="go" style="color:#888">Creating enumerable property factory</span><br><span class="go" style="color:#888">Making isEnumerable enumerable</span><br><span class="go" style="color:#888">Creating enumerable property factory</span><br><span class="go" style="color:#888">Creating non-enumerable property factory</span><br><span class="go" style="color:#888">Making resultIsEnumerable non-enumerable</span><br><span class="go" style="color:#888">Making resultIsEnumerable enumerable</span><br><span class="go" style="color:#888">Creating non-enumerable property factory</span><br><span class="go" style="color:#888">Making isNotEnumerable non-enumerable</span><br><span class="go" style="color:#888">Creating non-enumerable property factory</span><br><span class="go" style="color:#888">Creating enumerable property factory</span><br><span class="go" style="color:#888">Making resultIsNotEnumerable enumerable</span><br><span class="go" style="color:#888">Making resultIsNotEnumerable non-enumerable</span><br><span class="go" style="color:#888">isEnumerable</span><br><span class="go" style="color:#888">resultIsEnumerable</span><br></pre></div>
</td></tr></table>

The first decorator factory builds its factory first, but executes the factory last. The second decorator's build and execution are sandwiched between the two components of the first. The more decorators chained, the deeper the nesting. To resolve the composition, each call must be finished in turn.

## Recap

Decorators provide a way for children to manage their responsibilities and options. TypeScript supports decorators (experimentally for now) with a very simple interface. When basic decorators don't cut it, the vanilla options can be extended with decorator factories. Composing decorators with decorators allows us to combine multiple decorators on the same object.

I think I'm going to look at the generated JavaScript next. Don't hold me to that.

## Legal

The TS logo is a [modified `@typescript` avatar](https://www.npmjs.com/~typescript); I turned the PNG into a vector. I couldn't find the original and I didn't see any licensing on the other art, so it's most likely covered by [the TypeScript project's Apache 2.0 license](https://github.com/Microsoft/TypeScript/blob/master/LICENSE.txt). Any code from the TS project is similarly licensed.

If there's a problem with anything, my email's in the footer. Stay awesome.
