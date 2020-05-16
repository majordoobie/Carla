from discord import Embed
import logging

EMBED_COLORS = {
    'info': 0x000080,       # blue
    'error': 0xff0010,      # red
    'success': 0x00ff00,    # green
    'warning': 0xFFFF00,    # yellow
    'ERROR': 0xFF0000,
    'WARNING': 0xFFFF00,
    'INFO': 0x00FF00,
    'DEBUG': 0x9933FF
}

async def embed_print(bot_version=None, ctx=None, title='', description=None, color='info',
                      codeblock=False, _return=False):
    """
    Method used to standardized how stuff is printed to the users
    Parameters
    ----------
    bot_version
    ctx
    title
    description
    color

    Returns
    -------
    """
    if len(description) < 1000:
        if codeblock:
            description = f'```{description}```'
        embed = Embed(
            title=f'{title}',
            description=description,
            color=EMBED_COLORS[color]
        )
        if bot_version:
            embed.set_footer(text=bot_version)
        if _return:
            return embed
        await ctx.send(embed=embed)

    else:
        blocks = await text_splitter(description, codeblock)
        embed_list = []
        embed_list.append(Embed(
            title=f'{title}',
            description=blocks[0],
            color=EMBED_COLORS[color]
        ))
        for i in blocks[1:]:
            embed_list.append(Embed(
                description=i,
                color=EMBED_COLORS[color]
            ))
        if bot_version:
            embed_list[-1].set_footer(text=bot_version)
        if _return:
            return embed_list

        for i in embed_list:
            await ctx.send(embed=i)


async def text_splitter(text, codeblock):
    '''
    Method is used to split text by 1000 character increments to avoid hitting the
    1400 character limit on discord
    '''
    blocks = []
    block = ''
    for i in text.split('\n'):
        if (len(i) + len(block)) > 1000:
            block = block.rstrip('\n')
            if codeblock:
                blocks.append(f'```{block}```')
            else:
                blocks.append(block)
            block = f'{i}\n'
        else:
            block += f'{i}\n'
    if block:
        if codeblock:
            blocks.append(f'```{block}```')
        else:
            blocks.append(block)
    return blocks
