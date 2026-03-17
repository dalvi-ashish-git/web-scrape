import pandas as pd

def refine_structured_data(json_data):
    """
    Refinement Module: Polishes the LLM output using Pandas.
    """
    if not json_data:
        return pd.DataFrame()

    df = pd.DataFrame(json_data)
    
    # 1. Standardize Whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # 2. Intelligent Price Formatting
    # Locate any column that looks like a price/cost
    price_cols = [c for c in df.columns if any(k in c.lower() for k in ['price', 'cost', 'amount'])]
    for col in price_cols:
        # Remove currency symbols ($) and convert to float for sorting
        df[col] = df[col].astype(str).replace(r'[\$,\€\£\,]', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # 3. Proper Capitalization
    if 'Status' in df.columns:
        df['Status'] = df['Status'].str.capitalize()

    # 4. Remove empty or "garbage" rows where Name is N/A or empty
    if not df.empty and df.columns[0]:
        first_col = df.columns[0]
        df = df[df[first_col].str.lower() != 'n/a']
        df = df[df[first_col] != '']

    return df.drop_duplicates()