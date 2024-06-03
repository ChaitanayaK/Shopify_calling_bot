import http.client
import json
# import openai
from dotenv import load_dotenv, find_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

p_ = load_dotenv(find_dotenv())

class Extractor:
    def __init__(self, phone_number):
        self.shopify_store = "vkaps-amit.myshopify.com"
        self.api_version = "2022-10"
        self.access_token = os.environ.get("ACCESS_TOKEN")
        self.phone_number = phone_number
        self.conn = http.client.HTTPSConnection(self.shopify_store)
        self.headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.access_token
        }

    def extractData(self):
        self.conn.request("GET", f"/admin/api/{self.api_version}/customers/search.json?phone={self.phone_number}", '', self.headers)

        res = self.conn.getresponse()
        data = res.read()

        decoded_data = data.decode("utf-8")
        json_data = json.loads(decoded_data)
        # print(json_data)

        customer_id = json_data["customers"][0]["id"]
        # print(customer_id)

        payload = ''
        self.conn.request("GET", f"/admin/api/2024-04/orders.json?status=any&customer_id={customer_id}", payload, self.headers)
        res = self.conn.getresponse()
        data = res.read()
        decoded_data = data.decode("utf-8")
        json_data = json.loads(decoded_data)

        # print(json_data)

        for element in json_data['orders']:
            # print(element['order_number'])
            if str(element['order_number']) == str(self.order_number):
                order_details = json.dumps(element)
                # print(order_detail
        return 
        return None


if __name__ == "__main__":
    extractor = Extractor("+917000321403", 1162)
    print(extractor.extractData())