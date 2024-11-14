import requests
from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime, timedelta
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed  # For multi-threading

BASE_URL = "https://www.mse.mk/mk/stats/symbolhistory/KMB" 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}


def collect_issuers():
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, 'html.parser')

        dropdown = soup.find("select", {"id": "Code"})

        if not dropdown:
            print("Issuer dropdown not found on the page.")
            return []

        issuers = [option.get("value").strip() for option in dropdown.find_all("option") if
                   option.get("value") and not re.search(r'\d', option.get("value"))]

        with open("issuers.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Issuer"]) 
            writer.writerows([[issuer] for issuer in issuers]) 

        print(f"{len(issuers)} issuer codes saved to issuers.csv")
        return issuers

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {BASE_URL}: {e}")
        return []


def collect_issuer_data(issuer_code):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 10)  

    base_url = f"https://www.mse.mk/mk/stats/symbolhistory/{issuer_code}"

    issuer_data = []

    while start_date < end_date:
        range_end_date = min(start_date + timedelta(days=365), end_date)
        start_date_str = start_date.strftime('%d.%m.%Y')
        range_end_date_str = range_end_date.strftime('%d.%m.%Y')

        payload = {
            'Code': issuer_code,
            'FromDate': start_date_str,
            'ToDate': range_end_date_str,
            'action': 'Прикажи'
        }

        response = requests.post(base_url, headers=HEADERS, data=payload)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find("table", {"id": "resultsTable"})
        if not table:
            print(f"No data available for {issuer_code} from {start_date_str} to {range_end_date_str}")
            start_date = range_end_date + timedelta(days=1)
            continue

        rows = table.find_all("tr")[1:]
        for row in rows:
            columns = row.find_all("td")
            if len(columns) >= 9:
                data = {
                    'Issuer': issuer_code,
                    'Date': columns[0].text.strip(),
                    'Last Transaction Price': columns[1].text.strip(),
                    'Max': columns[2].text.strip(),
                    'Min': columns[3].text.strip(),
                    'Average Price': columns[4].text.strip(),
                    '% Change': columns[5].text.strip(),
                    'Quantity': columns[6].text.strip(),
                    'Trading Volume (Denars)': columns[7].text.strip(),
                    'Total Volume (Denars)': columns[8].text.strip()
                }
                issuer_data.append(data)

        start_date = range_end_date + timedelta(days=1)

    return issuer_data


def main():
    start_time = time.time()

    issuers = collect_issuers()

    if not issuers:
        print("No issuers found, exiting.")
        return

    all_data = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(collect_issuer_data, issuer_code): issuer_code for issuer_code in issuers}
        for future in as_completed(futures):
            issuer_code = futures[future]
            try:
                issuer_data = future.result()
                all_data.extend(issuer_data)
                print(f"Data collected for issuer: {issuer_code}")
            except Exception as e:
                print(f"Error collecting data for issuer {issuer_code}: {e}")

    df = pd.DataFrame(all_data)
    df.to_csv("all_issuers_data_last_10_years.csv", index=False, encoding='utf-8')
    print("Data collection complete. Saved to all_issuers_data_last_10_years.csv.")

    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
