import requests
import os
import sys
import json
from package.api.prompt import Prompt

class Gpt(object):
    def __init__(self,config):
        self.config = config
        self.__API_KEY = config["api"]["gpt"]["token"]
        self.__request_url = config["api"]["gpt"]["request_url"]

    def tryToGetResponse(self,content:str,prompt:Prompt,temperature:float):
        # 自定义请求头
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.__API_KEY
        }
        message = {
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ],
            "temperature": temperature
        }
        response = requests.post(
            url=self.__request_url,
            headers=headers,
            json=message
        )
        try:
            content = response.json()["choices"][0]["message"]["content"]
            return content

        except Exception as e:
            print("ERROR(gpt.py->getResponse(self,content:str,prompt:Prompt)):API 连接失败，内容可能被屏蔽")
            return False



if __name__ == "__main__":
    # gpt = Gpt()
    # prompt = Prompt()
    # r = gpt.tryToGetResponse("could you speck english?",prompt.prompt_block_complex_response,0.8)
    # print(r)

    gpt = Gpt()
    prompt = Prompt()
    r = gpt.tryToGetResponse("",prompt.music_player,0)
    print(r)

