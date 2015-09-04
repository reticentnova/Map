import csv
import pprint
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


rawTagList = []
tagList = []
cabTagList = []
rawVisualList = []
visualMatches = []
visualList = []
writeList = []

lastRow = [""]

def findTags(rawTagList):
    tagRegex = r"""(?P<TagNum>[U]\d{6})(_)(?P<TagType>.[^']*)"""
    cabinetTagRegex = r"""(?P<TagNum>[C][C]\d+)(_)(?P<TagType>.[^']*)"""
    compile_tag = re.compile(tagRegex)
    compile_cabinet = re.compile(cabinetTagRegex)
    
    for row in rawTagList:
        match_tag = compile_tag.search(str(row))
        if match_tag:
            tagList.append(match_tag)

    for row in rawTagList:
        match_tag = compile_cabinet.search(str(row))
        if match_tag:
            cabTagList.append(match_tag)

    #pprint.pprint(tagList)
    #pprint.pprint(cabTagList)

            

def findVisuals(rawVisualList):
    visualRegex = r"""(?P<Visual>[U]\d{6}[^', ']*)(', ')(?P<Property>\w+)"""
    cabinetVisualRegex = r"""(?P<Visual>[C][C]\d+.\w+)(', ')(?P<Property>\w+)"""
    csVisualRegex = r"""(?P<Visual>[C][S]\d+.\w+)(', ')(?P<Property>\w+)"""
    compile_visual = re.compile(visualRegex)
    compile_cabinet_visual = re.compile(cabinetVisualRegex)
    compile_cs_visual = re.compile(csVisualRegex)
    
    for row in rawVisualList:
        match_visual = compile_visual.search(str(row))
        if match_visual:
            visualMatches.append(match_visual)

    for row in rawVisualList:
        match_visual = compile_cabinet_visual.search(str(row))
        if match_visual:
            visualMatches.append(match_visual)

    for row in rawVisualList:
        match_visual = compile_cs_visual.search(str(row))
        if match_visual:
            visualMatches.append(match_visual)

    #pprint.pprint(visualMatches)    

def match(tagList, visualMatches, tagDict):
    exclude = ["Aux","Mtr","MOL","Power","Mtr_Reset","Speed_FPM","LOCK","TripFault","DeleteLoadAfter",
               "DeleteRules","TripFault","DIRECTION","BrakeInstalled","FPM","FPM1","FPM2",
               "FLT_1","FLT_2","FLT_3","FLT_4","Speed_1","Speed_2","Speed_3","Speed_4",
               "Command","SPEED_XFER","SPEED_XPORT","BRK","CTRL","SS_AUT"]
    
    #List comp to remove any anything that should be excluded from our visualMatches list
    visualMatches[:] = [prop for index, prop in enumerate(visualMatches) if prop.group("Property") not in exclude]

    for index, item in enumerate(visualMatches):
        pprint.pprint(visualMatches[index].group("Visual") + ' ' + visualMatches[index].group("Property"))
        
def write(writeList):
    with open('131388_Map.csv', 'wb') as f:
        writer = csv.writer(f)
        fieldnames = ['Item','Server','Access','Visual','Property']
        writer.writerow(fieldnames)

        for row in writeList:
            writer.writerow(row)


if __name__ == "__main__":
    with open("131388_Emulation_Tag_Export_TEST.csv") as tags_obj:
        tagReader = csv.reader(tags_obj)

        for row in tagReader:
            rawTagList.append(row)
        tagDict = dict(rawTagList)



    with open("131388-01VisualProperties_TEST.csv") as visuals_obj:
        visualReader = csv.reader(visuals_obj)

        for row in visualReader:
            rawVisualList.append(row)
    #pprint.pprint(rawVisualList)


    findTags(rawTagList)

    findVisuals(rawVisualList)

    match(tagList,visualMatches,tagDict)
