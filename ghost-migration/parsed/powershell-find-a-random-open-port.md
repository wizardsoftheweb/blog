---
title: "Find a Random Open Port in PowerShell"
slug: "powershell-find-a-random-open-port"
date: "2018-01-04T01:00:00.000Z"
author: "CJ Harries"
description: "Quick and dirty module to get an open port."
tags: 
  - PowerShell
  - CLI
  - Windows
draft: true
---

This has been sitting in my drafts for some time. Based on some of my experiences this week and some of the stuff we're trying to do at work, I'll probably have more PowerShell soon. Unfortunately.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">RandomizedPort.psm1</div></td>
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
39</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="cm" style="color:#75715e">&lt;#</span><br><span class="sd" style="color:#e6db74">.SYNOPSIS</span><span class="cm" style="color:#75715e"></span><br><span class="cm" style="color:#75715e">Generates a random port number in a (hopefully) open range.</span><br><span class="sd" style="color:#e6db74">.LINK</span><span class="cm" style="color:#75715e"></span><br><span class="cm" style="color:#75715e">https://www.cymru.com/jtk/misc/ephemeralports.html</span><br><span class="cm" style="color:#75715e">#&gt;</span><br><span class="k" style="color:#66d9ef">Function</span> <span class="nb" style="color:#f8f8f2">Get-RandomPort</span><br><span class="p">{</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="nb" style="color:#f8f8f2">Get-Random</span> <span class="n">-Max</span> <span class="n">32767</span> <span class="n">-Min</span> <span class="n">10001</span><span class="p">;</span><br><span class="p">}</span><br><br><span class="k" style="color:#66d9ef">Function</span> <span class="nb" style="color:#f8f8f2">Test-PortInUse</span><br><span class="p">{</span><br>    <span class="k" style="color:#66d9ef">Param</span><span class="p">(</span><br>        <span class="p">[</span><span class="k" style="color:#66d9ef">Parameter</span><span class="p">(</span><span class="k" style="color:#66d9ef">Mandatory</span><span class="p">=</span><span class="nv" style="color:#f8f8f2">$true</span><span class="p">)]</span><br>        <span class="no" style="color:#66d9ef">[Int]</span> <span class="nv" style="color:#f8f8f2">$portToTest</span><br>    <span class="p">);</span><br>    <span class="nv" style="color:#f8f8f2">$count</span> <span class="p">=</span> <span class="n">netstat</span> <span class="n">-aon</span> <span class="p">|</span> <span class="n">find</span> <span class="p">`"</span><span class="err" style="background-color:#1e0010; color:#960050" bgcolor="#1e0010">:</span><span class="nv" style="color:#f8f8f2">$portToTest</span> <span class="p">`"</span> <span class="p">/</span><span class="n">c</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="no" style="color:#66d9ef">[bool]</span><span class="p">(</span><span class="nv" style="color:#f8f8f2">$count</span> <span class="o" style="color:#f92672">-gt</span> <span class="n">0</span><span class="p">);</span><br><span class="p">}</span><br><br><span class="k" style="color:#66d9ef">Function</span> <span class="nb" style="color:#f8f8f2">Get-RandomUsablePort</span><br><span class="p">{</span><br>    <span class="k" style="color:#66d9ef">Param</span><span class="p">(</span><br>        <span class="no" style="color:#66d9ef">[Int]</span> <span class="nv" style="color:#f8f8f2">$maxTries</span> <span class="p">=</span> <span class="n">100</span><br>    <span class="p">);</span><br>    <span class="nv" style="color:#f8f8f2">$result</span> <span class="p">=</span> <span class="p">-</span><span class="n">1</span><span class="p">;</span><br>    <span class="nv" style="color:#f8f8f2">$tries</span> <span class="p">=</span> <span class="n">0</span><span class="p">;</span><br>    <span class="k" style="color:#66d9ef">DO</span><br>    <span class="p">{</span><br>        <span class="nv" style="color:#f8f8f2">$randomPort</span> <span class="p">=</span> <span class="nb" style="color:#f8f8f2">Get-RandomPort</span><span class="p">;</span><br>        <span class="k" style="color:#66d9ef">if</span> <span class="p">(</span><span class="o" style="color:#f92672">-Not</span> <span class="p">(</span><span class="nb" style="color:#f8f8f2">Test-PortInUse</span><span class="p">(</span><span class="nv" style="color:#f8f8f2">$randomPort</span><span class="p">)))</span><br>        <span class="p">{</span><br>            <span class="nv" style="color:#f8f8f2">$result</span> <span class="p">=</span> <span class="nv" style="color:#f8f8f2">$randomPort</span><span class="p">;</span><br>        <span class="p">}</span><br>        <span class="nv" style="color:#f8f8f2">$tries</span> <span class="p">+=</span> <span class="n">1</span><span class="p">;</span><br>    <span class="p">}</span> <span class="k" style="color:#66d9ef">While</span> <span class="p">((</span><span class="nv" style="color:#f8f8f2">$result</span> <span class="o" style="color:#f92672">-lt</span> <span class="n">0</span><span class="p">)</span> <span class="o" style="color:#f92672">-and</span> <span class="p">(</span><span class="nv" style="color:#f8f8f2">$tries</span> <span class="o" style="color:#f92672">-lt</span> <span class="nv" style="color:#f8f8f2">$maxTries</span><span class="p">));</span><br>    <span class="k" style="color:#66d9ef">return</span> <span class="nv" style="color:#f8f8f2">$result</span><span class="p">;</span><br><span class="p">}</span><br></pre></div>
</td>
</tr>
</table>