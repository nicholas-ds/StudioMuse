# StudioMuse LLM Refactor Plan

Based on our work so far, here's a step-by-step plan to complete your LLM refactoring. We've only successfully implemented the first step (BaseLLM and PerplexityLLM updates). Here are the remaining steps:

## 1. Fix GeminiLLM Implementation 

The issue with GeminiLLM is that it needs special handling since it uses Google's client library:

```python
# llm/gemini_llm.py
import os
from typing import Dict, Any
from google import genai
from .base_llm import BaseLLM

class GeminiLLM(BaseLLM):
    def __init__(self, model="gemini-2.0-flash", temperature=0.7, api_key=None):
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        super().__init__(
            model=model,
            api_url="unused_for_gemini",
            temperature=temperature,
            api_key=api_key
        )
        
        # Initialize client
        self.genai_client = genai.Client(api_key=api_key)
    
    def call_api(self, prompt: str) -> Dict[str, Any]:
        """Override for Gemini's specialized client library."""
        try:
            response = self.genai_client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return {"text": response.text}
        except Exception as e:
            raise Exception(f"Error calling Gemini API: {str(e)}")
```

## 2. Create PaletteDemystifyerLLM Using Composition

Rather than inheriting from GeminiLLM, use composition:

```python
# llm/PaletteDemystifyerLLM.py
from datetime import datetime
import json
from gi.repository import Gimp

class PaletteDemystifyerLLM:
    def __init__(self, gimp_palette_colors, physical_palette_data):
        # Import at initialization to avoid circular imports
        from .gemini_llm import GeminiLLM
        self.llm = GeminiLLM(temperature=0.7)
        
        self.analysis_result = {}
        self.created_date = datetime.now().isoformat()
        self.gimp_palette = gimp_palette_colors
        self.physical_palette = physical_palette_data
    
    def format_prompt(self):
        from .prompts import palette_dm_prompt
        return palette_dm_prompt.format(
            rgb_colors=self.gimp_palette,
            entry_text=self.physical_palette
        )
    
    def clean_and_verify_json(self, response):
        try:
            cleaned = (response
                .replace('```json\n', '')
                .replace('```', '')
                .strip())
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            Gimp.message(f"JSON parsing error: {e}")
            raise Exception(f"Failed to parse LLM response as JSON: {e}")
    
    def call_llm(self):
        try:
            prompt = self.format_prompt()
            response = self.llm.call_api(prompt)
            
            if isinstance(response, dict) and "text" in response:
                text = response["text"]
            else:
                text = str(response)
                
            self.analysis_result = self.clean_and_verify_json(text)
            return self.analysis_result
        except Exception as e:
            Gimp.message(f"Error in palette analysis: {e}")
            raise
```

## 3. Update LLMPhysicalPalette Similarly

Convert LLMPhysicalPalette to use composition:

```python
# llm/LLMPhysicalPalette.py
from pydantic import BaseModel
from datetime import datetime
from colorBitMagic_utils import clean_and_verify_json

class LLMPhysicalPalette:
    def __init__(self, physical_palette_name="Default Palette Name", palette_source="unknown"):
        # Import locally to avoid circular imports
        from .perplexity_llm import PerplexityLLM
        self.llm = PerplexityLLM()
        
        self.physical_palette_name = physical_palette_name
        self.colors_listed = []
        self.num_colors = 0
        self.llm_num_colors = 0
        self.created_date = datetime.now().isoformat()
        self.palette_source = palette_source
        self.additional_notes = ""
        self.raw_response = {}

    def call_llm(self, entry_text):
        try:
            from .prompts import add_physical_palette_prompt
            prompt = f"{add_physical_palette_prompt}\n\n The user's physical palette is: {entry_text}"
            response_data = self.llm.call_api(prompt)
            self.raw_response = response_data

            if "choices" in response_data and response_data["choices"]:
                color_json = clean_and_verify_json(response_data['choices'][0]['message']['content'])
                self.colors_listed = color_json['colors']
                self.llm_num_colors = color_json['piece_count']
                self.num_colors = len(self.colors_listed)
                self.physical_palette_name = color_json['set_name']
                self.additional_notes = color_json['additional_notes']
                self.palette_source = "Perplexity"
                self.created_date = datetime.now().isoformat()

            return self
        except Exception as e:
            return f"Error processing LLM response: {type(e).__name__}: {e}"
```

## 4. Create LLMServiceProvider

Create a service provider that manages LLM instances:

```python
# llm/llm_service_provider.py
from typing import Dict, Type, Optional
from .base_llm import BaseLLM
from .perplexity_llm import PerplexityLLM
from .gemini_llm import GeminiLLM

class LLMServiceProvider:
    """Factory class for LLM service instances."""
    
    _instances = {}
    _providers = {
        'perplexity': PerplexityLLM,
        'gemini': GeminiLLM
    }
    
    @classmethod
    def get_llm(cls, provider_name, **kwargs):
        """Get an instance of the specified LLM provider."""
        key = f"{provider_name}:{hash(frozenset(kwargs.items()))}"
        
        if key not in cls._instances:
            if provider_name not in cls._providers:
                raise ValueError(f"Unknown LLM provider: {provider_name}")
            
            llm_class = cls._providers[provider_name]
            cls._instances[key] = llm_class(**kwargs)
            
        return cls._instances[key]
    
    @classmethod
    def register_provider(cls, name, provider_class):
        """Register a new LLM provider."""
        cls._providers[name] = provider_class
```

## 5. Create Palette Data Models and Processor

Start creating basic data models for palette processing:

```python
# utils/palette_models.py
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ColorData(BaseModel):
    """Represents a single color."""
    name: str
    r: float = 0.0
    g: float = 0.0 
    b: float = 0.0
    a: float = 1.0

class PaletteData(BaseModel):
    """Base model for palette data."""
    name: str
    colors: List[ColorData]
    created_date: datetime = datetime.now()
    
    @property
    def color_count(self):
        return len(self.colors)

class PhysicalPalette(PaletteData):
    """Physical art supply palette."""
    source: str = "unknown"
    additional_notes: str = ""
```

```python
# utils/palette_processor.py 
from typing import List, Dict, Any
from gi.repository import Gimp, Gegl
from .palette_models import ColorData, PaletteData, PhysicalPalette

class PaletteProcessor:
    """Handles palette processing operations."""
    
    @staticmethod
    def load_gimp_palette(palette_name):
        """Load colors from a GIMP palette."""
        try:
            palette = Gimp.Palette.get_by_name(palette_name)
            if not palette:
                return None
                
            colors = palette.get_colors()
            color_data = []
            
            for i, color in enumerate(colors):
                if isinstance(color, Gegl.Color):
                    rgba = color.get_rgba()
                    color_data.append(ColorData(
                        name=f"Color {i+1}",
                        r=rgba[0],
                        g=rgba[1],
                        b=rgba[2],
                        a=rgba[3]
                    ))
            
            return PaletteData(
                name=palette_name,
                colors=color_data
            )
        except Exception as e:
            Gimp.message(f"Error loading palette: {e}")
            return None
```

## 6. Next Steps for Completing Refactor

1. **Delete `call_llm.py`** - It's now redundant
2. **Update dialog code** to use the new classes (incrementally)
3. **Add JSON schema validation** for LLM responses 
4. **Implement error handling and retry logic**
5. **Restructure utility functions** as outlined in your refactor.md

This step-by-step approach lets you incrementally implement the refactor while understanding each change. I recommend tackling one component at a time, testing after each change to ensure everything works before moving to the next step.