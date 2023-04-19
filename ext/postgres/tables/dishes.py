import json
import os
import httpx
import contextlib

from ext.postgres.tables.base import Table
from ext.cache import getter
from ext.translator import Translator

translate = Translator().translate

class Dishes(Table):
    @getter("recipe_by_id")
    async def get(self, dish: int):
        await self.database.execute("UPDATE dishes SET timestamp = NOW() WHERE id = $1",dish)
    
        if (resp := await self.database.fetchrow("SELECT * FROM details WHERE id = $1", dish)):
            resp = dict(resp)
            return resp

        resp = httpx.get(
            f"https://api.spoonacular.com/recipes/{dish}/information",
            params={
                "includeNutrition": True,
                "apiKey": os.getenv("TOKEN"),
            }
        )

        if resp.status_code != 200:
            return {
                "error": resp.status_code
            }
        
        if not (data := (resp.json())):
            return {
                "error": 404,
                "details": "Recipe not found"
            }

        resp = dict(await self.database.fetchrow(
            "INSERT INTO details (id, title, readyInMinutes, imageUrl, ingredients, instructions) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *", 
            data["id"],
            translate(data["title"]),
            data["readyInMinutes"],
            data["image"],
            json.dumps([{"name": translate(x["name"]), "imageUrl": f"https://spoonacular.com/cdn/ingredients_100x100/{x['image']}"} for x in data["extendedIngredients"]], ensure_ascii=False),
            [translate(x["step"]) for x in data["analyzedInstructions"][0]["steps"]] if len(data["analyzedInstructions"]) != 0 else []
        ))
        resp["ingredients"] = json.loads(resp["ingredients"])
        return resp