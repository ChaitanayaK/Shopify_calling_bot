from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import json
from dotenv import load_dotenv

load_dotenv()

import time

class Model:
    def __init__(self, state=None):
        self.llm = ChatOpenAI(temperature=0.4, model="gpt-4o")
        self.memory = ConversationBufferMemory()

        if state:
            self.memory = self.deserialize_memory(state)
        else:
            self.memory.save_context(
                {"system": """You are a helpful call assistant who assists users with their order related queries. You answer to every question as a human would answer
                 for example."""}, 
                {"output": ""}
            )

        self.conversation = ConversationChain(
            llm=self.llm, 
            memory = self.memory,
            verbose=False
        )
    
    def chat(self, prompt):
        output = self.conversation.predict(input=prompt)
        return output
    
    def serialize(self):
        return json.dumps(self.memory.load_memory_variables({}))

    @staticmethod
    def deserialize(serialized_data):
        state = json.loads(serialized_data)
        return Model(state=state)

    @staticmethod
    def deserialize_memory(state):
        memory = ConversationBufferMemory()
        listed_dic = Model.jsonConvertor(state)

        for dic in listed_dic:
            memory.save_context(inputs={"Human": dic['Human']}, outputs={"AI": dic['AI']})
        return memory

    @staticmethod
    def jsonConvertor(data):
        history = data['history'].replace('\n', '')
        parts = history.split('Human: ')
        conversations = []

        for part in parts[1:]:
            human, ai = part.split('AI: ')
            conversations.append({'Human': human.strip(), 'AI': ai.strip()})
        
        return conversations

if __name__ == "__main__":
    model = Model()
    model.chat("Hi")
    model.chat('What is the last thing you remember?')
    model.chat('Tell me the name of the most powerful pokemon in the kanto region')

    new_model = model.serialize()
    new_model = Model.deserialize(new_model)
    print(new_model.memory.load_memory_variables({}))
