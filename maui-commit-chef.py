import os
import re
import sys
import subprocess
import xml.etree.ElementTree as ET

working_dir: str = os.getcwd()

def get_csproj ()-> str:
    dir_entries = os.scandir(working_dir)
    for entry in dir_entries:
        if entry.name.endswith(".csproj"):
            return entry.path
    return None

def check_stderr(stderr):
    errored =  bool (stderr.decode("utf-8").strip())  
    if errored:
        sys.exit(stderr.decode("utf-8"))

def get_git_tags ():
    fetch_results = subprocess.run(["git", "fetch","--all", "--tags"], capture_output=True)
    check_stderr(fetch_results.stderr) 
    
    results = subprocess.run(["git", "tag","-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    check_stderr(results.stderr) 

    tag_list = results.stdout.decode("utf-8").split("\n")
    return [tag for tag in tag_list if bool(tag.strip())]

def git_tag_show(tag: str)-> str:
    results = subprocess.run(["git", "show", tag], capture_output=True)
    check_stderr(results.stderr)

    return results.stdout.decode("utf-8")

def get_last_tag_block(tag: str)-> str:
    str_message = git_tag_show(tag)

    tag_block_tester = re.compile("tag(.+)\nTagger:(.+)\nDate:(.+)")
    matches = tag_block_tester.search(str_message)
    groups = matches.groups()
    (version, tagger, date) = groups
    return {
        "version": version.strip(),
        "tagger": tagger.strip(),
        "date": date.strip() 
    }

def git_commits_after_date(date):
    results = subprocess.run(["git", "log", f"--since={date}", "--oneline"], capture_output=True)
    check_stderr(results.stderr)

    lines = results.stdout.decode("utf-8").strip().split("\n")
    return [line for line in lines if line!="None"]

def bump_version(new_commits, original_version):
    (major, minor, patch) = original_version
    for commit in new_commits:
            commit_stem = commit.split(":", maxsplit=1)[0]
            (is_major, is_minor, is_patch) = "!" in commit_stem, "feat" in commit_stem, "fix" in commit_stem
            
            if is_major:
                major +=1
                minor = 0
                patch = 0
                continue

            if is_minor:
                minor += 1
                patch = 0
                continue
            
            if is_patch:
                patch +=1
                continue
    return (major, minor, patch)

def generate_csproj(csProj: str, new_version):
    (major, _, _) = new_version
    new_proj_file = None
    with open(csProj, "r", encoding="utf-8") as f:
        text = f.read()                
        root = ET.fromstring(text)
        for property_group in root.iter("PropertyGroup"):
            app_display_version = property_group.find("ApplicationDisplayVersion")
            if app_display_version is not None:
                app_display_version.text = ".".join([str(version_num) for version_num in new_version]) 
                print(app_display_version.text)

            app_version = property_group.find("ApplicationVersion")
            if app_version is not None:
                app_version.text = str(major)
                print(app_version.text)
        
        new_proj_file = ET.tostring(root, encoding="unicode")
    return new_proj_file

def write_cs_proj(newCsProj: str, filePath: str):
    with open(filePath, "w", encoding="utf-8") as f:
        f.write(newCsProj)

if __name__ == "__main__":
    
    try:
        csproj_path = get_csproj()
        
        if not csproj_path:
            raise Exception("csproj not found")
        
        tags = get_git_tags()
        last_tag = tags [-1]
        
        last_tag_block = get_last_tag_block(last_tag)
        
        new_commits = git_commits_after_date(last_tag_block["date"])
        new_commits = list(reversed(new_commits))
        
        if len(new_commits) == 0:
            sys.exit() 
        
        last_version = last_tag_block["version"]
        [major, minor, patch] = last_version.replace("v", "").split(".")

        initial_version = major, minor, patch = 0,1,0
        
        # loop over each commit, updating the build
        new_version = bump_version(new_commits, initial_version)

        if new_version != initial_version:
            new_cs_proj = generate_csproj(csproj_path, new_version)
            write_cs_proj(new_cs_proj, csproj_path)
    except:
        sys.exit("Failed to run Maui commit chef")