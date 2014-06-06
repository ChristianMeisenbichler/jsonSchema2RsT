'''
Created on 06.06.2014

@author: chm
'''

def toRsT(schema):
    RsT=''
    subschema=schema['properties']
    for key in subschema.keys():
       
        RsT+="Property:"+key+"\n"
        RsT+=typetoRST(subschema[key])+"\n"
        if 'properties' in subschema[key]:
            RsT+=toRsT(subschema[key])
        
    return RsT
    
def typetoRST(typedic):
    rst=''
    if 'description' in typedic:
        rst+=typedic['description']+'\n'
        
    if typedic['type']=='array':
            rst+=arraytoRST(typedic)
    else:
        rst+="  Type:"+typedic['type']
        if 'units'in typedic:
            rst+=" in "+ typedic['units']
        
    rst+='\n'
    
    if typedic['required']==True:
        rst+="  required\n"
    else:
        rst+="  defaultvalue: " +typedic['default']
    return rst

def arraytoRST(typedic):
    rst=u''
    rst+='array('+str(typedic['maxItems'])+')'
    rst+=" items: "
    for item in typedic['items']:
        rst+=item['type']+" "
        
    return rst