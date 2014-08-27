'''
    Created on 06.06.2014
    
    @author: chm
'''
import json
import collections
class jsonschematorst:
    def __init__(self,schemapath):
        
        self.schema=json.load(
                                    open(schemapath),
                                    object_pairs_hook=collections.OrderedDict
                                    )
    def toRsT(self,schema=None, jsonpath='',key=''):
        """
        converts subschema to RST Markup
        """
        if schema is None:
            schema=self.schema
        if jsonpath=='': 
            jsonpath+=":ref:`# <root>` "
        RsT=''
        if '$schema'in schema:
            RsT+=".. raw:: html\n\n    <style> .red {color:red} </style>\n\n"
            RsT+=".. role:: red\n\n.. _root:"
            RsT+=".. _required:\n\n The ':red:`*`' signifies a required Field.\n\n"
            
        
        RsT+=self.typetoRST(schema,"",jsonpath)+"\n"
        RsT+=self.serialisejson(self.makejsonexample(schema,key))
        if 'properties'in schema:
            subschema=schema['properties']
            RsT+=self.makesection(subschema,jsonpath)
        if 'items' in schema:
            for item in schema['items']:
                if 'properties'in item:
                    RsT+=self.makesection(item['properties'], jsonpath+'[0]')
        elif 'oneOf'in schema:
            subschema=schema['oneOf']
            for oneschema in subschema:  
                if 'properties'in oneschema:
                    RsT+=self.makesection(oneschema['properties'], jsonpath)
                else:
                    RsT+=self.typetoRST(oneschema, key, jsonpath)
                
            
        return RsT
        
    def typetoRST(self,typedic,key,jsonpath):
        rst=''
        key=''
        if True:
          
            if 'description' in typedic:
                rst+=""+self.printdesc(typedic['description'])+'\n\n'
            if "type" in typedic:    
                if typedic['type']=='array':
                        rst+=self.arraytoRST(typedic)
                else:
                    rst+=":Type:\n  "+typedic['type']
                    if 'units'in typedic:
                        rst+=" in "+ typedic['units']
            else:
                rst+=':type:\n  object\n\n'
            rst+='\n'
            if 'enum' in typedic:
                rst+=":values:\n  ``"+str(typedic["enum"])+"``\n\n"
            if 'properties' in typedic:
                rst+=":Contains:\n  " 
                proploop=0
                for prop in typedic['properties'].keys():
                    if "$ref" in typedic['properties'][prop]:
                        rst+=':ref:`'+prop+"<"+typedic['properties'][prop]['$ref']+">`"
                    else:
                        rst+=':ref:`'+prop+" <"+self.getid(typedic['properties'],prop)+'>`'
                    if "required" in typedic['properties'][prop]:
                        if typedic['properties'][prop]['required']:
                            rst+=":red:`*`"
                    proploop+=1
                    if proploop!=len(typedic['properties'].keys()):
                        rst+=', '
                    else:
                        rst+='\n'
            
            
            if 'oneOf' in typedic:
                rst+=":Contains:\n one of  "
                proploop=0
                for oneofschema in typedic['oneOf']:
                    if 'properties'in oneofschema:
                        for key in oneofschema['properties'].keys():
                          
                            if key!="comment":
                                proploop+=1    
                                rst+=':ref:`'+key+'`'
                                
                                if proploop<len(typedic['oneOf']):
                                    rst+=' or '
                                else:
                                    rst+='\n'
                
            
            
            if 'required' in typedic:
                rst+=":Required:\n  "+str (typedic['required'])+'\n'
            else:
                rst+=":Required:\n  "+str (False)+'\n'
        
            if 'default'in typedic:
                rst+=":Default:\n  " +str(typedic['default'])+'\n'
            if "minimum"in typedic or "maximum" in typedic:
                rst+=":Constraints:\n  "  
                if "minimum" in typedic:
                    rst+="min:"+ str(typedic["minimum"])
                if "maximum" in typedic:
                    rst+=",max:"+ str(typedic["maximum"])
                rst+="\n\n"
                    
                 
            
            rst+=":JSON Path:\n  * "+jsonpath+"\n"
            if jsonpath.startswith("//"):
                if "id" in typedic:
                    print self.jsonPathAllRefsTothis(typedic['id'])
                    rst+="  * "+"\n  * ".join(self.jsonPathAllRefsTothis(typedic['id']) )
            if "appinfo" in typedic:
                if "oldsymbol" in typedic['appinfo']:
                    rst+=":Old Symbol:\n  ``"+typedic['appinfo']['oldsymbol']+"``\n"
        return rst
    def jsonPathAllRefsTothis(self,idst):
        path="/"
        return self.walkpathsWref(self.schema['properties'],idst,path)+self.walkpathsWref(self.schema['definitions'],idst,"//")
    
    
    def walkpathsWref(self,schema,idst,path):
            pathlist=[]
         
            for key in schema:
                if 'properties' in schema[key]:
                    npath=self.addkeytojsonpath(path, key, self.getid(schema, key))
                    if "properties" in schema[key]:
                        pathlist=pathlist+(self.walkpathsWref(schema[key]['properties'],idst,npath))
                    
                if  "$ref" in schema[key]:
                    if schema[key]['$ref']==idst:
                        npath=self.addkeytojsonpath(path, key, self.getid(schema, key))
                        pathlist.append(npath)
                
            return pathlist
        
    def searchkeyrecursive(self,mydict,searchkey):
        found=False
        for key in mydict:
            if key==searchkey:
                return True
            print type(mydict[key])
            if type(mydict[key])=="<class 'collections.OrderedDict'>":
                found= self.searchkeyrecursive(mydict[key],searchkey)
        return found
    def arraytoRST(self,typedic):
        rst=u''
        rst+=':Type:\n  array('
        if 'maxItems' in typedic:
            rst+=str(typedic['maxItems'])
        rst+=')'
        rst+=" items: "
        for item in typedic['items']:
            if item["type"]=="object":
                rst+="{"
                count=1
                for p in item['properties']:
                    rst+=":ref:`"+p+'`'
                 
                    if count!= len(item['properties']):
                        rst+=", "
                    count+=1
                rst+='}'
            else:
                rst+=item['type']+" "
            
        return rst
    def printdesc(self,desc):
        rst=""
        
        rst+=desc+'\n'
        return rst
    def addkeytojsonpath(self,jsonpath,key,ids):
        return jsonpath+"[':ref:`"+key+" <"+ ids +">`']"
    
    def getid(self,typeo,key):
        if 'id' in typeo[key]:
            return typeo[key]["id"]
        else:
            return key
    def indent(self,lines, amount, ch=' '):
        padding = amount * ch
        return padding + ('\n'+padding).join(lines.split('\n'))
    def serialisejson(self,dictype):
        rst="Example JSON: "
        #rst+="You can copy this code in you configuration file to the appropriate locations.\n\n"
        rst+="\n\n.. code:: json\n\n"
        jasonstr= json.dumps(dictype, separators=(',', ': '))
        if len(jasonstr)>60:
            jasonstr=json.dumps(dictype, indent=2,separators=(',', ': '))
        rst+= self.indent(
                    jasonstr
                     ,4)+"\n\n"
        return rst
    
    def makejsonexample(self,schema,key):
        if key=="":
            return self.gentypeexample(schema,key)
        else:
            return collections.OrderedDict([(key,self.gentypeexample(schema,key))])
        
    def gentypeexample(self,schema,key):
        dictype=collections.OrderedDict()
        #if "$ref" in schema:
        #    schema,key=self.resolveref(schema)
        if "enum" in schema:
            return schema['enum'][0] 
        else:
            if 'oneOf' in schema:
                for key in schema["oneOf"][0]['properties']:
                    if key!="comment":
                        
                        dictype[key]=self.gentypeexample(schema["oneOf"][0]['properties'][key],key)
                return dictype
            if "type" in schema:
                if schema["type"]=="object":         
                    dictype ={} 
                    if 'properties' in schema:
                        for key in schema["properties"]:
                            print key
                            if "$ref" in schema["properties"][key]:
                                if "required" in schema["properties"][key]:
                                    if schema["properties"][key]["required"]:
                                        refschema,refkey=self.resolveref(schema["properties"][key]["$ref"])
                                        dictype[key]=self.gentypeexample(refschema,refkey)
                            elif 'required' in schema["properties"][key]:
                                if schema["properties"][key]["required"]:
                                    dictype[key]=self.gentypeexample(schema["properties"][key],key)
                            if 'default' in schema:
                                print "+++++++++++++++++++++++default",key 
                                if schema['default'] ==key:
                                    dictype[key]=self.gentypeexample(schema["properties"][key],key)
                                   
                        return dictype
                   
                else:
                    if schema["type"]=="number" or schema["type"]=="integer":
                        if 'default'in schema:
                            return schema["default"]
                        else:
                            return 0
                    if schema["type"]=="string":
                        if 'default'in schema:
                            return schema["default"]
                        else:
                            return ""
                    if schema['type']=="array":
                        if 'default'in schema:
                            return schema["default"]
                        else:
                            if 'minItems'in schema:
                                return range(schema['minItems'])
                    if schema['type']=="boolean":
                        if 'default'in schema:
                            return schema["default"]
                        else:
                            return True
            else:
                return collections.OrderedDict([])
                    
    
    def makesection(self,oneschema,jsonpath):
        RsT=""
        for key in oneschema.keys():
            if not '$ref' in oneschema[key]:
                RsT+=".. _"+self.getid(oneschema,key)+':\n\n'+key+"\n"+"--------------------\n\n"
                RsT+=self.toRsT(schema=oneschema[key],key=key,jsonpath=self.addkeytojsonpath(jsonpath,key,self.getid(oneschema,key)))
               
        return RsT   
    def refstoRST(self):
            jsonpath="//"
            return self.makesection(self.schema['definitions'],jsonpath)
    def resolveref(self,ref):
        
        for key in self.schema['definitions']:
            if self.schema['definitions'][key]["id"]==ref:
                return self.schema['definitions'][key],key
            
        
        
        