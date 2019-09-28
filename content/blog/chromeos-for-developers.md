---
title: "ChromeOS for developers"
date: 2019-09-28T16:03:38+02:00
thumbnail: "images/blog/logo-chromeos-for-developers.png"
description: "ChromeOS architecture and usage as a developer/SRE"
tags: ["devops", "developer", "sre", "chromeos", "chromebook", "Chromium", "ChromiumOS"]
---

I recently decided to get a new laptop as my 2013's Macbook pro was starting to fail from all sides
(broken speaker, randomly working screen backlight, getting really slow), I wanted the following features for my new laptop :

- Good battery life: Because it's a laptop.
- Touch screen: Because for some workflows it's much better than the mouse, having a 2-in-1 is also a big plus but optional.
- Small'ish screen with a good resolution: I don't like bulkly laptops, but I want a good screen on it (understand high DPI)
- Robust hardware: Because I want it to last for a few years.
- Developer friendly: Because I'm mostly using it for development and SRE stuff.

Those are the tasks I want to be able to do on my laptop :

- Web browsing
- Media playback (Netflix, Youtube, Spotify, etc...)
- Web / Go / Python development
- SRE tools (Remote SSH, kubectl, etc..)
- SDR (Software Defined Radio)

I considered the following options :

- Getting a new Macbook: I don't like their unreliable keyboard, and I didn't really like the last versions of MacOs (Much less reliable and more buggy than a few years ago), also they are quite expensive, and this would mean no touch-screen.
- Getting a new ThinkPad: That was the best other option, Linux first citizen, ok to good battery life (As Windows is still much more optimized than Linux on that because of better hardware support), but I didn't really find anything good on my budget.
- Getting an old ThinkPad: I really liked the x230 in the past, but today it's quite hard to find good batteries for them, and the display is really bad for today's standards and the trackpad is really obsolete.
- Getting a Chromebook: This was the last option, I was not completely sure at the beginning because I didn't know much about Chromebooks and ChromeOS and there is the cliché that you can only use Chromebook to run web apps and nothing local.

So I started to check for Chromebooks, the best option I found was the Asus Chromebook C434, I wanted at least 8GB of memory, a good and robust design, an backlight keyboard, so this one is the perfect match.

<center>![Asus C434](/images/blog/asus-c434.jpg)</center>

So I decided to order it, from the US as it's a mess in France to get a QWERTY keyboard, I got very surprised by the build quality once received it, it feels very solid (Even more than the recent Macbooks).

# ChromeOS

<center>![ChromeOS Architecture](/images/blog/chromeos-architecture.png)</center>


ChromeOS itself is a Linux distribution but you will not get access to the root account or even to a full shell (Except if you go to developer mode but that will basically shut most of the security systems and that's not what we want).

You basically have 3 ways of running applications on ChromeOS:

- ChromeOS Web applications, you install them directly in ChromeOS, those are basically SPA or Chrome extensions (with a few more things when running in ChromeOS)
- Android applications: You can install any Android application on your ChromeOS, I use this for Google Keep or Spotify for example.
- Linux applications: You have a Linux VM available in Crostini that allows you to have full access and install what you want (I talk about it now)

As ChromeOS top priority is security, each of those subsystem is sandboxed from each others, it's even more true for the Linux mode as you get 2 levels of isolation (LXD and KVM)

In this article I will talk about the the third one as this is the one interesting in our case.

First, let's pick a quick text from the Google documentation:



> **Crostini** is the umbrella term for making Linux application support easy to use and integrating well with Chrome OS. It largely focuses on getting you a Terminal with a container with easy access to installing whatever developer-focused tools you might want. It's the default first-party experience.
> 
> The **Terminal** app is the first entry point to that environment. It‘s basically just crosh. It takes care of kicking off everything else in the system that you’ll interact with.
> 
> **crosvm** is a custom virtual machine monitor that takes care of managing KVM, the guest VM, and facilitating the low-level (virtio-based) communication.
> 
> **Termina** is a VM image with a stripped-down Chrome OS linux kernel and userland tools. Its only goal is to boot up as quickly as possible and start running containers. Many of the programs/tools are custom here. In hindsight, we might not have named it one letter off from “Terminal”, but so it goes.
> 
> **Maitred** is our init and service/container manager inside of the VM, and is responsible for communicating with concierge (which runs outside of the VM). Concierge sends it requests and Maitred is responsible for carrying those out.
> 
> **Garcon** runs inside the container and provides integration with Concierge/Chrome for more convenient/natural behavior. For example, if the container wants to open a URL, Garcon takes care of plumbing that request back out.
> 
> **Sommelier** is a Wayland proxy compositor that runs inside the container. Sommelier provides seamless forwarding of contents, input events, clipboard data, etc... between applications inside the container and Chrome. Chrome does not run an X server or otherwise support the X protocol; it only supports Wayland clients. So Sommelier is also responsible for translating the X protocol inside the container into the Wayland protocol that Chrome can understand.

Source: https://chromium.googlesource.com/chromiumos/docs/+/8c8ac04aed5d45bb6a14605c422dbbd01eeadf15/containers_and_vms.md

So we are already getting a lot of information, and you know what, as all this is part of the Chromium project, everything is open source and available for us to look at : https://chromium.googlesource.com/chromiumos/platform2/+/HEAD/vm_tools

When you enable the Linux mode (called Crostini) on the ChromeOS setting, ChromeOS will download a Linux image and start it with KVM, this container host is called Termina.

And you also get a Terminal application installed, I would not recommend using it much as it's quite limited.
You will quickly see that the installed container is in fact a Debian (9 at this time, but it's easy to upgrade with the usual procedure) and of course you get full root access.

You can install without issue graphical applications like Visual Studio Code or another Terminal application (I use gnome-terminal in my case), and as Google do things correctly, you even have a GTK theme matching Material design installed by default.

However be careful when using some heavy GUI application, the GPU acceleration is still in beta (Like the whole Crostini) and not available everywhere yet.

From now you have your usual Linux shell and can setup everything you want and still have a great battery life.

So now let's say you want something else than Debian, as this is standard LXD, you can use any image coming for example from https://us.images.linuxcontainers.org/

To do so, you need to start `crosh` that is the native ChromeOS limited shield, to do so, start Google Chrome and use `ctrl+alt+t`, you will get a terminal tab inside your web browser:

{{< highlight bash >}}
[Pro Tip] Use 'Open as Window' or 'Fullscreen' to prevent Ctrl-W from closing your terminal!
[Pro Tip] See [crosh] for more information.

Welcome to crosh, the Chrome OS developer shell.

If you got here by mistake, don't panic!  Just close this tab and carry on.

Type 'help' for a list of commands.

If you want to customize the look/behavior, you can use the options page.
Load it by using the Ctrl+Shift+P keyboard shortcut.

crosh> 
{{</ highlight >}}

From there need to jump inside the `Termina` VM that is the LXD container host and we can already start using the standard `lxc` CLI and check for our default container running (The one you to go with the Terminal app by default):

{{< highlight bash >}}
crosh> vsh termina
(termina) chronos@localhost ~ $ lxc list
+---------|---------|-----------------------|------|------------|-----------+
|  NAME   |  STATE  |         IPV4          | IPV6 |    TYPE    | SNAPSHOTS |
+---------|---------|-----------------------|------|------------|-----------+
| penguin | RUNNING | 100.115.92.195 (eth0) |      | PERSISTENT | 0         |
+---------|---------|-----------------------|------|------------|-----------+
{{</ highlight >}}
```

So one thing you may want to do is being able to interract with LXD without having to go `crosh` then jumping to `termina`, good thing, LXD allows remote control, so let's set it up so we can control it from our `penguin` container, we will need to spawn a temporary ubuntu instance to get a compatible LXC client:

{{< highlight bash >}}
(termina) chronos@localhost ~ $ lxc config set core.https_address :8443
(termina) chronos@localhost ~ $ lxc config set core.trust_password wowsupersecret
(termina) chronos@localhost ~ $ lxc launch images:ubuntu/18.04 ubuntu
(termina) chronos@localhost ~ $ lxc exec ubuntu -- apt install -y lxd-client
(termina) chronos@localhost ~ $ lxc file pull ubuntu/usr/bin/lxc /tmp/lxc
(termina) chronos@localhost ~ $ lxc file push /tmp/lxc penguin/usr/local/bin/lxc
(termina) chronos@localhost ~ $ lxc stop --force ubuntu
(termina) chronos@localhost ~ $ lxc delete ubuntu
{{</ highlight >}}

Then on your `penguin` container:

{{< highlight bash >}}
> $ ip -4 route show
default via 100.115.92.193 dev eth0 
100.115.92.192/28 dev eth0 proto kernel scope link src 100.115.92.195

> $ lxc remote add crostini 100.115.92.193
Admin password for crostini:
Client certificate stored at server:  crostini
> $ lxc remote set-default crostini
> $ lxc list                                                                                                                                      
+---------|---------|-----------------------|------|------------|-----------+                                                                     
|  NAME   |  STATE  |         IPV4          | IPV6 |    TYPE    | SNAPSHOTS |                                                                     
+---------|---------|-----------------------|------|------------|-----------+                                                                     
| penguin | RUNNING | 100.115.92.195 (eth0) |      | PERSISTENT | 0         |                                                                     
+---------|---------|-----------------------|------|------------|-----------+
{{</ highlight >}}

There you should be able to control everything from your `penguin` container.

So far I didn't had the need for another VM than the basic one, I do my full development workflow inside the `penguin` VM, but I understand than sometime you may want something different than Debian.

You need to know that by default you won't have the same level of integration with others containers, like automatic integration of the desktop apps (They will appear in ChromeOS once installed like if it was a Gnome desktop) and shared folders between ChromeOS and your container, most of those features are available after some configuration on others containers.

So far everything is working fine, I do see some issues sometimes, with Jetbrains IDE typically, I get some random freezes on the whole ChromeOS, that should not happen and I reported the issue to the Chromium OS issue tracker.

Also as you know Chromebook are fanless and low-power computers, you may expect thermal throttling during intense compute (So if you plan to use Rust or Java... you'll understand).

The fact that for now you can't expose directly sockets to the outside world (Just to the ChromeOS host) can be problematic.

The USB limitation also make impossible the use of ChromeOS for SDR (Software Defined Radio) as the container will not see connected USB devices.

Except that, everything is working perfectly fine, ChromeOS may finally be the Linux coming to the desktop reason ? And having this separated environment make mostly impossible to crash your whole computer because developers like to tweak everything. (And here you get snapshots for free on your containers by the way)

So at the end, about ChromeOS for developers/SRE :

- The design is secure by default, it's a good thing as it's very hard to break into (Don't enable development mode) but can be limiting for some specific cases (see after)
- Not having raw USB access can be an issue, no way to connect specific external devices like usb-to-serial adapters or SDR systems
- Your containers are isolated from the network, you don't have bridged network to your interfaces and can't expose sockets to the outside
- Being able to run Android applications is cool
- Battery life is excellent (10 hours)
- Linux GUI applications work fine, but be careful as there are no GPU acceleration on those

But let's remember that Crostini is still in beta, so hopefully most of those limitations will be fixed (in a secure way)

I hope you liked this article, feel free to comment, hopefully I will post more in the future about ChromeOS.

There you have some related links :

- [Linux for Chromebooks: Secure Development (Google I/O ’19)](https://www.youtube.com/watch?v=pRlh8LX4kQI&t=1403s)
- [Running Custom Containers Under Chrome OS](https://chromium.googlesource.com/chromiumos/docs/+/master/containers_and_vms.md)
- [/r/ChromeOS](https://www.reddit.com/r/chromeos/)
- [/r/crostini](https://www.reddit.com/r/Crostini/)
