import discord
import aiohttp
from discord import app_commands
from discord.ext import tasks
import datetime

CANAL_LITURGIA = 1474387528575356958


class Liturgia(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        self.enviar_liturgia.start()  # inicia a task automática

    async def on_ready(self):
        print(f"O Bot {self.user} foi ligado com sucesso.")

    # 🔔 Envio automático às 15:00 UTC
    @tasks.loop(time=datetime.time(hour=15, minute=0, tzinfo=datetime.timezone.utc))
    async def enviar_liturgia(self):
        canal = self.get_channel(CANAL_LITURGIA)

        if not canal:
            print("Canal não encontrado.")
            return

        dados = await buscar_liturgia()

        if not dados:
            await canal.send("❌ Não consegui buscar a liturgia.")
            return

        embed = criar_embed(dados)

        await canal.send(embed=embed)


bot = Liturgia()


async def buscar_liturgia():
    url = "https://liturgia.up.railway.app/"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resposta:
            if resposta.status == 200:
                return await resposta.json()
            return None


def criar_embed(dados):

    cores_liturgicas = {
        "roxo": discord.Color.purple(),
        "verde": discord.Color.green(),
        "vermelho": discord.Color.red(),
        "branco": discord.Color.light_grey(),
        "rosa": discord.Color.from_rgb(255, 105, 180),
        "preto": discord.Color.dark_grey()
    }

    cor_embed = cores_liturgicas.get(
        dados['cor'].lower(),
        discord.Color.blue()
    )

    embed = discord.Embed(
        title=f"🕯 Liturgia do Dia\n📆 {dados['data']}",
        description=f"**{dados['liturgia']}**\nCor litúrgica: *{dados['cor']}*",
        color=cor_embed
    )

    embed.add_field(
        name=f"📖 {dados['primeiraLeitura']['titulo']} ({dados['primeiraLeitura']['referencia']})",
        value=dados['primeiraLeitura']['texto'][:1000],
        inline=False
    )

    embed.add_field(
        name=f"✝ Salmo ({dados['salmo']['referencia']})",
        value=f"Refrão: {dados['salmo']['refrao']}\n{dados['salmo']['texto'][:900]}",
        inline=False
    )

    embed.add_field(
        name=f"🕊 Evangelho ({dados['evangelho']['referencia']})",
        value=dados['evangelho']['texto'][:1000],
        inline=False
    )

    embed.set_footer(text="Doctrina Verbi")

    return embed


@bot.tree.command(name="liturgia", description="Mostra a liturgia do dia")
async def liturgia(interaction: discord.Interaction):

    await interaction.response.defer()

    dados = await buscar_liturgia()

    if not dados:
        await interaction.followup.send("❌ Não consegui buscar a liturgia.")
        return

    embed = criar_embed(dados)

    await interaction.followup.send(embed=embed)

async def buscar_versiculo(livro, capitulo, versiculo):
    referencia = f"{livro} {capitulo}:{versiculo}"
    url = f"https://bible-api.com/{livro}+{capitulo}:{versiculo}?translation=almeida"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resposta:
            if resposta.status == 200:
                return await resposta.json()
            return None

@bot.tree.command(name="versiculo", description="Busca um versículo ou intervalo da Bíblia")
@app_commands.describe(
    livro="Nome do livro (ex: João)",
    capitulo="Número do capítulo",
    versiculos="Versículo ou intervalo (ex: 16 ou 1-15)"
)
async def versiculo(
    interaction: discord.Interaction,
    livro: str,
    capitulo: int,
    versiculos: str
):

    await interaction.response.defer()

    referencia = f"{livro} {capitulo}:{versiculos}"
    url = f"https://bible-api.com/{livro}+{capitulo}:{versiculos}?translation=almeida"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resposta:
            if resposta.status == 200:
                dados = await resposta.json()
            else:
                dados = None

    if not dados or "text" not in dados:
        await interaction.followup.send("❌ Não encontrei essa referência.")
        return

    texto = dados["text"]

    # Discord limita embed a 4096 caracteres
    if len(texto) > 4000:
        texto = texto[:4000] + "\n\n(...continuação truncada)"

    embed = discord.Embed(
        title=f"📖 {dados['reference']}",
        description=texto,
        color=discord.Color.gold()
    )

    embed.set_footer(text="Doctrina Verbi")

    await interaction.followup.send(embed=embed)

import os
TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print("Token não encontrado!")
else:
    bot.run(TOKEN)

