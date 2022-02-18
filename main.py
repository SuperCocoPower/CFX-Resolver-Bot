from os import system, name, path

try:
    import discord
    from requests import get
    from discord.ext import commands
    from datetime import datetime
    from json import loads
    from base64 import b64decode
except ModuleNotFoundError:
    system("pip install -r requirements.txt")
    exit()

try:
    config = loads(open("config.json", "r").read())
    int(config['cooldown'])
except:
    open("config.json", "w").write('{\n    "prefix": "+",\n    "cooldown": 10,\n    "token": ""\n}')
    print("Please configure the bot settings (config.json)")
    exit()

client = commands.Bot(command_prefix=config['prefix'])

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity = discord.Activity(type=discord.ActivityType.watching, name=f"{config['prefix']}help - AkaDevloppement"))
    print(f"""
           _____ ________   __ ______                _                
          /  __ \|  ___\ \ / / | ___ \              | |               
          | /  \/| |_   \ V /  | |_/ /___  ___  ___ | |_   _____ _ __ 
          | |    |  _|  /   \  |    // _ \/ __|/ _ \| \ \ / / _ \ '__|
          | \__/\| |   / /^\ \ | |\ \  __/\__ \ (_) | |\ V /  __/ |   
          \.____/\_|   \/   \/ \_| \_\___||___/\___/|_| \_/ \___|_|
                          
         The bot is actually logged in as {client.user.display_name} on {len(client.guilds)} guild(s).
                            The actual prefix is : {config['prefix']}
            
                     https://github.com/AkaDevloppement/""")

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		await ctx.reply(f"{ctx.message.author.mention} **Cooldown active**, you have to wait {round(error.retry_after)} seconds.", delete_after=int(round(error.retry_after)));return await ctx.message.delete()

@client.command(aliases=["cfx", "resolve"])
@commands.cooldown(1, int(config['cooldown']), commands.BucketType.user)
async def resolver(ctx, cfx):
    if "cfx.re/join/" not in cfx: 
        return
    if "https://" in str(cfx.lower()):
        cfx = str(cfx.lower()).split("https://")[1]

    embed = discord.Embed()
    embed.colour = 0x303135

    try:
        r = get(f"https://{cfx}")
        ownerinfo = get(f"https://servers-frontend.fivem.net/api/servers/single/{cfx.split('/')[2]}", headers={"Host": "servers-frontend.fivem.net","Connection": "keep-alive","sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',"Accept": "application/json, text/plain, */*","sec-ch-ua-mobile": "?0","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36","sec-ch-ua-platform": "Windows","Origin": "https://servers.fivem.net","Sec-Fetch-Site": "same-site","Sec-Fetch-Mode": "cors","Sec-Fetch-Dest": "empty","Referer": "https://servers.fivem.net/","Accept-Language": "fr-FR,fr;q=0.9","Accept-Encoding": "gzip, deflate",})
        if "Не найден." in r.text or '{"error": "404 Not Found"}' in ownerinfo.text:
            icon = False
        else:
            icon = True
        ip = str(r.headers['X-Citizenfx-Url'].split("/")[2])
    except:
        ip = "`Unable to connect`"

    embed.add_field(name="🌐 IP Address", value=f"`{ip}`")
    try:
        ip.split(':')[0]
    except:
        ipinfo = get(f"http://ip-api.com/json/{ip}?fields=66846719").json()
    else:
        ipinfo = get(f"http://ip-api.com/json/{ip.split(':')[0]}?fields=66846719").json()
    
    try:
        ipinfo['isp']
    except:
        embed.add_field(name="🖥 ISP", value=f"`Unknown`")
        embed.add_field(name="❓ Status", value="`❌ Failed`")
        embed.add_field(name="💻 Proxy ?", value=f"`Unknown`")
        embed.add_field(name="💾 Hosting ?", value=f"`Unknown`")
    else:
        embed.add_field(name="🖥 ISP", value=f"`{ipinfo['isp']}`")
        embed.add_field(name="❓ Status", value=(f"`✅ Success`" if ipinfo['status'] == "success" else "`❌ Failed`"))
        embed.add_field(name="💻 Proxy ?", value=f"`{ipinfo['proxy']}`")
        embed.add_field(name="💾 Hosting ?", value=f"`{ipinfo['hosting']}`")

    try: 
        dynamic = get(f"http://{ip}/dynamic.json", timeout=5) 
    except: 
        embed.add_field(name="⚠ Error", value="`An error has occurred while sending request to dynamic.json`", inline=False)
    else:
        embed.add_field(name="🌟 Slots", value=f"`{str(dynamic.json()['clients'])}/{str(dynamic.json()['sv_maxclients'])}`")
        embed.add_field(name="🗺 Mapname", value=(f"`{dynamic.json()['mapname']}`" if '"mapname":"' in dynamic.text and dynamic.json()['mapname'] != "" else "`Not Found`"))
        embed.add_field(name="🎮 Gametype", value=(f"`{dynamic.json()['gametype']}`" if '"gametype":"' in dynamic.text and dynamic.json()['gametype'] != "" else "`Not Found`"))

    try:
        info = get(f"http://{ip}/info.json", timeout=5)
    except:
        embed.add_field(name="⚠ Error", value="`An error has occurred while sending request to info.json`", inline=False)
    else:
        embed.title = info.json()['vars']['sv_projectName']
        embed.description = f"Description : `{info.json()['vars']['sv_projectDesc']}`\nOnline Players : http://{ip}/players.json"
        embed.add_field(name="🛡 Anti Cheat", value=(f"`{loads(info.text.lower())['vars']['anticheat']}`" if '"anticheat":"' in info.text.lower() else "`Not Found`"))
        embed.add_field(name="🔮 Discord", value=(f"`{loads(info.text.lower())['vars']['discord']}`" if '"discord":"' in info.text.lower() else "`Not Found`"))
        server_ressources = 0
        for _ in info.json()['resources']:
            server_ressources += 1
        embed.add_field(name="🛒 Ressources", value=f"`{server_ressources}`")
        embed.add_field(name="🐌 FiveM Version", value=f"`{info.json()['vars']['sv_enforceGameBuild']}`")
        embed.add_field(name="🎨 Tags", value=f"```{str(info.json()['vars']['tags']).replace(',', ', ')}```", inline=False)
        embed.add_field(name="⚙ Server File", value=f"`{info.json()['server']}`", inline=False)
        embed.set_image(url=(info.json()['vars']['banner_connecting'] if '"banner_connecting":"' in info.text else None))
        open(f"{ip.split(':')[0]}.png", "wb+").write(b64decode(info.json()['icon']))

    if icon == True:
        embed.set_author(name=f"{ownerinfo.json()['Data']['ownerName']}'s CFX Server", url=ownerinfo.json()['Data']['ownerProfile'], icon_url=f"attachment://{ip.split(':')[0]}.png")
    else:
        embed.set_author(name="Unknown CFX", url="https://github.com/AkaDevloppement", icon_url="https://avatars.githubusercontent.com/u/25160833?s=280&v=4")

    embed.timestamp = datetime.now()
    embed.set_footer(text="© 2022 ~ AkaDevloppement", icon_url="https://avatars.githubusercontent.com/u/82453396?v=4")

    await ctx.reply(file = (discord.File(f"{ip.split(':')[0]}.png") if icon == True else None), embed=embed)
    if path.isfile(f"{ip.split(':')[0]}.png"):
        system(f"del {ip.split(':')[0]}.png" if name == "nt" else f"rm -f {ip.split(':')[0]}.png")

@client.command(name="credits")
async def credits(ctx):
    embed = discord.Embed()
    embed.set_author(name="AkaDevloppement", url="https://github.com/AkaDevloppement", icon_url="https://cdn.discordapp.com/attachments/890460077692190720/931628740813918258/AkaGen.gif")
    embed.title = "Credits"
    embed.description = "**Github : https://github.com/AkaDevloppement**"
    embed.timestamp = datetime.utcnow()
    embed.colour = 0x303135
    embed.set_footer(text="© 2022 ~ AkaDevloppement", icon_url="https://avatars.githubusercontent.com/u/82453396?v=4")
    return await ctx.reply(embed=embed)

@client.command(name="pp")
@commands.cooldown(1, 5, commands.BucketType.user)
async def getuseravatarurl(ctx, *, member: discord.Member = None):
    if member is None:
        member = ctx.message.author
    embed = discord.Embed(colour=0x303135).set_author(name=member.name, url="https://github.com/AkaDevloppement", icon_url=member.avatar_url).set_image(url=member.avatar_url)
    return await ctx.send(embed=embed)  

client.remove_command(name="help")

@client.command(name="help")
async def credits(ctx):
    embed = discord.Embed()
    embed.set_author(name="AkaDevloppement", url="https://github.com/AkaDevloppement", icon_url="https://cdn.discordapp.com/attachments/890460077692190720/931628740813918258/AkaGen.gif")
    embed.title = "Somone need help ?"
    embed.description = f"**{config['prefix']}cfx `<cfx_url>`**: resolve a CFX link (Alias: {config['prefix']}resolve)\n**{config['prefix']}pp `<memberID/ping>`** returns you the profile picture of the precised member.\n**{config['prefix']}credits**: bot credits"
    embed.colour = 0x303135
    embed.timestamp = datetime.utcnow()
    embed.set_footer(text="© 2022 ~ AkaDevloppement", icon_url="https://avatars.githubusercontent.com/u/82453396?v=4")
    return await ctx.reply(embed=embed)

client.run(config['token'])