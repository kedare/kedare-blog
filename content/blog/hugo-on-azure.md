+++
date = "2017-05-03T22:41:18+02:00"
draft = false
tags = ["golang", "hugo", "azure", "cdn", "ci", "hexo", "lektor"]
title = "Hugo on Azure (Web App, CDN, CI)"
description = "Learn how to deploy Hugo on Azure with continuous integration"
thumbnail = "images/blog/logo-hugo-on-azure.png"
+++

I recently moved my blog (this one) from S3 + CloudFront to Azure because I wanted to experiment the Azure CDN and I've had a quite good surprise.

I am using the Premium Verizon VPN from Azure and I am getting more or less twice better performance than what I was getting from CloudFront.

The artifacts are now hosted directly in an Azure Web App instead of a bucket. 
I replaced CloudFront by Azure CDN (Premium Verizon) and I've also setup a CI workflow using Microsoft Visual Studio Team Service (for free).

Of course, this article can be used without any issue with any other website generator (Lektor, Hexo, etc.). Easly, just swap the Hugo part on the CI by your static site generator.

<!--more-->


EDIT: There is now a plugin to automate the building part (Downloading/extracting hugo and running it), this should make this part easier, but this tutorial still applies for all the rest (Setting up CDN / Web App, CI integration, etc.) : https://marketplace.visualstudio.com/items?itemName=giuliovdev.hugo-extension

All the Azure part will be done on the Azure portal: https://portal.azure.com

The inner: Azure Web App
==========================

The application itself will be hosted as an Azure Web App.

For this component, you can use without any problem the free version, you don't need SSL at this level (The CDN will provide it) or the custom domain (The CDN will also provide it).

Start by creating your new Web App, define a new resource group if needed, make sure you create a new App Service in your location (Well it doesn't really matter as the CDN will redistribute your content), the only real important thing on your App Service is to select the "Free" pricing tier (Except if you expect your artifacts to exceed 1GB).

<center>![Free pricing tier](/images/blog/azure-hugo-web-app-setup.png)</center>

Once created, you should be able to open the default website in your Azure Web App, for example, http://kedare-lab-blog.azurewebsites.net/

If this is working fine (This should), we can continue.

The outer: Azure CDN
=========================

Now that you have your azure web app running, we need to be able to publish it on our own domain and with SSL.

Initial configuration
---------------------

We are going to create the CDN profile, go to the marketplace and search for the CDN module from Microsoft, then click "Create".

Here enter the basic information, like the name, I recommend using the same name than your Web App.

On the Pricing tier, we will select ```Premium Verizon```, because for most blog, the traffic should not be big enough to really have an important price, feels free to try with another pricing tier, everything should work the same (But with lower performances, also Akamai is very slow to purge the CDN (Around 8 minutes vs 2 minutes for Verizon)).

Once your CDN profile has been created, open its blade (panel) and create a new Endpoint, here again, enter the name of the endpoint (the same than the CDN profile and the web app if possible), select ```Web App``` as origin type, select your web app as ```Origin hostname```, the ```Origin path``` should be left blank, and the ```Origin host header``` too (As your application doesn't use it for static file), make sure you keep both HTTP and HTTPS selected. Then create it.

Once the endpoint has been created, you can access it using a default DNS like https://kedare-lab-blog.azureedge.net/

You will see for many hours a 404 error, as the endpoint needs to be replicated to every CDN POP, this is normal, most CDN operations take a lot of time as this is a distributed system.

We can still continue, so we will avoid more waiting time.

Custom domain
--------------

Make sure you setup your custom domain to point with a CNAME to the ```Endpoint hostname``` you got from this endpoint. (This is required as without this we cannot setup the custom DNS (If anyone know a way to do this without having to set the DNS before, that could be really useful, in case of service migration for example), once you have done the configuration on your side, on your CDN endpoint blade, select ```+ Custom domain``` and just fill your FQDN in the proper field (It will be validated at this time) and then "Add".

HTTPS
-----

Now, to start the SSL certification process, you first need to make sure that WHOIS technical contact on your domain name is pointing to an email address you have access to, because Azure (Well, Verizon) will send you an (automated) email at this address to validate the domain ownership before delivering a certificate.

Once you have made sure this was correct, click on your custom domain, and on the new blade, toggle the ```Custom domain HTTPS``` to YES. (Make sure you read the info box).

Once this is done, you will receive an email in the new minutes/hours to validate the domain, and then after many hours (Probably the day after), you will have the HTTPS working!

Now you have a blank HTTPS Azure Web App, yay.


Publishing Hugo to Azure automatically.
======================================

From now, the configuration will be done in the ```Visual Studio Team Service``` here: https://app.vsaex.visualstudio.com/me

From here, you can either use an existing account or create a new one.

Then on the account, create a new project, set your ```project name```, ```description```, ```revision control``` to ```git```, the ```work item process``` doesn't matter (in my case).

In this case, we are going to keep using Github as source control, but if you prefer, you can put your version control in VSTS directly.

Once we have created the project, we go to ```Build & Release``` &rarr; ```Builds``` &rarr; ```New``` and select ```start with an empty process``` on the left part of the page.

Get sources
-----------

First, configure the ```Get Source``` part to point to your repository, you may have to authenticate yourself against Github, make sure you select the correct branch.

Download Hugo distribution
--------------------------

Then you need to add a new task of type ```Powershell```, set a display name, set the type to ```Inline script```, and then in the ```Inline script```, set the following (Ajust depending on the Hugo version you need):

{{< highlight powershell >}}
Write-Host "Downloading Hugo"
Invoke-WebRequest -Uri https://github.com/spf13/hugo/releases/download/v0.20.7/hugo_0.20.7_Windows-64bit.zip -OutFile hugo.zip
{{< / highlight >}}

Note: ``Start-BitsTransfer``` would have been more efficient but is not available on VSTS.

Extract Hugo binary
--------------------

Then once you have downloaded Hugo, you need to extract it, create a new task of type ```Extract Files```, set the ```Archive file patterns``` to ```hugo.zip``` and ```Destination Folder``` to ```.```, make sure to uncheck ```Clean destination folder before extracting```.

Generate static website
------------------------

Then we create a new ```Powershell``` task to generate the website using Hugo, same than before but with another ```Inline script```:

{{< highlight powershell >}}
Write-Host "Building website"
& hugo
{{< / highlight >}}

Publish artifacts (optional)
----------------------------
This is an optional task, but useful if you want to keep a copy somewhere of each generated version, create a ```Publish Build Artifacts``` task, set the ```Path to publish``` to ```$(Build.SourcesDirectory)\public\``` and ```Artifact Type``` to ```Server```.

Deploy to Azure Web App
-----------------------

Here is the important part, create a new ```Azure App Service Deploy```, make sure you select the correct ```Azure subscription``` (You may have to connect it first), then select the ```App Service Name``` of your Azure Web App.

The only other thing that needs to be modified is the ```Package or folder``` to ```$(Build.SourcesDirectory)\public\```.

You can try it now, but you will not see any change when using your domain on the CDN because your content is probably cached, we need to purge it.

Purge CDN
---------

The last task you need to create will be a ```Azure Powershell``` task.

Make sure you set ```Azure Connection Type``` to ```Azure Resource Manager```, and set your correct ```Azure RM Subscription```.

Then we are going to set this inline script (You will need to adapt the parameters to match your azure web app name and resource group name:

{{< highlight powershell >}}
Unpublish-AzureRmCdnEndpointContent -ResourceGroupName kedare-lab-blog -ProfileName kedare-lab-blog -EndpointName kedare-lab-blog -PurgeContent "/*"
{{< / highlight >}}

Then save everything, you can queue it to try if it's working fine.

Result
------

Here is how the full process should looks like :

<center>![Free pricing tier](/images/blog/azure-hugo-process.png)</center>

Web Hook
=========

Setup
-----

Now we need to connect set the job to run everytime you commit to your Github repository, to do so, go to the ```Triggers``` tab of your job and enable ```Continuous integration```, then save, VSTS will automatically configure the Webhook on the Github side.

Try it
------
Then you can try it, make sure you have already your repository with everything you need (All your Hugo directory basically), try to commit and push something, this should trigger the job.


Bonus: Force HTTPS
========

To force HTTPS in your Hugo website on Azure, you need to add this ```web.config``` in ```static/```:

{{< highlight xml >}}
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
{{< / highlight >}}

Then every time you build your site using ```hugo```, it will be placed in your website root (And read by IIS when uploaded).

Conclusion
==========

There you go, you have your Hugo/Hexo/Lektor/... website ready on Azure :)

And that will probably only cost you less than 2$ per month.

Let me know if you see any improvement that could be done in this workflow/article.

Also, if you know a way to setup a CDN custom domain without having to point the domain on it (In the case of a migration where we want to setup it before pointing the production DNS on it), that would be really useful.

Feel free to comment.
