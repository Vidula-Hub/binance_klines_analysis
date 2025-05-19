from utils.analysis import get_ohlc, detect_outliers

def main():
    df = get_ohlc()
    if df.empty:
        print("No data retrieved. Exiting.")
        return
    
    print(" Columns in DataFrame:", df.columns.tolist())
    print(" DataFrame Preview:")
    print(df.head())

    # Example: Detect outliers on 'close' prices
    df_with_outliers = detect_outliers(df, column='close', threshold=3)
    print("\n Outlier Detection Preview:")
    print(df_with_outliers.head())

if __name__ == "__main__":
    main()
