---
title: "Keycloak + ASP.NET Identity"
date: 2023-08-06T00:00:00+01:00
thumbnail: "images/blog/keycloak-aspnet-identity.png"
description: "How to use Keycloak as identity broker for ASP.NET Identity"
tags: ["openid", "authentication", "oidc", "keycloak", "dotnet", "csharp", "programming" ]
---

## Introduction

In this article we are going to see how to use the [Keycloak](https://www.keycloak.org/) IDP as identity broker.

Keycloak is one of the major opensource identity provider in the world.

It is used in many large institutions, for example [France Connect](https://franceconnect.gouv.fr/), which if the official french identity system for public services is built on top of it.

## Initial setup

We are going to start from a simple Angular SPA template with ASP.NET API (it could be the react template also, we are not going to do any changes on the Frontend code).

Start by creating your application (no need if you already have one you want to use with this)

```bash
dotnet new angular
```
It should have most of the code needed to work on this project.

You can already make sure it is working fine by running it and making sure that you can properly access the local website, create a local user, connect and browse protected pages (the Fetch Data one for example).

Once you made sure everything is working fine, we can start by the Keycloak setup (if you have one already, skip this step)


## Keycloak initial setup

You will need to download keycloak from the official website (it can be also used with docker, but I did not test it), and run it directly.

```bash
wget https://github.com/keycloak/keycloak/releases/download/22.0.1/keycloak-22.0.1.tar.gz
tar xvf keycloak-22.0.1.tar.gz
cd keycloak-22.0.1.tar.gz
./bin/kc.sh start-dev
```

> This is not a production setup, to make your keycloak useable in production, please follow the [official documentation](https://www.keycloak.org/documentation)

You can now connect to the local interface and initialize it by browsing to [The Keycloak root page](http://localhost:8080)

You will be asked to configure an initial user on the `master` realm, which is the administrative realm that allows you to configure Keycloak and all the other realms.

Once you have created your initial user and connected to the [administration interface](http://localhost:8080/admin/master/console/), you would need to create a new realm for your applications.

Let's go to the expanding menu on the top left, select `Create Realm` and create a new one (`external` for example), you should now see your 2 realms in the menu, make sure you now select the `external` one.

<center>

  ![Realms list](/images/blog/keycloak-realms-list.png)

</center>

Make sure you have at least 1 user you can use for this article, check the `Users` tab on the left, create one if you don't have any (just put an Username, email, and after saving it, set its password in the Credentials tab)

## OIDC configuration

Now are are going to configure the OpenID Connect protocol between our ASP.NET application and our Keycloak setup.

The good thing with OIDC is that is provices more things than oAuth2 out of the boxes, you will have less things to configure than if you were doing oAuth2 (like to get the user profile, etc...)

First thing, we are going to create the client on the Keycloak server.

The `Client` is not the user but the application that will request the authentication and get the final token from the provider, in OIDC, the user is usually called a `Resource Owner`

To create the client, go to `Clients` on the left menu, then `Create client` on the client list (you already have a few clients used internally by Keycloak and the various internal apps, you can ignore them).

Make sure the `Client type` is set to `OpenID Connect`, then you can fill the form with your data, for example:

| Form Field | Form value    |
|------------|----------------|
| Client ID  | my-aspnet-app  |
| Name       | My ASP.NET App |

Leave the rest by default, then click `Next`

Here you get more important fields to configure


| Form Field             | Form value    |
|------------------------|---------------|
| Client Authentication  | On            |
| Authorization          | On            |
| Authentication flow    | Standard flow |

You may need more authentication flows enabled depending on the use case, but for what is covered by this article, this is the only flow needed.


Then on the last configuration page, you would have a few urls to configure.

Here we assume the root URL of our ASP.NET application is `https://localhost:44418/`


| Form Field          | Form value                                          |
|---------------------|-----------------------------------------------------|
| Root URL            | https://localhost:44418/                            |
| Home URL            | https://localhost:44418/                            |
| Valid redirect URIs | https://localhost:44418/.well-known/openid-callback |
| Web origins         | https://localhost:44418/*                           |

> We are using the https://localhost:44418/.well-known/openid-callback url instead of for example https://localhost:44418/oidc/callback,
as I could not find an easy way to configure the ASP.NET SPA proxy to force this URL to be forwarded to the backend and not the frontend. (if anyone has an idea)

Then click Save

The configuration of Keycloak is now done, you will just need to get the `Client secret` from the `Credentials` tab to use it in the ASP.NET configuration after.


## ASP.NET Identity configuration

Now let's go back to our application code that was working fine.

We need update the `Program.cs` file that contains the service configuration.

Locate the part of the the code related to your identity configuration and make sure it matches the configuration required for Keycloak, you normally only have to add the `AddOpenIdConnect` part.

```csharp
builder.Services.AddAuthentication()
    .AddIdentityServerJwt()
    .AddOpenIdConnect("keycloak", "Keycloak", options =>
    {
        options.CallbackPath = "/.well-known/openid-callback";
        options.Authority = "http://localhost:8080/realms/external"; // Use https in production
        options.ClientId = "my-aspnet-app";
        options.ClientSecret = "Jmqezm95ZG3JJCVRxypZBafst5VjSivK";
        options.ResponseType = "code";
        options.GetClaimsFromUserInfoEndpoint = true;
        options.RequireHttpsMetadata = false; // Don't use this for production
    });
```

This is all you need to do, now compile the application, run is, and you should now see a new option on the login page:

<center>

![ASP.NET identity login page with Keycloak option](/images/blog/keycloak-aspnet-sso.png)

</center>

You can click on the Keycloak button to initiate the login with the user you previously created.

Once you are logged in, you should now be back to the ASP.NET application, you may have a confirmation of your email before creating the account, then once everything has been validated, you now see your email in the top menubar on the right.

You can now test the authentication by accesing a page that requires an authenticated endpoint like the "Fetch Data" tab of the app.

## There's more

This is the only thing we will cover in this article, as an introduction to the usage of Keycloak with ASP.NET Identity.

Do not use the keycloak setup like this in production as this not a reliable nor secure setup for something in production :)

There are a lot more features available on both Keycloak and on the OpenID protocol if you are more curious.

One advantage of Keycloak is that you can use it as identity broker, meaning that you can configure keycloak so it would allow you to connect using external identity providers.

This is useful if for example you can to keep your appication code simple or if you have a lot of different applications but don't want to integrate each of them with all the external providers.

You can for example integrate Keycloak with "Sign in with Apple" to provide seamless SSO automatically to allow all your applications (both web or native apps) to take advantage of it via Keycloak.

This also allows you to have multiple social network associated with a single Keycloak account that your applications will use, if you have more apps to integrated in the future, just connect them to Keycloak and this will automatically give you access to all the identity providers connected to it (same if you want to just add a new identity providers to all your existing applications)
