import json
import os
from scripts.generation.ad_script_genrator import AdScriptGenerator

def get_script(target_brand,live_moment):
    # ==========================================
    # 1. DEFINE INPUTS
    # ==========================================
    # In a real pipeline, 'target_brand' might come from a UI selection,
    # and 'live_moment' would come from the output of main_event_detector.py

    print(f"🚀 Starting Ad Generation for: {target_brand}")
    print(f"🏏 Context: {live_moment['event_type']} - {live_moment['excerpt']}")

    # ==========================================
    # 2. INITIALIZE GENERATOR
    # ==========================================
    # This initializes the Azure OpenAI client and the Brand Manager
    generator = AdScriptGenerator()

    # ==========================================
    # 3. GENERATE SCRIPT
    # ==========================================
    try:
        # This function fetches brand insights (or scrapes them if missing)
        # and uses LLM to write a script connecting the brand to the moment.
        final_script = generator.create_script(target_brand, live_moment)

        print("\n" + "="*40)
        print(f"✨ GENERATED SCRIPT FOR {target_brand.upper()} ✨")
        print("="*40)
        print(final_script)
        
        # ==========================================
        # 4. SAVE OUTPUT
        # ==========================================
        output_dir = "data/output_scripts"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{target_brand}_{live_moment['event_type']}_{live_moment['start_time'].replace(':','-')}.txt"
        output_path = os.path.join(output_dir, filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_script)
            
        print(f"\n✅ Script saved to: {output_path}")

    except Exception as e:
        print(f"\n❌ Error generating script: {e}")
