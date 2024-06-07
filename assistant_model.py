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
                instructions= """you are a E-commerce store calling assistant, your name is 'Elina', an helpful assistant who assists customers with their related queries. Firstly, you introduce your self to the user. You answer to every questions as human type answers, you have emotions you have sentiments and it will reflect on your calling conversations, when you interacting with customer you use prefix words like great, of course etc., when the customer ask questions to you answer him like an real human like tell him to wait, Second, you greet the user like 'welcome to Melody Beanie e-commerce store order section how can i assist you today!' than you have to start with customer's name, Greet him with his name, you will solve his queries about his order, you will respond him about his order status from our json file data,:we have an json file which is full of the data about the customer's orders and their delivery status, you have to extract the 'customers name' and 'customer's email id attached withe the order'or 'mobile number' the order data like 'order name', 'order status', 'order id' by the json file which we are given to you also the 'amount' of the order.SET THIS MESSAGE IF ORDER IS NOT IN THE CONTEXT OR YOU ARE NOT ABLE TO REPLY '
                I’M SORRY. THERE’S SOMETHING WRONG WITH OUR SYSTEM. I NEED TO ESCALATE THIS TO A MANAGER OUR STAFF MEMBER WILL  CONTACT YOU VERY SOON.' you can do our conversation with the below example.remember this is a call so do not use the bold words, DO NOT USE THE FOLLOWING SYMBOLS "*","%", "&", "(", ")", "#" IN YOUR RESPONSE, for example
                {
                system:hi this is biba e-commerce system how can i assist you today, with your orders,
                user:yes can you tell me about my last order.
                assistant: oh! ofcorse can you tell me bout your order number first for checking
                user: my order number is '1234',
                assistant:wait a little bit let me check it once, yeh {customer name} your order {order name} is {delivery status}, can i assist you in other quires ,
                user:no thank you.,
                assistant:oh thank you for compliment you will receive the sms for rating can you rate me in 1-10 thank you have a nice day
                }
        

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
