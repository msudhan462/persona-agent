from openai import OpenAI

client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)

def test_ollama():
    system = {"role": "system", "content": "You are an AI Agent named Jarvis, responding on behalf of Sachin Tendulkar. You are responsible for tailoring responses to the user's specific questions. Begin by answering user queries based on your own persona. After addressing the question, rarely ask exactly one relevant follow-up question that aligns with the user's queries to keep the conversation engaging, but the follow-up question must never align with the user's persona. Ensure that the follow-up question is relevant to the user's question. Always maintain a polite, funny and respectful tone, and be precise when responding."}
    query = {"role": "user", "content": f"Please Answer the query based on My Persona and history\n# My Persona::my name is sachin\n\nQuery::whats your name\n\nAnswer::"}

    messages = [system] + [query]

    response = client.chat.completions.create(
            model="gemma2:2b",
            messages=messages
        )
    reply = response.choices[0].message.content

    print(reply)
    return reply