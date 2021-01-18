import discord
from discord.ext import commands
from random import randint
import json
import re
import smtplib
from email.mime.text import MIMEText
import secrets

with open('secrets.json') as f:
  data = json.load(f)

# logging into our email client
gmail_user = data['email']
gmail_password = data['password']

try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
except:
    print('Something went wrong...')

client = commands.Bot(command_prefix='!')
client.remove_command("help")

commands_list={
    "help": "`!help <command>`\nDisplays details about a specific command, or all commands if <command> field is empty",
    "flip": "`!flip`\nFlips a coin (heads or tails)",
    # "verify": "`!verify <Full Name>`\nVerifies you into the server if you are registered via the Google Form",
    "purge": "`!purge <limit>`\n**ADMIN ONLY!**\nDeletes a certain number of messages",
    "ping":"`!ping`\nDisplays latency in ms"
}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Unverified")
    await member.add_roles(role)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await client.process_commands(message)

# Commands

@client.command()
async def ping(ctx):
    await ctx.send(f"Latency: {round(client.latency * 1000)}ms")

@client.command()
async def flip(ctx):
    x=randint(0,1)
    messages=["HEADS\nhttps://tenor.com/view/champagne-heads-tails-heads-or-tails-coin-gif-13943298", "TAILS\nhttps://tenor.com/view/champagne-heads-tails-heads-or-tails-coin-gif-13943297"]
    await ctx.send(messages[x])

@client.command()
async def roll(ctx, arg):
    x=randint(1,int(arg))
    await ctx.send(f"You rolled a {x}")

@client.command()
@commands.has_role("Admin")
async def anon(ctx, *, arg):
    await ctx.message.delete()
    await ctx.send(arg)


# Thank you to Wahid Bawa for allowing me to use his code for this help menu
# View his code here: https://github.com/UWindsor-Robotics-Tech/UWin-Robotics-Robot/blob/master/robot/main.py
@client.command()
async def help(ctx, *, command=None):
    embed = discord.Embed(title="HELP", colour=0xcccc00)
    if command is None:
        for i in commands_list:
            embed.add_field(name=i, value=commands_list[i], inline=False)
    elif command in commands_list:
        embed.add_field(name=command, value=commands_list[command], inline=False)
    else:
        await ctx.send("This is not an existing command")
        return
    await ctx.send(embed=embed)


@client.command()
@commands.has_role("Admin")
async def purge(ctx, arg):
    await ctx.message.channel.purge(limit=int(arg))



@client.command()
async def verify(ctx, *, arg):
    email_addr = re.match(r'\w+@uwindsor.ca', arg)
    if email_addr:
        v_code = secrets.token_hex(7)
        address = email_addr.group()
        email_text = 'Your Verification Code is: '+v_code

        msg = MIMEText(email_text)
        msg['Subject'] = 'UWin Discord Verification Code'
        msg['From'] = gmail_user
        msg['To'] = address
        server.send_message(msg)
        # server.sendmail(gmail_user, address, email_text)
        # server.sendmail(gmail_user, address, 'email_text')
        await ctx.send(f'valid email: {address}')
        with open('users.txt', 'a') as f:
            f.write(f'{address},{v_code}\n')
    else:
        await ctx.send('invalid email')
    # if arg in col:
    #     role = discord.utils.get(ctx.guild.roles, name='Unverified')
    #     await ctx.message.author.remove_roles(role)
    #     role = discord.utils.get(ctx.guild.roles, name='Verified')
    #     await ctx.message.author.add_roles(role)
    #     await ctx.message.delete()

@client.command()
async def code(ctx, *, email, v_code):
    users = []
    with open('users.txt', 'r') as f:
        for i in f:
            i = i.strip()
            users.append(i.split(','))
    
    await ctx.send('h')


client.run(data['token'])