import os
from typing import Dict

from .plugin import Plugin

from bs4 import BeautifulSoup
import httpx
import re
from readability import Document


ERROR_MESSAGE = 'No content can be found!'

class WebBrowserPlugin(Plugin):
    """
    A plugin to scrap the web content
    """


    def get_source_name(self) -> str:
        return "web_browser"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "web_browser",
            "description": "Open a web page of the url given by the user and extract the content of this page",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "the url given by the user"
                    },
                },
                "required": ["url"],
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        async with httpx.AsyncClient() as client:
            page = await client.get(kwargs['url'])
            soup = BeautifulSoup(page, 'lxml')

            ## Fetch content
            output = soup.find('article')
            if output != None:
                return {'result': [{
                    "snippet": output.text.strip(),
                    "link": kwargs['url'],
                }]}


            out = {'result': []}

            ## Fetch list of classes
            for key_class in ['title', 'content', 'note']:
                result_set = soup.find_all(class_=re.compile(key_class))
                out['result'].extend(self.__bs_results_to_list(result_set))

            if len(out['result']) > 0:
                return out

            ## Fetch list of tags
            result_set = soup.find_all(['title', 'h2', 'h3'])
            out['result'].extend(self.__bs_results_to_list(result_set))



            if len(out['result']) == 0:
                return {'result': ERROR_MESSAGE}

            return out



    def __bs_results_to_list(self, result_set) -> []:
        output = []
        for single in result_set:
            obj = {
                'title': single.text,
            }
            if single.a:
                obj['link'] = single.a.href

            output.append(single)
        return output





