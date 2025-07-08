from langdetect import detect, LangDetectException
import pandas as pd


def language_identifier(funder_401_path="funder_with_401code.csv", output_path="language_identified.csv"):
    # Load the CSV file into a pandas DataFrame
    funders_df = pd.read_csv(funder_401_path)
    funders = funders_df.to_dict(orient='records')

    result = set()
    lang_count = 0
    not_found_count = 0
    total_funders = len(funders_df)


    for funder in funders:
        if funder["Code"] == "not_found":
            try:
                lang = detect(funder["Name"])
                lang_count += 1
                result.add(lang)
            except LangDetectException:
                not_found_count += 1
    
    # Convert the set to a list and create a DataFrame
    lang_list = list(result)
    lang_df = pd.DataFrame(lang_list, columns=["Language"])

    # Save the DataFrame to a CSV file
    lang_df.to_csv(output_path, index=False)

    print(f"Processed {total_funders} funders. Languages detected: {lang_count}. Not found: {not_found_count}. Results saved to {output_path}.")



#example
language_identifier()