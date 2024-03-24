import disnake
from disnake.ext import commands
from utils.data_shop import ShopDB # методы базы данных
from components.shop_select import ShopView # компоненты для магазина

class RoleShop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = ShopDB()

    @commands.slash_command(name="магазин", description="Показать магазин ролей")
    async def shop(self, interaction):
        embeds = await self.db.get_shop(interaction) # список ролей в эмбеде
        selects = await self.db.get_selects_shop(interaction) # селекты с ролями

        if not selects or not embeds:
            return await interaction.response.send_message(f'Магазин ролей пуст', ephemeral=True) # возвращает при условии отсутсвия ролей в магазине

        view = ShopView(embeds, interaction, selects) # компоненты мазагина
        view.add_item(selects[0]) # добавление первую страницу селекта
        await interaction.response.send_message(embed=embeds[0], view=view)


    @commands.slash_command(description="Добавить роль в магазин")
    @commands.has_permissions(administrator=True)
    async def add_role(self, interaction, role: disnake.Role, price: int):
        role_id = role.id
        await self.db.add_role_to_store(interaction.guild.id, role_id, price)
        await interaction.send(f"Роль {role.mention} добавлена в магазин по цене {price} 🪙")


    @commands.slash_command(description="Удалить роль из магазина")
    @commands.has_permissions(administrator=True)
    async def remove_role(self, interaction, role: disnake.Role):
        role_id = role.id
        await self.db.remove_role_from_store(role_id)
        await interaction.send(f"Роль {role.mention} удалена из магазина.")  

def setup(bot):
    bot.add_cog(RoleShop(bot))

