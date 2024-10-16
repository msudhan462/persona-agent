
# from pathlib import Path
# # pip install accelerate
# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch


# import torch
# print(torch.cuda.is_available())
# print("$"*20)
# print(torch.cuda.current_device())
# print("$"*20)
# print(torch.cuda.device_count())
# print("$"*20)
# print(torch.cuda.get_device_name(torch.cuda.current_device()))
# print("$"*20)



# models_dir = Path(__file__).parent.absolute().joinpath(".cache")
# print(models_dir)

# tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it",  cache_dir=models_dir)
# model = AutoModelForCausalLM.from_pretrained(
#     "google/gemma-2b-it",
#     device_map="auto",
#     # torch_dtype=torch.bfloat16,
#     cache_dir=models_dir
# )

# text_model_max_length = tokenizer.model_max_length

# input_text = "Write me a poem about Machine Learning."
# input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

# with torch.no_grad():
#     outputs = model.generate(**input_ids)
#     print("$"*20)
#     print("output")
#     print(outputs)
#     print("$"*20)
#     print("decoding")
#     print(tokenizer.decode(outputs[0]))
