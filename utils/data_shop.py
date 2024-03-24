import aiosqlite
import disnake

class ShopDB:
    def __init__(self):
        self.name = 'db/shop.db'
    async def create_table(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = '''
            CREATE TABLE IF NOT EXISTS shop (
                id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                role_id INTEGER,
                price INTEGER
            )
            '''
            await cursor.execute(query)
            await db.commit() # создание таблицы для магазина ролей

    async def get_store(self, guild_id):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'SELECT * FROM shop WHERE guild_id = ?'
            await cursor.execute(query, (guild_id,))
            return await cursor.fetchall() # получение списков ролей

    async def add_role_to_store(self, guild_id, role_id, price):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'INSERT INTO shop (guild_id, role_id, price) VALUES (?, ?, ?)'
            await cursor.execute(query, (guild_id, role_id, price))
            await db.commit() # добавление роли в список

    async def remove_role_from_store(self, role_id):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = 'DELETE FROM shop WHERE role_id = ?'
            await cursor.execute(query, (role_id,))
            await db.commit() # удаление роли из списка ролей

    async def get_selects_shop(self, inter):
        store = await self.get_store(inter.guild.id)
        if not store:
            return [None]
        options = []
        selects = []
        loop_count = 0
        for role_id, price in store:
            role = inter.guild.get_role(role_id)
            if role:
                options.append(disnake.SelectOption(label=role.name, description=f'Цена: {price} монет', value=role_id))
                loop_count += 1
                if loop_count % 5 == 0 or loop_count - 1 == len(store) - 1:
                    select = disnake.ui.Select(placeholder="Выбери желаемую роль", options=options, min_values=0, max_values=1, custom_id=f"roleshop_{loop_count}")
                    selects.append(select)
                    options = []
        if not selects:
            return None
        return selects # получение селектов с ролями(получаем сразу несколько селектов в зависимости от кол-во ролей в магазине)

    async def get_shop(self, inter):
        store = await self.get_store(inter.guild.id)
        if not store:
            return [disnake.Embed(title="Магазин ролей", description="Магазин пуст.", color=0x2F3136)]
        embeds = []
        text = ""
        loop_count = 0
        n = 0
        for role_id, price in store:
            role = inter.guild.get_role(role_id)
            if role:
                text += (f"> {role.mention}\n"
                         f"— Цена: {price} 🪙\n\n")
                loop_count += 1
                if loop_count % 5 == 0 or loop_count - 1 == len(store) - 1:
                    embed = disnake.Embed(title="Магазин ролей", description=text, color=0x2F3136)
                    embed.set_thumbnail(url=inter.author.display_avatar)
                    embeds.append(embed)
                    text = ""
        return embeds # получение список ролей(получаем сразу несколько эмбедов в зависимости от кол-во ролей в магазине))
