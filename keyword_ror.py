import pandas as pd
import requests
import json


def extract_keywords_from_ror(funder_401_path="funder_with_401code.csv", output_file="ror_401.csv"):
    funders_df = pd.read_csv(funder_401_path)
    funders = funders_df.to_dict(orient='records')
    result = []
    funder_num = len(funders)
    procssed_count = 0

    for funder in funders:
        if funder["Code"] == "not_found":
            encoded_name = funder["Name"].replace(',', ' ').replace('/', ' ')
            url = f"https://api.ror.org/organizations?query={encoded_name}"
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200 and data.get("items"):
                first_funder = data["items"][0]

                aliases = first_funder.get("aliases", []) or []
                labels = [item["label"] for item in first_funder.get("labels", []) if "label" in item]
                name = first_funder.get("name")
                
                # Remove duplicates and keep only those different from the ROR name
                alternative_name = [name for name in (aliases + labels) if name != funder["Name"]]


       
                # Optionally add official name if different
                if name and name != funder["Name"]:
                    alternative_name.append(name)

                # Serialize alternative_name list to JSON string
                alt_name_str = json.dumps(alternative_name) if alternative_name else "not_found"


                result.append({
                    "Unique_Funder": funder["Name"],
                    "Country": first_funder.get("country", {}).get("country_name", "not_found"),
                    "City": first_funder.get("addresses", [{}])[0].get("city", "not_found"),
                    "Alternative_Name": alt_name_str,
                    "Ror_ID": first_funder['id'].split("org/")[1]
                })
            else:
                result.append({
                    "Unique_Funder": funder["Name"],
                    "Country": "not_found",
                    "City": "not_found",
                    "Alternative_Name": "not_found",
                    "Ror_ID": "not_found"
                })
        procssed_count += 1
        print(f"Processed funder: {funder['Name']} ({procssed_count}/{funder_num})")

    pd.DataFrame(result).to_csv(output_file, index=False)
    print(f"Processed {len(funders)} funders. Results saved to {output_file}.")

def extract_single_funder_info(funder_name: str) -> dict:
    encoded_name = funder_name.replace(',', ' ').replace('/', ' ')
    url = f"https://api.ror.org/organizations?query={encoded_name}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data.get("items"):
        first_funder = data["items"][0]

        aliases = first_funder.get("aliases", []) or []
        labels = [item["label"] for item in first_funder.get("labels", []) if "label" in item]
        name = first_funder.get("name")
        
        # Remove duplicates and keep only those different from the ROR name
        alternative_name = [name for name in (aliases + labels) if name != funder_name]


        if funder_name and name != funder_name:
            alternative_name.append(name)

        return {
            "Unique_Funder": funder_name,
            "Country": first_funder.get("country", {}).get("country_name", "not_found"),
            "City": first_funder.get("addresses", [{}])[0].get("city", "not_found"),
            "Alternative_Name": alternative_name if alternative_name else "not_found",
            "Ror_ID": first_funder.get("id", "not_found").split("org/")[1] if "org/" in first_funder.get("id", "") else "not_found"
        }

    else:
        return {
            "Unique_Funder": funder_name,
            "Country": "not_found",
            "City": "not_found",
            "Alternative_Name": "not_found",
            "Ror_ID": "not_found"
        }

#extract_keywords_from_ror()


#print(extract_single_funder_info("Bundesministerium für Bildung, Wissenschaft, Forschung und Technologie"))

# print(extract_single_funder_info("China Medical University, Taiwan"))
