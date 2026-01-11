import aiohttp

class FoodService:
    BASE_URL = "https://world.openfoodfacts.org/cgi/search.pl"

    async def search_products(
        self,
        query: str,
        page: int = 1,
        page_size: int = 5
    ) -> tuple[list[dict], int]:

        params = {
            "action": "process",
            "search_terms": query,
            "page": page,
            "page_size": page_size,
            "json": "true"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, params=params) as response:
                if response.status != 200:
                    return [], 0

                data = await response.json()
                products = data.get("products", [])
                count = data.get("count", 0)

                total_pages = max(1, (count + page_size - 1) // page_size)

                result = [
                    {
                        "code": p.get("code"),
                        "name": p.get("product_name", "Без названия"),
                        "calories": p.get("nutriments", {}).get("energy-kcal_100g", 0)
                    }
                    for p in products
                ]

                return result, total_pages
