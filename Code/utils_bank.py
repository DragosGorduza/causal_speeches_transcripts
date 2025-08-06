
from pydantic import BaseModel
import streamlit as st
import httpx
import ssl
from requests_kerberos import HTTPKerberosAuth
from openai import AsyncOpenAI, OpenAI
import pymupdf as fitz
from enum import Enum
from pathlib import Path
import asyncio
import numpy as np
import textwrap
import PyPDF2
import re
import pandas as pd
import streamlit as st
import pandas as pd
import io
import msoffcrypto
import docx
from io import BytesIO

class LLM():

    def __init__(self):



        self.init_openai_client_async()
        self.init_openai_client()

    def init_openai_client_async(self):

        proxy_url = 'http://:@browse.vip.dmz.bankofengland.co.uk:8080'
        parsed_proxy = 'browse.vip.dmz.bankofengland.co.uk'

        auth = HTTPKerberosAuth(force_preemptive=True)
        self.ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='cacert.pem')
        negotiate_details = auth.generate_request_header(None, parsed_proxy, is_preemptive=True)
        proxy_headers = {}
        proxy_headers['Proxy-Authorization'] = negotiate_details
        self.proxy = httpx.Proxy(proxy_url, headers=proxy_headers)

        self.httpx_async = httpx.AsyncClient(verify=self.ctx, proxy = self.proxy,
                                                timeout=10**6,
                                                max_redirects=10**6,
                                               limits=httpx.Limits(max_keepalive_connections = 10**5,
                                                                   max_connections=10**5))
        self.client_oai_async = AsyncOpenAI(
                    api_key=open('_secret_key', 'r').readline(),
                    http_client=self.httpx_async
                    )


    def init_openai_client(self):

        proxy_url = 'http://:@browse.vip.dmz.bankofengland.co.uk:8080'
        parsed_proxy = 'browse.vip.dmz.bankofengland.co.uk'

        auth = HTTPKerberosAuth(force_preemptive=True)
        self.ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='cacert.pem')
        negotiate_details = auth.generate_request_header(None, parsed_proxy, is_preemptive=True)
        proxy_headers = {}
        proxy_headers['Proxy-Authorization'] = negotiate_details
        self.proxy = httpx.Proxy(proxy_url, headers=proxy_headers)

        # Ensure httpx.Client is only created once and reused to avoid issues with Azure OpenAI
        self.httpx = httpx.Client(verify=self.ctx, proxy=self.proxy, timeout=10**6,
                                      max_redirects=10**6,
                                       limits=httpx.Limits(max_keepalive_connections = 10**5,max_connections=10**5,
                                       ))
        self.client_oai = OpenAI(
                            api_key=open('_secret_key', 'r').readline(),
                            http_client=self.httpx
        )


    def get_answer(self, message_chain):
        self.init_openai_client()   #@TODO remove this once we have access to AzureOpenAI
        response = self.client_oai.chat.completions.create(
            messages=message_chain,
            model="gpt-4.1",
            temperature=0,
            )
        return response.choices[0].message.content


    def get_answer_structured(self, message_chain, output_format):
        self.init_openai_client()  #@TODO remove this once we have access to AzureOpenAI
        response = self.client_oai.responses.parse(
        input=message_chain,
        model="gpt-4.1",
        temperature=0,
        text_format = output_format)
        return response.output_parsed


    async def get_answer_structured_async(self, message_chain, output_format):
        self.init_openai_client_async()  #@TODO remove this once we have access to AzureOpenAI
        response = await self.client_oai_async.responses.parse(
            input = message_chain,
            model="gpt-4.1",
            temperature=0,
            text_format = output_format
        )
        return response.output_parsed


    async def member_analysis_async(self, text, topics):

        topic_list = ", ".join(topics)

        system_prompt = Prompts.SYSTEM_PROMPT_ALL_MEMBERS.format(topic_list=topic_list)
        print("System prompt", system_prompt)

        class TopicOutput(BaseModel):
            topic_name: str
            question_1_count_topic_mentions : int
            question_2_weight: str
            question_2_explanation: str
            question_3_view: str

        class OutputFormat(BaseModel):
            topics : list[TopicOutput]

        message_chain = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Speech: {text}"}
        ]

        output = await self.get_answer_structured_async(message_chain, OutputFormat)
        return output.dict()


    # Analysis with all 9 members - Question 1
    def member_analysis(self, text, topics):


        topic_list = ", ".join(topics)

        system_prompt = Prompts.SYSTEM_PROMPT_ALL_MEMBERS.format(topic_list=topic_list)
        print("System prompt", system_prompt)

        class TopicOutput(BaseModel):
            topic_name: str
            question_1_count_topic_mentions : int
            question_2_weight: str
            question_2_explanation: str
            question_3_view: str

        class OutputFormat(BaseModel):
            topics : list[TopicOutput]

        message_chain = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Speech: {text}"}
        ]

        output = self.get_answer_structured(message_chain, OutputFormat)
        return output.dict()

    # Analysis with all 9 members - Question 2
    def topic_summary_analysis(self, text: str):

        system_prompt = Prompts.SYSTEM_PROMPT_ALL_MEMBERS_DIFFERENCES
        print("System prompt", system_prompt)

        class TopicComparison(BaseModel):
            topic_name: str
            differences_members: str

        class OutputFormat(BaseModel):
            topics: list[TopicComparison]

        message_chain = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{text}"}
        ]

        output = self.get_answer_structured(message_chain, OutputFormat)
        return output.dict()

    # Analysis with all 9 members - Question 2
    def get_speaker_background(self, text=''):

        system_prompt = "You are an economist working in central banking."
        text = "Where did Peter Mooslechner study?"#Prompts.SYSTEM_PROMPT_ALL_MEMBERS_DIFFERENCES
        print("System prompt", system_prompt)

        class TopicComparison(BaseModel):
            study_location: str

        class OutputFormat(BaseModel):
            topics: list[TopicComparison]

        message_chain = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{text}"}
        ]

        output = self.get_answer_structured(message_chain, TopicComparison)
        return output.dict()



    def clean_text(self,text):
        message_chain = [
            {"role": "system", "content": Prompts.SYSTEM_PROMPT_CLEAN_TEXT},
            {"role": "user", "content": text}
            ]
        class OutputFormat(BaseModel):
            paragraphs : list[str]
        output = self.get_answer_structured(message_chain, OutputFormat)
        return "\n".join(output.paragraphs)


    async def prompt_iterator(self,list_to_run, prompt, system_prompt):

        """
        Run the list through the prompts, returning a new dataframe with the results.
        list contains dictionaries with keys 'section' and 'randomiser', for example.
        """

        class SentenceOutput(BaseModel):
            sentence : str
            point_estimate_sentiment: int
            sentiment_lower_bound: int
            sentiment_upper_bound: int

        class OutputFormat(BaseModel):
            explanation: str
            point_estimate_sentiment: int
            sentiment_lower_bound: int
            sentiment_upper_bound: int
            sentences : list[SentenceOutput]

        async def run_prompt(p):
            message_chain = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": p}]
            return (await st.session_state.LLM.get_answer_structured_async(message_chain=message_chain, output_format = OutputFormat)).dict()

        batch_size = 100
        all_bk = []
        for batch_start in range(0,len(list_to_run), batch_size):
            bk = await asyncio.gather(*[run_prompt(prompt.format(**list_to_run[i])) for i in range(batch_start, min(batch_start + batch_size, len(list_to_run)))])
            all_bk += bk

        return all_bk



    def run_day2_prompt(self, text, task='', variant = 'gdp'):

        self.init_openai_client()  #@TODO remove this once we have access to AzureOpenAI
        if task == 'Future Bank rate':
            with open('prompts/system_prompt_day2notes_futureRates.txt', 'r',encoding='utf-8') as file:
                user_prompt=file.read()
            user_prompt+='\n\n'
            user_prompt += f"""
        The speech to be assessed is : {text}
        """

        elif task == 'Balance of risks':

            if variant == 'inflation':
                with open('prompts/system_prompt_balance_of_risks.txt', 'r',encoding='utf-8') as file:
                    user_prompt=file.read()
                user_prompt+='\n\n'
                user_prompt += f"""
            The speech to be assessed is : {text}
            """
            else :
                with open('prompts/system_prompt_balance_of_risks_gdp.txt', 'r',encoding='utf-8') as file:
                    user_prompt=file.read()
                user_prompt+='\n\n'
                user_prompt += f"""
            The speech to be assessed is : {text}
            """

        else :
            user_prompt = """
            No instructions
            """

        message_chain = [
            {"role": "system", "content": user_prompt},
            {"role": "user", "content": text}
            ]

        print(message_chain)
        class OutputFormat(BaseModel):
            answer : str

        class EntitiesModel(BaseModel):
            upside: str
            downside: str
            #justification: str

        response = self.get_answer_structured(message_chain,
                                              OutputFormat if task == 'Future Bank rate' else EntitiesModel,
                                              )

        return response, user_prompt

