import sys
import requests
import lxml.html

def main(argv):
    if(len(argv) != 2):
        print("Usage: python %s <address>" %argv[0])
        return -1

    doc = lxml.html.fromstring(requests.get(argv[1]).content)
	# Open a file for output.
    filed = open('./answers5c.txt', 'w')

    filed.write("Website:\n%s" % argv[1])
    
    # A. get all src attribute for imagaes that has attribute @alt and @alt is not empty
    filed.write("\n\na. All 'src' attributes of images that has a non-empty 'alt' attribute:\n")
    for src in doc.xpath("//img[@alt and not(@alt = '')]/@src"):
        filed.write("---\t" + src + "\n")
    
    # B. external links that contains "http" in @href, from domain contains ".co.il" in @href
    filed.write("\n\nb. All external links with co.il domain:\n")
    for link in doc.xpath("//a[contains(@href,'.co.il') and contains(@href,'http')]/@href"):
        filed.write("---\t" + link + "\n")
    
    # C. the content of the first 'table', second 'tr' label, text of each column ('td' label)
    filed.write("\n\nc. The content of the second row of the first table:\n")
    for cont in doc.xpath("//table[1]//tr[position()=2]//td//text()"):
        filed.write("---\t" + cont + "\n")
    
    # D. all text that is in 'ITALIC' mode
    filed.write("\n\nd. All text that with ITALIC:\n")
    for italicWord in doc.xpath("//i//text()"):
        filed.write("---\t" + italicWord + "\n")
    
	# Close the file at the end.
    filed.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
