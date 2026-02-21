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

@bot.tree.command(name="olá-mundo",description="Primeiro comando do Bot")
async def olamundo(interaction:discord.Interaction):
    await interaction.response.send_message(f"Olá {interaction.user.mention}!")

@bot.tree.command(name="soma",description="Some dois números distintos")
@app_commands.describe(
    numero1="Primeiro numero a somar",
    numero2="Segundo número a somar"
)
async def olamundo(interaction:discord.Interaction,numero1:int,numero2:int):
    numero_somado = numero1 + numero2
    await interaction.response.send_message(f"O numero somado é {numero_somado}.",ephemeral=True)

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

    embed = discord.Embed(
        title=f"📖 Liturgia do Dia - {dados['data']}",
        description=f"**{dados['liturgia']}**\nCor: {dados['cor']}",
        color=discord.Color.purple() if dados['cor'].lower() == "roxo" else discord.Color.green()
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

    embed.set_footer(text="Liturgia diária automática ✨")

    await interaction.followup.send(embed=embed)

bot.run("TOKEN")

