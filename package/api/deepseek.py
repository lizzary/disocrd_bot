import os
import sys
import json
from openai import OpenAI
from package.api.prompt import Prompt

class Deepseek(object):
    def __init__(self,config:dict):
        self.config = config
        self.__API_KEY = config["api"]["deepseek"]["token"]
        self.__request_url = config["api"]["deepseek"]["request_url"]


    def tryToGetResponse(self,content:str,prompt:Prompt,temperature:float):
        try:
            client = OpenAI(api_key=self.__API_KEY, base_url=self.__request_url)

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content},
                ],
                temperature=temperature,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"ERROR(gpt.py->getResponse(self,{content},prompt:Prompt)):API 连接失败，内容可能被屏蔽")
            return False



if __name__ == "__main__":
    config_path = '../../config.json'
    with open(config_path, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    gpt = Deepseek(config)
    prompt = Prompt()
    r = gpt.tryToGetResponse("看看我的歌单",prompt.prompt_block_complex_response,1.5)
    print(r)



