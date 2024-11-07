
import wikipedia

search_texts = ["elon musk", "elon", "musk", "spaceX", "twitter", "tesla", "neuralink"]

real = "elon musk"
wikipedia.set_lang("en")

text = ""
real_lower = real.lower()

repeated = []
for st in search_texts:
    re = wikipedia.search(st)
    for r in re:
        if real_lower in r.lower() and r not in repeated:
            print(r)
            try:
                text += wikipedia.page(r).content
            except:
                print(r)
                pass
            repeated.append(r)

    
file_name = real_lower.replace(" ","_") + ".txt"
with open(file_name, "w+") as f:
    f.write(text)

print(st+" completed")
