#! python3
# CheckWMS.py - CheckWMS if alaive
# command line or clipboard.

import PushToGspread
import os
import requests
from PIL import Image
from io import StringIO
from owslib.wms import WebMapService
from math import sqrt
import sys

def WmsSources (my_input,my_sheet,my_creds):


        def check_blank(content):
            """
            Uses PIL (Python Imaging Library to check if an image is a single colour - i.e. blank
            Images are loaded via a binary content string
            Checks for blank images based on the answer at:
            http://stackoverflow.com/questions/1110403/how-can-i-check-for-a-blank-image-in-qt-or-pyqt
            """

            im = Image.open(content)
            # we need to force the image to load (PIL uses lazy-loading)
            # otherwise get the following error: AttributeError: 'NoneType' object has no attribute 'bands'
            im.load() 
            bands = im.split()

            # check if the image is completely white or black, if other background colours are used
            # these should be accounted for
            is_all_white = all(band.getextrema() == (255, 255)  for band in bands)
            is_all_black = all(band.getextrema() == (0, 0)  for band in bands)

            is_blank = (is_all_black or is_all_white)

            return is_blank

        #define functions
        # in this wrapper class you can use a string list instead of a full string like Im doing
        class StdOutWrapper:
                lines = []
                def write(self,txt):
                        self.lines.append(txt)
                def get_text(self):
                        return str('\n'.join(self.lines))

        #define ScaleHint based bbox
        def  calculateBounds(center, scaleDenominator, size_b):
            resolution = 1 / ((1 / scaleDenominator) * 4374754 * 72)
            halfWDeg = (size_b[0] * resolution) / 2 #width
            halfHDeg = (size_b[1] * resolution) / 2 #height
            return(
                center['lon'] - halfWDeg,
                center['lat'] - halfHDeg,
                center['lon'] + halfWDeg,
                center['lat'] + halfHDeg
                                )


        #Set Var
        size_b=(300, 250)
        my_sheet="WMSTEST"
        my_temp="checkwms_result/"
        my_creds="kompost-08abcd76df4c.json"
        my_data={"WMS_IDENT_TITLE":"n.a.","URL":"n.a","Layer":"n.a","Test_OGC":"n.a.","Test_Speed":"-9999","Test_Browser":"n.a.","MapGeo_Link":"n.a.","OtherError":""}


        #wms = WebMapService('http://wms.zh.ch/OrthoZHWMS?SERVICE=WMS&Request=GetCapabilities')
        #wms = WebMapService('https://ows.terrestris.de/osm/service')
        #my_input='https://wms.geo.gl.ch/'
        #my_input=('https://wms.geo.admin.ch/')
        #my_input='http://wms.geo.gr.ch/wms/admineinteilung'
        #wms = WebMapService('http://wms.vd.ch/public/services/wmsVD/Mapserver/Wmsserver')

        #check if server exists at all on level httpp
        try:
                request = requests.get(my_input)
                if request.status_code == 200:
                        #READ WMS
                            mystdout = StdOutWrapper() #-> undocument for production, when testing promtpt is messed up
                            sys.stdout = mystdout      #-> undocument for production, when testing promtpt is messed up
                            sys.stderr = mystdout      #-> undocument for production, when testing promtpt is messed up 
                            try:
                                wms = WebMapService(my_input)
                                my_data["OtherError"]= my_data["OtherError"]+" "+str(mystdout.get_text()) #-> undocument for production, when testing promtpt is meesed 
                                sys.stdout = sys.__stdout__ #-> undocument for production, when testing promtpt is meesed 
                                sys.stderr = sys.__stderr__ #-> undocument for production, when testing promtpt is meesed 

                                #filling in global variables
                                my_data["WMS_IDENT_TITLE"]= wms.identification.title
                                my_data["URL"]=wms.url

                                #playground for debugging
                                wms.identification.type
                                wms.identification.title
                                wmsurl=wms.url
                                list(wms.contents)
                                layers=list(wms.contents)

                                #JUST FOR TESTING FAST each WMS THIS LINE BELOW
                                #######layers=layers[0:1]#remove this line

                                #loop through layers of WMS

                                for i in layers:
                                        #Layer Name
                                        my_data["Layer"]= wms[i].title
                                        center_orig={'lat':(wms[i].boundingBoxWGS84[1]+wms[i].boundingBoxWGS84[3])/2,'lon':(wms[i].boundingBoxWGS84[0]+wms[i].boundingBoxWGS84[2])/2} #image center coordinates
                                        #Map.geo.admin.ch URL
                                        my_data["MapGeo_Link"] = r"https://map.geo.admin.ch/?bgLayer=ch.swisstopo.pixelkarte-grau&layers=WMS||"+wms[i].title+"||"+wms.url+"?||"+wms[i].title+"||"+wms.identification.version
                                        if wms[i].scaleHint is None:
                                                bbox_b=(wms[i].boundingBoxWGS84)
                                                #print('full extent taken')
                                        else:
                                                minscale=((float(wms[i].scaleHint['min'])/sqrt(2))*75/2.54*100)
                                                maxscale=((float(wms[i].scaleHint['max'])/sqrt(2))*75/2.54*100)
                                                bbox_b=(calculateBounds(center_orig,(maxscale-1000),size_b))
                                        #print('maxscale taken')
                                        #try:
                                        #print(wms[i].title)
                                        img = wms.getmap(   layers=[i],
                                                    srs=wms[i].crsOptions[0],
                                                    #srs='EPSG:4326',
                                                    bbox=bbox_b,
                                                    size=size_b,
                                                    #format=wms.getOperationByName('GetMap').formatOptions[0]
                                                    format='image/jpeg'
                                                    )
                                        #the follwoing url has been called
                                        #my_geturl=(img.geturl())
                                        outfile=my_temp+"getmapimage.jpeg"
                                        out = open(outfile, 'wb')
                                        out.write(img.read())
                                        out.close()
                                        #response time
                                        my_data["Test_Speed"]=requests.get(img.geturl()).elapsed.total_seconds()
                                        resp=requests.get(img.geturl())

                        #TEST OGC
                                        #check if image is empty
                                        if resp.headers['content-type'] == 'image/jpeg':
                                                # a PNG image was returned
                                                is_blank = check_blank(outfile)
                                                if is_blank:
                                                        print(wms[i].title+" : blank image but OK")
                                                        log_file = open(my_temp+"_deadwms.txt", 'a+')
                                                        log_file.write(wms[i].title+" : blank image"+"\n")
                                                        log_file.close()
                                                        my_data["Test_OGC"]="ok (blank_image)"
                                                        os.remove(outfile)
                                                        #send to gmail
                                                        PushToGspread.ExportToGoogle(my_data,my_sheet,my_creds)
                                                else:
                                                        #print("The image contains data.")
                                                        print(wms[i].title+" : OK")
                                                        my_data["Test_OGC"]="ok"
                                                        os.remove(outfile)
                                                        #send to gmail
                                                        PushToGspread.ExportToGoogle(my_data,my_sheet,my_creds)

                                        else:
                                                # if there are errors then these can be printed out here
                                                print(resp.content)
                                                #send to gmail
                                                PushToGspread.ExportToGoogle(my_data,my_sheet,my_creds)
                                    
                            except Exception as e:
                                    sys.stdout = sys.__stdout__ #-> undocument for production, when testing promtpt is messed 
                                    sys.stderr = sys.__stderr__ #-> undocument for production, when testing promtpt is messed 
                                    my_data["OtherError"]= my_data["OtherError"]+" "+str(mystdout.get_text()) #-> undocument for production, when testing promtpt is messed 
                                    log_file = open(my_temp+"_deadwms.txt", 'a+')
                                    log_file.write(my_input+", "+str(e)+"\n")
                                    log_file.close()
                                    print (e)
                                    my_data["Test_OGC"]= e
                                    my_data["URL"]= my_input
                                    #send to gmail
                                    PushToGspread.ExportToGoogle(my_data,my_sheet,my_creds)
                else:
                        log_file = open(my_temp+"_deadwms.txt", 'a+')
                        log_file.write(" 404 Client Error: Not Found for url:"+my_input+"\n")
                        log_file.close()
                        print ("404 Client Error: Not Found for url: "+my_input)
                        my_data["Test_OGC"]= "404 Client Error: Not Found for url: "+my_input
                        my_data["URL"]= my_input
                        my_data["OtherError"]= my_data["OtherError"]+"404 Client Error: Not Found for url: "+my_input
                        PushToGspread.ExportToGoogle(my_data,my_sheet,my_creds)
        except Exception as e_request:
                log_file = open(my_temp+"_deadwms.txt", 'a+')
                log_file.write(str(e_request)+" "+my_input+"\n")
                log_file.close()
                print (e_request)
                my_data["Test_OGC"]= str(e_request)+" "+my_input
                my_data["URL"]= my_input
                my_data["OtherError"]= my_data["OtherError"]+str(e_request)+" "+my_input
                PushToGspread.ExportToGoogle(my_data,my_sheet,my_creds)

        print(my_input+"..done")

        # create screenshot (wkhmtmltopdf is missing catch errors)
        #imgkit.from_url('http://google.com/retwertwer/fsdf/.index.html', 'out.jpg',options={"xvfb": ""})
