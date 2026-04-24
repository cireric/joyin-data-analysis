# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "你是什么模型？你的上下文长度是多少？有哪些核心能力？代码生成方面处于什么样水平？是否具有视觉识别？"},
    ],
    stream=False
)

print(response.choices[0].message.content)