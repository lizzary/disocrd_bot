import discord
import yt_dlp as youtube_dl
import asyncio
import os
import requests
import asyncio
from package.api.music_list import Music_list

class Youtube_music_player(object):

    def __init__(self,config:dict,client:discord.Client,message:discord.Message):
        """
        :param client: client是实例化后的主类，包含了机器人的所有运行逻辑
        :param message: message实例是一个锚点，记录了所有有关触发者的信息，包括触发者位于的服务器、名字等...
        """
        self.config = config
        self.client:discord.Client = client
        self.message:discord.Message = message

        self.music_id = '' #当前实例正在播放的歌曲id
        self.url = '' #当前实例正在播放的url
        self.stream_url = '' #当前实例正在流式播放的url

        self.stop_bool = False #用于禁用回调函数__loop_after_playing的循环播放功能

    async def tryToStart(self,music_id:str,url:str,stream_url:str,setting:str):
        """

        :param music_id: 需要播放音频的youtube的序号（该序号用于歌单播放和记录上一次播放）
        :param url: 需要播放音频的YouTube的url
        :param stream_url: 需要播放音频的YouTube的流式传输url，使用流式传输url可以省去解析url的时间
        :param setting: 'loop': 循环播放, 'continue': 播放歌单下一首， ‘once': 播放一次就暂停
        :return:
        """
        # 检查用户是否在语音频道中
        if self.message.author.voice is None:
            await self.message.channel.send("你需要在一个语音频道中才能播放音乐!")
            return

        #self.message.guild返回的是当前被触发逻辑的服务器的实例（有人发信息），self.message.guild.voice_client.channel返回的就是当前机器人所处的语音频道
        bot_voice_channel = self.message.guild.voice_client.channel if self.message.guild.voice_client != None else None

        #机器人不在语音频道，则
        if bot_voice_channel is None:
            voice_client = await self.message.author.voice.channel.connect()
        else:
            voice_client = self.message.guild.voice_client


        #若新的url和旧的url且上一次播放还没结束不一样则先停止上一次的播放然后在切换新的url
        if self.url != url and voice_client.is_playing():
            self.stop_bool = True #禁用回调函数__loop_after_playing的循环播放功能
            voice_client.stop()

        self.stop_bool = False
        self.music_id = music_id
        self.url = url
        self.stream_url = stream_url
        Music_list(self.config).setUserLastPlay(str(self.message.author.id),music_id)
        await self.__start(voice_client,setting)



    def __stop_after_playing(self, error):
        if error:
            return
        #以确保self.client.loop线程安全的形式异步执行self.message.guild.voice_client.disconnect(force=True)
        asyncio.run_coroutine_threadsafe(self.message.guild.voice_client.disconnect(force=True),loop=self.client.loop)

    async def __start(self,voice_client:discord.VoiceClient,setting:str):
        """

        :param voice_client: discord.VoiceClient实例，记录了发出信息的用户所处的语音频道
        :param setting: 'loop': 循环播放, 'continue': 播放歌单下一首， ‘once': 播放一次就暂停
        :return:
        """
        ydl_opts = {
            'format': 'bestaudio',
            'cookiefile':'cookies.txt',
            'noplaylist': True,
            'extract_flat': True
        }
        audio_quality = '192k'
        buffer_size = '2M'
        #设置-reconnect 1使其允许重新链接，否则discord机器人会因未知原因重置\切断流式传输使播放中断
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10',
            'options': f'-vn -ar 48000 -ac 2 -b:a {audio_quality} -buffer_size {buffer_size} -dn -sn -ignore_unknown',
            'executable': r'./ffmpeg/bin/ffmpeg.exe'
        }
        # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        #
        #     if setting == 'loop':
        #         #尝试使用流式传输url播放，如果url过期则会抛出异常
        #         if "http" in self.stream_url and requests.head(self.stream_url,allow_redirects=True).status_code == 200:
        #             print(self.stream_url)
        #             voice_client.play(discord.FFmpegPCMAudio(self.stream_url, **ffmpeg_options), after=self.__loop_after_playing)
        #         else:
        #             print("enter:::")
        #             print(Exception)
        #             #若流式传输url过期则在此处解析一个新的流式传输url
        #             song_info = ydl.extract_info(self.url, download=False)
        #             voice_client.play(discord.FFmpegPCMAudio(song_info["url"], **ffmpeg_options), after=self.__loop_after_playing)
        #             Music_list(self.config).setNewStreamUrlForMusic(str(self.message.author.id),self.music_id,song_info["url"])
        #     if setting == 'continue':
        #         voice_client.play(discord.FFmpegPCMAudio(song_info["url"], **ffmpeg_options), after=self.__continue_after_playing)
        resource_url = self.__getResourceUrl()
        if setting == 'loop':
            print(f"current: {self.music_id}: {resource_url}")
            voice_client.play(discord.FFmpegPCMAudio(resource_url, **ffmpeg_options), after=self.__loop_after_playing)
        if setting == 'continue':
            voice_client.play(discord.FFmpegPCMAudio(resource_url, **ffmpeg_options),after=self.__continue_after_playing)

    async def __getResourceUrl(self):
        #将视频url解析为音频连接的设置
        loop = asyncio.get_event_loop()
        ydl_opts = {
            'format': 'bestaudio',
            'cookiefile':'cookies.txt',
            'noplaylist': True,
            'extract_flat': True
        }
        #检查流式传输的url是否过期，如果过期则重新解析url来获得一个新的流式传输url
        if "http" in self.stream_url and requests.head(self.stream_url, allow_redirects=True).status_code == 200:
            print("使用流式传输")
            print(self.stream_url)
            return self.stream_url
        else:
            ydl = youtube_dl.YoutubeDL(ydl_opts)
            print("解析新连接,旧流式传输为：",self.stream_url," End")
            song_info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            #将新的流式传输url写入config中
            Music_list(self.config).setNewStreamUrlForMusic(str(self.message.author.id), self.music_id,song_info["url"])
            return song_info["url"]
    def __loop_after_playing(self,error):
        if error:
            return
        if self.stop_bool:
            return
        # 以确保self.client.loop线程安全的形式异步执行self.message.guild.voice_client.disconnect(force=True)
        last_play = Music_list(self.config).tryToGetUserLastPlay(str(self.message.author.id))
        asyncio.run_coroutine_threadsafe(self.tryToStart(last_play,self.url,self.stream_url,'loop'), loop=self.client.loop)

    def __continue_after_playing(self,error):
        if error:
            return
        if self.stop_bool:
            return
        # 以确保self.client.loop线程安全的形式异步执行self.message.guild.voice_client.disconnect(force=True)
        next_music_id,next_music_url = Music_list(self.config).tryToGetUserNextMusic(str(self.message.author.id))
        asyncio.run_coroutine_threadsafe(self.tryToStart(next_music_id, next_music_url, self.stream_url,'continue'), loop=self.client.loop)

if __name__ == "__main__":
    url = 'https://upos-hz-mirrorakam.akamaized.net/upgcxcode/18/01/432200118/432200118-1-30280.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1741883089&gen=playurlv2&os=akam&oi=2946464089&trid=e17b3df47f3a4f3caef0569f0b83024eu&mid=87704030&platform=pc&og=hw&upsig=48f2fbdf59e21c4ebdabcc2d45904aae&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&hdnts=exp=1741883089~hmac=4cbee8aa11e003767d6a81a1e9439146846f32aec50ba7a432a9a0c85f810e7c&bvc=vod&nettype=0&orderid=0,2&buvid=A393D02A-E501-5A29-C20B-C2E86DF709A776995infoc&build=0&f=u_0_0&agrr=0&bw=40343&logo=80000000'
    session = requests.Session()
    response = session.get(url)
    print(response.status_code)

