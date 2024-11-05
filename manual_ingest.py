from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
import torch
from pinecone import Pinecone
# from uuid import uuid4
from pathlib import Path
# from huggingface_hub import login as hf_login

# HUGGINGFACE LOGIN
# hf_token = "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"
# hf_login(hf_token)

# Load the tokenizer and model from Hugging Face
# model_name = "BAAI/bge-large-en-v1.5"
# models_dir = Path(__file__).parent.absolute().joinpath(".cache")
# print(models_dir)

# tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=models_dir)
# model = AutoModel.from_pretrained(model_name, cache_dir=models_dir)
# print("embedding model max length",tokenizer.model_max_length)


# import os
# os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"


# # empty cache 
# torch.cuda.empty_cache()
# print("Empty the cache")

# Load tokenizer and model
# text_gen_model_name = "google/gemma-2b-it"
# text_tokenizer = AutoTokenizer.from_pretrained(text_gen_model_name, cache_dir=models_dir, device_map="auto")
# # text_model = AutoModelForCausalLM.from_pretrained("google/gemma-2b-it",device_map={"": "cuda:0"},torch_dtype=torch.bfloat16,cache_dir=models_dir)
# text_model = AutoModelForCausalLM.from_pretrained("google/gemma-2b-it",device_map="auto",torch_dtype=torch.bfloat16,cache_dir=models_dir)
# text_model_max_length = text_tokenizer.model_max_length
# print("################## tex gen model loaded ####################")

def get_embeddings(text):
    
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)

    with torch.no_grad():
        outputs = model(**inputs)

    sentence_embedding = outputs.last_hidden_state.mean(dim=1)

    return sentence_embedding

def chunk_text(text, chunk_size = 1000, combine_chunk=100, type="heirarchal"):
    si = 0
    ei = chunk_size
    total_length = len(text)

    total_chunks =  []
    chunk_count = 0
    while ei < total_length:
        if si == 0:
            chunk = text[si : ei]
        else:
            chunk = text[si-combine_chunk : ei]
        
        si = ei
        ei += chunk_size
        chunk_count += 1
        total_chunks.append(chunk)
    
    return total_chunks

class VectorDB:

    def __init__(self) -> None:
        self.pc = Pinecone(api_key="2f068841-49a0-4cf7-879c-e67be425859b")
        self.index = self.pc.Index("sachin")
    
    def insert(self, vectors):
        if isinstance(vectors, list):
            self.index.upsert(vectors=vectors)
        elif isinstance(vectors, dict):
            self.index.upsert(vectors=[vectors])
        else:
            raise ValueError("Please send as list or dict format")
    
    def search(self, vectors, top_k=5, filters={}):
        # print(vectors)
        return self.index.query(
            vector=vectors,
            top_k=top_k,
            # include_values=True,
            include_metadata=True,
        )

vector_db = VectorDB()




# def get_inference(messages):

#     # Input text
#     text = ""
#     print(messages)
#     for di in messages:
#         text += f"Role: {di['role']}\nContent: {di['content']}\n\n"

#     # Tokenize input
#     inputs = text_tokenizer(text, return_tensors="pt").to("cuda")
#     print(inputs)

#     inputs = inputs.to('cpu')

#     # Generate text
#     outputs = text_model.generate(
#         **inputs, 
#         max_length=text_model_max_length,
#         return_full_text=False,
#         eos_token_id=text_tokenizer.eos_token_id,
#         pad_token_id=text_tokenizer.eos_token_id, 
#     )

#     # Decode and print the generated text
#     generated_text = text_tokenizer.decode(outputs[0], skip_special_tokens=True)
    
#     return generated_text

# with open("sachin_tendulkar.txt") as f:
#     t = f.read()
#     chunks = chunk_text(t)
#     for chunk_count, ch in enumerate(chunks, start=1):
#         emds = get_embeddings(ch)[0]
#         id = uuid4()
#         data = {
#             "id":str(id),
#             "values":emds,
#             "metadata":{"text":ch}
#         }
#         vector_db.insert(data)
#         print(chunk_count)

#     print("Done")
# history = []
# while True:
#     search_text = input("Madhusudhan:: ") #"When did recieve Padma Vibhushan award"
#     embd = get_embeddings(search_text)[0].tolist()
#     context = vector_db.search(embd)

#     text = ""
#     for c in context["matches"]:
#         text += c['metadata']['text'] + "\n\n"
    
#     from openai import OpenAI

#     client = OpenAI(
#         base_url = 'http://localhost:11434/v1',
#         api_key='ollama', # required, but unused
#     )
#     system = {"role": "system", "content": "You are an AI Agent named Jarvis, responding on behalf of Sachin Tendulkar. You are responsible for tailoring responses to the user's specific questions. Begin by answering user queries based on your own persona. After addressing the question, rarely ask exactly one relevant follow-up question that aligns with the user's queries to keep the conversation engaging, but the follow-up question must never align with the user's persona. Ensure that the follow-up question is relevant to the user's question. Always maintain a polite, funny and respectful tone, and be precise when responding."}
#     query = {"role": "user", "content": f"Please Answer the query based on My Persona and history\n# My Persona::{text}\n\nQuery::{search_text}\n\nAnswer::"}
#     messages = [system]+history+[query]
#     response = client.chat.completions.create(
#         model="gemma2:2b",
#         messages=messages
#     )
#     reply = response.choices[0].message.content
#     print("Sachin:: ",reply)
#     history = history + [{"role":"user","content":search_text},{"role":"assistant","content":reply}]
