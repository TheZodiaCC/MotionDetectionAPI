import discord
from config import DiscordConfig, BotConfig
from utils import log_utils
import os


class MotionDetectorBOT(discord.Client):
    def __init__(self):
        super().__init__()

    def get_current_guild(self):
        return discord.utils.get(self.guilds, name=DiscordConfig.DISCORD_TARGET_GUILD)

    def get_target_channel(self):
        guild = self.get_current_guild()

        return discord.utils.get(guild.channels, name=DiscordConfig.DISCORD_TARGET_CHANNEL)

    async def on_ready(self):
        guild = self.get_current_guild()
        target_channel = self.get_target_channel()

        log_utils.log_bot(f"Logged on as {self.user}, Guild: {guild}, Target Channel: {target_channel}")

    async def on_message(self, message):
        target_channel = self.get_target_channel()

        if message.author != self.user and message.channel.name == target_channel.name:
            if message.content[0] == DiscordConfig.BOT_COMMAND_PREFIX:

                output = self.commands_handler(message)

                if output[BotConfig.MESSAGE_TYPE_KEY_NAME] == BotConfig.MESSAGE_TYPE_MESSAGE_KEY_NAME:
                    await target_channel.send(output[BotConfig.MESSAGE_CONTENT_KEY_NAME])

                elif output[BotConfig.MESSAGE_TYPE_KEY_NAME] == BotConfig.FILE_TYPE_MESSAGE_KEY_NAME:
                    await target_channel.send(file=discord.File(output[BotConfig.MESSAGE_CONTENT_KEY_NAME]))

    def commands_handler(self, command):
        command_content = command.content.replace("!", "")

        output = {
            BotConfig.MESSAGE_TYPE_KEY_NAME: BotConfig.MESSAGE_TYPE_MESSAGE_KEY_NAME,
            BotConfig.MESSAGE_CONTENT_KEY_NAME: "Not Found"
        }

        try:
            if command_content == "list":
                output[BotConfig.MESSAGE_CONTENT_KEY_NAME] = self.list_command()

            elif command_content == "help":
                output[BotConfig.MESSAGE_CONTENT_KEY_NAME] = "list\ndownload\n"

            elif command_content.split(" ")[0] == "download" and len(command_content.split(" ")) == 2:
                download_content = self.download_command(command_content)

                if download_content:
                    output[BotConfig.MESSAGE_TYPE_KEY_NAME] = BotConfig.FILE_TYPE_MESSAGE_KEY_NAME
                    output[BotConfig.MESSAGE_CONTENT_KEY_NAME] = download_content

        except Exception as e:
            output[BotConfig.MESSAGE_CONTENT_KEY_NAME] = "Error while performing command"

        finally:
            return output

    def list_command(self):
        return "\n".join(os.listdir(BotConfig.LOG_FILES_DIR_PATH))

    def download_command(self, command):
        output = ""

        target_channel = self.get_target_channel()

        download_file_name = command.split()[1]

        if target_channel and download_file_name:
            if download_file_name in os.listdir(BotConfig.LOG_FILES_DIR_PATH):
                output = os.path.join(BotConfig.LOG_FILES_DIR_PATH, download_file_name)

        return output
