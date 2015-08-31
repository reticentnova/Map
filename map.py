import csv
import pprint
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


rawTagList = []
tagList = []
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
            tagList.append(match_tag.group(0))

    for row in rawTagList:
        match_tag = compile_cabinet.search(str(row))
        if match_tag:
            tagList.append(match_tag.group(0))

    #pprint.pprint(tagList)

            

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

    lastRow = []
    
    for count, item in enumerate(visualMatches):
        visualList.append(visualMatches[count].group("Visual")+' '+visualMatches[count].group("Property"))
        
    choices = tagList
    exclude = ["MOL","Power","Mtr_Reset","Speed_FPM","LOCK","TripFault","DeleteLoadAfter",
               "DeleteRules","TripFault","DIRECTION","BrakeInstalled","FPM","FPM1","FPM2",
               "FLT_1","FLT_2","FLT_3","FLT_4","Speed_1","Speed_2","Speed_3","Speed_4",
               "Command","SPEED_XFER","SPEED_XPORT","BRK","CTRL","SS_AUT"]
    
    for count, item in enumerate(visualMatches):
        print(visualMatches[count].group("Visual")+' '+visualMatches[count].group("Property"))
        
        match1, match2, match3= process.extract(visualMatches[count].group("Visual")+' '+visualMatches[count].group("Property"),choices,limit=3)


            ##Exclude Junk##
        
        if(visualMatches[count].group("Property") in exclude):
            print("This is excluded")
            del visualMatches[count]
            pass


            ##Map Con to MTR for Using Contactor with VFDs##

        elif(visualMatches[count].group("Property") == "Con"):
            if("MTR" in match1[0]):
                conMatch = match1[0]
            elif("MTR" in match2[0]):
                conMatch = match2[0]
                
                tempMatch = [conMatch, 'ControlLogix', 'ReadFromPLC', visualMatches[count].group("Visual"), visualMatches[count].group("Property")]
            if(tempMatch != lastRow):
                writeList.append(tempMatch)
                del visualMatches[count]
            lastRow = tempMatch
                

            ##Map SRM to SLG Tag##

        elif(visualMatches[count].group("Property") == "SRM"):
            srmMatch = visualMatches[count].group("Visual")+"_IM_SLG"

            tempMatch = [srmMatch, 'ControlLogix', 'ReadFromPLC', visualMatches[count].group("Visual"), visualMatches[count].group("Property")]

            if(tempMatch != lastRow):
                writeList.append(tempMatch)
                del visualMatches[count]
            lastRow = tempMatch

            

            ##VFD Matching##

        elif(visualMatches[count].group("Property") == "iDriveStatus"):
            vfdInputTag = visualMatches[count].group("Visual")+"_VFD:I.DriveStatus"
            tempMatch = [vfdInputTag, 'ControlLogix', 'WriteToPLC', visualMatches[count].group("Visual"), visualMatches[count].group("Property")]

            if(tempMatch != lastRow):
                writeList.append(tempMatch)
                del visualMatches[count]
            lastRow = tempMatch

        elif(visualMatches[count].group("Property") == "iOutputFreq"):
            vfdInputTag = visualMatches[count].group("Visual")+"_VFD:I.OutputFreq"
            tempMatch = [vfdInputTag, 'ControlLogix', 'WriteToPLC', visualMatches[count].group("Visual"), visualMatches[count].group("Property")]

            if(tempMatch != lastRow):
                writeList.append(tempMatch)
                del visualMatches[count]
            lastRow = tempMatch

        elif(visualMatches[count].group("Property") == "oLogicCommand"):
            vfdInputTag = visualMatches[count].group("Visual")+"_VFD:O.LogicCommand"
            tempMatch = [vfdInputTag, 'ControlLogix', 'ReadFromPLC', visualMatches[count].group("Visual"), visualMatches[count].group("Property")]

            if(tempMatch != lastRow):
                writeList.append(tempMatch)
                del visualMatches[count]
            lastRow = tempMatch

        elif(visualMatches[count].group("Property") == "oFreqCommand"):
            vfdInputTag = visualMatches[count].group("Visual")+"_VFD:O.FreqCommand"
            tempMatch = [vfdInputTag, 'ControlLogix', 'ReadFromPLC', visualMatches[count].group("Visual"), visualMatches[count].group("Property")]

            if(tempMatch != lastRow):
                writeList.append(tempMatch)
                del visualMatches[count]
            lastRow = tempMatch


    
           ##Match Uncertain Cases##         

        elif((match1[1]<75) and (visualMatches[count].group("Property") not in match1[0])):
            print(match1)
            print(match2)
            print(match3)

            narrowChoices = [match1[0] ,match2[0], match3[0]]
            match4 = process.extractOne(visualMatches[count].group("Property"), narrowChoices)
            
            if (match4[1] > 40):
                
                if("I" in tagDict[match4[0]]): 
                    tempMatch = [match4[0], 'ControlLogix', 'WriteToPLC', visualMatches[count].group("Visual"), visualMatches[count].group("Property")]

                elif("O" in tagDict[match4[0]]): 
                    tempMatch = [match4[0], 'ControlLogix', 'ReadFromPLC', visualMatches[count].group("Visual"), visualMatches[count].group("Property")]
                if(tempMatch != lastRow):
                    writeList.append(tempMatch)
                    del visualMatches[count]
                lastRow = tempMatch
            else:
                print("Confidence not high enough. Confirm manually.")
                pass

            

            ##Normal Matching##
            
        else:
            print(match1)
            print(match2)
            print(match3)


            if("I" in tagDict[match1[0]]): 
                tempMatch = [match1[0], 'ControlLogix', 'WriteToPLC', visualMatches[count].group("Visual"), visualMatches[count].group("Property")]

            elif("O" in tagDict[match1[0]]): 
                tempMatch = [match1[0], 'ControlLogix', 'ReadFromPLC', visualMatches[count].group("Visual"), visualMatches[count].group("Property")]

            if(tempMatch != lastRow):
                writeList.append(tempMatch)
                del visualMatches[count]
                
            lastRow = tempMatch
        print("\n")


    print("**********LEFTOVERS**********")
    for count, item in enumerate(visualMatches):
        print(visualMatches[count].group("Visual")+' '+visualMatches[count].group("Property"))
    write(writeList)

def write(writeList):
    with open('129414_Map.csv', 'wb') as f:
        writer = csv.writer(f)
        fieldnames = ['Item','Server','Access','Visual','Property']
        writer.writerow(fieldnames)

        for row in writeList:
            writer.writerow(row)


if __name__ == "__main__":
    with open("129414_Emulation_Tag_Export.csv") as tags_obj:
        tagReader = csv.reader(tags_obj)

        for row in tagReader:
            rawTagList.append(row)
        tagDict = dict(rawTagList)



    with open("129414_101VisualProperties.csv") as visuals_obj:
        visualReader = csv.reader(visuals_obj)

        for row in visualReader:
            rawVisualList.append(row)
    pprint.pprint(rawVisualList)


    findTags(rawTagList)

    findVisuals(rawVisualList)

    match(tagList,visualMatches,tagDict)
