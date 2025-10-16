def smart_split(s: str):
    # splits on commas and semicolons without being too fancy
    for sep in [",", ";", "\n"]:
        s = s.replace(sep, "|")
    return [x.strip() for x in s.split("|")]
