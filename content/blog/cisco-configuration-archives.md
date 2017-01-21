+++
title = "Tips: Cisco Configuration Archives"
date = "2014-02-11"
tags = ["cisco", "telco"]
description = "How to make your Cisco configuration versioned"
thumbnail = "images/blog/logo-cisco.png"
+++

Here are some tips to show you the basics of the configuration archive function on Cisco IOS

<!--more-->

You can setup you router to store all older versions of your configuration, like this :

```
archive
  log config
  record rc
  logging enable
  notify syslog contenttype plaintext
  path flash:startup-config
  maximum 14
  rollback filter adaptive
  write-memory
```

This will, every time you write memory, copy your old startup-config to a file with the current date, like this :

```
16 -rw- 7391 Mar 20 2012 20:30:04 +02:00 startup-configMar-20-18-30-05.366-52
17 -rw- 7391 Mar 21 2012 16:42:50 +02:00 startup-configMar-21-14-42-50.316-53
```

You can see the current in-memory archives :

```
> sh archive
The maximum archive configurations allowed is 14.
There are currently 3 archive configurations saved.
The next archive file will be named flash:startup-config--3
Archive Name
1 flash:startup-configNov-15-20-28-19.132-0
2 flash:startup-configNov-16-07-39-50.027-1
3 flash:startup-configNov-24-15-32-20.014-2
```
