from core.changelog_fetcher import fetch_mock_changelog
tools = ["Zoom", "365", "Bloomberg"]

for tool in tools:
    changelogs = fetch_mock_changelog(tool)
    print(f"\n🔧 {tool} Updates:")
    if not changelogs:
        print("No changelogs found.")

    else:
        for update in changelogs:
            print(
                f"  📅 {update['date']}: {update['title']} — {update['description']}")
