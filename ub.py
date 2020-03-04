import requests
data = {"name": "helloWorld",
  "description": "",
  "importAutomatically": False,
  "useVfs": True,
  "sourceConfigPlugin": "File System (Versioned)",
  "defaultVersionType": "FULL",
  "properties": {
    "FileSystemVersionedComponentProperties/basePath": "/home/user1/artifacts/shared/helloWorld"
  }}
response = requests.put('https://ucdevcore1.metlife.com:8443/cli/component/create', data=data, verify=False, auth=('nsmith', 'passwd\n'))

#https://www.ibm.com/support/knowledgecenter/SS4GSP_6.2.0/com.ibm.udeploy.reference.doc/topics/rest_api_ref_example.html