+++
title = "My point of view on Google Cloud"
draft = false
date = "2016-12-05T12:24:07+01:00"
thumbnail = "images/blog/logo-google-cloud.png"
description = "POV on my not so favorite cloud platform"
tags = ["cloud", "google-cloud", "aws"]
+++

Having worked a lot on AWS at my previous workplace I gained a lot of experience about it and to be honest I still think it's the best cloud platform today.

<!--more-->

At my current work I am managing a product hosted on Google Cloud
(I made most of the operation part of the migration from a hosted dedicated hardware to Cloud).

I have to say that I miss AWS; Google cloud is very immature in a LOT of points.

I'm gonna try to list most of the flaws I've encountered, but also the good points I've seen.

Negative points
================

Google is blocking some countries from accessing their hosting platform
--------------------------------------------------------------

Something good to know if you plan to make your infrastructure available to the worldwide Internet.
Google is blocking many countries from accessing the resources hosted on Google Cloud
and you have no way to allow them to access your platform without having to do some dirty hacking (like putting a reverse proxy
outside of your platform with a DNS server capable of doing geo-discrimination to forward those "forbidden" countries
to your external reverse proxy).

We had the surprise when one of our new clients from Iran could not connect to our platform and we would not see any packet coming to any of our servers, even after deep analysis.

After contacting the Google Cloud support we got the confirmation, with surprise, that they do block some countries : https://support.google.com/a/answer/2891389?hl=en

>  Google restricts access to some of its business services in certain countries or regions, such as Crimea, Cuba, Iran, North Korea, Sudan, and Syria.

And from a support ticket :

> After reviewing your case as well as our documentation, I can confirm that we block access to the Google Cloud Platform services for certain countries which includes Iran.

> The decision to block or not block traffic for services for a particular country is a decision made by the US Government and interpreted by our legal team, and then implemented in our infrastructure.

> Our technical troubleshooting skills do not include legal analysis and as you can visit the following URL for more information on the topic.
US Department of Treasury, Iran Sanctions:

> http://www.treasury.gov/resource-center/sanctions/Programs/Pages/iran.aspx


BGP over IPSEC works but not for your container networks
-----------------------------------------------------------

Something to know is that, if you plan to use VPN and a Container network (with managed Kubernetes) there are no ways (for now) to be able to distribute using BGP the networks from Kubernetes, so you will have to both use BGP for your compute networks and static routing for your containers networks or static routing for everything.

Instances can only have a single private IP
--------------------------------------------

Only one IP and one network interface per instance. That sucks if you want to do a VIP-like system as there are no real solutions except to play with the routing tables to forward an IP or a subnet to an instance, but that feels like tweaking compared to having a real moveable internal IP.

Instance private IP can only be changed by destroying the instance
-----------------------------------------------------------------

This is one of the worst points. If you have to change the IP of your instance you have to destroy it by keeping the disks and create a new instance with the new IP and the previous disks mounted... No, you can't change the IP even if the instance is shutdown.

Windows instances will only activate if they have a public IP
--------------------------------------------------------------

We had a surprise when our Windows instances showed the "Activate now" messages and after many tentatives to activate them, seeing that they could not contact the Google Cloud KMS correctly and after dealing with the support, we had to add a public IP on every instance so they can contact correctly the KMS server. Using a NAT instance didn't work here. (So yes, if you have your ADDS in Google Cloud, they will need public IPs to activate correctly...)

IAM is VERY limited
--------------------

Most of the IAM settings are either "Read access on everything", "Write access on everything" or "Admin access on everything".

Load-balancers have to be public
--------------------------------

The load balancers can only have a public front address and reach instances that have a public IP...

There is a beta of the new load balancer that can be private but I didn't have the occasion to take a look yet (Last time I tried, I could not make it work correctly).


Cloud SQL is limited to MySQL
-----------------------------

As some may know, I'm really not a big fan of MySQL.

Currently, the only supported managed database is MySQL.

There is also a feature request about having a managed PostgreSQL, but no more information from Google about that.

> https://code.google.com/p/googlecloudsql/issues/detail?id=96

No managed cache (Redis, Memcached)
------------------------------------

For now, there is no managed cache and no plan to have something like Redis or Memcached. It's sad because it's one of the most important components of any good web application.


Positive points
================

Your subnets are not bound to a zone
-------------------------------------

Something nice is that the subnets you define can spread over many availability zones. No need to have a subnet per zone. This allows you to migrate the instances between zones by keeping your internal IP addresses but you have to do it manually because the migration tool doesn't guarantee that your instance will take the same IP than before.

Managed Kubernetes is awesome
-----------------------------

I had a horrible experience with Amazon ECS when I tried it. Ok, it was just released, I hope they improved it since.
My tests on Kubernetes showed me something far more mature, reliable and easy to use but also more complicated in terms of features.

Automatic SSH keys distribution management
------------------------------------------

No more manual SSH keys management. Just put your SSH keys in the global metadata and they will automatically be distributed in all the instances of your account. However, I didn't try to check how it works when an SSH key is removed.
Is it deleted from the instances or left there ?

Automatic migration of the instances in case of hardware failure or maintenance
-------------------------------------------------------------------------------

When you create an instance you can define a policy about how to react when the host is having an issue or when a maintenance is planned. Either shut it down or migrate it without downtime to another host.
We just left it to migrate automatically and never had any issue, except some surprises when we saw in the Google Cloud logs that we had a lot of critical instances that got migrated without any service interruption.

Lower price on long running instance
-------------------------------------

Something to know is that if you leave your instance running permanently, Google gives you a 30% discount on its price.

> If you run an instance for a significant portion of the billing month, you can qualify for a sustained use discount. When you use an instance for more than 25% of a month, Compute Engine automatically gives you a discount for every incremental minute you use for that instance. The discount increases with usage and you can get up to a 30% net discount for instances that run the entire month. Sustained use discounts are calculated and applied to your bill as your project earns them.


Custom machines
---------------

One option I didn't see anywhere else is that you can either use predefined instances type or build your own type (i.e.: I want X CPUs with X Gigabytes of RAM)

So..
=====

I think right now the only advantages of Google Cloud is mostly the price of the platform.
It's usually far cheaper than AWS or Azure but far more time expensive as a lot of features are missing.
You will need a lot of time to implement highly available solutions because of their very limited network layer if you don't use their own managed solution (If you plan to setup an H.A PostgreSQL or an H.A RabbitMQ, etc.)
Also Kubernetes is a very good platform compared to AWS ECS.

Google Cloud is still very new. I hope one day they will really compete with AWS in terms of features, but for now, as far as I've seen they have a quite slow progress when you compare to what you see on the AWS like with "reInvent" that releases like 20 features in one shot (and BIG ones).

Let's hope Google will invest more into its cloud platform to take on AWS.

I would personally not use it for a new project if I know I need some missing managed services (Like PostgreSQL and Redis that are quite basic), I'll stick on AWS and observe from far the progress on Google Cloud.

The only case that would make you run into Google Cloud is if you are full Kubernetes, then, in this case, go ! :)
