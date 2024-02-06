import os,argparse,sys,uuid,json,gspread
from pyakamai import pyakamai
from oauth2client.service_account import ServiceAccountCredentials


jobId = str(uuid.uuid1())
logfilepath = ''
gsheetName = "Network18BasicAuth"
gsheetTab = "MasterSheet"
credsLocation = "creds.json"
scope = ["https://spreadsheets.google.com/feeds", 
        'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", 
         "https://www.googleapis.com/auth/drive"]
 
 
# Assign credentials ann path of style sheet
creds = ServiceAccountCredentials.from_json_keyfile_name(credsLocation, scope)
client = gspread.authorize(creds)
sheet = client.open(gsheetName)
configJson = {}




def getBasicAuthHeader(username,password):
    import base64
    credentials = f'{username}:{password}'
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    encoded_credentialsstr = 'Basic {}'.format(encoded_credentials)
    return encoded_credentialsstr

def getRule(hostname,username,password):
    f = open('template.json','r')
    authrule = json.load(f)
    authrule['name'] = "Auth - {}".format(hostname)
    authrule['criteria'][0]['options']['values'] = [hostname]
    authrule['children'][0]['criteria'][1]['options']['values'] = [getBasicAuthHeader(username,password)]
    return authrule


def prepareData(startRow,endRow):
    startRow = int(startRow)
    endRow = int(endRow)
    if startRow <= 0 or endRow <=0 or startRow > endRow:
        print("Invalid Values for startRow or endRow. Please try again!",file=sys.stderr)
        exit(1)
    try:
        sheet_instance = sheet.worksheet(gsheetTab)
    except:
        print("Wrong SheetName.Please Provide the correct sheet name and try again!",file=sys.stderr)
        exit(2)
    startRow = startRow-2
    endRow = endRow-2
    data = sheet_instance.get_all_records()
    for i in range(startRow,endRow+1):
        item = {}
        item['HostName'] = data[i]['HostName']
        item['Username'] = data[i]['Username']
        item['Password'] = data[i]['Password']
        
        if data[i]['Config'] not in configJson:
            configJson[data[i]['Config']] = [item]
        else:
            configJson[data[i]['Config']].append(item)
    print("Data Preparation Done!")
    print(json.dumps(configJson,indent=2))


def addRule(ChangeID,accountSwitchKey):
    for key in configJson.keys():
        config = key
        pyakamaiObj = pyakamai(accountSwitchKey=accountSwitchKey,debug=False,verbose=False) 
        akamaiconfig = pyakamaiObj.client('property')
        akamaiconfig.config(config)
        newversion = akamaiconfig.createVersion(akamaiconfig.getProductionVersion())
        #newversion = akamaiconfig.getProductionVersion()
        ruleTree = akamaiconfig.getRuleTree(newversion)
        for hosts in configJson[key]:
            childrule = getRule(hosts['HostName'],hosts['Username'],hosts['Password'])
            print("Preparing the rule for {} for the config {}".format(hosts['HostName'],config))
            ruleTree['rules']['children'].append(childrule)
        
        ruleTree['ruleFormat'] = 'v2023-10-30'
        propruleInfo_json = json.dumps(ruleTree,indent=2)
        print("Updating the rules for the config {}".format(config))
        addRuleStatus = akamaiconfig.updateRuleTree(newversion,propruleInfo_json)
        updateNoteStatus = akamaiconfig.addVersionNotes(newversion,ChangeID)
        if addRuleStatus == True and updateNoteStatus == True:
            print("Updated the Rule succesfully to the config {}".format(config))
            activationStatus = akamaiconfig.activateStaging(newversion,ChangeID,["apadmana@akamai.com"])
            if activationStatus == True:
                print("Initiated the activation of the config {}".format(config))
            else:
                print("Failed to the activate of the config {}".format(config))
        else:
            print("Failed to update the Rule succesfully to the config {}".format(config))
        print('*'*80)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Times CDN Onboarding Tool.')
    # Storage migration
    parser.add_argument('--start', required=True, help='Starting Row Number')
    parser.add_argument('--end', required=True, help='End Row')
    parser.add_argument('--accountSwitchKey', default=None,help='Account SwitchKey')
    parser.add_argument('--ChangeID',required=True, help='ChangeID')

    args = parser.parse_args()


    curdir = os.getcwd()
    dirpath = os.path.dirname(curdir + '/logs')
    logfilepath = dirpath + "/"  + jobId+'.txt'

    #sys.stdout = open(logfilepath, 'w+')

    prepareData(args.start,args.end)
    addRule(args.ChangeID,args.accountSwitchKey)

'''
python addrule.py --accountSwitchKey 1-ssss --ChangeID 'Adding Phase2 Basic Auth' --start 2 --end 2 
'''
