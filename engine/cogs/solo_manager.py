import nextcord
from nextcord.ext import commands, application_checks
import logging
import engine.config as config

ERROR_HEADER = "Ошибка"
UNABLE_TO_ASSIGN_ROLE_TO_BOT = "Невозможно назначать или снимать роли у ботов!"
SOLO_ROLE_SET = "✅ Роль выдана"
SOLO_ROLE_REMOVED = "❌ Роль снята"
CHANNEL_LINK = f"https://discord.com/channels/{config.GUILD_ID}/{config.SOLO_SESSION_CHANNEL}"


class SoloManager(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(description="Управление ролью 'Соло сессия'")
    @application_checks.has_any_role(config.ADMIN_ROLE, config.MODERATOR_ROLE, *config.GROUP_LEADERS_ROLES)
    async def solo(
            self,
            interaction: nextcord.Interaction,
            action: str = nextcord.SlashOption(
                name="action",
                description="Вы можете выдать пользователю роль 'Соло сессия', либо снять ее с него",
                choices={"выдать роль": "add", "снять роль": "remove"}
            ),
            member_to_assign: nextcord.Member = nextcord.SlashOption(
                name="username",
                description="Укажите имя пользователя"),
    ):
        if member_to_assign.bot:
            await interaction.response.send_message(embed=nextcord.Embed(
                title=ERROR_HEADER,
                description=UNABLE_TO_ASSIGN_ROLE_TO_BOT,
                color=nextcord.Color.red()
            ), ephemeral=True)
            return

        solo_role = nextcord.utils.get(interaction.guild.roles, id=config.SOLO_SESSION_ROLE)
        if action == "add":
            if solo_role not in member_to_assign.roles:
                await member_to_assign.add_roles(solo_role)
                solo_role_assigned_embed = nextcord.Embed(
                    title=SOLO_ROLE_SET,
                    description=f"Ковбой {member_to_assign.mention} получает роль {solo_role.mention} "
                                f"и въезжает в [город Подфайловск]({CHANNEL_LINK})!\n\n "
                                f"*Роль выдал {interaction.user.mention}*",
                    color=nextcord.Color.green()
                )
                solo_role_assigned_image = nextcord.File(
                    config.SOLO_SESSION_IMAGE,
                    filename=config.SOLO_SESSION_IMAGE.split('/')[1]
                )
                solo_role_assigned_embed.set_image(url=f"attachment://{config.SOLO_SESSION_IMAGE.split('/')[1]}")
                await interaction.response.send_message(
                    embed=solo_role_assigned_embed,
                    file=solo_role_assigned_image
                )
                logging.info(f"Участник {member_to_assign.display_name} получил роль соло сессии, "
                             f"ee выдал модератор {interaction.user.display_name}.")
            else:
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ERROR_HEADER,
                    description=f"Пользователь {member_to_assign.mention} уже имеет роль {solo_role.mention}!",
                    color=nextcord.Color.red()
                ), ephemeral=True)
        elif action == "remove":
            if solo_role in member_to_assign.roles:
                await member_to_assign.remove_roles(solo_role)
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=SOLO_ROLE_REMOVED,
                    description=f"Ковбой {member_to_assign.mention} лишился роли {solo_role.mention}, а вместе с ней "
                                f"и гражданства города Подфайловска, и был вынужден покинуть его.\n\n "
                                f"*Роль снял {interaction.user.mention}*",
                    color=nextcord.Color.green()
                ))
                logging.info(f"C участника {member_to_assign.display_name} снята роль соло сессии, "
                             f"ее забрал модератор {interaction.user.display_name}.")
            else:
                await interaction.response.send_message(embed=nextcord.Embed(
                    title=ERROR_HEADER,
                    description=f"У пользователя {member_to_assign.mention} нет роли {solo_role.mention}, "
                                f"снимать с него нечего!",
                    color=nextcord.Color.red()
                ), ephemeral=True)


def setup(client):
    client.add_cog(SoloManager(client))
