---
title: "Sensible SSH with Ansible: An Ansible Primer"
slug: "sensible-ssh-with-ansible-ansible-primer"
date: "2018-01-21T01:00:00.000Z"
feature_image: "/images/2017/11/gear-7.png"
author: "CJ Harries"
description: "This post serves as an Ansible primer. It looks at each component of an Ansible playbook with plenty of examples."
tags:
  - Sensible SSH with Ansible
  - Ansible
  - Vagrant
  - ssh
  - Automation
  - security
  - OpenSSH
---
<!-- markdownlint-disable MD037 MD052 -->

This is the third in a series of several posts on how to manage `ssh` via Ansible. It was inspired by [a warning from Venafi](https://www.venafi.com/blog/ssh-keys-lowest-cost-highest-risk-security-tool) that gained traction in the blogosphere (read: my Google feed for two weeks). I don't know many people that observe good `ssh` security, so my goal is to make it more accessible and (somewhat) streamlined.

This post serves as an Ansible primer. It assumes shell knowledge but nothing else. The post looks at each component of an Ansible playbook with plenty of examples. It doesn't explain any of the Ansible modules in detail, but does occasionally investigate how Ansible core works. If you're already familiar with Ansible, you can probably skip this. I removed anything involving the overarching project to simplify things.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#the-series-so-far)
- [Code](#code)
- [Note](#note)
- [Ansible](#ansible)
- [Configuration](#configuration)
  - [`ansible-config`](#ansible-config)
- [Inventory](#inventory)
- [Ad-Hoc Commands](#ad-hoc-commands)
- [Playbooks](#playbooks)
  - [Jinja2](#jinja2)
  - [Play Meta](#play-meta)
  - [Tasks](#tasks)
  - [Handlers](#handlers)
- [Roles](#roles)
- [Recap](#recap)

## The Series so Far

1. [Overview](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-overview)
2. [Creating the Status Quo](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-vagrant-setup)
3. [An Ansible Primer](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-ansible-primer)

(This section should get updated as series progresses.)

## Code

You can view the code related to this post [under the `post-03-ansible-primer` tag](//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/post-03-ansible-primer).

## Note

The first post has [a quick style section](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-overview#note) that might be useful.

If you're using Vagrant on Windows with Hyper-V, there's a good chance you'll need to append `--provider=hyperv` to any `vagrant up` commands. If you're not sure, don't worry. Windows will be very helpful and crash with a BSOD (technically green now) if you use the wrong provider. The first post has [more information](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-overview#windows) on this useful feature.

I'm still fairly new to Ansible, so if something is horribly wrong, please let me know and I'll fix it ASAP. I've tried to follow [the best practices](http://docs.ansible.com/ansible/latest/playbooks_best_practices.html). I still don't know what I don't know about Ansible, so the code might change drastically from post to post as I discover new things.

## Ansible

Ansible is great. Using basic markup, you can script most of the things you can think of doing via a good command line (so not PowerShell). It even got me to begrudgingly learn Python. Rather than waste time gushing about how easy it is to use and how much it can change your life, I'll jump right in.

## Configuration

If you're a masochist and enjoy manually specifying every option and every flag on every Ansible command directly, skip this section. If that doesn't sound fun, you can instead use a configuration file to [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) your scripting.

[Out of the box](http://docs.ansible.com/ansible/latest/intro_configuration.html), Ansible loads its (possibly empty) global configuration file, `/etc/ansible/ansible.cfg`. If you're working in a shared environment, or previously set up Ansible, Ansible might load an environment or userspace config file instead. Luckily, Ansible conveniently provides its discovered config with the `--version` flag:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible --version<br><span class="go" style="color:#888">ansible 2.4.1.0</span><br><span class="go" style="color:#888">  config file = None</span><br><span class="go" style="color:#888">  ...</span><br><span class="gp" style="color:#66d9ef">$</span> touch ~/.ansible.cfg<br><span class="gp" style="color:#66d9ef">$</span> ansible --version<br><span class="go" style="color:#888">ansible 2.4.1.0</span><br><span class="go" style="color:#888">  config file = /home/user/.ansible.cfg</span><br><span class="go" style="color:#888">  ...</span><br></pre></div>
</td></tr></table>

Ansible only loads the first file it finds. It won't merge, say, a local directory config and your global `$HOME` config. Ansible starts with [its base configuration](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/config/base.yml) and updates only the values you've specified. If you're not paying attention, this can often bite you. For example, the default inventory, `/etc/ansible/hosts`, probably doesn't contain the hosts you're about to set up. You'll either have to specify a local inventory at execution via the `-i`nventory flag always or add `inventory = /path/to/inventory` to the project's main config file once. I prefer the latter option.

### `ansible-config`

If you're using Ansible `>=2.4`, you can quickly verify config via `ansible-config`. If you're not using Ansible `>=2.4` and don't have a serious architecture reason to resist change, pause, go update Ansible, and come back.

The `--only-changed` flag with `dump` is mind-blowingly useful when trying to figure out what's not stock:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-config dump --only-changed<br></pre></div>
</td></tr></table>

You can also view the entire configuration, which is just as insanely useful for debugging as the `--only-changed` refinement.

## Inventory

[Ansible's inventory](http://docs.ansible.com/ansible/latest/intro_inventory.html) provides all the information necessary to manage the desired machines, local or remote. You'll need to add things like addresses and usernames, so be careful with its contents. I personally wouldn't store that information, even encrypted, in a public repo, but YMMV.

(Quick aside: You can also use [dynamic inventories](http://docs.ansible.com/ansible/latest/intro_dynamic_inventory.html), generated from local code or API returns. I really want to try this, and might hit it later.)

While inventories can be one of many supported filetypes, I'll be using YAML files. I find it easier to keep track of all the Ansible configuration when I don't have to swap between syntaxes (as similar as they are).

The first component of an inventory entry ([in YAML, at least](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/plugins/inventory/yaml.py#L97)) is the owning group. `all` is a magic group that can be used when you don't want to explicitly name the group of hosts; even if you don't use it, `all` will get all the hosts in the inventory.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">inventory</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">---</span><br><span class="l l-Scalar l-Scalar-Plain">my_first_group</span><span class="p p-Indicator">:</span><br>  <span class="c1" style="color:#75715e"># ...</span><br><span class="l l-Scalar l-Scalar-Plain">all</span><span class="p p-Indicator">:</span><br>  <span class="c1" style="color:#75715e"># ...</span><br>  <span class="c1" style="color:#75715e"># also magically contains my_first_group</span><br></pre></div>
</td>
</tr>
</table>

Below the group is its defining characteristics such as its child `hosts`, any `children` groups, and group-scope `vars`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">inventory</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">---</span><br><span class="l l-Scalar l-Scalar-Plain">all</span><span class="p p-Indicator">:</span><br>  <span class="l l-Scalar l-Scalar-Plain">hosts</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">specific_host</span><span class="p p-Indicator">:</span><br>      <span class="c1" style="color:#75715e"># ...</span><br>    <span class="l l-Scalar l-Scalar-Plain">other_host</span><span class="p p-Indicator">:</span><br>      <span class="c1" style="color:#75715e"># ...</span><br>  <span class="l l-Scalar l-Scalar-Plain">children</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">child_group</span><span class="p p-Indicator">:</span><br>      <span class="l l-Scalar l-Scalar-Plain">hosts</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">turtles_all_the_way_down</span><span class="p p-Indicator">:</span><br>          <span class="c1" style="color:#75715e"># ...</span><br>  <span class="l l-Scalar l-Scalar-Plain">vars</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">group_scoped_variable</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'can</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">be</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">overriden</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">per</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">host'</span><br></pre></div>
</td>
</tr>
</table>

Each of the `hosts` may redefine [connection behavior](http://docs.ansible.com/ansible/latest/intro_inventory.html#list-of-behavioral-inventory-parameters) and can also defined host-specific variables (not related to Ansible):

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">inventory</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">---</span><br><span class="l l-Scalar l-Scalar-Plain">all</span><span class="p p-Indicator">:</span><br>  <span class="l l-Scalar l-Scalar-Plain">hosts</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">specific_host</span><span class="p p-Indicator">:</span><br>      <span class="l l-Scalar l-Scalar-Plain">ansible_user</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">cool_user</span><br>      <span class="l l-Scalar l-Scalar-Plain">host_scoped_variable</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'not</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">accessible</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">to</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">its</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">group'</span><br></pre></div>
</td>
</tr>
</table>

To make managing all of this information easier, you can split out group and host `vars`. Ansible searches for `group_vars/groupname.yml` and `host_vars/hostname.yml` in the `inventory` path. If found, Ansible merges those `vars` in with the variables defined in the `inventory_file`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> tree example-inventory<br><span class="go" style="color:#888">example_inventory</span><br><span class="go" style="color:#888">├── group_vars</span><br><span class="go" style="color:#888">│   ├── all.yml</span><br><span class="go" style="color:#888">│   └── named_group.yml</span><br><span class="go" style="color:#888">├── host_vars</span><br><span class="go" style="color:#888">│   └── specific_hostname.yml</span><br><span class="go" style="color:#888">├── named_group.yml</span><br><span class="go" style="color:#888">└── ungrouped.yml</span><br><br><span class="go" style="color:#888">2 directories, 5 files</span><br></pre></div>
</td></tr></table>

[The precedence](http://docs.ansible.com/ansible/latest/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable) might be surprising: facts from an inventory file are replaced by facts from `(group|host)_vars`. Using the above example, these values represent the final value of facts defined in multiple locations (assuming they're only set in the inventory):

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
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
30</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">---</span><br><span class="c1" style="color:#75715e"># Set in:</span><br><span class="c1" style="color:#75715e"># - under named_group vars in named_group.yml</span><br><span class="l l-Scalar l-Scalar-Plain">group_inventory_final_say</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'named_group.yml'</span><br><br><span class="c1" style="color:#75715e"># Set in:</span><br><span class="c1" style="color:#75715e"># - under named_group vars in named_group.yml</span><br><span class="c1" style="color:#75715e"># - group_vars/all.yml</span><br><span class="l l-Scalar l-Scalar-Plain">all_group_vars_final_say</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'group_vars/all.yml'</span><br><br><span class="c1" style="color:#75715e"># Set in:</span><br><span class="c1" style="color:#75715e"># - under named_group vars in named_group.yml</span><br><span class="c1" style="color:#75715e"># - group_vars/all.yml</span><br><span class="c1" style="color:#75715e"># - group_vars/named_group.yml</span><br><span class="l l-Scalar l-Scalar-Plain">group_vars_final_say</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'group_vars/named_group.yml'</span><br><br><span class="c1" style="color:#75715e"># Set in:</span><br><span class="c1" style="color:#75715e"># - under named_group vars in named_group.yml</span><br><span class="c1" style="color:#75715e"># - group_vars/all.yml</span><br><span class="c1" style="color:#75715e"># - group_vars/named_group.yml</span><br><span class="c1" style="color:#75715e"># - under specific_hostname (directly) in named_group.yml</span><br><span class="l l-Scalar l-Scalar-Plain">host_inventory_final_say</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'named_group.yml'</span><br><br><span class="c1" style="color:#75715e"># Set in:</span><br><span class="c1" style="color:#75715e"># - under named_group vars in named_group.yml</span><br><span class="c1" style="color:#75715e"># - group_vars/all.yml</span><br><span class="c1" style="color:#75715e"># - group_vars/named_group.yml</span><br><span class="c1" style="color:#75715e"># - under specific_hostname (directly) in named_group.yml</span><br><span class="c1" style="color:#75715e"># - host_vars/specific_hostname.yml</span><br><span class="l l-Scalar l-Scalar-Plain">host_vars_final_say</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'host_vars/specific_hostname.yml'</span><br></pre></div>
</td>
</tr></table>

## Ad-Hoc Commands

Ansible exposes its API for quick access via [ad-hoc commands](http://docs.ansible.com/ansible/latest/intro_adhoc.html). Ad-hoc commands aren't run as part of a playbook, so they're very useful for debugging or one-off calls. Similar to tasks inside a playbook (explained [later](#playbooks)), you must specify the host(s), the module, and its arguments.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible &lt;host or group&gt; -m &lt;module name&gt; -a <span class="s2" style="color:#e6db74">"&lt;arguments to pass to the module&gt;"</span><br></pre></div>
</td></tr></table>

A common "hello world" command uses [the `ping` module](http://docs.ansible.com/ansible/latest/ping_module.html):

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible --connection<span class="o" style="color:#f92672">=</span><span class="nb" style="color:#f8f8f2">local</span> localhost -m ping<br><span class="go" style="color:#888">localhost | SUCCESS =&gt; {</span><br><span class="go" style="color:#888">    "changed": false,</span><br><span class="go" style="color:#888">    "failed": false,</span><br><span class="go" style="color:#888">    "ping": "pong"</span><br><span class="go" style="color:#888">}</span><br></pre></div>
</td></tr></table>

[The `debug` module](http://docs.ansible.com/ansible/latest/debug_module.html) provides a fast way to view variables. For example, let's check a few Ansible variables against `localhost`:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible --connection<span class="o" style="color:#f92672">=</span><span class="nb" style="color:#f8f8f2">local</span> localhost -m debug -a <span class="s1" style="color:#e6db74">'msg="Host is {{ ansible_host }} as {{ inventory_hostname }} defined {{ \"locally\" if inventory_file is not defined else (\"in \" + inventory_file) }}"\'</span><br><span class="go" style="color:#888">localhost | SUCCESS =&gt; {</span><br><span class="go" style="color:#888">    "msg": "Host is 127.0.0.1 as localhost defined locally"</span><br><span class="go" style="color:#888">}</span><br></pre></div>
</td></tr></table>

There are no ad-hoc commands in [the actual codebase](//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/post-03-ansible-primer/provisioning), as the calls are all in playbooks or roles. However, I might occasionally use an ad-hoc command to illustrate a task, and I highly recommend running tasks here as commands to understand how they work.

## Playbooks

Ansible proper runs blocks of actions on hosts in [YAML files called playbooks](http://docs.ansible.com/ansible/latest/playbooks_intro.html). Playbooks are lists of plays, which contain targets, variables, and actions to execute. [The previous section](#ad-hoc-commands) can be rewritten as follows:
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">playbook.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">---</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">hosts</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">localhost</span><br>  <span class="l l-Scalar l-Scalar-Plain">connection</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">local</span><br><br>  <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ping the host</span><br>      <span class="l l-Scalar l-Scalar-Plain">ping</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Print hostname metadata</span><br>      <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"Host</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">is</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">ansible_host</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">as</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">inventory_hostname</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">defined</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">'locally'</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">if</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">inventory_file</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">is</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">not</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">defined</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">else</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">('in</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">'</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">+</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">inventory_file)</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br></pre></div>
</td>
</tr>
</table>

When run, it looks something like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml<br><span class="go" style="color:#888">PLAY [localhost] **********************************************************</span><br><br><span class="go" style="color:#888">TASK [Gathering Facts] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Ping the host] *****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Print hostname metadata] ********************************************</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; {</span><br><span class="go" style="color:#888">    "msg": "Host is 127.0.0.1 as localhost defined locally"</span><br><span class="go" style="color:#888">}</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=3    changed=0    unreachable=0    failed=0</span><br></pre></div>
</td></tr></table>

### Jinja2

Ansible templates playbooks (and related files) via [Jinja2](http://jinja.pocoo.org/). [The docs](http://docs.ansible.com/ansible/latest/playbooks_templating.html) include wonderfully handy details, like [useful transformation filters](http://docs.ansible.com/ansible/latest/playbooks_filters.html) (which links [Jinja2's built-in filters](http://jinja.pocoo.org/docs/2.10/templates/#builtin-filters), an equally handy read). I'm just going to explain Jinja2 basics in Ansible here, as covering [a rich templating engine](http://jinja.pocoo.org/docs/2.10/api/) is beyond the scope of this post and project.

Jinja2 searches each template for `{{ <expression> }}` (actual templates might [include other delimiters](http://jinja.pocoo.org/docs/2.10/templates/#synopsis), e.g. when using [the `template` module](http://docs.ansible.com/ansible/latest/template_module.html)). For the most part, these are [variables to replace](http://jinja.pocoo.org/docs/2.10/templates/#variables), possibly after applying [a filter](http://jinja.pocoo.org/docs/2.10/templates/#filters), but Jinja2 expressions can also include valid code so long as it returns a value (I think; I don't know enough about Python yet to really explore potential counter-examples).

All of Ansible's playbook YAML files are rendered with Jinja2 before being sent to the target (I believe that logic is [here](https://github.com/ansible/ansible/tree/v2.4.1.0-1/lib/ansible/template); those classes showed up elsewhere while investigating playbook execution). Recent versions of Ansible have begun to include some template style feedback (e.g. [no templates in conditionals](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/conditional.py#L131)), but, for the most part, you're on your own.

Personally, I wrap anything templated in double quotes, e.g. `"{{ variable_name }}"`, which means I can quickly distinguish between strings that are templated and those that are not, i.e. `"is {{ 'templated' }}"` vs `'is not templated'`. Ansible's [interpretation of the YAML spec](https://github.com/ansible/ansible/tree/v2.4.1.0-1/lib/ansible/parsing/yaml) is fairly loose (as is [the spec](https://www.reddit.com/r/programming/comments/7ctwi7/yaml_sucks/)); the docs highlight [a few important gotchas](http://docs.ansible.com/ansible/latest/YAMLSyntax.html).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">---</span><br><span class="l l-Scalar l-Scalar-Plain">not_parsed</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">this entire string</span><br><span class="l l-Scalar l-Scalar-Plain">easier_to_skim_not_parsed</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'this</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">entire</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">string'</span><br><br><span class="l l-Scalar l-Scalar-Plain">user_config_directory</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"/home/{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">ansible_user</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}/.config"</span><br><span class="c1" style="color:#75715e"># /home/me/.config</span><br><br><span class="l l-Scalar l-Scalar-Plain">important_value</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">None</span><br><span class="l l-Scalar l-Scalar-Plain">important_setting</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">important_value|default('not</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">that</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">important</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">i</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">guess',</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">true)</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br><span class="c1" style="color:#75715e"># not that important i guess</span><br><br><span class="l l-Scalar l-Scalar-Plain">number_of_seconds_in_a_day_usually</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">60</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">*</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">60</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">*</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">24</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br><span class="c1" style="color:#75715e"># 86400</span><br><br><span class="l l-Scalar l-Scalar-Plain">a_dict</span><span class="p p-Indicator">:</span><br>  <span class="l l-Scalar l-Scalar-Plain">property_one</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">yes</span><br>  <span class="l l-Scalar l-Scalar-Plain">property_two</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">no</span><br><span class="l l-Scalar l-Scalar-Plain">templated_dict</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">a_dict</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br><span class="c1" style="color:#75715e"># { 'property_one': true, 'property_two': false }</span><br><br><span class="l l-Scalar l-Scalar-Plain">a_list</span><span class="p p-Indicator">:</span><br>  <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">one</span><br>  <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">two</span><br><span class="l l-Scalar l-Scalar-Plain">templated_list</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">a_list</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br><span class="c1" style="color:#75715e"># [ 'one', 'two' ]</span><br></pre></div>
</td>
</tr></table>

### Play Meta

The first (logically, at least) components of a play are its metadata. A play first lists its targets, defines local variables (including overriding inherited values), and [gathers pertinent host facts](http://docs.ansible.com/ansible/latest/setup_module.html).

Plays begin with a `hosts` variable, which can be a specific host, a group, or [a group pattern](http://docs.ansible.com/ansible/latest/intro_patterns.html). As of `2.4`, you can additionally [specify the `order`](http://docs.ansible.com/ansible/latest/playbooks_intro.html#hosts-and-users) a group will follow. [By default](http://docs.ansible.com/ansible/latest/playbooks_variables.html#information-discovered-from-systems-facts), each play will attempt to gather information about all the targeted hosts. If you don't want Ansible to do this, e.g. the play doesn't need any host information, you can disable it with `gather_facts: no`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">playbook.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">---</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">hosts</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">specific-host</span><br>  <span class="l l-Scalar l-Scalar-Plain">...</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">hosts</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">some-group</span><br>  <span class="l l-Scalar l-Scalar-Plain">...</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">hosts</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">all:!except-for-this-host</span><br>  <span class="l l-Scalar l-Scalar-Plain">...</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">hosts</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">all</span><br>  <span class="l l-Scalar l-Scalar-Plain">gather_facts</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">no</span><br>  <span class="l l-Scalar l-Scalar-Plain">...</span><br></pre></div>
</td>
</tr>
</table>

Plays can (re)define a variety of Ansible options, which come from its superclasses `Base` ([source](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/base.py#L150)), `Taggable`([source](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/taggable.py#L30)), and `Become` ([source](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/become.py#L33)). Plays inherit the options defined in the inventory. Anything specified in a play will override the inventory value, e.g. a play's `remote_user` will replace a host's `ansible_user`.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">playbook.yml</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">...</span><br>  <span class="l l-Scalar l-Scalar-Plain">tags</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="s" style="color:#e6db74">'is_tagged'</span><br>  <span class="l l-Scalar l-Scalar-Plain">remote_user</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">differentuser</span><br>  <span class="l l-Scalar l-Scalar-Plain">connection</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">docker</span><br><span class="nn" style="color:#f8f8f2">...</span><br></pre></div>
</td>
</tr>
</table>

(Full disclosure: I couldn't actually find a full list of play options [in the docs](http://docs.ansible.com/ansible/latest/playbooks.html) when I started this project. I did find [host options](http://docs.ansible.com/ansible/latest/intro_inventory.html#list-of-behavioral-inventory-parameters), so I just used those. I just now, while writing this post, discovered all the cool things available by delving in the source code. I suppose I should have done that sooner.)

Like hosts, plays can define `vars` or [include external `vars`](http://docs.ansible.com/ansible/latest/playbooks_variables.html#variable-file-separation). As usual, these will override host values.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">playbook.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">...</span><br>  <span class="l l-Scalar l-Scalar-Plain">vars</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">play_scoped_value</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'accessible</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">to</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">its</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">child</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">elements'</span><br>    <span class="l l-Scalar l-Scalar-Plain">host_scoped_value</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'replaces</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">the</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">host</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">value'</span><br>  <span class="l l-Scalar l-Scalar-Plain">var_files</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">/path/to/a/vars/file.yml</span><br><span class="nn" style="color:#f8f8f2">...</span><br></pre></div>
</td>
</tr>
</table>

### Tasks

Plays execute a collection of actions, called `tasks`, against their `hosts`. For convenience, Ansible provides three `tasks` blocks, `pre_tasks`, `tasks`, and `post_tasks`, executed [in that order](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/play.py#L271). `tasks` are [a list of module calls](http://docs.ansible.com/ansible/latest/playbooks_intro.html#tasks-list). You can get a list of installed modules via `ansible-doc -l`, browse its documentation via `ansible-doc <module name>`, and test its syntax via [ad-hoc usage](#ad-hoc-commands). The list of modules [online in the docs](http://docs.ansible.com/ansible/latest/list_of_all_modules.html) may or may not be current, and won't include any extensions you've installed locally.

Task attributes are defined [locally](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/task.py#L69) and in its superclasses `Base` ([source](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/base.py#L150)), `Conditional` ([source](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/conditional.py#L45)), `Taggable`([source](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/taggable.py#L30)), and `Become` ([source](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/become.py#L33)). The simplest task form is just a module call:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">tasks.yml</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">...</span><br>  <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'barebones'</span><br><span class="nn" style="color:#f8f8f2">...</span><br></pre></div>
</td>
</tr>
</table>

In practice, it's usually a good idea to at least provide a `name` for logging:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">tasks.yml</div></td>
</tr>
<tr>
<td class="linenos" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0"><div class="linenodiv"><pre style="background:#272822; color:#57584f; border:none; font-size:1em; line-height:125%; padding:0 10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0; border-radius:0; border-right:1px solid #57584f">1
2
3
4
5
6</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">...</span><br>  <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Log a simple message</span><br>      <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'barebones</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">with</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">name'</span><br><span class="nn" style="color:#f8f8f2">...</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml<br><span class="go" style="color:#888">PLAY **********************************************************************</span><br><br><span class="go" style="color:#888">TASK [setup] **************************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [debug] **************************************************************</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; {</span><br><span class="go" style="color:#888">    "msg": "barebones"</span><br><span class="go" style="color:#888">}</span><br><br><span class="go" style="color:#888">TASK [Log a simple message] ***********************************************</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; {</span><br><span class="go" style="color:#888">    "msg": "barebones with name"</span><br><span class="go" style="color:#888">}</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=3    changed=0    unreachable=0    failed=0</span><br></pre></div>
</td></tr></table>

It's often useful to pass information from one task to another. Each module returns the result (if any) of its action (check its format via `ansible-doc` or the online docs) as well as [common values](http://docs.ansible.com/ansible/latest/common_return_values.html). Usually, you're getting [the result of `AnsibleModule.run_command`](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/module_utils/basic.py#L2559) after the module processes its results. To access this return elsewhere, include `register: name_to_register_as`, which [creates a new fact](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/plugins/strategy/__init__.py#L368) scoped to the play, i.e. accessible to tasks within the play but not elsewhere.

(Quick aside: The scope works because, as the `variable_manager` is passed around, it is [serialized via `pickle`](https://docs.python.org/2/library/pickle.html) and, [when deserialized](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/vars/manager.py#L144), the nonpersistent cache is initialized to an empty `dict`. If that explanation is wrong, I apologize; I don't fully grok the process and am making a few logical jumps based off the code I was able to figure out and trace.)

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">tasks.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">...</span><br>  <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Illustrate registering a task's output</span><br>      <span class="l l-Scalar l-Scalar-Plain">stat</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">path</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">/tmp/provisioning</span><br>      <span class="l l-Scalar l-Scalar-Plain">register</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">demo_register</span><br><br>    <span class="c1" style="color:#75715e"># This puts the item in the logs</span><br>    <span class="c1" style="color:#75715e"># Alternatively, you could just run the playbook verbosely</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Output previous result</span><br>      <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">var</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">demo_register</span><br><span class="nn" style="color:#f8f8f2">...</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml<br><span class="go" style="color:#888">PLAY **********************************************************************</span><br><br><span class="go" style="color:#888">TASK [setup] **************************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Illustrate registering a task's output] *****************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Output previous result] *********************************************</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; {</span><br><span class="go" style="color:#888">    "demo_register": {</span><br><span class="go" style="color:#888">        "changed": false,</span><br><span class="go" style="color:#888">        "stat": {</span><br><span class="go" style="color:#888">            "exists": false</span><br><span class="go" style="color:#888">        }</span><br><span class="go" style="color:#888">    }</span><br><span class="go" style="color:#888">}</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=3    changed=0    unreachable=0    failed=0</span><br></pre></div>
</td></tr></table>

Tasks can be run conditionally via `when`. There are plenty of good reasons for conditional tasks, like performing OS-specific actions, running state-dependent processes, or including/excluding items based on local facts. Tasks whose execution is dependent on the status of other tasks are better handled (pun intended) via [Handlers](#handlers).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">tasks.yml</div></td>
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
35</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">...</span><br>  <span class="l l-Scalar l-Scalar-Plain">vars</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">max_cache_age</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">60</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">*</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">60</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">*</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">24</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">*</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">7</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>    <span class="l l-Scalar l-Scalar-Plain">cachefile_path</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">/tmp/cachefile</span><br>    <span class="l l-Scalar l-Scalar-Plain">true_in_ancestor</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">false</span><br><br>  <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Badger Windows users</span><br>      <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">You should consider using a more pleasant, less proprietary operating system.</span><br>      <span class="c1" style="color:#75715e"># The regex_search filter returns matched contents if found and None otherwise</span><br>      <span class="l l-Scalar l-Scalar-Plain">when</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">(ansible_distribution|regex_search('([mM]icrosoft|[wW]indows)')) or (ansible_bios_version|regex_search('([hH]yper-[vV])'))</span><br><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Check cache age</span><br>      <span class="l l-Scalar l-Scalar-Plain">stat</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">path</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">cachefile_path</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>      <span class="l l-Scalar l-Scalar-Plain">register</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">cache_age</span><br><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Nuke stale cache</span><br>      <span class="l l-Scalar l-Scalar-Plain">copy</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">content</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">''</span><br>        <span class="l l-Scalar l-Scalar-Plain">dest</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">cachefile_path</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>        <span class="l l-Scalar l-Scalar-Plain">force</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">yes</span><br>        <span class="l l-Scalar l-Scalar-Plain">owner</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">ansible_user</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>        <span class="l l-Scalar l-Scalar-Plain">group</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">ansible_user</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>        <span class="l l-Scalar l-Scalar-Plain">mode</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'ugo=rw'</span><br>      <span class="l l-Scalar l-Scalar-Plain">when</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">cache_age.stat.exists == false or cache_age.stat.mtime|int &lt; (ansible_date_time.epoch|int - max_cache_age|int)</span><br><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Run when local fact is truthy</span><br>      <span class="l l-Scalar l-Scalar-Plain">expect</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">command</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">passwd AzureDiamond</span><br>        <span class="l l-Scalar l-Scalar-Plain">responses</span><span class="p p-Indicator">:</span><br>          <span class="l l-Scalar l-Scalar-Plain">(?i)password</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'hunter2'</span><br>      <span class="l l-Scalar l-Scalar-Plain">when</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">true_in_ancestor</span><br><span class="nn" style="color:#f8f8f2">...</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml<br><span class="go" style="color:#888">PLAY [localhost] **********************************************************</span><br><br><span class="go" style="color:#888">TASK [Gathering Facts] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Badger Windows users] ***********************************************</span><br><span class="go" style="color:#888">skipping: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Check cache age] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Nuke stale cache] ***************************************************</span><br><span class="go" style="color:#888">skipping: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Run when local fact is truthy] **************************************</span><br><span class="go" style="color:#888">skipping: [localhost]</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=2    changed=0    unreachable=0    failed=0</span><br></pre></div>
</td></tr></table>

Tasks can also be [looped via `with_items`](http://docs.ansible.com/ansible/latest/playbooks_loops.html). This makes duplicating tasks much easier, and also allows each task to focus solely on a single action. The task iterates the contents of `with_items`, (coerced to) a list, using `item` as a placeholder. ([The loop docs](http://docs.ansible.com/ansible/latest/playbooks_loops.html) cover other very useful possibilities, like `with_filetree` and renaming `loop_var`; RTFM) For example, the [suggested way to install packages](http://docs.ansible.com/ansible/latest/playbooks_loops.html#standard-loops) (on targets whose shell can install packages by default, so not Windows) looks like this:
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">loop.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">...</span><br>  <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensure dependencies are installed</span><br>      <span class="l l-Scalar l-Scalar-Plain">package</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">item</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>        <span class="l l-Scalar l-Scalar-Plain">state</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">present</span><br>      <span class="l l-Scalar l-Scalar-Plain">with_items</span><span class="p p-Indicator">:</span><br>        <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">git</span><br>        <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">bash</span><br>      <span class="l l-Scalar l-Scalar-Plain">become</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">yes</span><br><span class="nn" style="color:#f8f8f2">...</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-playbook provisioning/scratch.yml --ask-become-pass<br><span class="go" style="color:#888">SUDO password:</span><br><br><span class="go" style="color:#888">PLAY [localhost] **********************************************************</span><br><br><span class="go" style="color:#888">TASK [Gathering Facts] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Ensure dependencies are installed] **********************************</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; (item=git)</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; (item=bash)</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=2    changed=0    unreachable=0    failed=0</span><br></pre></div>
</td></tr></table>

### Handlers

[Handlers](http://docs.ansible.com/ansible/latest/playbooks_intro.html#handlers-running-operations-on-change) are a specific subclass of tasks whose purpose is to execute task-state-dependent tasks. That's a lot to unpack, so let's look at the most common example:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">tasks.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">...</span><br>  <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensure templated config is in place</span><br>      <span class="l l-Scalar l-Scalar-Plain">template</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">src</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">etc/some/service.conf.j2</span><br>        <span class="l l-Scalar l-Scalar-Plain">dest</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">/etc/some/service.conf</span><br>      <span class="l l-Scalar l-Scalar-Plain">register</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">some_service_config</span><br><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Reload some-service on config change</span><br>      <span class="l l-Scalar l-Scalar-Plain">service</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">some-service</span><br>        <span class="l l-Scalar l-Scalar-Plain">state</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">restarted</span><br>      <span class="l l-Scalar l-Scalar-Plain">when</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">some_service_config|changed</span><br><span class="nn" style="color:#f8f8f2">...</span><br></pre></div>
</td>
</tr>
</table>

This play templates the config for `some-service`, and, if the file changed, restarts `some-service`. Ansible will always attempt to run the second task, skipping it when nothing changed, as you can see below:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml<br><span class="go" style="color:#888">PLAY [localhost] **********************************************************</span><br><br><span class="go" style="color:#888">TASK [Gathering Facts] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Ensure templated config is in place] ********************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Reload some-service on config change] *******************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=3    changed=1    unreachable=0    failed=0</span><br><br><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml<br><span class="go" style="color:#888">PLAY [localhost] **********************************************************</span><br><br><span class="go" style="color:#888">TASK [Gathering Facts] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Ensure templated config is in place] ********************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Reload some-service on config change] *******************************</span><br><span class="go" style="color:#888">skipping: [localhost]</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=2    changed=0    unreachable=0    failed=0</span><br></pre></div>
</td></tr></table>

Handlers provide a convenience wrapper for that logic. Rather than `register`ing its output, a task can `notify` a handler. Handlers are defined in the `handlers` block of a play. Since `handlers` aren't executed in the linear manner `tasks` are run, you can quickly reuse the same handler across an entire `tasks` block. By default, `handlers` are queued at the end of each `tasks` without duplication. You can immediately flush the `handlers` queue by including a `meta: flush_handlers` task to override this behavior (do note the queue will still be flushed at the end of the `tasks` block). Like `tasks`, `handlers` are executed linearly in [the order they are defined](http://docs.ansible.com/ansible/latest/playbooks_intro.html#handlers-running-operations-on-change). This provides some structure for handler dependencies and makes notifying multiple handlers easier; after you declare the `handlers` in the order they must be run, you can `notify` them in any order.

Refactoring the leading example gives something like this:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">handler.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">...</span><br>  <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensure templated config is in place</span><br>      <span class="l l-Scalar l-Scalar-Plain">template</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">src</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">etc/some/service.conf.j2</span><br>        <span class="l l-Scalar l-Scalar-Plain">dest</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">/etc/some/service.conf</span><br>      <span class="l l-Scalar l-Scalar-Plain">notify</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">restart some-service</span><br><br>  <span class="l l-Scalar l-Scalar-Plain">handlers</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">restart some-service</span><br>      <span class="l l-Scalar l-Scalar-Plain">service</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">some-service</span><br>        <span class="l l-Scalar l-Scalar-Plain">state</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">restarted</span><br><span class="nn" style="color:#f8f8f2">...</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml<br><span class="go" style="color:#888">PLAY [localhost] **********************************************************</span><br><br><span class="go" style="color:#888">TASK [Gathering Facts] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Ensure templated config is in place] ********************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">RUNNING HANDLER [restart some-service] ************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=3    changed=1    unreachable=0    failed=0</span><br><br><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml<br><span class="go" style="color:#888">PLAY [localhost] **********************************************************</span><br><br><span class="go" style="color:#888">TASK [Gathering Facts] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Ensure templated config is in place] ********************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=2    changed=0    unreachable=0    failed=0</span><br></pre></div>
</td></tr></table>

It's also possible to trigger multiple `handlers` with a single `notify`. Include `listen: 'some string'` in the handler body to add additional `notify` topics. `listen` is [defined as a `list`](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/handler.py#L28), so you can add multiple triggers if desired.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">task-and-handlers.yml</div></td>
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
40</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">...</span><br>  <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Trigger immediate handler</span><br>      <span class="l l-Scalar l-Scalar-Plain">command</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">echo 'By default, command|changed is always true'</span><br>      <span class="l l-Scalar l-Scalar-Plain">notify</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">immediate handler</span><br><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Immediately flush handlers queue</span><br>      <span class="l l-Scalar l-Scalar-Plain">meta</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">flush_handlers</span><br><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Trigger named handler</span><br>      <span class="l l-Scalar l-Scalar-Plain">command</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">/bin/true</span><br>      <span class="l l-Scalar l-Scalar-Plain">notify</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">named handler</span><br><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Trigger listen topic</span><br>      <span class="l l-Scalar l-Scalar-Plain">command</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">/bin/true</span><br>      <span class="l l-Scalar l-Scalar-Plain">notify</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'listen</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">topic'</span><br><br>  <span class="l l-Scalar l-Scalar-Plain">handlers</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">unnamed handler</span><br>      <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'unnamed</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">handler</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">executed'</span><br>      <span class="l l-Scalar l-Scalar-Plain">listen</span><span class="p p-Indicator">:</span><br>        <span class="p p-Indicator">-</span> <span class="s" style="color:#e6db74">'listen</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">topic'</span><br>        <span class="p p-Indicator">-</span> <span class="s" style="color:#e6db74">'never</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">called</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">topic'</span><br><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">immediate handler</span><br>      <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'immediate</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">handler</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">executed'</span><br><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">named handler</span><br>      <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'named</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">handler</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">executed'</span><br>      <span class="l l-Scalar l-Scalar-Plain">listen</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'listen</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">topic'</span><br><br>    <span class="c1" style="color:#75715e"># Removing the name prevents accidental name notification</span><br>    <span class="c1" style="color:#75715e"># It will only execute on 'listen topic' after the others are finished</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'order</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">dependent</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">handler</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">executed'</span><br>      <span class="l l-Scalar l-Scalar-Plain">listen</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'listen</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">topic'</span><br><span class="nn" style="color:#f8f8f2">...</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml<br><span class="go" style="color:#888">PLAY [localhost] **********************************************************</span><br><br><span class="go" style="color:#888">TASK [Gathering Facts] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Trigger immediate handler] ******************************************</span><br><span class="go" style="color:#888">changed: [localhost]</span><br><br><span class="go" style="color:#888">RUNNING HANDLER [immediate handler] ***************************************</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; {</span><br><span class="go" style="color:#888">    "msg": "immediate handler executed"</span><br><span class="go" style="color:#888">}</span><br><br><span class="go" style="color:#888">TASK [Retrigger named handler] ********************************************</span><br><span class="go" style="color:#888">changed: [localhost]</span><br><br><span class="go" style="color:#888">TASK [Trigger listen topic] ***********************************************</span><br><span class="go" style="color:#888">changed: [localhost]</span><br><br><span class="go" style="color:#888">RUNNING HANDLER [unnamed handler] *****************************************</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; {</span><br><span class="go" style="color:#888">    "msg": "unnamed handler executed"</span><br><span class="go" style="color:#888">}</span><br><br><span class="go" style="color:#888">RUNNING HANDLER [named handler] *******************************************</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; {</span><br><span class="go" style="color:#888">    "msg": "named handler executed"</span><br><span class="go" style="color:#888">}</span><br><br><span class="go" style="color:#888">RUNNING HANDLER [debug] ***************************************************</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; {</span><br><span class="go" style="color:#888">    "msg": "order dependent handler executed"</span><br><span class="go" style="color:#888">}</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=8    changed=3    unreachable=0    failed=0</span><br></pre></div>
</td></tr></table>

## Roles

Roles provide a way to reuse Ansible code across plays and playbooks. You can think of a `role` as an isolated play that can be inserted anywhere (don't go around the internet quoting me verbatim; while not technically true, it's a good analogy). Roles usually live beside the playbook in the `./roles` (you can specify fancier setups via `roles_path`), and have [a well-defined directory structure](http://docs.ansible.com/ansible/latest/playbooks_reuse_roles.html#role-directory-structure). Instead of being declared in a single file like playbooks, roles are constructed from the contents of their respective directory, `<role path>/<role name>`. Any missing components are simply ignored, although at least one has to exist.

Examples make that wall of text more palatable. Let's recode one of the [Tasks](#tasks) as `roles`. A great starting point is the `package` task. A descriptive name like `installs_common_dependencies` makes it easy to reference. To simply duplicate the task example, this is all that's necessary:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> tree roles<br><span class="go" style="color:#888">roles</span><br><span class="go" style="color:#888">└── installs_common_dependencies</span><br><span class="go" style="color:#888">    └── tasks</span><br><span class="go" style="color:#888">        └── main.yml</span><br><br><span class="go" style="color:#888">2 directories, 1 file</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">roles/installs_common_dependencies/tasks/main.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e"># roles/installs_common_dependencies/tasks/main.yml</span><br><span class="nn" style="color:#f8f8f2">---</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensure dependencies are installed</span><br>  <span class="l l-Scalar l-Scalar-Plain">package</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">item</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>    <span class="l l-Scalar l-Scalar-Plain">state</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">present</span><br>  <span class="l l-Scalar l-Scalar-Plain">with_items</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">git</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">bash</span><br>  <span class="l l-Scalar l-Scalar-Plain">become</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">yes</span><br></pre></div>
</td>
</tr>
</table>

The role can now easily be included in a play as a top-level attribute. The `roles` block is compiled to a list of `tasks` and run exactly like a `task` block. `roles` are [run after `pre_tasks` but before `tasks`](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/play.py#L271).

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">playbook.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="nn" style="color:#f8f8f2">---</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">hosts</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">localhost</span><br>  <span class="l l-Scalar l-Scalar-Plain">connection</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">local</span><br><br>  <span class="l l-Scalar l-Scalar-Plain">roles</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">role</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">installs_common_dependencies</span><br><br>  <span class="l l-Scalar l-Scalar-Plain">pre_tasks</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">pre_tasks</span><br><br>  <span class="l l-Scalar l-Scalar-Plain">tasks</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>        <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">tasks</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml --ask-become-pass<br><span class="go" style="color:#888">SUDO password:</span><br><br><span class="go" style="color:#888">PLAY [localhost] **********************************************************</span><br><br><span class="go" style="color:#888">TASK [Gathering Facts] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [debug] **************************************************************</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; {</span><br><span class="go" style="color:#888">    "msg": "pre_tasks"</span><br><span class="go" style="color:#888">}</span><br><br><span class="go" style="color:#888">TASK [installs_common_dependencies : Ensure dependencies are installed] ***</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; (item=git)</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; (item=bash)</span><br><br><span class="go" style="color:#888">TASK [debug] **************************************************************</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; {</span><br><span class="go" style="color:#888">    "msg": "tasks"</span><br><span class="go" style="color:#888">}</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=4    changed=0    unreachable=0    failed=0</span><br></pre></div>
</td></tr></table>

By default, Ansible searches each block component directory for a `main.yml` file, e.g. Ansible needs `tasks/main.yml` but doesn't care about `files/main.yml` (more on that later). You can include other files in those directories without issue. Ansible will completely ignore them (i.e. anything not `main.yml`) until you explicitly include them.

If we try to run `installs_common_dependencies` on a Windows target, we're going to run into issues. `package` doesn't work on operating systems whose default package manager is Bing via Internet Explorer. Let's expand the tasks to handle different OS families:

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> tree roles<br><span class="go" style="color:#888">roles</span><br><span class="go" style="color:#888">└── installs_common_dependencies</span><br><span class="go" style="color:#888">    └── tasks</span><br><span class="go" style="color:#888">        ├── main.yml</span><br><span class="go" style="color:#888">        ├── not_windows.yml</span><br><span class="go" style="color:#888">        └── windows.yml</span><br><br><span class="go" style="color:#888">2 directories, 3 files</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">roles/installs_common_dependencies/tasks/main.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e"># roles/installs_common_dependencies/tasks/main.yml</span><br><span class="nn" style="color:#f8f8f2">---</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">include_tasks</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">windows.yml</span><br>  <span class="l l-Scalar l-Scalar-Plain">when</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">ansible_distribution|regex_search('([mM]icrosoft|[wW]indows)')</span><br><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">include_tasks</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">not_windows.yml</span><br>  <span class="l l-Scalar l-Scalar-Plain">when</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">not ansible_distribution|regex_search('([mM]icrosoft|[wW]indows)')</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">roles/installs_common_dependences/tasks/not_windows.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e"># roles/installs_common_dependences/tasks/not_windows.yml</span><br><span class="nn" style="color:#f8f8f2">---</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensure dependencies are installed</span><br>  <span class="l l-Scalar l-Scalar-Plain">package</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">item</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>    <span class="l l-Scalar l-Scalar-Plain">state</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">present</span><br>  <span class="l l-Scalar l-Scalar-Plain">with_items</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">git</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">bash</span><br>  <span class="l l-Scalar l-Scalar-Plain">become</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">yes</span><br></pre></div>
</td>
</tr>
</table>

**WARNING:** I haven't actually tested this (or any of following improvements) on a Windows machine because [setting it up](http://docs.ansible.com/ansible/latest/intro_windows.html) requires more time than I feel like spending in PowerShell this weekend. Use at your own risk.
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">roles/installs_common_dependences/tasks/windows.yml</div></td>
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
28</pre></div></td>
<td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e"># roles/installs_common_dependences/tasks/windows.yml</span><br><span class="nn" style="color:#f8f8f2">---</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Badger the user</span><br>  <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'There</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">is</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">hope</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">available--Google</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">"microsoft</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">windows</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">replacement"'</span><br><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensure dependences are installed via chocolatey</span><br>  <span class="l l-Scalar l-Scalar-Plain">win_chocolatey</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">item</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>    <span class="l l-Scalar l-Scalar-Plain">state</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">present</span><br>  <span class="l l-Scalar l-Scalar-Plain">with_items</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">posh-git</span><br><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensures necessary features are installed</span><br>  <span class="l l-Scalar l-Scalar-Plain">win_feature</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">item</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>    <span class="l l-Scalar l-Scalar-Plain">state</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">present</span><br>    <span class="l l-Scalar l-Scalar-Plain">include_management_tools</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">yes</span><br>    <span class="l l-Scalar l-Scalar-Plain">include_sub_features</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">yes</span><br>  <span class="l l-Scalar l-Scalar-Plain">register</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">features_update</span><br>  <span class="l l-Scalar l-Scalar-Plain">with_items</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">Windows Subsystem for Linux</span><br><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Reboot if necessary (usually is)</span><br>  <span class="l l-Scalar l-Scalar-Plain">win_reboot</span><span class="p p-Indicator">:</span><br>  <span class="c1" style="color:#75715e"># I honestly have no idea if this works</span><br>  <span class="c1" style="color:#75715e"># I also honestly have no idea how to build a context to test it</span><br>  <span class="l l-Scalar l-Scalar-Plain">when</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">True in features_update.results|map(attribute='reboot_required')|list|unique</span><br></pre></div>
</td>
</tr>
</table>

Splitting out the OS tasks has created a maintenance annoyance: we've now got two files to update when we want to modify the role. Luckily, Ansible has a solid solution for that.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> tree roles<br><span class="go" style="color:#888">roles</span><br><span class="go" style="color:#888">└── installs_common_dependencies</span><br><span class="go" style="color:#888">    ├── defaults</span><br><span class="go" style="color:#888">    │   └── main.yml</span><br><span class="go" style="color:#888">    └── tasks</span><br><span class="go" style="color:#888">        ├── main.yml</span><br><span class="go" style="color:#888">        ├── not_windows.yml</span><br><span class="go" style="color:#888">        └── windows.yml</span><br><br><span class="go" style="color:#888">3 directories, 4 files</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">roles/installs_common_dependencies/defaults/main.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e"># roles/installs_common_dependencies/defaults/main.yml</span><br><span class="nn" style="color:#f8f8f2">---</span><br><span class="l l-Scalar l-Scalar-Plain">common_dependencies</span><span class="p p-Indicator">:</span><br>  <span class="l l-Scalar l-Scalar-Plain">easy</span><span class="p p-Indicator">:</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">git</span><br>    <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">bash</span><br>  <span class="l l-Scalar l-Scalar-Plain">hard</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">choco</span><span class="p p-Indicator">:</span><br>      <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">poshgit</span><br>    <span class="l l-Scalar l-Scalar-Plain">features</span><span class="p p-Indicator">:</span><br>      <span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">Windows Subsystem for Linux</span><br></pre></div>
</td>
</tr>
</table>
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">roles/installs_common_dependences/tasks/not_windows.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e"># roles/installs_common_dependences/tasks/not_windows.yml</span><br><span class="nn" style="color:#f8f8f2">---</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensure dependencies are installed</span><br>  <span class="l l-Scalar l-Scalar-Plain">package</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">item</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>    <span class="l l-Scalar l-Scalar-Plain">state</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">present</span><br>  <span class="l l-Scalar l-Scalar-Plain">with_items</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">common_dependencies['easy']</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>  <span class="l l-Scalar l-Scalar-Plain">become</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">yes</span><br></pre></div>
</td>
</tr>
</table>
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">roles/installs_common_dependences/tasks/windows.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e"># roles/installs_common_dependences/tasks/windows.yml</span><br><span class="nn" style="color:#f8f8f2">---</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Badger the user</span><br>  <span class="l l-Scalar l-Scalar-Plain">debug</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">msg</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'There</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">is</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">hope</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">available--Google</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">"microsoft</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">windows</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">replacement"'</span><br><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensure dependences are installed via chocolatey</span><br>  <span class="l l-Scalar l-Scalar-Plain">win_chocolatey</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">item</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>    <span class="l l-Scalar l-Scalar-Plain">state</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">present</span><br>  <span class="l l-Scalar l-Scalar-Plain">with_items</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">common_dependencies['hard']['choco']</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensures necessary features are installed</span><br>  <span class="l l-Scalar l-Scalar-Plain">win_feature</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">item</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>    <span class="l l-Scalar l-Scalar-Plain">state</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">present</span><br>    <span class="l l-Scalar l-Scalar-Plain">include_management_tools</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">yes</span><br>    <span class="l l-Scalar l-Scalar-Plain">include_sub_features</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">yes</span><br>  <span class="l l-Scalar l-Scalar-Plain">register</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">features_update</span><br>  <span class="l l-Scalar l-Scalar-Plain">with_items</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">common_dependencies['hard']['features']</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Reboot if necessary (usually is)</span><br>  <span class="l l-Scalar l-Scalar-Plain">win_reboot</span><span class="p p-Indicator">:</span><br>  <span class="c1" style="color:#75715e"># I honestly have no idea if this works</span><br>  <span class="c1" style="color:#75715e"># I also honestly have no idea how to build a context to test it</span><br>  <span class="l l-Scalar l-Scalar-Plain">when</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">True in features_update.results|map(attribute='reboot_required')|list|unique</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml --ask-become-pass<br><span class="go" style="color:#888">SUDO password:</span><br><br><span class="go" style="color:#888">PLAY [localhost] **********************************************************</span><br><br><span class="go" style="color:#888">TASK [Gathering Facts] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [installs_common_dependencies : include_tasks] ***********************</span><br><span class="go" style="color:#888">skipping: [localhost]</span><br><br><span class="go" style="color:#888">TASK [installs_common_dependencies : include_tasks] ***********************</span><br><span class="go" style="color:#888">included: &lt;truncated&gt;/roles/installs_common_dependencies/tasks/not_windows.yml for localhost</span><br><br><span class="go" style="color:#888">TASK [installs_common_dependencies : Ensure dependencies are installed] ***</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; (item=git)</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; (item=bash)</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=3    changed=0    unreachable=0    failed=0</span><br></pre></div>
</td></tr></table>

Roles also provide a local directory for includable files and templates. Any items in `<role name>/files` or `<role name>/templates` can be referenced relatively, rather than trying to piece together an absolute path. If these directories contain a `main.yml`, it won't do anything unless referenced as the target of a module.

We can quickly expand the current example to copy a common `.gitconfig` to the user's home directory. (Note: I'm going to abandon the pretense of Windows support because I have more interesting things to write about. Sorry not sorry.) I like to treat `files` and `templates` as `/`, which makes managing the imports and templates much easier at the cost of lots of directories.

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> tree roles<br><span class="go" style="color:#888">roles</span><br><span class="go" style="color:#888">└── installs_common_dependencies</span><br><span class="go" style="color:#888">    ├── defaults</span><br><span class="go" style="color:#888">    │   └── main.yml</span><br><span class="go" style="color:#888">    ├── files</span><br><span class="go" style="color:#888">    │   └── home</span><br><span class="go" style="color:#888">    │       └── user</span><br><span class="go" style="color:#888">    │           └── gitconfig</span><br><span class="go" style="color:#888">    └── tasks</span><br><span class="go" style="color:#888">        ├── main.yml</span><br><span class="go" style="color:#888">        ├── not_windows.yml</span><br><span class="go" style="color:#888">        └── windows.yml</span><br><br><span class="go" style="color:#888">6 directories, 5 files</span><br></pre></div>
</td></tr></table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">roles/installs_common_dependencies/files/home/user/gitconfig</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e"># roles/installs_common_dependencies/files/home/user/gitconfig</span><br><span class="p p-Indicator">[</span><span class="nv" style="color:#f8f8f2">help</span><span class="p p-Indicator">]</span><br>        <span class="l l-Scalar l-Scalar-Plain">autocorrect = 1</span><br><span class="l l-Scalar l-Scalar-Plain">[core]</span><br>        <span class="l l-Scalar l-Scalar-Plain">autocrlf = input</span><br><span class="l l-Scalar l-Scalar-Plain">[push]</span><br>        <span class="l l-Scalar l-Scalar-Plain">default = matching</span><br></pre></div>
</td>
</tr>
</table>
<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%">
<tr class="code-header" style="height:40px; padding:5px 0 0" height="40">
<td style="border:none; background-image:none; background-position:center; background-repeat:no-repeat"></td>
<td class="code-header" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; height:40px; padding:5px 0 0" height="40"><div class="code-tab active" style="color:#f8f8f2; display:inline-block; font-size:0.9em; height:35px; line-height:35px; margin:0 30px 0 0; padding:0 5px; border-bottom:1px solid #57584f" height="35">roles/installs_common_dependences/tasks/not_windows.yml</div></td>
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
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="c1" style="color:#75715e"># roles/installs_common_dependences/tasks/not_windows.yml</span><br><span class="nn" style="color:#f8f8f2">---</span><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensure dependencies are installed</span><br>  <span class="l l-Scalar l-Scalar-Plain">package</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">item</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>    <span class="l l-Scalar l-Scalar-Plain">state</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">present</span><br>  <span class="l l-Scalar l-Scalar-Plain">with_items</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">common_dependencies['easy']</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>  <span class="l l-Scalar l-Scalar-Plain">become</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">yes</span><br><br><span class="p p-Indicator">-</span> <span class="l l-Scalar l-Scalar-Plain">name</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">Ensure user gitconfig exists</span><br>  <span class="l l-Scalar l-Scalar-Plain">copy</span><span class="p p-Indicator">:</span><br>    <span class="l l-Scalar l-Scalar-Plain">src</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">home/user/gitconfig</span><br>    <span class="l l-Scalar l-Scalar-Plain">dest</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"/home/{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">ansible_user</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}/.gitconfig"</span><br>    <span class="l l-Scalar l-Scalar-Plain">force</span><span class="p p-Indicator">:</span> <span class="l l-Scalar l-Scalar-Plain">no</span><br>    <span class="l l-Scalar l-Scalar-Plain">owner</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">ansible_user</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>    <span class="l l-Scalar l-Scalar-Plain">group</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">"{{</*/span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74">ansible_user</span><span class="nv" style="color:#f8f8f2"> </span><span class="s" style="color:#e6db74"*/>}}"</span><br>    <span class="l l-Scalar l-Scalar-Plain">mode</span><span class="p p-Indicator">:</span> <span class="s" style="color:#e6db74">'ug=rw,o=r'</span><br></pre></div>
</td>
</tr>
</table>

<table class="highlighttable" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><tr><td class="code" style="border:none; background-image:none; background-position:center; background-repeat:no-repeat; padding:10px 0">
<div class="highlight" style='border-radius:5px; display:block; font-family:Consolas, "Courier New", monospace; min-width:300px; overflow:auto; width:100%; background:#272822; color:#f8f8f2' width="100%"><pre style="background:#272822; color:#f8f8f2; border:none; font-size:1em; line-height:125%; padding:10px; margin-bottom:0; margin-top:0; padding-bottom:0; padding-top:0"><span></span><span class="gp" style="color:#66d9ef">$</span> ansible-playbook scratch.yml --ask-become-pass<br><span class="go" style="color:#888">SUDO password:</span><br><br><span class="go" style="color:#888">PLAY [localhost] **********************************************************</span><br><br><span class="go" style="color:#888">TASK [Gathering Facts] ****************************************************</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">TASK [installs_common_dependencies : include_tasks] ***********************</span><br><span class="go" style="color:#888">skipping: [localhost]</span><br><br><span class="go" style="color:#888">TASK [installs_common_dependencies : include_tasks] ***********************</span><br><span class="go" style="color:#888">included: &lt;truncated&gt;/roles/installs_common_dependencies/tasks/not_windows.yml for localhost</span><br><br><span class="go" style="color:#888">TASK [installs_common_dependencies : Ensure dependencies are installed] ***</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; (item=git)</span><br><span class="go" style="color:#888">ok: [localhost] =&gt; (item=bash)</span><br><br><span class="go" style="color:#888">TASK [installs_common_dependencies : Ensure user gitconfig exists] ********</span><br><span class="go" style="color:#888">ok: [localhost]</span><br><br><span class="go" style="color:#888">PLAY RECAP ****************************************************************</span><br><span class="go" style="color:#888">localhost                  : ok=4    changed=0    unreachable=0    failed=0</span><br></pre></div>
</td></tr></table>

Roles can also include metadata via `<role name>/meta`. At the moment, there are [only three meta attributes](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/role/metadata.py):

- `allow_duplicates`: This allows a `role` [to be duplicated](http://docs.ansible.com/ansible/latest/playbooks_reuse_roles.html#role-duplication-and-execution) without unique options. By default, a `role` is only executed once per play no matter how many times it's referenced.
- `dependencies`: This list allows you to [prepend any `role` dependencies](http://docs.ansible.com/ansible/latest/playbooks_reuse_roles.html#role-dependencies) before executing the current `role`. The process [loads recursively](https://github.com/ansible/ansible/blob/v2.4.1.0-1/lib/ansible/playbook/role/__init__.py#L278), so you don't have to worry about including dependency dependencies. If the order of inclusion matters, consider setting `allow_duplicates` on the dependencies (but first try to refactor that behavior out).
- `galaxy_info`: This contains metadata for [Ansible Galaxy](https://galaxy.ansible.com/). Ansible Galaxy is a fantastic resource for both great roles and Ansible usage, as it contains roles written by solid developers consumed by users all over (I can say they're written by solid developers because I haven't published any roles yet).

## Recap

Ansible is amazing. By now you should be able to [set its configuration](#configuration), quickly [test tasks](#ad-hoc-commands), [construct playbooks](#playbooks), and create [reusable content](#roles). The best part of this whole post is that I've barely scratched the surface. Google, StackExchange, and the official docs have so many good ideas to try out. There's so much more that I'd love to write about but I really need to publish this and move on to the actual project: automating and securing SSH configuration.

Before you go, check out [popular roles on Ansible Galaxy](https://galaxy.ansible.com/list#/roles?page=1&page_size=10&order=-download_count,name). It's useful to see some of this in action. Those repos are chock full of little tools and styles that get overlooked in a post like this.
