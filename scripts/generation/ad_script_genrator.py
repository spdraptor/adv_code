import json
from config.settings import settings
from src.utils.brand_manager import BrandManager

class AdScriptGenerator:
    """
    Generates creative ad scripts based on live moments and brand DNA.
    """
    def __init__(self):
        self.client = settings.get_openai_client()
        self.deployment_name = settings.AZURE_DEPLOYMENT_NAME
        self.brand_manager = BrandManager()

    def create_script(self, brand_name, moment_data):
        brand_insights = self.brand_manager.get_knowledge_base(brand_name)
        event = moment_data.get('event_type', 'event')
        excerpt = moment_data.get('excerpt', '')

        print(f"\n🎬 Generating script for Moment: {event}")

        prompt = f"""
        You are a Creative Director for {brand_name}.
        
        **BRAND DNA:**
        {json.dumps(brand_insights, indent=2)}

        **LIVE MOMENT:**
        - Event: {event}
        - Commentary: "{excerpt}"

        **TASK:**
        Write a 10-second TVC script connecting this specific cricket moment to the brand's promise.
        
        **OUTPUT FORMAT:**
        - Title:
        - Visual:
        - Audio:
        - Voiceover:
        """

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        return response.choices[0].message.content