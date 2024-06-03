import json
import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
import pandas as pd

class Parser:
    def __init__(self):
        p_ = load_dotenv(find_dotenv()) # read local .env file
        openai.api_key = os.environ['OPENAI_API_KEY']

        self.review_template = """\
            For the following conversation, extract the following information:

            order_number: Extract the order number from the conversation. \
            Return two string, first order number in format as named 'formated' '123456789' , and after that return separate number like if order id named as 'spoken' if '1234' you will say 'one two three four'.. if any present, else return None.

            Format the output as JSON with the following keys:
            order_number

            conversation: {conversation}
        """
        self.prompt_template = ChatPromptTemplate.from_template(self.review_template)
        self.order_number_schema = ResponseSchema(name="order_number",
                             description="Extract the order number from the conversation. \
                    Return string order number, as separate number like if order id is '1234' you will say 'one two three four'.. if any present, else return None.")

        self.response_schemas = [self.order_number_schema]
    
    def parse(self, conversation):
        messages = self.prompt_template.format_messages(conversation=conversation)
        chat = ChatOpenAI(temperature=0.0, model='gpt-4o')
        response = chat(messages)
        output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        output_dict = output_parser.parse(response.content)
        return output_dict['order_number']



if __name__== "__main__":
    print(Parser().parse("hi my order number is 70472100327"))
