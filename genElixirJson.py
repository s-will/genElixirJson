#!/usr/bin/env python
from Cheetah.Template import Template
import argparse

def stripThem(them):
    return [ s.strip() for s in them ]

def parseNestedMultipleEntries(formatString):
    """
    Parse entry with multiple sub-entries, separated by '|',
    which are multiple entries separated by ','
    """
    return [ stripThem(f.split(',')) 
             for f in stripThem(formatString.split("|")) ]

def parseMultipleEntries(typeString):
    """
    Parse entry with multiple sub-entries, separated by '|'
    """
    return stripThem(typeString.split("|"))

def fillRowDict(keyNames,line):
    entries=dict()
    print
    F=line.split('\t')
    for i,key in enumerate(keyNames):
        F[i]=F[i].strip()
        print('#',key,"=",F[i])
        entries[key]=F[i]
    return entries

def processMultipleEntries(entries):
    # handle "optional input"
    entries["Input_format"] = entries["Essential_input_format"] #  +" | "+entries["Optional_input_format"]
    entries["Input_type"] = entries["Essential_input"]+" | " #  +entries["Optional_input"]
    
    # process multiple input fields
    for x in ["Input_format","Output_Format"]:
        entries[x] = entries[x].replace("PNG","Image format")
        entries[x] = entries[x].replace("SVG","Image format")
        entries[x] = parseNestedMultipleEntries(entries[x])
        
    for x in ["Contact1_Role","Contact2_Role","Input_type","Output_Type","Topic","Function_name_EDAM_operation"]:
        entries[x] = parseMultipleEntries(entries[x])
    
    return entries

def cleanHeaderName(h):
    return h.rstrip().replace(" ","_").replace("(","").replace(")","")

def fillTemplateFromTableRows(tablefile,templateDef):
    with open(tablefile) as fh:
        header=map(cleanHeaderName, fh.readline().split('\t'))
        for line in fh:
            entries = fillRowDict(header,line)
            
            entries = processMultipleEntries(entries)
            
            entries["Credits_Developer"] = entries["Contact2"]
            
            entries["PMID"] = (entries["PMID"].split(";"))[0]

            # ----------------------------------------
            # fill template and write to file
            t = Template(templateDef, searchList=entries)
            
            with open(entries["Name"]+".json","w") as fh:
                fh.write( t.respond() )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ELIXIR Json records from table")
    parser.add_argument('--template',default="ELIXIR_json_template.cheetah",help="Template file")
    parser.add_argument('--table',help="Table file")
    
    args = parser.parse_args()
    with open(args.template) as fh:
        templateDef=fh.read()
        fillTemplateFromTableRows(args.table,templateDef)
