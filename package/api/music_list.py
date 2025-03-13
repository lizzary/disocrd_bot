
class Music_list(object):
    def __init__(self,config:dict):
        """

        :param config: 配置文件
        """
        self.config = config
        self.music_list = config["music_list"]
        """
        self.music_list的结构：
        "music_list": {
            "1014099918031433830": {
                "last_stop_at": "0",
                "1": {
                    "platform": "youtube",
                    "title": "SAMPLE",
                    "url": "https://sample"
                },
                "2":{...},
                "3":{...},
                ...
            },
            "1234567890": {
                ...
            }
        *歌曲的序号会被按照升序维护
        """



    def tryToFindMusicById(self, user_id:str, music_id:str):
        """
        以歌曲序号寻找歌曲，若该用户不在歌单内则为其新建一个空歌单
        :param user_id: 用户的唯一标识符，一般为message.author.id
        :param music_id: 歌曲序号
        :return: 若搜索不到返回(False,"None)，若搜索到了则返回(True, (歌曲id, 歌曲平台, 歌曲标题, url))，若没有url则url为None
        """
        # 如果歌单里没有用户的记录，则为这个用户新建一个空歌单
        if user_id not in self.music_list:
            self.music_list[user_id] = {"last_stop_at": "0"}

        if music_id not in self.music_list[user_id]:
            return (False,"None")

        return (
            True,
            (music_id,self.music_list[user_id][music_id]["platform"],self.music_list[user_id][music_id]["title"],self.music_list[user_id][music_id]["url"],self.music_list[user_id][music_id]["stream_url"])
        )

    def tryToFindMusicByTitle(self, user_id:str, music_title:str):
        """
        以歌曲的名字**模糊**搜索歌曲，若该用户不在歌单内则为其新建一个空歌单
        :param user_id: 用户的唯一标识符，一般为message.author.id
        :param music_title: 歌曲标题
        :return: 若搜索不到返回(False,"None)，若搜索到了则返回(True, (歌曲id, 歌曲平台, 歌曲标题, url))，若没有url则url为None
        """
        # 如果歌单里没有用户的记录，则为这个用户新建一个空歌单
        if user_id not in self.music_list:
            self.music_list[user_id] = {"last_stop_at": "0"}

        for music_id, music_info in self.music_list[user_id].items():
            #跳过"last_stop_at": "0"
            if not isinstance(music_info,dict):
                continue
            if music_title in music_info["title"]:
                return (
                    True,
                    (music_id,music_info["platform"],music_info["title"],music_info["url"],music_info["stream_url"])
                )

        return (False,"None")

    def tryToGetMusicListByUserId(self, user_id:str):
        # 如果歌单里没有用户的记录，则为这个用户新建一个空歌单
        if user_id not in self.music_list:
            self.music_list[user_id] = {"last_stop_at": "0"}
            return self.music_list[user_id]

        return self.music_list[user_id]

    def tryToGetUserLastPlay(self,user_id):
        """
        寻找指定用户上一次播放的序号
        :param user_id:
        :return: 返回可用的str型的序号
        """
        return self.music_list[user_id]["last_stop_at"]

    def tryToGetUserNextMusic(self,user_id):
        """
        寻找指定用户的下一首歌的序号
        :param user_id:
        :return: 如果可以找到下一顺位的歌曲，则返回(下一顺位歌曲的序号,对应的url)，否则视为歌单循环，从第一首歌开始，返回("1",对应的url)；
        """
        #如果可以找到下一顺位的歌曲，则返回
        last_play = self.music_list[user_id]["last_stop_at"]
        next_music = str(int(last_play) + 1)
        if next_music in self.music_list[user_id]:
            return (
                str(int(last_play) + 1),
                self.music_list[user_id][next_music]["url"]
            )

        else:
            return (
                "1",
                self.music_list[user_id]["1"]["url"]
            )

    def setUserLastPlay(self,user_id:str,last_play_music_id:str):
        self.music_list[user_id]["last_stop_at"] = last_play_music_id

    def setNewStreamUrlForMusic(self,user_id:str,music_id:str,new_stream_url:str):
        self.music_list[user_id][music_id]["stream_url"] = new_stream_url






