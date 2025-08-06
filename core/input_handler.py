import pandas as pd

REQUIRED_COLUMNS = {"Tool Name", "Category", "Used By"}


def load_input(file_path: str) -> pd.DataFrame:
    """
    Load and validate firm's tech stack input file.
    """
    try:
        df = pd.read_csv("data/tech_stack_list.csv")

    except Exception as e:
        raise ValueError(f"Failed to load CSV: {e}")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.dropna(subset=["Tool Name"])
    df = df.drop_duplicates(subset=["Tool Name"])

    return df


if __name__ == "__main__":
    df = load_input("data/tech_stack_list.csv")  # adjust path as needed
    print("✅ CSV loaded successfully.\n")
    print(df.head())               # Print first few rows
    print("\n📊 DataFrame info:")
    print(df.info())               # Summary of structure
