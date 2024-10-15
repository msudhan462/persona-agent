
import wikipedia

search_texts = ["List of international cricket centuries by Sachin Tendulkar"]

for st in search_texts:
    re = wikipedia.search(st)
    text = ""
    st_lower = st.lower()
    for r in re:
        if st_lower == r.lower():
            text += wikipedia.page(st).content
    
    file_name = st_lower.replace(" ","_") + ".txt"
    with open(file_name, "w+") as f:
        f.write(text)
    
    print(st+" completed")


class TextExtract:
    pass