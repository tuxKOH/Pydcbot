import discord
from discord.ext import commands
import asyncio

# 設定你的 bot token
TOKEN = 'MTQwNjYwMTU3MjQxODU4NDY2OA.G0x21c.HUo-GQcSyNFCpw--V0vAhtPvxkAL9SPIuOEBcE'

# 設定指令前綴
bot = commands.Bot(command_prefix='?', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Bot 已登入為 {bot.user}')

@bot.command()
async def deletemsg(ctx, *, name: str):
    """刪除指定用戶的全部訊息"""
    # 檢查是否有 name: 前綴
    if name.startswith('name:'):
        name = name[5:].strip()
    
    # 檢查權限
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("你沒有權限使用此指令！")
        return
    
    # 取得伺服器成員
    member = None
    for m in ctx.guild.members:
        if name.lower() in m.name.lower() or name.lower() in m.display_name.lower() or str(m.id) == name:
            member = m
            break
    
    if not member:
        await ctx.send(f"找不到名為 {name} 的用戶！")
        return
    
    # 確認訊息
    confirm = await ctx.send(f"即將刪除 {member.display_name} 的所有訊息，請確認 (輸入✅確認，❌取消)")
    await confirm.add_reaction('✅')
    await confirm.add_reaction('❌')
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirm.id
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await confirm.delete()
        await ctx.send("操作已取消（超時）")
        return
    
    if str(reaction.emoji) == '❌':
        await confirm.delete()
        await ctx.send("操作已取消")
        return
    
    # 開始刪除訊息
    await confirm.edit(content=f"正在刪除 {member.display_name} 的訊息，這可能需要一些時間...")
    
    deleted = 0
    channels = ctx.guild.text_channels
    
    for channel in channels:
        try:
            async for message in channel.history(limit=None):
                if message.author == member:
                    try:
                        await message.delete()
                        deleted += 1
                    except:
                        pass
                    await asyncio.sleep(0.5)  # 避免速率限制
        except:
            pass
    
    await confirm.edit(content=f"已刪除 {member.display_name} 的 {deleted} 條訊息")

bot.run(TOKEN)
