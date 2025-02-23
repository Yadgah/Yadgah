import subprocess
import os
from datetime import datetime

def get_last_commit():
    # Get the information of the last commit
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=format:%H%n%an%n%ad%n%s", "--date=short"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("Error executing git commands.")
        return None
    return result.stdout.strip().split("\n")

def update_changelog(commit_info, lang):
    if not commit_info or len(commit_info) < 4:
        print("Invalid commit information.")
        return

    commit_hash, author, date, message = commit_info
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Choose the filename based on the language
    changelog_file = f"CHANGELOG_{lang.upper()}.md"

    # Translate sections for Persian and English files
    if lang == 'fa':
        changelog_title = "تغییرات پروژه"
        intro = "تمام تغییرات مهم این پروژه در اینجا مستند می‌شود."
        added_title = "اضافه شد"
        fixed_title = "رفع شد"
    else:
        changelog_title = "Changelog"
        intro = "All significant changes to this project will be documented here."
        added_title = "Added"
        fixed_title = "Fixed"
    
    # Template for the new entry
    new_entry = f"- **{message}**: {message} [{author}]\n"

    if os.path.exists(changelog_file):
        with open(changelog_file, "r") as file:
            content = file.readlines()
    else:
        # If the file doesn't exist, create a new file with the initial structure
        content = [
            f"# {changelog_title}\n\n",
            f"{intro}\n\n",
        ]

    # Check if a section for today's date exists
    today_section = f"## [{today}]\n"
    if today_section in content:
        # Add the new entry to the existing date section
        index = content.index(today_section) + 2
        content.insert(index, new_entry)
    else:
        # Create a new section for today's date
        content.append("\n---\n\n")
        content.append(today_section)
        content.append(f"### {added_title}\n")
        content.append(new_entry)

    with open(changelog_file, "w") as file:
        file.writelines(content)

    print(f"{changelog_file} has been updated.")

if __name__ == "__main__":
    commit_info = get_last_commit()
    
    # Update both Persian and English files
    update_changelog(commit_info, 'fa')
    update_changelog(commit_info, 'eng')

