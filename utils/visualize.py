import matplotlib.pyplot as plt

def plot_with_outliers(df, outliers):
    plt.figure(figsize=(12,6))
    plt.plot(df["open_time"], df["close"], label="Close Price", color="blue")
    plt.scatter(outliers["open_time"], outliers["close"], color="red", label="Outliers")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.title("Close Prices with Outliers")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("close_price_outliers.png")  # Save plot
    plt.show()
