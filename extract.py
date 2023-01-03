import os
import json


with open("schema.sql", "w", encoding="utf-8") as main:
    for file in os.listdir():
        if not file.endswith(".json"):
            continue
        
        with open(file, "r", encoding="UTF-8") as f:
            try:
                data = json.loads(f.read())
                dishes =  f"INSERT INTO dishes (id, title, imageUrl, ingredients) VALUES ({data['id']}, {data['title']}, {data['imageUrl']}, {json.dumps([(x['name']) for x in data['ingredients']], ensure_ascii=False)});\n"
                details = f"INSERT INTO details (id, title, readyInMinutes, imageUrl, ingredients, instructions) VALUES ({data['id']}, {data['title']}, {data['readyInMinutes']}, {data['imageUrl']}, {json.dumps(data['ingredients'], ensure_ascii=False)}, {json.dumps(data['ingredients'], ensure_ascii=False)};\n"
            except:
                print(f"{f.name!r} has failed to load!")
            else:
                    main.write(dishes)
                    main.write(details)
                    main.write("\n")
