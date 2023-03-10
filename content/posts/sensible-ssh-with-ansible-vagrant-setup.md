---
title: "Sensible SSH with Ansible: Vagrant Setup"
slug: "sensible-ssh-with-ansible-vagrant-setup"
date: "2017-11-14T01:00:00.000Z"
feature_image: "/images/2017/11/gear.png"
author: "CJ Harries"
tags:
  - Sensible SSH with Ansible
  - Ansible
  - Vagrant
  - ssh
  - Automation
  - security
  - OpenSSH
---

This is the second in a series of several posts on how to manage `ssh` via Ansible. It was inspired by [a warning from Venafi](https://www.venafi.com/blog/ssh-keys-lowest-cost-highest-risk-security-tool) that gained traction in the blogosphere (read: my Google feed for two weeks). I don't know many people that observe good `ssh` security, so my goal is to make it more accessible and (somewhat) streamlined.

This post looks at how to quickly and easily mimick common environments in Vagrant. If you're using a different tool, feel comfortable with Vagrant multi-machine setups, or plan on running Vagrant from a pleasant operating system, you can probably skip this post.

<p class="nav-p"><a id="post-nav"></a></p>

- [The Series so Far](#the-series-so-far)
- [Code](#code)
- [Note](#note)
- [Creating the Status Quo](#creating-the-status-quo)
- [A Word of Caution](#a-word-of-caution)
- [Vagrant](#vagrant)
- [Defining the Control Machine](#defining-the-control-machine)
  - [In a Perfect World](#in-a-perfect-world)
  - [`ansible_local` Specificity](#ansible_local-specificity)
  - [`synced_folders` Type](#synced_folders-type)
  - [Networking](#networking)
    - [Brief Aside: `Default Switch`](#brief-aside-default-switch)
  - [In the Real world](#in-the-real-world)
- [Defining the Nodes](#defining-the-nodes)

## The Series so Far

1. [Overview](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-overview)
2. [Creating the Status Quo](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-vagrant-setup)

(This section should get updated as series progresses.)

## Code

You can view the code related to this post [under the `post-02-vagrant-setup` tag](//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/post-02-vagrant-setup).

## Note

The first post has [a quick style section](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-overview#note) that might be useful.

If you're using Vagrant on Windows with Hyper-V, there's a good chance you'll need to append `--provider=hyperv` to any `vagrant up` commands. If you're not sure, don't worry. Windows will be very helpful and crash with a BSOD (technically green now) if you use the wrong provider. The first post has [more information](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-overview#windows) on this useful feature.

## Creating the Status Quo

Rather than try to make up some convoluted scenario that sounds really cool but is really just a tiny special case (hello, math degree), I'm going to use what I know. My environments across work, my VPS, my home network, some mobile access, and all those `ssh` services (well, just GitHub at home and GitLab at work, but that's more than one) are complicated enough to serve as a good basis, and I feel like they incorporate a majority of the primary use cases. Some of the things my environment covers are

- a reused `ssh` key, `work_rsa`, that serves as my primary work identity
- a collection of users I am authorized to authenticate as, e.g. `vertical@vertical-production`
- unique keys per machine for GitHub access
- a reused `ssh` key, `wizards_rsa`, that serves as my primary LLC identity
- a horrible mess of intertwined `authorized_keys` below the surface
- mostly default `sshd_config`s, be it the base default from a fresh install or VPS (Digital Ocean, RackSpace) default/suggested configs (I did actually change the port on one personal host but we have never done that at work)

## A Word of Caution

Your `ssh` files are private. You should never store them in a repo, be it public or private. You should never share them, which also means you shouldn't use shared keys unless you absolutely have to. Remember, your keys can be used to authenticate as you, which means anyone that has them can pretend to be you.

I'm going to display a good chunk of information that you should never expose. I'm comfortable doing that for a few reasons:

1. The exposed config is being used to illustrate the process, so obfuscation potentially makes understanding more difficult.
2. You can duplicate everything I show using the provided `Vagrantfile`, so there are no secrets. Everything's already public.
3. Absolutely none of the config here (aside from the Ansible runner) exists in the real world. If it did actually exist as presented, I wouldn't have duplicated it with Vagrant.

I plan to investigate a few secure methods for sharing `ssh` files, such as [GitLab secrets](http://docs.gitlab.com/ce/ci/variables/README.html#secret-variables) and [Ansible Vault](https://docs.ansible.com/ansible/2.4/vault.html). I'll try to update this warning with those caveats when I'm able to write (and attempt to break) that code.

## Vagrant

While I could just develop all of this in the wild using my existing configuration on real machines, I try follow a solid aphorism, "Everything always breaks" (which, surprisingly, isn't common enough to have legit Google results). If you want to develop on prod and push code at 4p on a Friday, you have my blessing as well as my condolences. If not, or you like making sure things work before giving them escalated access on sensitive systems, Vagrant is an easy solution.

Vagrant supports [multi-machine configurations](https://www.vagrantup.com/docs/multi-machine/), which makes mimicking an existing network a breeze. We can create a network of wildly different operating systems with a messy connection diagram, just like the real world. Or, for a quick demo, we can create a uniform network with common options because it's really fast to make. I went with the latter for now.

## Defining the Control Machine

As Ansible doesn't work on Windows, the control machine must use a good operating system. I don't use one of those, unfortunately, so I built up a virtual control machine in Vagrant. I'd argue developing with and testing on a virtual control is a useful step even if you do use an operating system that can be used for more than running proprietary office software.

One of the many reasons I really like Vagrant is its [OOTB Ansible support](https://www.vagrantup.com/docs/provisioning/ansible.html). On top of that, Vagrant understands the joy that is working from operating systems that refuse to use common standards unless they wrote them, and provides [a secondary Ansible provisioner, `ansible_local`](https://www.vagrantup.com/docs/provisioning/ansible_local.html), which runs entirely on the guest.

Most of the servers I work with on a day-to-day basis are in the RHEL ecosystem. Most run Centos 7, and those that don't are either dev machines running Scientific or Fedora or old Centos 6 machines that need to be rebuilt with Centos 7. As such, I'm going to use Centos 7 as a base for everything. Because Vagrant is awesome, it doesn't care about distro-specific APIs (e.g. package managers) and just works (via judicious `sh` usage).

For now, ignore the contents of the Ansible tasks. Assume they work (or don't, which is probably a better assumption) and focus on the Vagrant config.

### In a Perfect World

This would define my control machine:

```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.box = 'centos/7'
  config.vm.hostname = 'generic'
  config.vm.synced_folder './provisioning/', '/tmp/provisioning', type: 'nfs'
  config.vm.provision 'ansible_local' do |ansible|
    ansible.playbook = 'initial-setup.yml'
    ansible.install_mode = 'pip'
  end
end
```

I know a perfect world exists, but, working from Windows, I know it does not exist around me.

### `ansible_local` Specificity

I had you going, didn't I? You thought this issue was going to be about Windows. Gotcha! The last issue is about Windows, and the next one is only mostly about Windows. This one is not.

Vagrant is very good at holding your hand. So much so that, in some situations, it's difficult to get Vagrant to let go. Assuming we tried to provision the perfect config with `ansible.verbose = true` added for good measure, we'd get this error:

```text
`playbook` does not exist on the guest: /vagrant/initial-setup.yml
```

We've [missed `provisioning_path`](https://www.vagrantup.com/docs/provisioning/ansible_local.html#provisioning_path):
> An absolute path on the guest machine where the Ansible files are stored. The ansible-galaxy and ansible-playbook commands are executed from this directory. This is the location to place an ansible.cfg file, in case you need it.

Adding `ansible.provisioning_path = '/tmp/provisioning'` nets a new error:

```text
Running ansible-playbook...
cd /tmp/provisioning && PYTHONUNBUFFERED=1 ANSIBLE_FORCE_COLOR=true ansible-playbook --limit="controller" --inventory-file=/tmp/vagrant-ansible/inventory -v initial-setup.yml
Using /tmp/provisioning/ansible.cfg as config file

PLAY [setup] *******************************************************************
skipping: no hosts matched

PLAY RECAP *********************************************************************

 [WARNING]: Could not match supplied host pattern, ignoring: setup
```

On first glance, it's picked up the proper config file (which contains an explicit path to the inventory), but it's not actually finding the inventory. On second glance, it failed because Vagrant has added flags `--limit` and `--inventory-path` with defaults even though we didn't specify them. The docs are currently [wrong about `inventory_path`](https://www.vagrantup.com/docs/provisioning/ansible_common.html#inventory_path), but [state `limit`](https://www.vagrantup.com/docs/provisioning/ansible_common.html#limit) is reasonably added by default to restrict Ansible to only tasks that affect the host.

This is everything I had to add to get it to work properly:

```ruby
  config.vm.provision 'ansible_local' do |ansible|
    ansible.playbook = 'initial-setup.yml'
    ansible.install_mode = 'pip'
    ansible.verbose = true
    ansible.limit = config.vm.hostname
    ansible.provisioning_path = '/tmp/provisioning'
    ansible.inventory_path = '/tmp/provisioning/inventory'
  end
```

### `synced_folders` Type

(Quick aside: `choco install rsync` and `type: rsync` do not work on Windows without a ton of manual setup; unsurprisingly, it involves [standard tools not working as intended on Windows](https://github.com/hashicorp/vagrant/issues/3086))

On Vagrant hosts that can easily interact with the rest of the world, you can use normal shares like `nfs` or `rsync`. If you explicitly want to make things hard for yourself or you're running Vagrant from Windows, you can run into trouble. For example, on Windows, a `samba` share is your best bet, [via `type: 'smb'`](https://www.vagrantup.com/docs/synced-folders/smb.html). However, exotic mount types (i.e. not vanilla) might cause problems. Continuing the Windows example, when attempting to sync via `type: 'smb'`, Centos can't run the generated `mount -t cifs ...` command because `cifs-utils` isn't a default package. Not a problem, because Vagrant can mix-and-match `synced_folders` with `shell` provisioners... except it is a problem, because [Vagrant mounts everything before any provisioning](https://github.com/hashicorp/vagrant/issues/2701). The suggested solution, adding `disabled: true`, doesn't actually send any mount information to the guest (to verify, you can run `vagrant up --debug` with a `disable`d folder and consume the log in such a way that you can search for the folder mount point).

An obvious solution is to use a more specific Vagrant box. However, the suggested Windows box I kept seeing, [`serveit/centos-7`](https://app.vagrantup.com/serveit/boxes/centos-7), doesn't exist anymore (`404` on the external host). The others, like [`geerlingguy/centos7`](https://app.vagrantup.com/geerlingguy/boxes/centos7), don't support the Hyper-V provider. I could build my own and publish it, or I could just explicitly tell any consumers of my Vagrantfile that they'll have to run

```bash
$ vagrant up
# errors trying to mount
$ vagrant provision
# errors on anything involving the synced_folders
$ vagrant reload --provision
# finally runs as intended
```

I'm using `centos/7`; I'll let you figure out which path I took.

For reference, here's a way to automatically determine the type based on the Vagrant host:

```ruby
  # These were vetted on RHEL and Debian; dunno about others
  mount_packages = ['nfs-utils', 'nfs-utils-lib']
  mount_type = 'nfs'
  if Vagrant::Util::Platform.windows?
    mount_packages = ['cifs-utils']
    mount_type = 'smb'
  end

  # You might have to replace yum with your package manager
  config.vm.provision 'shell' do |sh|
    sh.inline = "rpm -qa | egrep -i \'#{mount_packages.join('|')}\' || yum install -y #{mount_packages.join(' ')}"
    sh.privileged = true
  end

  config.vm.synced_folder './provisioning/', '/tmp/provisioning', type: mount_type
```

### Networking

Vagrant is [very candid about the Hyper-V limitations](https://www.vagrantup.com/docs/hyperv/limitations.html). Unsurprisingly, Vagrant can't configure networking yet because Hyper-V exposes a completely foreign and proprietary networking API. Reading between the lines, it seems like Vagrant is saying it should be possible to control the networking from Windows, like with [a PowerShell script called from Vagrant](//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/post-02-vagrant-setup/powershell). However, I've now run [the linked script](//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/post-02-vagrant-setup/powershell/network.ps1), built directly from [the official docs](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/user-guide/setup-nat-network), on three different machines with three different results. None of them worked. As far as my experience shows, confirmed with the sysadmins at work, the Hyper-V GUI (`virtmgmt.msc`) is the only way to create reliable networks. That means you need to set everything up before you run Vagrant. If you set up Hyper-V and allow it to create a default switch, you'll probably have access to `Default Switch`. With a working switch, you can either select it manually during `vagrant up|reload` or use [this clever hack](https://github.com/hashicorp/vagrant/issues/7915#issuecomment-286874774) to sidestep it:

```ruby
  config.vm.network 'public_network', bridge: "the name of your working switch"
```

#### Brief Aside: `Default Switch`

It appears the `VMSwitch` feature underwent some fairly major changes between whatever came before 1709 and 1709. When I described this to the sysadmins at work, they had never seen `Default Switch` before. All of us figured I screwed something up during the feature installation. Last week, one of them started using a copy of 1709 and immediately ran into the same issues I've been having. It's also [started to turn up online](https://social.technet.microsoft.com/Forums/windows/en-US/0aadbb19-f3cb-4539-a377-b1a67dbcdcdc/hyperv-1709-default-switch-is-it-manageable?forum=win10itprovirt). When I started trying to manage Hyper-V via PowerShell a few weeks ago, there was absolutely no documentation on the feature.

**tl;dr:** `Default Switch` is forced on you post-1709; it does [very weird things](https://github.com/docker/for-win/issues/1166)

### In the Real world

Putting all of that stuff together, plus throwing in some `provider`-specific variables, my basic control machine looks like this:

[`Vagrantfile` (source)](//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/post-02-vagrant-setup/Vagrantfile):

```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

unless Vagrant.has_plugin?('vagrant-triggers')
  `vagrant plugin install vagrant-triggers`
end

# TODO: pull these from ENV with defaults
# HYPER_V_SWITCH = 'NATWotwSsh'
# HYPER_V_SWITCH_IP_FIRST_THREE = '10.47.1'

HYPER_V_SWITCH = 'Default Switch'

Vagrant.configure('2') do |config|
  # Be careful; triggers are run for each machine
  # if Vagrant::Util::Platform.windows?
  #   [:up, :reload].each do |command|
  #     config.trigger.before command do
  #       run "powershell.exe powershell/network.ps1 -Switch #{HYPER_V_SWITCH} -LeadingThree #{HYPER_V_SWITCH_IP_FIRST_THREE} -Create"
  #     end
  #   end
  #   config.trigger.after :destroy do
  #     run "powershell.exe powershell/network.ps1 -Switch #{HYPER_V_SWITCH} -Destroy"
  #   end
  # end

  config.vm.box = 'centos/7'
  config.vm.network 'private_network', type: 'dhcp'

  config.vm.provider 'hyperv' do |hyperv|
    config.vm.network 'public_network', bridge: HYPER_V_SWITCH
  end

  # machines = ['trantor', 'terminus', 'kalgan']

  # machines.each do |machine|
  #   config.vm.define machine do |virtual_machine|
  #     virtual_machine.vm.hostname = machine

  #     virtual_machine.vm.provider 'virtualbox' do |virtualbox|
  #       virtualbox.name = machine
  #     end

  #     virtual_machine.vm.provider 'hyperv' do |hyperv|
  #       hyperv.vmname = machine
  #     end
  #   end
  # end

  config.vm.define 'controller' do |controller|
    controller.vm.hostname = 'generic'

    controller.vm.provider 'virtualbox' do |virtualbox|
      virtualbox.name = controller.vm.hostname
    end

    controller.vm.provider 'hyperv' do |hyperv|
      hyperv.vmname = controller.vm.hostname
    end

# Doesn't work; folders are mounted pre-provisioning
# See https://seven.centos.org/2017/09/updated-centos-vagrant-images-available-v1708-01/
# Run in this order to fix:
# vagrant up
# vagrant provision
# vagrant reload --provision
    # These were vetted on RHEL and Debian; dunno about others
    mount_packages = ['nfs-utils', 'nfs-utils-lib']
    mount_type = 'nfs'
    if Vagrant::Util::Platform.windows?
      mount_packages = ['cifs-utils']
      mount_type = 'smb'
    end

    # You might have to replace rpm and yum with your distro's tools
    controller.vm.provision 'shell' do |sh|
      sh.inline = "rpm -qa | egrep -i \'#{mount_packages.join('|')}\' || yum install -y #{mount_packages.join(' ')}"
      sh.privileged = true
    end

    controller.vm.synced_folder './provisioning/', '/tmp/provisioning', type: mount_type
# End doesn't work

    # WARNING: DUPLICATE THIS IN YOUR ENVIRONMENT AT YOUR OWN RISK
    # If you're running on Windows, you have to virtualize ansible anyway, so no
    # harm there. Either way, I highly recommend you test it virtually to
    # understand how it works before applying it to your environment.
    # See https://www.vagrantup.com/docs/provisioning/ansible_local.html#install
    controller.vm.provision 'ansible_local' do |ansible|
      ansible.playbook = 'initial-setup.yml'
      ansible.install_mode = 'pip'
      ansible.limit = controller.vm.hostname
      ansible.provisioning_path = '/tmp/provisioning'
      ansible.inventory_path = '/tmp/provisioning/inventory'
    end
    # END WARNING
  end
end
```

## Defining the Nodes

Once again, assume the Ansible stuff works (or doesn't) because I want to focus on the Vagrant config here.

Without the Ansible detail, adding additional machines to the `Vagrantfile` is as simple as defining each machine and including its Ansible provisioning. For example, using [my simplified example](#in-the-real-world) where several options are set on `config` rather than `controller`, you can set an array of machines and iterate over it, defining each one:

```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.box = 'centos/7'

  machines = ['trantor', 'terminus', 'kalgan']

  machines.each do |machine|
    config.vm.define machine do |virtual_machine|
      virtual_machine.vm.hostname = machine
    end
  end

  config.vm.define 'controller' do |controller|
  ...
  end
end
```

If the real world were as simple, I probably would have finished this post last weekend. Using the basic idea, you could extend this with something like this:

```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

# Docs: http://ruby-doc.org/core-2.4.0/Struct.html
# (or older)
Host = Struct.new(:hostname, :vagrant_box)
machines = [
    Host.new('trantor', 'centos/6'),
    Host.new('terminus', 'hashicorp/precise64'),
    Host.new('kalgan')
]

Vagrant.configure('2') do |config|
  config.vm.box = 'centos/7'

  machines.each do |machine|
    config.vm.define machine.hostname do |virtual_machine|
      virtual_machine.vm.box = machine.vagrant_box || config.vm.box
      virtual_machine.vm.hostname = machine.hostname
    end
  end

  config.vm.define 'controller' do |controller|
  ...
  end
end
```

Because I will be using Ansible to provision each of the hosts, I'm not too concerned about actually setting up the boxes beyond starting with the correct OS and using the correct hostname. You could easily add more keys to `Host` and define other options like networking if you're running Vagrant from a host that respects a desire for common interfaces.

Given the volatility of Ansible in development, I'd highly recommending setting a `provider`-specific name for each machine which you can use in a pinch in case everything goes south and Ansible has totally removed `vagrant`'s ability to act locally and remotely. I'm not quite sure how to screw it up locally, but I lost several remotely due to improper `ssh` settings or bad `sudo` configs, so there's a chance you might be able to screw things up worse than I did. It's always good to have a backup fubar solution in case `vagrant destroy` doesn't work. A quick example shows naming is pretty simple:

```ruby
    # inside the machines loop from above
      virtual_machine.vm.provider 'virtualbox' do |virtualbox|
        virtualbox.name = machine # (or machine.hostname if you went that route)
      end

      virtual_machine.vm.provider 'hyperv' do |hyperv|
        hyperv.vmname = machine # (or machine.hostname if you went that route)
      end
```

The final component is the Ansible integration. By default, if you define `provisioner`s for each machine, they will be run in sequence. However, [the docs](https://www.vagrantup.com/docs/provisioning/ansible.html#ansible-parallel-execution) show how to provision in parallel, which is a pretty neat party trick. Neither is important here; one of the jobs of [the initial playbook, `initial-setup.yml`](//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/post-02-vagrant-setup/provisioning/initial-setup.yml) is (or will be soon, if it's not there by the time you read this) to provision each of the nodes. I'd suggest a similar method if you're attempting to mimick your environment; it's much easier to rigorously define and validate a playbook than it is a full VM. Another alternative would be to create a Docker container for each node, but then you'd have to build all those individual `Dockerfile`s with so much copypasta maintenance would be a nightmare. My method, provisioning through the `ansible_local` playbook, adds no additional code to the `Vagrantfile` and can be used to build a nice collection of `roles` to feed your new Ansible habit. Alternative methods, like copying existing config via Vagrant, will require extra setup in Vagrant that has zero use once you're done with it.
