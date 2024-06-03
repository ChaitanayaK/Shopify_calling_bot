from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

class ActionExtractor:
    # def __init__(self) -> None:
    #     pass
    def getAction(self, user_message):
        # TODO: Add prompt for variables and 
        review_template = """
            Extract actions if any from the following user_message, else return None.\
            If actions is not None, then classify actions into 3 categories using similarity score with threshold of 0.8 out of 1 :\
                1. get order status
                2. get order history
                3. None\
            
            user_message : {user_message}\

            just return [classified_action] and nothing else
        """

        prompt_template = ChatPromptTemplate.from_template(review_template)
        messages = prompt_template.format_messages(user_message=user_message)

        chat = ChatOpenAI(temperature=0, model='gpt-4o')
        response = chat(messages)
        
        return response.content

        # listed_actions = []
        # for action in reply:
        #     # if action['action'] in actions:
        #     listed_actions.append(action)
        # return listed_actions



if __name__ == "__main__":
    os.system("cls")
    actionExtractor = ActionExtractor()

    while True:
        user_input = input("Enter input: ")
        print(actionExtractor.getAction(user_input))