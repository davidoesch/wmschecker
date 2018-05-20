import urllib.request
import checkwms2
import PushToGspread

my_sheet="WMSTEST"
my_creds="kompost-08abcd76df4c.json"

#read WMS from Github account. tbd from Geocat
url = 'https://raw.githubusercontent.com/geoadmin/mf-geoadmin3/master/src/js/ImportController.js'
urllib.request.urlretrieve(url,"import.js")

# Replace strings of präfix and postfix from github list
with open("import.js", 'r') as file :
  filedata = file.read()

# Replace the target string
filedata = filedata.replace("'http", "http")
filedata = filedata.replace("',", "")

# Write the file out again
with open("import.js", 'w') as file:
  file.write(filedata)

#remove geo.admin and commented line and the bllody wmts from zurich in the wms line  
bad_words = ['// non-SwissProjected',"geo.admin.ch","mapproxy/wmts/1.0.0/WMTSCapabilities"]

with open('import.js') as oldfile, open('import_clean.js', 'w') as newfile:
    for line in oldfile:
        if not any(bad_word in line for bad_word in bad_words):
            newfile.write(line)
newfile.close()

#look for the starting line in the file: containing only wms URLS 
with open("import_clean.js") as myFile:
    for num, line in enumerate(myFile, 1):
        if "servers = ["  in line:
            #print(num)
            numstart=num
#look for the End of WMS list in the import.json file
with open("import_clean.js") as myFile:
    for num, line in enumerate(myFile, 1):
        if "// WMTS servers"  in line:
            #print(num)
            numend=num
print(str(numend-numstart) + " to test")
#import cleaned json into a list var
lines = [] #Declare an empty list named "lines"
with open ('import_clean.js', 'rt') as in_file:  #Open file  for reading of text data.
    for line in in_file: #For each line of text store in a string variable named "line", and
        lines.append(line)  #add that line to our list of lines.

#print(lines)        #print the list object.
#extract the WMS list based on the s
urls=lines[numstart:numend-1]


#cleaning up existing spreadsheet
PushToGspread.ClearGoogle(my_sheet,my_creds)
print("emptying spreadsheet")

for i in urls:
	print(i.strip())
	checkwms2.WmsSources(i.strip(),my_sheet,my_creds)



