
import pandas as pd

from funder_41_match import convert_name_and_alt_into_list

def exact_match_after_ror(funder_401_path="ror_401.csv", internel_file="funder_401.csv", output_file="exact_ror_41.csv"):
    funders_df = pd.read_csv(funder_401_path)
    funders = funders_df.to_dict(orient='records')

    internel_funders_df = pd.read_csv(internel_file)
    internel_funders = internel_funders_df.to_dict(orient='records')
    result = []

    total_funder = len(funders)
    processed = 0

    for funder in funders:
        funderName_list = convert_name_and_alt_into_list(funder["Unique_Funder"], funder["Alternative_Name"])

        record = {
            "Unique_Funder": funder["Unique_Funder"],
            "Matched_Funder": "not_found",
            "Matched_Code": "not_found",
        }

        match_found = False
        for name in funderName_list:
            for internel_record in internel_funders:
                internel_name = internel_record.get("Name", "")
                if name.lower() in internel_name.lower() and funder['Country'].lower() in internel_name.lower() and funder['City'].lower() in internel_name.lower():
                    record["Matched_Funder"] = internel_record["Name"]
                    record["Matched_Code"] = internel_record["Code"]
                    match_found = True
                    break  # stop searching internel_funders
            if match_found:
                break  # stop searching funderName_list

        result.append(record)
        processed += 1
        print(f"Processed funder(exact): {funder['Unique_Funder']} ({processed}/{total_funder})")

    # Convert to DataFrame and save
    pd.DataFrame(result).to_csv(output_file, index=False)



exact_match_after_ror()

    

              


