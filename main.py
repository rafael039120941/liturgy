import discord
import aiohttp
from discord import app_commands

class Liturgia(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="$",
            intents=intents
        )
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"O Bot {self.user} foi ligado com sucesso.")

bot = Liturgia()

async def buscar_liturgia():
    url = "https://liturgia.up.railway.app/"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resposta:
            if resposta.status == 200:
                return await resposta.json()
            return None

@bot.tree.command(name="liturgia", description="Mostra a liturgia do dia")
async def liturgia(interaction: discord.Interaction):

    await interaction.response.defer()

    dados = await buscar_liturgia()

    if not dados:
        await interaction.followup.send("❌ Não consegui buscar a liturgia.")
        return

 # Mapeamento das cores litúrgicas
cores_liturgicas = {
    "roxo": discord.Color.purple(),
    "verde": discord.Color.green(),
    "vermelho": discord.Color.red(),
    "branco": discord.Color.light_grey(),
    "rosa": discord.Color.from_rgb(255, 105, 180),  # rosa personalizado
    "preto": discord.Color.dark_grey()
}

# Pega a cor correta ou usa padrão caso não encontre
cor_embed = cores_liturgicas.get(dados['cor'].lower(), discord.Color.blue())

embed = discord.Embed(
    title=f"📖 Liturgia do Dia - {dados['data']}",
    description=f"**{dados['liturgia']}**\nCor litúrgica: {dados['cor']}",
    color=cor_embed
)

    # Primeira Leitura
        embed.add_field(
        name=f"{dados['primeiraLeitura']['titulo']} ({dados['primeiraLeitura']['referencia']})",
        value=dados['primeiraLeitura']['texto'][:1000],
        inline=False
    )

    # Salmo
    embed.add_field(
        name=f"Salmo ({dados['salmo']['referencia']})",
        value=f"**Refrão:** {dados['salmo']['refrao']}\n\n{dados['salmo']['texto'][:900]}",
        inline=False
    )

    # Evangelho
    embed.add_field(
        name=f"{dados['evangelho']['titulo']} ({dados['evangelho']['referencia']})",
        value=dados['evangelho']['texto'][:1000],
        inline=False
    )

    embed.set_footer(text="Doctrina Verbi")

    await interaction.followup.send(embed=embed)

import os

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print("Token não encontrado!")
else:
    bot.run(TOKEN)


