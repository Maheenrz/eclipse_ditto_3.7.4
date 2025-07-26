import requests
import csv
from datetime import datetime

# === Configuration ===
SONAR_HOST = "https://sonarcloud.io"
SONAR_TOKEN = "6dbfbde7029bdc5aa18afaf3f52e0a222e0f5fa9"  
ORGANIZATION_KEY = "maheenrz"     
PROJECT_KEY = "maheenrz_eclipse-ditto-3-7-4"       
OUTPUT_FILE = f"{PROJECT_KEY.replace('/', '_')}_sonarcloud_issues.csv"

# === Initialize ===
auth = (SONAR_TOKEN, "")
headers = {'Accept': 'application/json'}
page = 1
page_size = 500
all_issues = []

print(f"Fetching issues for project: {PROJECT_KEY}...")

while True:
    params = {
        "componentKeys": PROJECT_KEY,
        "organization": ORGANIZATION_KEY,
        "ps": page_size,
        "p": page
    }

    response = requests.get(f"{SONAR_HOST}/api/issues/search", auth=auth, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error fetching issues: {response.status_code}, {response.text}")
        break

    data = response.json()
    issues = data.get("issues", [])
    all_issues.extend(issues)

    print(f"Fetched page {page}, issues retrieved: {len(issues)}")

    if len(issues) < page_size:
        break

    page += 1

# === Write CSV ===
if all_issues:
    print(f"Writing {len(all_issues)} issues to {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, mode="w", newline='', encoding='utf-8') as csv_file:
        fieldnames = [
            "issue_url", "key", "rule", "severity", "component", "project",
            "line", "message", "status", "resolution", "debt", "effort",
            "type", "creationDate", "updateDate", "closeDate", "tags", "language"
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for issue in all_issues:
            issue_url = f"{SONAR_HOST}/project/issues?id={PROJECT_KEY}&open={issue['key']}&resolved=false"
            writer.writerow({
                "issue_url": issue_url,
                "key": issue.get("key", ""),
                "rule": issue.get("rule", ""),
                "severity": issue.get("severity", ""),
                "component": issue.get("component", ""),
                "project": issue.get("project", ""),
                "line": issue.get("line", ""),
                "message": issue.get("message", ""),
                "status": issue.get("status", ""),
                "resolution": issue.get("resolution", ""),
                "debt": issue.get("debt", ""),
                "effort": issue.get("effort", ""),
                "type": issue.get("type", ""),
                "creationDate": issue.get("creationDate", ""),
                "updateDate": issue.get("updateDate", ""),
                "closeDate": issue.get("closeDate", ""),
                "tags": ",".join(issue.get("tags", [])),
                "language": issue.get("language", "")
            })

    print("✅ CSV export completed!")

    # === Summary ===
    from collections import Counter
    print("\n📊 Issue Summary:")

    print("By Status:", Counter(issue["status"] for issue in all_issues))
    print("By Severity:", Counter(issue["severity"] for issue in all_issues))
    print("By Type:", Counter(issue["type"] for issue in all_issues))
    print("By Language:", Counter(issue.get("language", "UNKNOWN") for issue in all_issues))

else:
    print("No issues found for the given project.")
