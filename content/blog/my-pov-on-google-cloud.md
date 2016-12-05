+++
title = "My point of view on Google Cloud"
draft = false
date = "2016-12-05T12:24:07+01:00"
thumbnail = "images/blog/logo-google-cloud.png"
+++

Having worked a lot on AWS on my previous company, I could gain a lot of experience about it,
and to be honest, I think it's still the best cloud platform today.

At my current work, I am managing a prodct hosted on Google Cloud
(I made most of the operation part of the migration from a hosted dedicated hardware to Cloud)

I have to say, I miss AWS, Google cloud is very immature in a LOT of points,

I'm gonna try to list most of the pains I've encoutered, but also the good points I've seen.

Negative points
================

Google is blocking some countries from their hosting platform
--------------------------------------------------------------

Something good to know if you plan to make your infrastructure available to the "global world".
Google is actually blocking many countries from accessing many resources hosted on Google Cloud,
and you have no way to allow them without having to d some disrty hacking like putting a reverse proxy
outside of your platform with a DNS server capable of doing geo-discrimination to forward those "forbidden" countries
to your external reverse proxy.

We had the surprise when one new client from Iran could not connect to our platform, and we would not see any packet coming to any of our servers.

After contacting the Google Cloud support, I got the confirmation with surprise that they do block some countries : https://support.google.com/a/answer/2891389?hl=en

>  Google restricts access to some of its business services in certain countries or regions, such as Crimea, Cuba, Iran, North Korea, Sudan, and Syria.


BGP over IPSEC works but not for your container networks
-----------------------------------------------------------

Something to know is that, if you plan to use VPN and a Container network (with managed Kubernetes), there are no ways for now to be able do distribute using BGP the networks from Kubernetes, so you will have to both use BGP for your compute networks and static routing for your containers networks, or static routing for everything.

Instances can only have a single private IP
--------------------------------------------

Only one IP and one network interface per instance, that sucks if you want to do a VIP-like system, there are no real solution except play with routing table to forward an IP or a subnet to an instance, but that feels like tweaking...

Instance private IP can only be change by destroying the instance
-----------------------------------------------------------------

This is one of the worst point, if you have to change the IP of your instance, you have to destroy it by keeping the disk, and create a new instance with the new IP with this disk mounted... No you can't change the IP even if the instance is shutdown.

Windows instances will only activate if they have a public IP
--------------------------------------------------------------

We had a surprise when our Windows instance shown the "Activate now" messages, and after many tentative to activate them, seeing that they could not contact the Google KMS correctly, after dealing with the support, we had to add a public IP on every instance so they can contact correctly the KMS server, using a nat instance didn't work here. (So yes, if you have you ADDS in Google Cloud, they will need public IP to activate correctly...)

IAM is VERY limited
--------------------

Most of the IAM settings are either "Read access on everything", "Write access on everything" or "Admin access on everything"

Load-balancers have to be public
----------------------

The load balancers can only have a public front address and reach instances that have a public IP...

There is a beta of the new load balancer that would allow if to be public, I didn't had the occasion to take a look yet (Last time I tried, I could not make it work correctly)


Positive points
================

Your subnets are not bound to a Zone
-------------------------------------

Something nice is that the subnets you define can spread over many availability zones, no need to have a subnet per zone, that allows you to migrate the instance between zones by keeping your internal IP address (But you have to do it manually because the migration tool doesn't guarantee that you instance will take the same IP than before.)

Managed Kubernetes is awesome
-----------------------------

I had an horrible experience with Amazon ECS when I tried it (Ok, it was just release, I hope they improved it), my tests on Kubernetes shown me something far more mature, reliable and easy to use (but also more complicated in term of features)

Automatic SSH keys distribution management
------------------------------------------

No more manual SSH keys management, just put your SSH keys in the global metadata and they will automatically be distributed in all the instances of your account. However I didn't try to check how it works when a SSH keys is removed (Is it deleted from the instances or left there ?)

Automatic migration of the instances in case of hardware failure or maintenance
-------------------------------------------------------------------------------

When you create an instance, you can define a policy about how to react when the host is having issue or when a maintenance is planned, either shut it down, or migrate it without downtime to another host.
We just left it to migrate automatically and never had any issue, except some surprise when we saw in the Google Cloud logs that we had a lot of critical instances that got migrated without any service interruption.
