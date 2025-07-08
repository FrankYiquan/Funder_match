import re
import spacy
import pycountry
from langdetect import detect, LangDetectException
import pandas as pd

def clean_china_subdivision_name(name):
    # Remove last word if more than one word (e.g., "Guangdong Province" → "Guangdong")
    parts = name.split()
    if len(parts) > 1:
        return " ".join(parts[:-1])
    return name

# Map language codes to spaCy models (only supported languages)
SPACY_MODEL_MAP = {
    "en": "en_core_web_sm",
    "de": "de_core_news_sm",
    "fr": "fr_core_news_sm",
    "pt": "pt_core_news_sm",
    "es": "es_core_news_sm",
    "it": "it_core_news_sm",
    "nl": "nl_core_news_sm"
}

# Preload country and region (subdivision) names
country_names = {c.name for c in pycountry.countries}
subdivision_map = {}
for subdiv in pycountry.subdivisions:
    country = pycountry.countries.get(alpha_2=subdiv.country_code).name
    subdiv_name = subdiv.name
    if country == "China":
        subdiv_name = clean_china_subdivision_name(subdiv_name)
    subdivision_map[subdiv_name] = country
# Cache loaded spaCy models
loaded_models = {}

def get_spacy_model(lang_code: str):
    model_name = SPACY_MODEL_MAP.get(lang_code)
    if not model_name:
        return None  # Don't fall back to English
    if model_name not in loaded_models:
        try:
            loaded_models[model_name] = spacy.load(model_name)
        except OSError:
            return None  # If model fails to load
    return loaded_models[model_name]

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"

def tokenize_text(text):
    return re.findall(r'\b\w[\w-]*\b', text)  # preserves hyphenated words

def identify_geo(funder_name: str):
    lang_code = detect_language(funder_name)
    nlp = get_spacy_model(lang_code)
    country = None
    region = None

    # Step 1: Use spaCy if available
    if nlp:
        doc = nlp(funder_name)
        for ent in doc.ents:
            ent_text = ent.text.strip().title()
            if ent_text in country_names:
                country = ent_text
            elif ent_text in subdivision_map:
                region = ent_text
                country = subdivision_map[ent_text]
    


    # Step 2: Token-by-token matching if nothing found
    if not country or not region:
        # Manual country keywords
        funder_name_lower = funder_name.lower()
        
        if  not country and "u.s." in funder_name_lower:
            country = "United States"

        if not country and "uk" in funder_name_lower:
            country = "United Kingdom"

        tokens = tokenize_text(funder_name.lower())

        # Match country names
        if not country:
            for name in country_names:
                if name.lower() in tokens:
                    country = name
                    break

        # Match regions
        if not region:
            for subdiv, parent in subdivision_map.items():
                if subdiv.lower() in tokens:
                    region = subdiv
                    if not country:
                        country = parent
                    break
        
       
    return {
        "funder_name": funder_name,
        "detected_language": lang_code,
        "country": country,
        "region": region
    }




def keyword_extract(funder_401_path="funder_with_401code.csv", output_path="keywords_extracted.csv"):
    # Load the CSV file into a pandas DataFrame
    funders_df = pd.read_csv(funder_401_path)
    funders = funders_df.to_dict(orient='records')
    results = []

    for funder in funders:
        if funder["Code"] == "not_found":
            try:
                geo_info = identify_geo(funder["Name"])
                results.append({
                    "funder_name": geo_info["funder_name"],
                    "detected_language": geo_info["detected_language"],
                    "country": geo_info["country"],
                    "region": geo_info["region"]
                })
            except Exception as e:
                results.append({
                    "funder_name": funder["Name"],
                    "detected_language": "error",
                    "country": None,
                    "region": None
                })
    
    # Convert results to DataFrame and save
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)
    print(f"Keyword extraction completed. Results saved to {output_path}.")

# Example usage
keyword_extract()









# #examole
# funder = "Basic and Applied Basic Research Foundation of Guangdong Province"
# result = identify_geo(funder)
# print(result)