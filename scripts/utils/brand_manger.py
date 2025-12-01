import os
import json
from config.settings import settings

class BrandManager:
    """
    Manages the retrieval and storage of Brand Knowledge Bases.
    """
    def __init__(self):
        self.firecrawl = settings.get_firecrawl_client()
        self.client = settings.get_openai_client()
        self.deployment_name = settings.AZURE_DEPLOYMENT_NAME

    def get_knowledge_base(self, brand_name):
        """
        Retrieves existing insights or triggers a new scrape if missing.
        """
        base_dir = f"data/brand_knowledge/{brand_name.lower().replace(' ', '_')}"
        insights_file = f"{base_dir}/{brand_name.lower()}_insights.json"

        # 1. Check existing
        if os.path.exists(insights_file):
            print(f"✅ Found existing knowledge base for {brand_name}. Loading...")
            with open(insights_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # 2. Build new
        print(f"⚠️ No knowledge base found for {brand_name}. Starting build process...")
        os.makedirs(base_dir, exist_ok=True)
        return self._build_knowledge_base(brand_name, base_dir, insights_file)

    def _build_knowledge_base(self, brand_name, base_dir, output_path):
        # Search
        print(f"🔍 Searching for {brand_name} advertisements...")
        search_results = self.firecrawl.search(
            query=f"{brand_name} brand advertisement campaign philosophy",
            limit=5,
        )
        
        urls = [item.url for item in search_results.web
                if all(k not in item.url for k in ["youtube.com", "tiktok.com", "instagram.com"])]

        # Scrape
        scraped_data = []
        print(f"🕷️ Scraping {len(urls)} URLs...")
        for i, url in enumerate(urls):
            try:
                result = self.firecrawl.scrape(url=url)
                content = result.markdown[:8000]
                scraped_data.append(content)
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")

        # Extract Insights via LLM
        print("🧠 Extracting brand DNA with LLM...")
        combined_text = "\n\n".join(scraped_data)[:15000]
        
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": "You are a senior brand strategist."},
                {"role": "user", "content": f"""
                Analyze the following text about {brand_name} and extract a JSON summary.
                REQUIRED FIELDS: brand_name, slogan_or_tagline, core_brand_values (list), 
                visual_style, tone_of_voice, target_audience, typical_ad_structure.
                Return ONLY valid JSON.
                TEXT: {combined_text}
                """}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        insights = json.loads(response.choices[0].message.content)

        # Save
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(insights, f, indent=2)
            
        print(f"💾 Knowledge base saved to {output_path}")
        return insights