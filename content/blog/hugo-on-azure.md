+++
date = "2017-05-03T22:41:18+02:00"
draft = true
tags = ["golang", "hugo", "azure", "cdn", "ci"]
title = "Hugo on Azure (Web App, CDN, CI)"
thumbnail = "images/blog/logo-hugo-on-azure.png"
+++

I recently moved my blog (this one) from S3 + CloudFront because I wanted to experiment the Azure CDN and I've had a quite good surprise.

I am using the Premium Verizon VPN from Azure and I am getting more or less the double that what I was getting from CloudFront.

The artifacts are now hosted directly in an Azure Web App instead of a bucket, I replace CloudFront by Azure CDN (Premium Verizon) as said just before, and more recently, I've setup CI using Microsoft Visual Studio Team Service (for free)


<!--more-->

All the Azure part will be done on the Azure portal: https://portal.azure.com

The inner: Azure Web App
==========================

The application itself will be hosted as an Azure Web App.

For this component, you can use without any problem the free version, you don't need SSL as this level (The CDN will provide it) or the custom domain (The CDN will also provide it)

Start by creating you new Web App, define a new resource group if needed, make sure you create a new App Service in your location (Well it doesn't really matter as the CDN will redistribute your content), the only real important thing on your App Service is to select the "Free" pricing tier (Except if you expect your hugo build result to exceed 1GB)

<center>![Free pricing tier](/images/blog/azure-hugo-web-app-setup.png)</center>

Once created, you should be able to open the default website in your Azure Web App, for example : http://kedare-lab-blog.azurewebsites.net/

If this is working fine (This should), we can continue.

The outer: Azure CDN
=========================

Now that you have your azure web app running, we need to be able to publish it on our own domain and with SSL.

Initial configuration
---------------------

We are going to create the CDN profile, go to the marketplace and search for the CDN module from Microsoft, then click "Create".

Here enter the basic informations, like the name, I recommend using the same name than your Web App.

On the Pricing tier, we will select ```Premium Verizon```, because for most blog, the traffic should not be big enough to really have an important price, feels free to try with another pricing tier, everything should work the same (But with lower performances, also Akamai is very slow to purge the CDN (Around 8 minutes vs 2 minutes for Verizon))

Once your CDN profile has been create it, open its blade (panel) and create a new Endpoint, here again, enter the name of the endpoint (the same than the CDN profile and the web app if possible), select ```Web App``` as origin type, select your web app as ```Origin hostname```, the ```Origin path``` should be left blank, and the ```Origin host header``` too (As your application doesn't use it for static file), make sure you keep both HTTP and HTTPS selected. Then create it.

Once the endpoing has been create, you can access it using a default DNS like https://kedare-lab-blog.azureedge.net/

You will see for many hours a 404 error, as the endpoint needs to be replicated to every CDN POP, this is normal, most CDN operations take a lot of time as this is a distributed system.

We can still continue, so we will avoid more waiting time.

Custom domain
--------------

Make sure you setup your custom domain to point with a CNAME to the '''Endpoint hostname''' you got from this endpoint. (This is required as without this we cannot setup the custom DNS (If anyone know a way to do this without having to set the DNS before, that could be really useful, in case of service migration for example), once you have done the configuration on your side, on your CDN endpoing blade, select ```+ Custom domain``` and just fill your FQDN in the proper field (It will be validated at this time) and then "Add".

HTTPS
-----

Now, to start the SSL certification process, you first need to make sure that WHOIS technical contact on your domain name is pointing to an email address you have access to, because Azure (Well, Verizon) will send you an (automated) email at this address to validate the domain ownership before delivering a certificate.

Once you have made sure this was correct, click on your custom domain, and on the new blade, toggle the ```Custom domain HTTPS``` to YES. (Make sure you read the info box).

Once this is done, you will receive an email in the new minutes/hours to validate the domain, and then after many hours (Probably the day after) your will have the HTTPS working !

Now you have a blank HTTPS Azure Web App, yay.


Publishing Hugo to Azure automatically.
======================================

From now, the configuration will be done in the ```Visual Studio Team Service``` here: https://app.vsaex.visualstudio.com/me

From here, you can either use an existing account or create a new one.

Then on the account, create a new project, set your ```project name```, ```description```, ```revision control``` to ```git```, the ```work item process``` doesn't matter (in my case)


TODO TODO TODO

Bonus: Force HTTPS
========

To force HTTPS in your Hugo website on Azure, you need to add this ```web.config``` in ```static/```:

```
<configuration xmlns="http://schemas.microsoft.com/.NetConfiguration/v2.0">
    <appSettings/>
    <connectionStrings/>
    <system.webServer>
     <rewrite>
      <rules>
       <rule name="Redirect to https">
        <match url="(.*)"/>
        <conditions>
         <add input="{HTTPS}" pattern="Off"/>
        </conditions>
        <action type="Redirect" url="https://{HTTP_HOST}/{R:1}"/>
       </rule>
      </rules>
     </rewrite>
    </system.webServer>
</configuration>
```

Then every time you build your site using ```hugo```, it will be placed in your website root (And read by IIS when uploaded)
