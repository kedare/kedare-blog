+++
title = "Observium LLDP graph generator"
date = "2015-01-25"
tags = ["observium", "python", "telco"]
description = "Introduction to my small observium LLDP graph script"
thumbnail = "images/blog/observium-map-generator.png"
+++

Here is a small script I made.

<!--more-->

It uses the Observium database to generate a FULL topology of your network using LLDP entities.
Links are colored using link load, and link size depend of the link capacity.
You just need to be sure that each device see its neighbours with correct hostnames.
It’s compatibles with all discovery protocols working with Observium (LLDP, CDP, FDP, AMAP, maybe more)

You can see a screenshot at the top of the page, and here is a link to my repository :
https://github.com/kedare/observium_map_generator

Observium may change with time so I can't guarantee it will still work in the future, feel free to fork it :)
