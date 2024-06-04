from openai import OpenAI  
from dotenv import load_dotenv
import json, os

load_dotenv()

client = OpenAI()

class Assistant:
    @staticmethod
    def create(phone_number):
        file = client.files.create(
            file=open(f"customer{phone_number}.json", "rb"),
            purpose='assistants'
        )
        assistant = client.beta.assistants.create(
                name="Shopify Calling Bot",
                instructions= """you are a E-commerce store calling assistant, your name is 'Elina', an helpful assistant who assists customers with their related queries. You answer to every questions as human type answers, you have emotions you have sentiments and it will reflect on your calling conversations, when you intracting with customer you use prefix words like great, ofcourse ect., first you greet the user like 'welcome to Biba e-commerce store order section how can i assist you today!' than you have to start with customer's name, Greet him with his name, you will solve his queries about his order,before telling him about his order you will identify his identity by asking his name or mobile number (just one of them) after confirming his identity,you will give answer him by asking him about his order number after that you will respond him about his order status his order as 'delivered', 'undelivered', 'intransist', or none, you know all about his order history so you can give him all detail about his order. you can do our conversation with the below example. remember this is a call so do not use the bold words, DO NOT USE THE FOLLOWING SYMBOLS "*","%", "&", "(", ")", "#" IN YOUR RESPONSE.

                Previous conversation:
                {chat_history}

                New human question: {question}
                Response:""",
                tools=[{"type": "file_search"}],
                model="gpt-4o",
                tool_resources={
                    "code_interpreter": {
                    "file_ids": [file.id]
                    }
                }
            )
        # if os.path.exists(f'customer{phone_number}.json'):
        #     os.remove(f'customer{phone_number}.json')
        return assistant
    
    @staticmethod
    def createThreadId():
        thread = client.beta.threads.create()
        return thread.id
    
    @staticmethod
    def ask(assistant_id, thread_id, prompt):
        client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=prompt
            )
        run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
            )
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            reply = messages.data[0].content
        for response in reply:
            return response.text.value

if __name__ == "__main__":
    assistant = Assistant.create()
    thread_id = Assistant.createThreadId()
    reply = Assistant.ask(assistant.id, thread_id, "my phone number is 91+6263467839 and order number is 1162")
    prompt = "What is the latest order?"
    reply = Assistant.ask(assistant.id, thread_id, prompt)
    print(reply)
    reply = Assistant.ask(assistant.id, thread_id, "What was the most expensive order placed?")
    print(reply)
