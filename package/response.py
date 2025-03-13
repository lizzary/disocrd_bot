from package.api.gpt import Gpt
from package.api.deepseek import Deepseek
from package.api.prompt import Prompt
from package.functional_module.youtube_music_player import Youtube_music_player
from package.api.music_list import Music_list
import discord
from random import randint

class Response(object):
    prompt = Prompt()
    def __init__(self,config:dict,client:discord.Client):
        """
        回应模块
        :param config: 配置文件
        :param client: 机器人实例本体
        """
        self.config = config
        self.client = client
        self.music_list = Music_list(config)

    async def getResponse(self,message:discord.Message):


        await self.__getNiyaResponse(message)

    async def __getNiyaResponse(self,message:discord.Message):

        #文本太长
        if len(message.content) > 100:
            pass
        await self.__music_player_module(message)

    async def __general_response(self,message:discord.Message,llm_model:str):
        """
        对message.content进行回复
        :param message:
        :param llm_model: deepseek 或 gpt
        :return:
        """
        llm = Deepseek(self.config)
        if llm_model == 'deepseek':
            llm = Deepseek(self.config)
        if llm_model == 'gpt':
            llm = Gpt(self.config)

        r = llm.tryToGetResponse(message.content, self.prompt.prompt_block_complex_response, 1.5)
        if r:
            await message.channel.send(message.author.mention + " " + r)
        else:
            return


    async def __response_for_mention_sb(self,message:discord.Message,llm_model:str):
        """
        回复的时候先@需要回复的对象
        :param message:
        :param llm_model: deepseek 或 gpt
        :return:
        """
        llm = Deepseek(self.config)
        if llm_model == 'deepseek':
            llm = Deepseek(self.config)
        if llm_model == 'gpt':
            llm = Gpt(self.config)

        r = await llm.tryToGetResponse(message.content, self.prompt.prompt_block_complex_response, 1.5)
        if r:
            await message.channel.send(message.author.mention + " " + r)
        else:
            await message.channel.send(f"呼姆姆？...(脑中有串神秘代码: Class-Response:async def __response_for_mention_sb(self,{message.content},{llm_model})->GET FALSE)")


    async def __music_player_module(self,message:discord.Message):
        vab_relate_to_music = [
            "音","乐","歌","曲","唱","声","音","旋律","播","放","停止","暂停"
        ]
        # 定义 ANSI 转义序列
        color_start = "[1;34m"  #蓝色
        color_end = "[0m"  # 重置样式
        r = ''
        for word in vab_relate_to_music:
            if word in message.content:
                gpt_for_music = Gpt(self.config)
                r = gpt_for_music.tryToGetResponse(message.content, self.prompt.music_player, 0)
                print(r)
                break

        if '未知指令' in r or 'ERROR' in r:
            return

        if "停止播放" in r:
            try:
                await message.guild.voice_client.disconnect(force=True)
            except Exception as e:
                return #有可能机器人不在语音频道但是触发了“停止播放”指令

        forget_message_cache = self.config["response_cache"]["forget"]
        forget_message = forget_message_cache[randint(0,len(forget_message_cache)-1)]

        """
        ↓↓↓↓↓单曲循环↓↓↓↓↓
        """
        if '单曲循环' in r:
            #单曲循环-None
            if 'None' in r:
                print("提示没有歌名")
                await message.channel.send(f"{message.author.mention}  {forget_message}  ")
                return
            #单曲循环-歌名/序号
            if '-' in r:
                query = r.split('-')[1]
                #序号
                if query.isdigit():
                    result = self.music_list.tryToFindMusicById(str(message.author.id), query)
                    if not result[0]:
                        await message.channel.send(f"{message.author.mention}  没找到哟~(*ノ` ▽｀)")
                        return
                    music_id,platform,title,url,stream_url = result[1]
                    if platform == "youtube" or platform =="bilibili":
                        music_player = Youtube_music_player(self.config, self.client, message)
                        await music_player.tryToStart(music_id, url, stream_url,'loop')
                        await message.channel.send(f"正在播放:{title}")

                #名字
                else:
                    result = self.music_list.tryToFindMusicByTitle(str(message.author.id), query)
                    if not result[0]:
                        await message.channel.send(f"{message.author.mention}  没找到哟~(*ノ` ▽｀)")
                        return
                    music_id,platform,title,url,stream_url = result[1]
                    if platform == "youtube" or platform =="bilibili":
                        music_player = Youtube_music_player(self.config, self.client, message)
                        await music_player.tryToStart(music_id, url, stream_url,'loop')
                        await message.channel.send(f"正在播放:{title}")
        """
        ↑↑↑↑↑单曲循环↑↑↑↑↑
        
        ↓↓↓↓↓播放歌单↓↓↓↓↓
        """
        if "播放歌单" in r:
            #播放歌单-None
            if 'None' in r:
                print("提示没有歌名")
                await message.channel.send(f"{message.author.mention}  {forget_message}  ")
                return

            if '-' in r:
                query = r.split('-')[1]
                #序号
                if query.isdigit():
                    result = self.music_list.tryToFindMusicById(str(message.author.id), query)
                    if not result[0]:
                        await message.channel.send(f"{message.author.mention}  没找到哟~(*ノ` ▽｀)")
                        return
                    music_id,platform,title,url,stream_url = result[1]
                    if platform == "youtube" or platform =="bilibili":
                        music_player = Youtube_music_player(self.config, self.client, message)
                        await music_player.tryToStart(music_id, url, stream_url,'continue')
                        await message.channel.send(f"正在播放:{title}")

                # 名字
                else:
                    result = self.music_list.tryToFindMusicByTitle(str(message.author.id), query)
                    if not result[0]:
                        await message.channel.send(f"{message.author.mention}  没找到哟~(*ノ` ▽｀)")
                        return
                    music_id, platform, title, url,stream_url = result[1]
                    if platform == "youtube" or platform =="bilibili":
                        music_player = Youtube_music_player(self.config, self.client, message)
                        await music_player.tryToStart(music_id, url, stream_url,'continue')
                        await message.channel.send(f"正在播放:{title}")


        if "查看歌单" in r:
            music_list = self.music_list.tryToGetMusicListByUserId(str(message.author.id))
            content = "```ansi\n"
            content += f"{message.author.display_name}的歌单: \n"
            for music_id,music_info in music_list.items():
                print(music_id)
                if not isinstance(music_info, dict):
                    continue
                # content += f"{music_id}.  "
                if music_id == music_list["last_stop_at"]:
                    content += f"{color_start}{music_id}. (上一次播放){color_end}"
                    content += '\n'
                    content += color_start + "标题: " + music_info["title"] + color_end + "\n"
                    content += color_start + "链接: " + music_info["url"] + color_end + "\n"
                    content += color_start + "来源: " + music_info["platform"] + color_end + "\n"
                else:
                    content += f"{music_id}. "
                    content += '\n'
                    content += "标题: " + music_info["title"] + "\n"
                    content += "链接: " + music_info["url"].replace("https://","") + "\n"
                    content += "来源: " + music_info["platform"] + "\n"
            content += "```"
            await message.channel.send(content)

















