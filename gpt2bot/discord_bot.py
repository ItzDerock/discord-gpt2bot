import os
from discord.ext import commands
from .utils import *
from dotenv import load_dotenv

# load .env
load_dotenv()

logger = setup_logger(__name__)

# main function
def run(**kwargs):
    """Run the discord bot."""

    # Check environment
    if os.getenv('TOKEN') == None:
        raise RuntimeError("No token found in .env")
    
    if os.getenv('CHANNEL') == None:
        raise RuntimeError("No channel found in .env")

    if os.getenv('PREFIX') == None:
        os.environ['PREFIX'] = 'ai!'
        logger.warn('WARN: No prefix found in .env, defaulting to "ai!".')

    if os.getenv('TURN_HISTORY') == None:
        os.environ['TURN_HISTORY'] = -1
        logger.warn('WARN: No max turn history set in .env, defaulting to infinite.')

    try:
        int(os.getenv('TURN_HISTORY'))
    except:
        raise RuntimeError("TURN_HISTORY is not a valid number. (.env)")

    # initialize discord bot.
    bot = commands.Bot(command_prefix="ai!")

    # Extract parameters
    general_params = kwargs.get('general_params', {})
    device = general_params.get('device', -1)
    seed = general_params.get('seed', None)
    debug = general_params.get('debug', False)

    generation_pipeline_kwargs = kwargs.get('generation_pipeline_kwargs', {})
    generation_pipeline_kwargs = {**{
        'model': 'microsoft/DialoGPT-medium'
    }, **generation_pipeline_kwargs}

    generator_kwargs = kwargs.get('generator_kwargs', {})
    generator_kwargs = {**{
        'max_length': 1000,
        'do_sample': True,
        'clean_up_tokenization_spaces': True
    }, **generator_kwargs}

    prior_ranker_weights = kwargs.get('prior_ranker_weights', {})
    cond_ranker_weights = kwargs.get('cond_ranker_weights', {})

    max_turns_history = int(os.getenv('TURN_HISTORY'))

    bot_prefix = os.getenv('PREFIX');

    # Prepare the pipelines
    generation_pipeline = load_pipeline('text-generation', device=device, **generation_pipeline_kwargs)
    ranker_dict = build_ranker_dict(device=device, **prior_ranker_weights, **cond_ranker_weights)

    # Run bot
    turns = {}
    logger.info("Starting discord bot...")

    # Ready event
    @bot.event
    async def on_ready():
        logger.info("Logged into discord. You may now use me!")

    # Listen for messages
    @bot.event
    async def on_message(message):
        if str(message.channel.id) != os.getenv('CHANNEL'):
            return # return if not right channel

        if message.author.bot:
            return # also don't reply to itself or other bots 

        if message.content.startswith(bot_prefix):
            # @bot.command() doesn't seem to work for me, so i will do manually

            if message.content.lower() == (bot_prefix + 'reset') and bool(os.getenv('RESET_ENABLED')):
                try:
                    del turns[message.author.id]
                    await message.reply(os.getenv('RESET_SUCCESSFUL'))
                except:
                    await message.reply(os.getenv('RESET_FAILURE'))
                
                return
            elif message.content.lower() == (bot_prefix + 'about') and bool(os.getenv('ABOUT_ENABLED')):
                await message.reply(os.getenv('ABOUT_RESPONSE'))
                return

        # start typing to notify user somethings happening
        async with message.channel.typing():
            turns.setdefault(message.author.id, [])

            # A single turn is a group of user messages and bot responses right after
            turn = {
                'user_messages': [],
                'bot_messages': []
            }

            turns[message.author.id].append(turn)
            turn['bot_messages'].append(message.content)

            # Merge turns into a single prompt (don't forget delimiter)
            prompt = ""
            from_index = max(len(turns[message.author.id]) - max_turns_history - 1, 0) if max_turns_history >= 0 else 0
            for turn in turns[message.author.id][from_index:]:
                # Each turn begins with user messages
                for user_message in turn['user_messages']:
                    prompt += clean_text(user_message) + generation_pipeline.tokenizer.eos_token
                for bot_message in turn['bot_messages']:
                    prompt += clean_text(bot_message) + generation_pipeline.tokenizer.eos_token

            # Generate bot messages
            bot_messages = generate_responses(
                prompt,
                generation_pipeline,
                seed=seed,
                debug=debug,
                **generator_kwargs
            )
            if len(bot_messages) == 1:
                bot_message = bot_messages[0]
            else:
                bot_message = pick_best_response(
                    prompt,
                    bot_messages,
                    ranker_dict,
                    debug=debug
                )

        await message.reply(bot_message or os.getenv('GENERAL_FAILURE'))
        if bot_message:
            turn['bot_messages'].append(bot_message)
    
    bot.run(os.getenv("TOKEN"))