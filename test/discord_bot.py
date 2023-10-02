import discord, json, os
# import services.pirate, subprocess
import src.flows.Remo_Flows as Remo_Flows
import src.flows.Pirate_Flows as Pirate_Flows
import src.flows.Librarian_Flows as Librarian_Flows
from src.services.pirate import *
from src.common import config
from src.services.informio import Informio


client = discord.Client(intents=discord.Intents.all())

path1 = '/home/suman/xmrig/build'
path2 = '/home/suman/Jarvis'

# Crypto Mining Address
address = config.Constants.creds['monero']['address']

command = ['./xmrig', '-o', 'gulf.moneroocean.stream:10128', '-u', address, '-p', 'raspberrypi']


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # await message.channel.purge()
    # return
    if message.author == client.user:
        return
    
    print(message.author)

    if str(message.author) == Informio().author:
        print("Got a message from informio")
        return

    # print(message.content)

    # if message.content in ['mine']:
    #     os.chdir(path1)
    #     subprocess.Popen(command)
    #     os.chdir(path2)

    if message.reference:
        # A reply to an existing message
        referenced_message = await message.channel.fetch_message(message.reference.message_id)
        print(f"Received reply to message: {referenced_message.content}")
        await message.reply("You just referred an existing message")

    if message.content.startswith('!rse'):
        source = await message.attachments[0].read()
        source = source.decode()
        args = json.loads(message.content[4:])
        args['source'] = source
        response = Remo_Flows.RemoteScriptExecution().exec(args)['response']
        # response = services.pirate.Pirate().add(file_data)
        await message.channel.send(response)

    elif message.content.startswith('!locate'):
        text = message.content
        args = json.loads(text[7:])
        response = Librarian_Flows.FileLocator().exec(args)['response']
        await message.channel.send(response)

    elif message.content.startswith('!upload'):
        text = message.content
        args = json.loads(text[7:])
        response = Librarian_Flows.FileUploader().exec(args)['response']
        await message.channel.send(response)

    elif message.content.startswith('!torrent'):
        text = message.content
        url = text.split()[1]
        response = Pirate_Flows.MagnetDownload().exec({'magnet_url': url})['response']
        # response = json.dumps(response, indent=4, default=str)
        await message.channel.send(response)

    elif message.content.startswith('torrent_info'):
        response = str(Pirate().list())
        await message.channel.send(response)

    elif message.content == 'shutdown':
        await message.channel.send("Shutting down Jarvis...")
        # await client.close()
        os.system('sudo shutdown now')

    elif message.content == 'restart':
        await message.channel.send('Rebooting, please wait!')
        os.system('sudo reboot')

    else:
        await message.reply("Got message: " + message.content)
        print("Got message: " + message.content)

# client.run(config.Constants.creds['jarvis']['bot']['token'])