# Code Central AI Bot
Welcome to the official repo for the [Code Central](https://discord.gg/rf5qN7C) AI Chatbot.
This is a fork of [gpt2bot](https://github.com/polakowo/gpt2bot) but with modifications to support discord.

# Installation 
Want to run the bot for yourself? Follow these steps.

> ⚠️ **I will NOT be providing installation help! Please do not open a issue requesting for support with installation.** ⚠️

## Requirements
- Python 3.X
- A working internet connection.

## Configuration
- Copy `.env.example` and rename it to `.env`
- Replace `[YOUR TOKEN HERE]` with your bot token.
- Replace `[CHANNEL ID]` with the channel you want the bot to listen in.

## Installing Dependencies
```bash
pip3 install -r requirements.txt
```

If you get `ERROR: Could not install packages due to an OSError: [WinError 2] The system cannot find the file specified:` try adding the `--user` switch.

## Running the bot
```bash
python3 ./run_bot.py --type=discord
```

# Contributing / Reporting Bugs
Found a bug in the bot? First identify where the issue is coming from. Is it a bug with the bot, or a bug with the AI?

AI responses are handled by [gpt2bot](https://github.com/polakowo/gpt2bot), while wrapping it to a discord bot is done in this repo. 

If it's a bug with my code, please either open a pull request with a fix or create a github issue. 