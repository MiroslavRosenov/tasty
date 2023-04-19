import httpx
import os

from typing import Dict, List
from quart import current_app

from ext.postgres.base import PostgreSQLClient
from ext.translator import Translator

translate = Translator().translate

async def search_tags(ingredients: List[str]) -> Dict:
    pool: PostgreSQLClient = current_app.db
    
    generated = "AND ".join([f"EXISTS (SELECT 1 FROM unnest(ingredients) AS value WHERE value LIKE '%{translate(x)}%')" for x in ingredients])
    query = f"SELECT * FROM dishes WHERE {generated} LIMIT 12;"

    if (resp := await pool.fetch(query)):
        return {"results": [dict(x) for x in resp]}
        
    resp = httpx.get(
        "https://api.spoonacular.com/recipes/findByIngredients",
        params={
            "ingredients": ",".join(ingredients),
            "apiKey": os.getenv("TOKEN"),
            "number": 8,
            "ranking": 1
        }
    )

    if resp.status_code != 200:
        return {
            "error": resp.status_code
        }
    
    if not (dishes := (resp.json())):
        return {
            "error": 404,
            "details": "Recipe not found"
        }
    
    return {"results": [dict(x) for x in [await pool.fetchrow("SELECT * FROM dishes WHERE id = $1", dish["id"]) or await pool.fetchrow("INSERT INTO dishes (id, title, imageUrl, ingredients) VALUES ($1, $2, $3, $4) RETURNING *", dish["id"], translate(dish["title"]), dish["image"], [translate(x["name"]) for x in [dish["usedIngredients"] + dish["missedIngredients"]]]) for dish in dishes]]}
