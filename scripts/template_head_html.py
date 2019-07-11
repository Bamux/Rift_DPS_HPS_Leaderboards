import codecs

html = []
head = "head.html"
html_file = "index.html"
title = "Rift Overall DPS Leaders"
template = codecs.open("../template/" + head, 'r', "utf-8")
for line in template:
    if '<title>' in line:
        html += "    <title>" + title + "</title>"
    elif html_file in line:
        html += ['                <li class="nav-item active">']
        line = line.split("</a>")[0]
        html += [line + '<span class="sr-only">(current)</span>']
    elif '<li class="nav-item active">' not in line:
        html += [line]
for line in html:
    print(line)

template.close()
