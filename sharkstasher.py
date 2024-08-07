import json
import os
import requests
import time

baseurl = "https://e621.net/posts.json"
headers = {"user-agent": "sharkstasher/0.90 (by liminaldot)"}

#searchtags = "rating:s female anthro shark solo"
searchlimit = 320
page = 1
pageparam = ""
islastpage = False
#finalurl = baseurl + "?tags=" + searchtags.replace(" ", "+") + "&limit=" + str(searchlimit)

gentags = []
gentagsuniq = []

NTFScharreplace = [
    (":", ";"),
    ("*", "(ast)"),
    ("\"", "'"),
    ("<=", "le"),
    (">=", "ge"),
    ("<", "lt"),
    (">", "gt"),
    ("/", ""),
    ("\\", ""),
    ("|", ""),
    ("?", "")
]

searchtags = input("Enter query: ").lower()
# replace Windows (NTFS) disallowed characters
queryfolder = searchtags
for disallowed, replace in NTFScharreplace:
    queryfolder = queryfolder.replace(disallowed, replace)

#if searchtags == "":
#    print("No tags specified.")
if not os.path.isdir(queryfolder):
    print("Creating folder \"%s\"..." %(queryfolder))
    os.mkdir(queryfolder)
else:
    print("Folder \"%s\" already exists" %(queryfolder))
print("Files will be saved to \"%s\"" %(queryfolder))
os.chdir(queryfolder)

finalurl = baseurl + "?tags=" + searchtags.replace(" ", "+") + "&limit=" + str(searchlimit)
print(finalurl)

while not islastpage:
    print("Getting page %d for %s..." %(page, searchtags))
    webpageget = requests.get((finalurl+pageparam), headers=headers)
    time.sleep(1)
    jsoncontent = webpageget.json()

    # offline mode -- bring your own posts.json
    #with open("posts.json", "r") as file:
    #    jsoncontent = json.load(file)

    if len(jsoncontent["posts"]) == 0:
        print("Nothing to do! (0 posts found)")
        islastpage = True
        continue

    for post in jsoncontent["posts"]:
        imageid = post["id"]
        imageext = post["file"]["ext"]
        imageurl = post["file"]["url"]
        imagefilename = str(imageid) + "." + imageext
        if not os.path.isfile(imagefilename):
            print("Downloading %s..." %(imagefilename))
            imageget = requests.get(imageurl, headers=headers)
            with open(imagefilename, "wb") as image:
                image.write(imageget.content)
        else:
            print("File %s already exists" %(imagefilename))
        imagegentags = post["tags"]["general"]
        gentags.extend(imagegentags)
    for tag in gentags:
        if tag not in gentagsuniq:
            gentagsuniq.append(tag)
    gentagsuniq.sort(key=gentags.count, reverse=True)
    #for tag in gentagsuniq:
    #    print("Occurrences of %s: %d" %(tag, gentags.count(tag)))

    # Returned results may span multiple pages.
    # If (current page) has (search limit) posts, get ID of last post
    # and append it to finalurl as "&page=b(lastID)"
    if len(jsoncontent["posts"]) == searchlimit:
        lastpostid = jsoncontent["posts"][(searchlimit-1)]["id"]
        pageparam = "&page=" + "b" + str(lastpostid)
        page += 1
    else:
        islastpage = True
        print("Reached last page~")
