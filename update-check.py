import json
import subprocess
import sys
import urllib.request


def git(*args):
    return subprocess.run(["git", *args], check=False).returncode


def latest_release():
    request = urllib.request.Request(
        "https://api.github.com/repos/protonmail/proton-bridge/releases/latest",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "protonmail-bridge-docker-update-check",
        },
    )

    with urllib.request.urlopen(request) as response:
        return json.load(response)


release = latest_release()
version = release["tag_name"]
deb_assets = [
    asset["browser_download_url"]
    for asset in release["assets"]
    if asset["name"].endswith(".deb")
]

if not deb_assets:
    print("No Debian package found on latest Proton Bridge release")
    sys.exit(1)

print(f"Latest release is: {version}")

with open("VERSION", "w") as f:
    f.write(version)

with open("deb/PACKAGE", "w") as f:
    f.write(deb_assets[0])

git("config", "--local", "user.name", "GitHub Actions")
git("config", "--local", "user.email", "actions@github.com")
git("add", "-A")

if git("diff", "--cached", "--quiet") == 0:
    print("Version didn't change")
    sys.exit(0)

if git("commit", "-m", f"chore: bump Proton Bridge to {version}") != 0:
    print("Git commit failed!")
    sys.exit(1)

is_pull_request = sys.argv[1] == "true"

if is_pull_request:
    print("This is a pull request, skipping push step.")
    sys.exit(0)

if git("push") != 0:
    print("Git push failed!")
    sys.exit(1)
