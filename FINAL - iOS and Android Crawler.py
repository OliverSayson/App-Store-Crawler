from google_play_scraper import app as google_play_app
import requests
from bs4 import BeautifulSoup
import chardet
import pandas as pd


def get_google_play_info(bundle_id):
    print(f"Processing Google Play bundle ID: {bundle_id}")
    try:
        app_info = google_play_app(bundle_id)

        name = app_info['title']
        url = app_info['url']
        application_category = app_info['genre']
        dev_website = app_info.get('developerWebsite', 'N/A')
        privacy_website = app_info.get('privacyPolicy', 'N/A')

        return {
            "Bundle ID": bundle_id,
            "Name": name,
            "URL": url,
            "Developer Website": dev_website,
            "Privacy Policy": privacy_website,
            "Category": application_category,
            "Platform": "Android"
        }

    except Exception as e:
        return {
            "Bundle ID": bundle_id,
            "Name": "Error",
            "URL": "N/A",
            "Developer Website": "N/A",
            "Privacy Policy": "N/A",
            "Category": "N/A",
            "Platform": "Android",
            "Error": str(e)
        }


def get_ios_info(bundle_id):
    base_url = "https://apps.apple.com/app/id"
    app_url = f"{base_url}{bundle_id}"
    print(f"Processing iOS bundle ID: {bundle_id}, URL: {app_url}")

    try:
        response = requests.get(app_url)

        if response.status_code == 200:
            encoding = chardet.detect(response.content)['encoding']
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)

            app_name_element = soup.find('h1', class_='product-header__title')
            app_name = app_name_element.get_text(strip=True) if app_name_element else "App Name not found"

            developer_element = soup.find('a', class_='link')
            developer = developer_element.get_text(strip=True) if developer_element else "Developer not found"

            category_element = soup.find('dt', class_='information-list__item__term', string='Category')
            if (category_element and (category_elem := category_element.find_next('dd').find('a'))):
                category = category_elem.get_text(strip=True)
            else:
                category = "Category not found"

            language_element = soup.find('dt', class_='information-list__item__term', string='Languages')
            if language_element:
                language = language_element.find_next('dd').get_text(strip=True)
            else:
                language = "Language not found"

            all_anchor_tags = soup.find_all('a')

            developer_website_url = "Developer Website not found"
            appsupport_website_url = "App Support Website not found"
            for anchor in all_anchor_tags:
                if "developer" in anchor.get_text().lower():
                    developer_website_url = anchor['href']
                elif "support" in anchor.get_text().lower():
                    appsupport_website_url = anchor['href']

            return {
                "Bundle ID": bundle_id,
                "Name": app_name,
                "URL": app_url,
                "Developer Website": developer_website_url,
                "Privacy Policy": appsupport_website_url,
                "Category": category,
                "Platform": "iOS"
            }

        else:
            return {
                "Bundle ID": bundle_id,
                "Name": "Error",
                "URL": app_url,
                "Developer Website": "N/A",
                "Privacy Policy": "N/A",
                "Category": "N/A",
                "Platform": "iOS",
                "Error": f"Failed to retrieve data: {response.status_code}"
            }

    except Exception as e:
        return {
            "Bundle ID": bundle_id,
            "Name": "Error",
            "URL": app_url,
            "Developer Website": "N/A",
            "Privacy Policy": "N/A",
            "Category": "N/A",
            "Platform": "iOS",
            "Error": str(e)
        }


def identify_and_process_bundles(bundle_ids):
    data = []
    for bundle_id in bundle_ids:
        if bundle_id.isdigit():
            data.append(get_ios_info(bundle_id))
        else:
            data.append(get_google_play_info(bundle_id))
    return data


# Example usage
bundle_ids = []
results = identify_and_process_bundles(bundle_ids)

# Create a DataFrame
df = pd.DataFrame(results)

# Save the DataFrame to a CSV file
df.to_csv("app_info_android.csv", index=False)
print("Data has been written to app_info.csv")
