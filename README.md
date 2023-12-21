# HTTP Basic Auth Bulk Addition
This repositry contains the code to bulk update any number of configs with Basic Auth Feature

### Credentials Setup
In order to use this configuration, you need to:
* Set up your credential files as described in [here](https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials)
* When working through this process you need to give grants for the property manager API.
* Setup Google Sheet API as describer in [here](https://www.evernote.com/shard/s222/sh/42e72b36-12c4-a0f4-0a3d-a225fa9157d7/5392dce76d0eae0b6fd7dcbf9aa22ca3)
* Create your own creds.json 


### Workflow
- Enter the config / hostname/username and password details in the [Google Sheet](https://docs.google.com/spreadsheets/d/1-Ifr0MeRkJqKyF5GhNBwQyQGE-h7qmjCEmhmFx75sa8/edit#gid=0)
- Framework will create a newversion on top of the production version
- Make the necessary changes.
- Activation of the configs to staging network.


### Install pip packages needed
```
$ pip install -r requirements.txt
```

### Add Rule to Single Row of Google Sheet
```
$:python addrule.py --accountSwitchKey 1-4as5FDXQsAV --ChangeID 'Phase1: Basic Auth Addition' --start 2 --end 2 
Data Preparation Done!
{
  "www_jiodemo_clone": [
    {
      "HostName": "beta.example.com",
      "Username": "stgnews18",
      "Password": "g3!pX$tR@ngE#92"
    }
  ]
}
Preparing the rule for beta.example.com for the config www_jiodemo_clone
Updating the rules for the config www_jiodemo_clone
Updated the Rule succesfully to the config www_jiodemo_clone
Initiated the activation of the config www_jiodemo_clone
********************************************************************************
```

### Add Rule to Multiple Row of Google Sheet
```
$:python addrule.py --accountSwitchKey 1-7989HV --ChangeID 'Phase1: Basic Auth Addition' --start 2 --end 5 
```
