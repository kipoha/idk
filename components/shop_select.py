import disnake
from disnake.ext import commands
from utils.data_shop import ShopDB

class ShopView(disnake.ui.View):
    def __init__(self, embeds, interaction, selects):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.interaction = interaction
        self.selects = selects
        self.offset = 0
        self.db = ShopDB()
        for emb in self.embeds:
            emb.set_footer(text=f'Страница {self.embeds.index(emb) + 1}/{len(self.embeds)}')

    async def update_view(self):
        offset = self.offset
        self.clear_items()
        self.add_item(self.selects[self.offset])
        self.add_item(self.back)
        self.add_item(self.forward)
        self.add_item(self.close)
        is_first_page = offset == 0
        is_last_page = offset == len(self.embeds) - 1
        self.back.disabled = is_first_page
        self.forward.disabled = is_last_page

    async def interaction_check(self, interaction: disnake.MessageInteraction):
        if self.interaction.author.id != interaction.user.id:
            embed = disnake.Embed(color=0xff0000).set_author(name="[Ошибка]")
            embed.description = (
                f"{interaction.author.mention}, Вы **не** можете использовать эту кнопку, "
                f"так как она предназначена для пользователя {self.interaction.author.mention}!")
            embed.set_thumbnail(url=interaction.author.display_avatar)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if 'roleshop_' in interaction.component.custom_id:
            selected_option = interaction.values[0] if interaction  .values else None
            if not selected_option:
                return False  # Не выбрана роль

            role_id = int(selected_option)
            role = interaction.guild.get_role(role_id)
            if not role:
                return False  # Роль не найдена

            user_data = await self.db.get_user(interaction.author)
            if not user_data:
                return False  # Данные пользователя не найдены

            role_price = await self.db.get_role_price(role_id)
            if role_price is None:
                return False  # Цена роли не найдена

            user_roles = [r.id for r in interaction.author.roles]
            if role_id in user_roles:
                await interaction.response.send_message(
                    f'{interaction.author.mention}, у вас уже есть эта роль.',
                    ephemeral=True
                )
                return False  # Роль уже куплена

            if user_data[1] < role_price:
                await interaction.response.send_message(
                    f'{interaction.author.mention}, у вас недостаточно средств для покупки этой роли.',
                    ephemeral=True
                )
                return False

            await self.db.update_money(interaction.author, -role_price)
            await self.db.add_transaction(
                interaction.author.id,
                -role_price,
                f"Покупка роли {role.mention}"
            )

            await interaction.author.add_roles(role)
            await interaction.response.send_message(f"Вы успешно купили роль {role.mention} за {role_price} <:terror88:1180955324056870973>!", ephemeral=True)

            return True

        return True  # Если custom_id не соответствует ни одной из кнопок или селектора

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji='⬅️', row=1, disabled=True)
    async def back(self, _, interaction: disnake.MessageInteraction):
        self.offset -= 1
        await self.update_view()
        await interaction.response.edit_message(embed=self.embeds[self.offset], view=self)

    @disnake.ui.button(style=disnake.ButtonStyle.grey, emoji='➡️', row=1)
    async def forward(self, _, interaction: disnake.MessageInteraction):
        self.offset += 1
        await self.update_view()
        await interaction.response.edit_message(embed=self.embeds[self.offset], view=self)

    @disnake.ui.button(emoji='🗑', style=disnake.ButtonStyle.red, row=1)
    async def close(self, _, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        await interaction.delete_original_response()
