# Discord modules
from discord.ext import commands
from discord import Embed, Game, Guild
import discord

# APIs
from APIs.discordBotAPI import BotAssist

# Built ins
import aiohttp
from configparser import ConfigParser
import datetime
import io
from sys import exit as ex
from sys import argv
from os import path

# Delete after production
import time

#####################################################################################################################
                                             # Set up the environment 
#####################################################################################################################
# Look for either the dev or live switch
if len(argv) == 2:
    if argv[-1] == "--live":
        botMode = "liveBot"
    elif argv[-1] == "--dev":
        botMode = "devBot"
    else:
        ex("\n[ERROR] Make sure to add the right switch to activate me.")
else:
    ex("\n[ERROR] Make sure to add the right switch to activate me.")

config = ConfigParser(allow_no_value=True)
emoticons = ConfigParser(allow_no_value=True)

if botMode == "liveBot":
    configLoc = 'KittyLitterConfig.ini'
    emoticonLoc = '/'
    if path.exists(configLoc):
        pass
    else:
        ex(f"Config file does not exist: {configLoc}")
    config.read(configLoc)
    emoticons.read(emoticonLoc)
    discord_client = commands.Bot(command_prefix = f"{config[botMode]['bot_prefix']}")
    discord_client.remove_command("help")

elif botMode == "devBot":
    configLoc = 'KittyLitterConfig.ini'
    emoticonLoc = 'CoC_APIs/emoticons.ini'
    if path.exists(configLoc):
        pass
    else:
        ex(f"Config file does not exist: {configLoc}")
    config.read(configLoc)
    emoticons.read(emoticonLoc)
    discord_client = commands.Bot(command_prefix = f"{config[botMode]['bot_prefix']}")
    discord_client.remove_command("help")

# Instanciate botAssit and DB
botAPI = BotAssist(botMode, configLoc)
# coc_client = ClashConnectAPI(config['Clash']['ZuluClash_Token'])

#####################################################################################################################
                                             # Discord Commands [info]
#####################################################################################################################
@discord_client.event
async def on_ready():
    """
    Simple funciton to display logged in data to terminal 
    """
    print(f'\n\nLogged in as: {discord_client.user.name} - {discord_client.user.id}\nDiscord Version: {discord.__version__}\n'
        f"\nRunning in [{botMode}] mode\n"
        "------------------------------------------\n"
        f"Prefix set to:          {config[botMode]['bot_Prefix']}\n"
        f"Config file set to:     {configLoc}\n"
        f"DB File set to:         None\n"
        "------------------------------------------")

    game = Game(config[botMode]['game_msg'])
    await discord_client.change_presence(status=discord.Status.online, activity=game)

#####################################################################################################################
                                             # Help Menu
#####################################################################################################################
@discord_client.command()
async def help(ctx, *option):
    pref = config[botMode]['bot_prefix']
    # Commands
    kill = (f"Send terminate singnal to bot to save memory contents to disc followed by a shut down\n "
        "\n\nKittyLitter Version 2.4\nhttps://github.com/majordoobie/KittyLitterBot2")
    archive = (f"Scan channels under category argument provided for new messages. If "
        "new messages are found - copy all contents to the mapped archive channel. See "
        "setup to configure archive channels")
    purge = (f"Scan channels under category argument provided for new messages. If "
        "new messages are found - delete all contents and apply new welcome message")
    helper = (f"Add or remove @Helper role to yourself or another user.\n**[Examples]**\n "
        f"{pref}helper --add\n{pref}helper --add <@mention>\n{pref}helper --remove\n{pref}helper --remove <@mention>\n{pref}helper --list")

    readconfig = (f"Read current configuration file.")

    setup = (f"Set up mapping or roles. Mappings is the channel you would like the bot to "
        "send archives to. Roles is specifying which Reddit Zulu roles you would "
        f"like the bot to sync with this server.\n**[Examples]**\n{pref}setup --mapping\n{pref}setup --roles")
    sync = (f"Sync Reddit Zulu server data with this server - limited to the Roles configuration")
    
    muster = (f"Display the current roster in three categories. Those with CoC Members Role, those who are bots and those who do not have "
        "the CoC Members role")
    autopur = (f"Combines the archive and purge commands into one.")
    help = (f"Show this help menu.\n**[Examples]**\n{pref}help --verbose")
    if len(option) == 0:
        embed = Embed(title='Meowwww!', description="Quick view of commands:" ,color=0x8A2BE2)
        embed.add_field(name=f"{pref}help [*options]", value=help, inline=False)
        embed.add_field(name=f"{pref}setup [*options]", value=setup, inline=False)
        embed.add_field(name=f"{pref}helper [*options]", value=helper, inline=False)
        embed.add_field(name=f"{pref}muster", value=muster, inline=False)
        embed.add_field(name=f"{pref}sync", value=sync, inline=False)
        embed.add_field(name=f"{pref}readconfig", value=readconfig, inline=False)
        embed.add_field(name=f"{pref}archive <#Category>", value=archive, inline=False)
        embed.add_field(name=f"{pref}purge <#Category>", value=purge, inline=False)
        embed.add_field(name=f"{autopur}autopurge <#Category>", value=autopur, inline=False)
        embed.add_field(name=f"{pref}killswitch", value=kill, inline=False)
        
        await ctx.send(embed=embed)
        return
    elif option[0] == "--verbose":
        desc1 = ("Thank you for using KittyLitter. KittyLitter conducts 3 main functions: "
            "archive/purge channels, sync roles and nicknames between Reddit Zulu and Zulu Base "
            "Planning (ZBP) and finally ping Reddit Zulu when a user in ZBP is requesting help in ZBP. "
            "Archiving and Purging channels were the original and sole functions of KittyLitter. The "
            "idea was to always have a clean channel every time a new war started. The problem with "
            "just purging a channel is that often times those old plans on previous wars would provide "
            "insight to our new enemies. Therefore, KittyLitter began to archive each war with the plans "
            "our members came up with and allowed our members to look through the archives to find old plans. ")
        desc2 = ("Syncing roles and nicknames is a new function that was introduced in version 2 of KittyLitter. "
            "Before KittyLitter, an admin would have to go through each user in ZBP to make sure they had "
            "up-to-date roles. This made it unreliable to ping th# or CWL since admins are constantly "
            "busy working on higher priority tasks. KittyLitter now performs these functions on the admin's "
            "behalf. Another addition to syncing roles is the ability for anyone to request the @Helper role. "
            "The @Helper role is used to ping volunteers in Reddit Zulu who are traditionally strong attackers "
            "with up to date knowledge of current metas for help.\n")

        desc3 = ("Finally, KittyLitter will monitor all war chats for the @Helper, @Zulu CWL, and @Elephino CWL mentions. "
            "This will then ping #war-current-war, #zulu-war-room, and #elephino-war-room respectively with a little "
            "reminder that there is a member requesting help in ZBP. The reminder contains the user name requesting "
            "along with the channel they are requesting form.\n\n"
            "[HISTORY]\n"
            "**[Version 2.1]**\n"
            "[update] muster function to see members in this server who no longer have CoC Members Role\n"
            "**[Version 2.0]**\n"
            "[update]  Changed purge/archive behavior. Instead of purging/archiving, all the bot will only act on channels that have any new messages.\n"
            "[update] Add/Remove Helper role\n"
            "[update] Global Reddit Zulu Role and Nickname sync\n"
            "[update] On server join: welcome new users and sync their profile with Reddit Zulu\n"
            "[update] Identity users missing in Zulu Base Planning\n"
            "[update] Ping Reddit Zulu server when user mentions @helper in Zulu Base Planning\n"
            "[bug-fix] Replaced searching functions with generators to speed up functions")
            
        await ctx.send(embed=Embed(title='Meowwww!', description=desc1 ,color=0x8A2BE2))
        await ctx.send(embed=Embed(description=desc2 ,color=0x8A2BE2))
        await ctx.send(embed = Embed( description=desc3 ,color=0x8A2BE2))
        embed = Embed(Title="Verbose output" ,color=0x8A2BE2)
        embed.add_field(name=f"{pref}help [*options]", value=help, inline=False)
        embed.add_field(name=f"{pref}setup [*options]", value=setup, inline=False)
        embed.add_field(name=f"{pref}helper [*options]", value=helper, inline=False)
        embed.add_field(name=f"{pref}sync", value=sync, inline=False)
        embed.add_field(name=f"{pref}readconfig", value=readconfig, inline=False)
        embed.add_field(name=f"{pref}archive <#Category>", value=archive, inline=False)
        embed.add_field(name=f"{pref}purge <#Category>", value=purge, inline=False)
        embed.add_field(name=f"{pref}killswitch", value=kill, inline=False)
        
        await ctx.send(embed=embed)
        return

#####################################################################################################################
                                             # Commands
#####################################################################################################################
@discord_client.event
async def on_member_join(pmember):
    if int(pmember.guild.id) == int(config['Discord']['plandisc_id']):
        channel = pmember.guild.get_channel(int(config['Discord']['welcome']))
        msg = (f"Welcome to Zulu Base Planning server, {pmember.mention}! "
        f"I will begin to sync your profile with Reddit Zulu, meantime please make your "
        "way to the ` #instruction-board ` to get a feel for how this server works.")
        await channel.send(msg)

        await channel.send("Syncing user... ")
        zbpRoles = [ (k,v) for k,v in config['roles'].items() ]
        zuluGuild = discord_client.get_guild(int(config['Discord']['zuludisc_id']))
        zmember = zuluGuild.get_member(pmember.id)

        if zmember == None:
            desc = f"Looks like you're not in the Reddit Zulu server"
            await channel.send(embed = discord.Embed(title="SYNC FAILURE", description=desc, color=0xFF0000))
            return
        
        if pmember.display_name != zmember.display_name:
            try:
                await pmember.edit(nick=zmember.display_name, reason="KittyLitter bot on Join function @sgtmajordoobie")
                await channel.send(f"[+] Nickname Synced")
            except discord.Forbidden:
                await channel.send(f"[-] Nickname Sync Failed: Elevated perms required")
        else:
            await channel.send(f"[+] Nickname Synced")

        roleStaging = []
        for role in zmember.roles:
            if role.name.lower() in ( roleTupe[0].lower() for roleTupe in zbpRoles ):
                result = next(( roleTupe[1] for roleTupe in zbpRoles if roleTupe[0].lower() == role.name.lower() ))
                roleObj = pmember.guild.get_role(int(result))
                roleStaging.append(roleObj)
            else:
                pass
        
        if str(pmember.id) in config['helpers']:
            roleObj = pmember.guild.get_role(int(config['Discord']['helper_id']))
            roleStaging.append(roleObj)
            
        try:
            await pmember.edit(roles=roleStaging, reason = "KittyLitter bot on Join function @sgtmajordoobie")
            await channel.send(f"[+] Roles Synced")
        except discord.Forbidden:
            await channel.send(f"[-] Role Sync Failed: Elevated perms required")

        msg = (f"You are ready to rock {pmember.mention}!")
        await channel.send(msg)

@discord_client.command()
async def kill(ctx):
    if botAPI.rightServer(ctx, config):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{botAPI.serverSettings(ctx, config, discord_client)}```")
        return

    if botAPI.authorized(ctx, config):
        await ctx.send("Tearing down, please hold.")
        await ctx.send("Closing config file")
        with open(configLoc, 'w') as f:
                config.write(f)
        await ctx.send("Terminating bot..")
        await ctx.send("_Later._")
        await discord_client.logout()
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

@discord_client.command()
async def muster(ctx):
    if botAPI.rightServer(ctx, config):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{botAPI.serverSettings(ctx, config, discord_client)}```")
        return
    if botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

    zuluGuild = discord_client.get_guild(int(config['Discord']['zuludisc_id']))
    present = [ mem.id for mem in zuluGuild.members if 'CoC Members' in (rol.name for rol in mem.roles) ]

    members = []
    nonmembers = []
    bots = []
    for member in ctx.guild.members:
        if member.id in present:
            members.append(member.display_name)
        elif 'bots bots bots' in (role.name for role in member.roles):
            bots.append(member.display_name)
        else:
            nonmembers.append(member.display_name)

    members.sort(key=lambda x: x.lower())
    nonmembers.sort(key=lambda x: x.lower())
    output = "# Members with CoC Member Role\n\n"
    for member in members:
        output += (f"{member}\n")

    output += (f"\n\n# Bots\n\n")
    for member in bots:
        output += (f"{member}\n")

    output += (f"\n\n# Members in this server without Members Role\n\n")
    for member in nonmembers:
        output += (f"{member}\n")

    await ctx.send(f"```\n{output}\n```")
    

@discord_client.command()
async def helper(ctx, action, *mention):
    if action.lower() not in ['--add', '--remove', '--list']:
        desc = f"Invalid argument provided. Please use {config[botMode]['bot_prefix']}help"
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        return
    
    if action == '--list':
        output = "Current Helpers\n"
        for k,v in config['helpers'].items():
            output += (f"{v}\n")
        await ctx.send(f"```{output}```")
        return

    if len(mention) == 0:
        if action == '--add':
            userObj = ctx.message.author
            if str(userObj.id) in config['helpers']:
                if "Helpers" in (role.name for role in userObj.roles):
                    await ctx.send(f"You're already a helper")
                    return
            else:
                try:
                    await userObj.add_roles(ctx.guild.get_role(int(config['Discord']['helper_id'])))
                    await ctx.send(f"[+] Helper role added")

                    config.set('helpers', f"{str(userObj.id)}", f"{str(userObj.display_name)}")
                    with open(configLoc, 'w') as configFile:
                        config.write(configFile)
                    return
                except discord.Forbidden:
                    await ctx.send(f"[-] Role Sync Failed: Elevated perms required")
                    return

        elif action == '--remove':
            userObj = ctx.message.author
            if str(userObj.id) not in config['helpers']:
                if "Helpers" in (role.name for role in userObj.roles):
                    await ctx.send(f"You don't have the role")
                    return
            else:
                try:
                    await userObj.remove_roles(ctx.guild.get_role(int(config['Discord']['helper_id'])))
                    await ctx.send(f"[+] Helper role removed")

                    config.remove_option('helpers', f"{userObj.id}")
                    with open(configLoc, 'w') as configFile:
                        config.write(configFile)
                    return
                except discord.Forbidden:
                    await ctx.send(f"[-] Role Sync Failed: Elevated perms required")
                    return

    elif len(mention) == 1:
        if botAPI.rightServer(ctx, config):
            pass
        else:
            desc = f"You are attempting to run a command destined for another server."
            await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
            await ctx.send(f"```{botAPI.serverSettings(ctx, config, discord_client)}```")
            return
        if botAPI.authorized(ctx, config):
            pass
        else:
            await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
            return
        if mention[0].startswith("<") == False:
            msg = (f"Could not interpret the {mention} argument. Make sure "
            "that you are mentioning the user such as @user")
            await ctx.send(embed=Embed(title=msg, color=0xff0000))
            return

        member_ID = ''.join(list(mention[0])[2:-1])
        if member_ID.startswith("!"):
            mention = member_ID[1:]
        else:
            mention = member_ID

        userObj = ctx.guild.get_member(int(mention))
        if userObj == None:
            await ctx.send(f"{mention} was not found in this server")
            return

        if action == '--add':
            if str(userObj.id) in config['helpers']:
                if "Helpers" in (role.name for role in userObj.roles):
                    await ctx.send(f"{userObj.display_name} already a helper")
                    return
            else:
                try:
                    await userObj.add_roles(ctx.guild.get_role(int(config['Discord']['helper_id'])))
                    await ctx.send(f"[+] {userObj.display_name}: Helper role added")

                    config.set('helpers', f"{userObj.id}", f"{str(userObj.display_name)}")
                    with open(configLoc, 'w') as configFile:
                        config.write(configFile)
                    return
                except discord.Forbidden:
                    await ctx.send(f"[-] Role Sync Failed: Elevated perms required")
                    return
        elif action == '--remove':
            if str(userObj.id) not in config['helpers']:
                if "Helpers" in (role.name for role in userObj.roles):
                    await ctx.send(f"{userObj.display_name} does not have the role")
                    return
            else:
                try:
                    await userObj.remove_roles(ctx.guild.get_role(int(config['Discord']['helper_id'])))
                    await ctx.send(f"[+] {userObj.display_name}: Helper role removed")
                    config.remove_option('helpers', f"{userObj.id}")
                    with open(configLoc, 'w') as configFile:
                        config.write(configFile)
                    return
                except discord.Forbidden:
                    await ctx.send(f"[-] Role Sync Failed: Elevated perms required")
                    return

    else:
        await ctx.send("Invalid arguments provided")
        return



        
@discord_client.command()
async def setup(ctx, *option):
    if botAPI.rightServer(ctx, config):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{botAPI.serverSettings(ctx, config, discord_client)}```")
        return
    if botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

    if option:
        pass
    else:
        desc = (f"Missing arguments")
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        return

    option = ' '.join(option).lower()
    if option in ["--mapping", "--roles"]:
        pass
    else:
        desc = (f"Invalid argument used")
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        return

    if option == "--mapping":
        inConfig = [ i for i in config['archive_mapping'] ]
        categories = [ (i.name.upper(), i.id) for i in ctx.guild.categories if i.name != "ARCHIVES" ]
        archives = []
        for i in ctx.guild.categories:
            if i.name.upper() == "ARCHIVES":
                for channel in i.channels:
                    archives.append((channel.name.upper(), channel.id))

        if inConfig:
            c = "Category"
            a = "Archive"
            output = f'{c:<15}-- --{a:>15}\n'
            for k,v in config['archive_mapping'].items():
                key = discord_client.get_channel(int(k)).name
                val = discord_client.get_channel(int(v)).name
                output += (f"{key:<15} > {val}\n")
        else:
            output = "Not configuration mapping set."
        await ctx.send(f"*Current category to archive channel mapping:*\n```{output}```")
        
        await ctx.send("Would you like to edit the category to archive mapping?\n(Yes/No)")
        msg = await discord_client.wait_for('message', check = botAPI.yesno_check)
        if msg.content.lower() == "no":
            await ctx.send(f"Exiting function")
            return
        await ctx.send("\n\n[-] Clearing mapping list")
        for i in config['archive_mapping']:
            config.remove_option('archive_mapping', str(i))
        with open(configLoc, "w", encoding='utf-8')as configFile:
            config.write(configFile)
        await ctx.send("[+] Done")
        
        for category in categories:
            await ctx.send(f"\n\nPick an archive channel to map to the category: {category[0]}")
            output = ''
            for index, archive in enumerate(archives):
                output += (f"[{index:>2}] {archive[0]}\n")
            output += "[ q] Quit"
            await ctx.send(f"```{output}```")
            num = False
            while num == False:
                msg = await discord_client.wait_for('message')
                if msg.content.lower() in ['q', 'quiz']:
                    await ctx.send("Exiting.")
                    return
                elif msg.content.isdigit():
                    if int(msg.content) in range(0, len(archives)):
                        await ctx.send(f"```Mapping {category[0]} -> {archives[int(msg.content)][0]}```")
                        config.set('archive_mapping', str(category[1]), str(archives[int(msg.content)][1]))
                        archives.pop(int(msg.content))
                        num = True
                        break
                await ctx.send("Either the input is not a integer or integer is out of range.")
            # <class 'discord.channel.CategoryChannel'>
            # <class 'discord.channel.TextChannel'>
        c = "Category"
        a = "Archive"
        output = f'{c:<15}-- --{a:>15}\n'
        for k,v in config['archive_mapping'].items():
            key = discord_client.get_channel(int(k)).name
            val = discord_client.get_channel(int(v)).name
            output += (f"{key:<15} > {val}\n")
        await ctx.send(f"```{output}```")
        await ctx.send("Would you like to save these settings?\n(Yes/No)")
        msg = await discord_client.wait_for('message', check = botAPI.yesno_check)
        if msg.content.lower() == 'no':
            await ctx.send("[-] Discarding changes")
            for i in config['archive_mapping']:
                config.remove_option('archive_mapping', str(i))
            await ctx.send("[+] Done")
            return
        await ctx.send("[-] Saving changes")
        with open(configLoc, 'w', encoding='utf-8') as configFile:
            config.write(configFile)
        await ctx.send("[+] Done")
        return

    elif option == "--roles":

        await ctx.send(f"Role config--")
        r = "Roles"
        output = f'{r}\n'
        for role in config['roles']:
            output += f"{role}\n"
        await ctx.send(f"```{output}```")
        await ctx.send("Would you like to edit the configuration above?\n(Yes/No)")
        msg = await discord_client.wait_for('message', check = botAPI.yesno_check)
        if msg.content.lower() == "no":
            await ctx.send(f"Exiting function")
            return
        await ctx.send("\n\n[-] Clearing roles list")
        for i in config['roles']:
            config.remove_option('roles', str(i))
        with open(configLoc, "w", encoding='utf-8')as configFile:
            config.write(configFile)
        await ctx.send("[+] Done\nStandby, loading Reddit Zulus roles")

        zuluGuild = discord_client.get_guild(int(config['Discord']['zuludisc_id']))
        output = ''
        for index, role in enumerate(zuluGuild.roles):
            output += (f"[{index:<2}] {role.name}\n")
        output += (f"[ q] Quit\n")
        await ctx.send(f"```{output}```")

        await ctx.send(f"Please type the index that represents the role you would like "
            "the Zulu Base Planning server to mimic from the Reddit Zulu server. Your entry "
            "should be integers only and space seperated.")

        msg = await discord_client.wait_for('message')
        if msg.content.lower() in ['q', 'quiz']:
            await ctx.send("Exiting funciton")
            return
        
        length = len(zuluGuild.roles)
        selections = msg.content.split(' ')
        for selection in selections:
            if selection.isdigit():
                if int(selection) in range(0, length):
                    pass
                else:
                    err = (f"One of your values is out of range of the list provided")
                    await ctx.send(embed = discord.Embed(title="ERROR", description=err, color=0xFF0000))
                    return
            else:
                err = (f"Values provided must be integers, or a single q")
                await ctx.send(embed = discord.Embed(title="ERROR", description=err, color=0xFF0000))
                return

        output = f'{r:^15}:\n'
        for selection in selections:
            output += f"[{selection:>2}] {(zuluGuild.roles[int(selection)].name)}\n"
        await ctx.send(f"```{output}```\nWould you like to keep your selection above?\n(Yes/No)")
        msg = await discord_client.wait_for('message', check = botAPI.yesno_check)
        if msg.content.lower() == "no":
            await ctx.send(f"Exiting function")
            return
        
        roles_configured = []
        for selection in selections:
            roles_configured.append(zuluGuild.roles[int(selection)].name)

        created = []    # roles already in the server
        create = []     # roles that need to be created
        for role in ctx.guild.roles:
            if role.name in roles_configured:
                created.append((role.name, role.id))
        
        for role in roles_configured:
            if role not in ( tupe[0] for tupe in created ):
                create.append(role)

        output = "Roles already created:\n"
        for role in created:
            output += f"{role[1]:<18} {role[0]}\n"
        output += f"\n\nRoles waiting to be created:\n"
        for role in create:
            output += f"{role}\n"
        await ctx.send(f"```{output}```")

        await ctx.send(f"Creating roles identified above, standby..")
        msg = "Created by KittyLitter sync function"
        for role in create:
            result = await ctx.guild.create_role(name=role, mentionable=True, reason=msg)
            if isinstance(result, discord.Role):
                await ctx.send(f"[+] Successfully created {role}")
                created.append((result.name, result.id))
            else:
                await ctx.send(f"[-] Unable to create {role}. Have I been given permission to do so?")

        output = "Configuration result\n"
        for role in created:
            output += f"{role[1]:<18} {role[0]}\n"
        await ctx.send(f"Would you like to save the configuration above?\n(Yes/No)")
        msg = await discord_client.wait_for('message', check = botAPI.yesno_check)
        if msg.content.lower() == "no":
            await ctx.send(f"Exiting function")
            return
        await ctx.send("\n\n[-] Saving configuration")
        for i in created:
            config.set('roles', i[0], str(i[1]) )
        with open(configLoc, "w", encoding='utf-8')as configFile:
            config.write(configFile)
        await ctx.send("[+] Done")    
    



@discord_client.command()
async def archive(ctx, *category):
    if category:
        pass
    else:
        await ctx.send(embed = discord.Embed(title="ERROR", description="Category is a mandatory argument.", color=0xFF0000))
        return
    if botAPI.rightServer(ctx, config):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{botAPI.serverSettings(ctx, config, discord_client)}```")
        return

    if botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

    category = ' '.join(category).upper()
    for i in ctx.guild.categories:
        if i.name.upper() != "ARCHIVES":
            if category == i.name.upper():
                category = ((i.name, i.id))
    
    if str(category[1]) in config['archive_mapping'].keys():
        for cat, tar in config['archive_mapping'].items():
            if str(category[1]) == cat:
                source_category = discord_client.get_channel(int(cat))
                dest_channel = discord_client.get_channel(int(tar))
    else:
        msg = (f"The category [{category[0]}] does not exist or it is not configured.")
        await ctx.send(embed = discord.Embed(title="INPUT ERROR", description=msg, color=0xFF0000))
        return

    activity = discord.Activity(type = discord.ActivityType.watching, name="channels get archived")
    await discord_client.change_presence(status=discord.Status.dnd, activity=activity)

    async with ctx.typing():
        for channel in source_category.channels:
            await ctx.send(f"Archiveing {channel.name}")
            if len(await channel.history(limit=3).flatten()) < 2:
                continue

            #await dest_channel.send(f"Starting archive from {channel.name}")
            msg = (f"Starting archive from {channel.name}")
            await dest_channel.send(embed = discord.Embed(title=msg, color=0x00FFFF))
            async for message in channel.history(limit=10000, reverse = True, after = datetime.datetime.utcnow() - datetime.timedelta(days=50)):
                if int(message.author.id) in [513291454349836289, 515978655978094603]:
                    continue
                send_message = (f"**[{message.author.display_name}]** {message.clean_content}")
                files = []
                try:
                    if message.attachments:
                        async with aiohttp.ClientSession() as session:
                            for attachment_obj in message.attachments:
                                async with session.get(attachment_obj.url) as resp:
                                    buffer = io.BytesIO(await resp.read())
                                    files.append(discord.File(fp=buffer, filename=attachment_obj.filename))
                    files = files or None
                    await dest_channel.send(send_message, files=files)
                except Exception as e:
                    msg = f"Could not archive the following message:\n{e}\n{e.args}\nMessage ID: {message.id}"
                    await dest_channel.send(msg)

    await ctx.send("All done!")
    game = Game(config[botMode]['game_msg'])
    await discord_client.change_presence(status=discord.Status.online, activity=game)


@archive.error
async def info_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def purge(ctx, *category):
    if category:
        pass
    else:
        await ctx.send(embed = discord.Embed(title="ERROR", description="Category is a mandatory argument.", color=0xFF0000))
        return
    if botAPI.rightServer(ctx, config):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{botAPI.serverSettings(ctx, config, discord_client)}```")
        return

    if botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

    exists = False
    category = ' '.join(category).upper()
    for i in ctx.guild.categories:
        if i.name.upper() != "ARCHIVES":
            if category == i.name.upper():
                exists = True
                category = ((i.name, i.id))

    if exists == False:
        ctx.send(f"Could not find {category}")
        return

    desc = (f"I will now begin to purge {category[0]}. Please be sure to have had "
        "archived the files before continuing. This can not be undone! Would you like "
        "to proceed?\n\n\nPlease Type: KittyLitterBot")
    await ctx.send(embed = Embed(title='WARNING!', description= desc, color=0xFF0000)) 
    msg = await discord_client.wait_for('message')
    if msg.content != 'KittyLitterBot':
        await ctx.send("You seem unsure. Going to abort.")
        return
    else:
        pass

    cwl = False
    if category[1] == 530386718084562955: #elephino
        cwl = True
        ping = "@Elephino CWL"
        ping_desc = ("Use @Elephino CWL to ping members who are also participating in your CWL team.")
    elif category[1] == 511742081056899084: #zulu cwl
        cwl = True
        ping = "@Zulu CWL"
        ping_desc = ("Use @Zulu CWL to ping members who are also participating in your CWL team.") 

    desc = ("Please use this channel to plan your attacks. To do so, paste a screenshot of the enemy base "
        "that you are considering attacking. Then comment on how you plan to attack the enemy base. For best "
        "results, use an image annotation app to include arrows and shapes in your screenshot.")
    
    desc_Helper = ("Use @Helpers to ping users who have volunteered to help. These are often times "
        "attack experts who are willing to help look over your plan. Want to become a helper?! See "
        "#instruction-board! to findout how!")

    desc_TH =("Alternatively you can use the @TH# mention to get advice from folks in your own townhall level.")
    desc_leader=("Lastly, if those two fail you can always mention our leaders with @CoC Leadership")
    newchannel = Embed(title='WELCOME!', description= desc, color=0x8A2BE2)
    newchannel.add_field(name="@Helpers", value=desc_Helper, inline=False)
    if cwl:
        newchannel.add_field(name=ping, value=ping_desc, inline=False)
    newchannel.add_field(name="@TH#s", value=desc_TH, inline=False)
    newchannel.add_field(name="@CoC Leadership", value=desc_leader, inline=False)

    activity = discord.Activity(type = discord.ActivityType.watching, name="messages get nuked")
    await discord_client.change_presence(status=discord.Status.dnd, activity=activity)
    catObj = discord_client.get_channel(int(category[1]))
    await ctx.send(f"Purging {category[0]}")
    async with ctx.typing():
        for channel in catObj.channels:
            if len(await channel.history(limit=3).flatten()) == 1:
                continue
            while len(await channel.history(limit=1).flatten()) != 0:
                deleted = await channel.purge(bulk=True)
                await ctx.send(f"Deleted {len(deleted)} message(s) from {channel.name}")
            await channel.send(embed=newchannel)

    game = discord.Game("with cat nip~")
    await discord_client.change_presence(status=discord.Status.online, activity=game)                       
    await ctx.send("All done!")
    return

@purge.error
async def purge_error(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def autopurge(ctx, *category):
    if category:
        pass
    else:
        await ctx.send(embed = discord.Embed(title="ERROR", description="Category is a mandatory argument.", color=0xFF0000))
        return
    if botAPI.rightServer(ctx, config):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{botAPI.serverSettings(ctx, config, discord_client)}```")
        return

    if botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

    category = ' '.join(category).upper()
    for i in ctx.guild.categories:
        if i.name.upper() != "ARCHIVES":
            if category == i.name.upper():
                category = ((i.name, i.id))
    
    if str(category[1]) in config['archive_mapping'].keys():
        for cat, tar in config['archive_mapping'].items():
            if str(category[1]) == cat:
                source_category = discord_client.get_channel(int(cat))
                dest_channel = discord_client.get_channel(int(tar))
    else:
        msg = (f"The category [{category[0]}] does not exist or it is not configured.")
        await ctx.send(embed = discord.Embed(title="INPUT ERROR", description=msg, color=0xFF0000))
        return

    # Send warning
    desc = (f"I will now begin to purge {category[0]}. Please be sure to have had "
        "archived the files before continuing. This can not be undone! Would you like "
        "to proceed?\n\n\nPlease Type: KittyLitterBot")
    await ctx.send(embed = Embed(title='WARNING!', description= desc, color=0xFF0000)) 
    msg = await discord_client.wait_for('message')
    if msg.content != 'KittyLitterBot':
        await ctx.send("You seem unsure. Going to abort.")
        return
    else:
        pass


    activity = discord.Activity(type = discord.ActivityType.watching, name="channels get archived")
    await discord_client.change_presence(status=discord.Status.dnd, activity=activity)

    async with ctx.typing():
        for channel in source_category.channels:
            await ctx.send(f"Archiveing {channel.name}")
            if len(await channel.history(limit=3).flatten()) < 2:
                continue

            #await dest_channel.send(f"Starting archive from {channel.name}")
            msg = (f"Starting archive from {channel.name}")
            await dest_channel.send(embed = discord.Embed(title=msg, color=0x00FFFF))
            async for message in channel.history(limit=10000, reverse = True, after = datetime.datetime.utcnow() - datetime.timedelta(days=50)):
                if int(message.author.id) in [513291454349836289, 515978655978094603]:
                    continue
                send_message = (f"**[{message.author.display_name}]** {message.clean_content}")
                files = []
                try:
                    if message.attachments:
                        async with aiohttp.ClientSession() as session:
                            for attachment_obj in message.attachments:
                                async with session.get(attachment_obj.url) as resp:
                                    buffer = io.BytesIO(await resp.read())
                                    files.append(discord.File(fp=buffer, filename=attachment_obj.filename))
                    files = files or None
                    await dest_channel.send(send_message, files=files)
                except Exception as e:
                    msg = f"{e}\n{e.args}\eMessage ID: {message.id}"
                    await dest_channel.send(msg)

    await ctx.send("\n\nAll done!\nWill not start to purge the channels.")
    game = Game(config[botMode]['game_msg'])
    await discord_client.change_presence(status=discord.Status.online, activity=game)

    cwl = False
    if category[1] == 530386718084562955: #elephino
        cwl = True
        ping = "@Elephino CWL"
        ping_desc = ("Use @Elephino CWL to ping members who are also participating in your CWL team.")
    elif category[1] == 511742081056899084: #zulu cwl
        cwl = True
        ping = "@Zulu CWL"
        ping_desc = ("Use @Zulu CWL to ping members who are also participating in your CWL team.") 

    desc = ("Please use this channel to plan your attacks. To do so, paste a screenshot of the enemy base "
        "that you are considering attacking. Then comment on how you plan to attack the enemy base. For best "
        "results, use an image annotation app to include arrows and shapes in your screenshot.")
    
    desc_Helper = ("Use @Helpers to ping users who have volunteered to help. These are often times "
        "attack experts who are willing to help look over your plan. Want to become a helper?! See "
        "#instruction-board! to findout how!")

    desc_TH =("Alternatively you can use the @TH# mention to get advice from folks in your own townhall level.")
    desc_leader=("Lastly, if those two fail you can always mention our leaders with @CoC Leadership")
    newchannel = Embed(title='WELCOME!', description= desc, color=0x8A2BE2)
    newchannel.add_field(name="@Helpers", value=desc_Helper, inline=False)
    if cwl:
        newchannel.add_field(name=ping, value=ping_desc, inline=False)
    newchannel.add_field(name="@TH#s", value=desc_TH, inline=False)
    newchannel.add_field(name="@CoC Leadership", value=desc_leader, inline=False)

    activity = discord.Activity(type = discord.ActivityType.watching, name="messages get nuked")
    await discord_client.change_presence(status=discord.Status.dnd, activity=activity)
    catObj = discord_client.get_channel(int(category[1]))
    await ctx.send(f"Purging {category[0]}")
    async with ctx.typing():
        for channel in catObj.channels:
            if len(await channel.history(limit=3).flatten()) == 1:
                continue
            while len(await channel.history(limit=1).flatten()) != 0:
                deleted = await channel.purge(bulk=True)
                await ctx.send(f"Deleted {len(deleted)} message(s) from {channel.name}")
            await channel.send(embed=newchannel)

    game = discord.Game("with cat nip~")
    await discord_client.change_presence(status=discord.Status.online, activity=game)                       
    await ctx.send("All done!")
    return


@autopurge.error
async def autopi(ctx, error):
    await ctx.send(embed = discord.Embed(title="ERROR", description=error.__str__(), color=0xFF0000))

@discord_client.command()
async def readconfig(ctx):
    await ctx.send(f"Channel mappings config--")
    c = "Category"
    a = "Archive"
    output = f'{c:<15}-- --{a:>15}\n'
    for k,v in config['archive_mapping'].items():
        key = discord_client.get_channel(int(k)).name
        val = discord_client.get_channel(int(v)).name
        output += (f"{key:<15} > {val}\n")
    await ctx.send(f"```{output}```")

    await ctx.send(f"Role config--")
    r = "Roles"
    output = f'{r:^15}:\n'
    for role in config['roles']:
        output += f"{role}\n"
    await ctx.send(f"```{output}```")

@discord_client.command()
async def sync(ctx):
    if botAPI.rightServer(ctx, config):
        pass
    else:
        desc = f"You are attempting to run a command destined for another server."
        await ctx.send(embed = discord.Embed(title="ERROR", description=desc, color=0xFF0000))
        await ctx.send(f"```{botAPI.serverSettings(ctx, config, discord_client)}```")
        return
    if botAPI.authorized(ctx, config):
        pass
    else:
        await ctx.send(f"Sorry, only leaders can do that. Have a nyan cat instead. <a:{config['Emoji']['nyancat_big']}>")
        return

    await ctx.send("Syncing..")
    # Grab roles we want to use
    zbpRoles = [ (k,v) for k,v in config['roles'].items() ]
    missing_members = []
    zuluGuild = discord_client.get_guild(int(config['Discord']['zuludisc_id']))
    for zmember in (mem for mem in zuluGuild.members if 'CoC Members' in (rol.name for rol in mem.roles)):
        # Attempt to find the user in ZBP server
        # if zmember.id != disc_id:
        #     continue
        pmember = ctx.guild.get_member(zmember.id)
        if pmember == None:
            missing_members.append(zmember.display_name)
            continue

        # If member exists
        await ctx.send(f"Syncing **{zmember.display_name}** ...")
        if pmember.display_name != zmember.display_name:
            try:
                await pmember.edit(nick=zmember.display_name, reason="KittyLitter bot Sync function @sgtmajordoobi")
                await ctx.send(f"[+] Nickname Synced")
            except discord.Forbidden:
                await ctx.send(f"[-] Nickname Sync Failed: Elevated perms required")
        else:
            await ctx.send(f"[+] Nickname Synced")
        
        roleStaging = []
        for role in zmember.roles:
            if role.name.lower() in ( roleTupe[0].lower() for roleTupe in zbpRoles ):
                result = next(( roleTupe[1] for roleTupe in zbpRoles if roleTupe[0].lower() == role.name.lower() ))
                roleObj = ctx.guild.get_role(int(result))
                roleStaging.append(roleObj)
            else:
                pass
        
        if str(pmember.id) in config['helpers']:
            roleObj = ctx.guild.get_role(int(config['Discord']['helper_id']))
            roleStaging.append(roleObj)
            
        try:
            await pmember.edit(roles=roleStaging, reason = "KittyLitter bot Sync function @sgtmajordoobie")
            await ctx.send(f"[+] Roles Synced")
        except discord.Forbidden:
            await ctx.send(f"[-] Role Sync Failed: Elevated perms required")
                
    if missing_members:
        output = ''
        for member in missing_members:
            output += (f"{member}\n")
        await ctx.send(f"Members missing in Zulu Base Planning\n```{output}``` "
            "Sync function is done. However, the personnel above are missing "
            "in this server. ")
        return
    await ctx.send("Syncing is done")
    return

@discord_client.event
async def on_message(message):
    if message.role_mentions:
        if message.channel.category_id in [520743187023921152, 511742081056899084, 530386718084562955]:
            for role in message.role_mentions: 
                if role.id in [542071254769991690, 542085052066955295, 479457431785701377]:
                    if role.name == "Helpers":
                        if message.channel.category_id == 520743187023921152: # Traditional War
                            warRoom = discord_client.get_channel(298641279720488960) #war-current-war
                            if warRoom != None:
                                desc = (f"Zulu members! {message.author.display_name} is requesting your help in "
                                    f"{message.channel.name}. Please give them your support!")
                                await warRoom.send(embed = discord.Embed(title="Support Request!", description=desc, color=0xA105C7))
                                return
                            return

                        elif message.channel.category_id == 511742081056899084: # CWL Zulu
                            warRoom = discord_client.get_channel(511421389153239041) #zulu-war-room
                            if warRoom != None:
                                desc = (f"Zulu members! **{message.author.display_name}** is requesting your help in "
                                    f"**{message.channel.name}** (Zulu Base Planning Server). Please give "
                                    f"{message.author.display_name} your support!")
                                await warRoom.send(embed = discord.Embed(title="Support Request!", description=desc, color=0xA105C7))
                                return
                            return

                        elif message.channel.category_id == 530386718084562955: # CWL Elephino
                            warRoom = discord_client.get_channel(511423310807040001) #elephino-war-room
                            if warRoom != None:
                                desc = (f"Zulu members! **{message.author.display_name}** is requesting your help in "
                                    f"**{message.channel.name}** (Zulu Base Planning Server). Please give "
                                    f"{message.author.display_name} your support!")
                                await warRoom.send(embed = discord.Embed(title="Support Request!", description=desc, color=0xA105C7))
                                return
                            return
                    
                    elif role.name == "Zulu CWL":
                        if message.channel.category_id == 511742081056899084: # CWL Zulu
                            warRoom = discord_client.get_channel(511421389153239041) #zulu-war-room
                            if warRoom != None:
                                desc = (f"Zulu members! **{message.author.display_name}** is requesting your help in "
                                    f"**{message.channel.name}** (Zulu Base Planning Server). Please give "
                                    f"{message.author.display_name} your support!")
                                await warRoom.send(embed = discord.Embed(title="Support Request!", description=desc, color=0xA105C7))
                                return
                            return

                    elif role.name == "Elephino CWL":
                        if message.channel.category_id == 530386718084562955: # CWL Elephino
                            warRoom = discord_client.get_channel(511423310807040001) #elephino-war-room
                            if warRoom != None:
                                desc = (f"Zulu members! **{message.author.display_name}** is requesting your help in "
                                    f"**{message.channel.name}** (Zulu Base Planning Server). Please give "
                                    f"{message.author.display_name} your support!")
                                await warRoom.send(embed = discord.Embed(title="Support Request!", description=desc, color=0xA105C7))
                                return
                            return

    await discord_client.process_commands(message)
if __name__ == "__main__":
    discord_client.run(config[botMode]['Bot_Token'])
