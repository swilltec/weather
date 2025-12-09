import openai

POE_API_KEY="e9nmhmxxEyy7baPpcVlk_Ju2-i1tF5LSMTeoZ4KdFxQ"

client = openai.OpenAI(
    api_key = POE_API_KEY,
    base_url = "https://api.poe.com/v1",
)

chat = client.chat.completions.create(
    model = "claude-sonnet-4.5",
    messages = [{"role": "user", "content": "Hello world"}]
)

print(chat.choices[0].message.content)