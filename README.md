# AudioSocket Framework

## ❗❗❗ **This repo is now deprecated. Check the [Vonage Developer Blog](https://developer.vonage.com/en/blog) for more blog posts and tutorials. For more sample Vonage projects, check the [Vonage Community GitHub repo](https://github.com/Vonage-Community).**

This is a Basic python tornado app for handling websocket audio from the Nexmo Voice API.

This is an ideal starting point for interfacing between Nexmo and an AI Bot platform.

## Features
* Generates an NCCO to be returned which will connect a call to the /socket endpoint of the server with the CLI in a meta data field.
* Exposes a websocket server to receive the connection from Nexmo
* Maintains a dict. of each connection object referenced by its CLI
* Breaks the stream of incomming audio into descreet buffered objects using Voice Acivity Detection to separate block of speech
* Provides a function to playback audio to a caller by CLI
* Provides a handler to print events to the console


# Installation

You'll need Python 2.7, and we recommend you install the code inside
a python virtualenv. You may also need header files for Python and OpenSSL,
depending on your operating system. The instructions below are for Ubuntu 14.04.

```bash
sudo apt-get install -y python-pip python-dev libssl-dev
pip install --upgrade virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Configuration

The application reads its configuration from an app.conf file in the root directory, a template file is included in the repo, rename this to `app.conf` and enter the approriate values

## Port

The `port` configuration variable is only required if you don't want to host on
port 8000. If you're running ngrok and you're not using port 8000 for anything
else, just run `ngrok http 8000` to tunnel to your Audiosocket service.

## Path
This is where the framework application will store audio files it records from the websocket it is only needed for the basic demo

## Host
Your audiosocket server needs to be available on a publicly hosted server. If
you want to run it locally, we recommend running [ngrok](https://ngrok.com/) to
create a publicly addressable tunnel to your computer.

Whatever public hostname you have, you should enter it into `app.conf`.
You'll also need to know this hostname for the next step, creating a Nexmo
application.

## Creating an application and adding a phone number

Use the [Nexmo command-line tool](https://github.com/Nexmo/nexmo-cli) to create
a new application and associate it with your server (substitute YOUR-HOSTNAME
with the hostname you've put in your `HOST` config file):

```bash
nexmo app:create "Audiosocket Demo" "https://YOUR-HOSTNAME/ncco" "https://YOUR-HOSTNAME/event"
```

If it's successful, the `nexmo` tool will print out the new app ID and a
private key. Put these, respectively in `config/APP_ID` and
`config/PRIVATE_KEY`.

If you need to, find and buy a number:

```bash
# Skip the first 2 steps if you already have a Nexmo number to use.

# Replace GB with your country-code:
nexmo number:search GB —voice

# Find a number you like, then buy it:
nexmo number:buy [NUMBER]

# Associate the number with your app-id:
nexmo link:app [NUMBER] [APPID]
```


# Running
Now you can start the audiosocket service with:

```bash
./venv/bin/python server.py
```

If you want to see more verbose logging messsages add a `-v` flag to the startup to see all DEBUG level messages

# Extending
This framework is meant to be a starting point for integrating whatever voice processing solution you desire, within the `Processor` class there is a function named `process` modify this to do whatever you want to with the blocks of speech, for example posting them to a transcription API, the current code jsut saves them to wav files which is useful for debuggin but you do not have to write to the filesystem if you don't need to store the audio.
Configuration for the processor for example API keys for 3rd party services can be passed in when the `processor` object is created at line 219, you will see in the demo that a path object is passed in to tell the processor where to save files. Again this can be removed if not required.
You can also playback audio responses to the caller using the `playback` funciton of the `Processor` this uses the CLI of the caller as an identifier to ensure it is played to the correct connection therefore you need to track this in your requests and pass it in as a parameter along with wav or raw audio `content` in the response.
