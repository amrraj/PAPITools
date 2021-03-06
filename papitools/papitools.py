'''
// I dedicate all this code, all my work, to my wife, who will
// have to support me once it gets released into the public.
Author: Vreddhi Bhat
Contact: vbhat@akamai.com
'''

import json


__all__=['Papitools']

class Papitools(object):
    """All basic operations that can be performed using PAPI """

    final_response = "NULL" #This variable holds the SUCCESS or FAILURE reason
    headers = {
        "Content-Type": "application/json"
    }

    access_hostname = "mandatory"
    property_name = "optional"
    version = "optional"
    notes = "optional"
    emails = "optional"
    groupId = "optional"
    contractId = "optional"
    propertyId = "optional"

    def __init__(self, access_hostname, property_name = "optional", \
                version = "optional",notes = "optional", emails = "optional", \
                groupId = "optional", contractId = "optional", propertyId = "optional"):
        self.access_hostname = access_hostname
        self.property_name = property_name
        self.version = version
        self.notes = notes
        self.emails = emails
        self.groupId = groupId
        self.contractId = contractId
        self.propertyId = propertyId

    def getContracts(self,session):
        """
        Function to fetch all contracts

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        contractsResponse : contractsResponse
            (contractsResponse) Object with all details
        """
        contractsUrl = 'https://' + self.access_hostname + '/papi/v0/contracts/'
        contractsResponse = session.get(contractsUrl)
        return contractsResponse

    def getPropertyInfo(self,session,property_name):
        """
        Function to fetch property ID and update the proerty object with corresponding values

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object
        property_name: <string>
            Property or configuration name

        Returns
        -------
        self : self
            (Papitools) Object with propertyId, contractId and groupId as attributes
        """
        groupsInfo = self.getGroups(session)
        for eachDataGroup in groupsInfo.json()['groups']['items']:
            try:
                contractId = [eachDataGroup['contractIds'][0]]
                groupId = [eachDataGroup['groupId']]
                url = 'https://' + self.access_hostname + '/papi/v0/properties/?contractId=' + contractId[0] +'&groupId=' + groupId[0]
                propertiesResponse = session.get(url)
                if propertiesResponse.status_code == 200:
                    propertiesResponseJson = propertiesResponse.json()
                    propertiesList = propertiesResponseJson['properties']['items']
                    for propertyInfo in propertiesList:
                        propertyName = propertyInfo['propertyName']
                        propertyId = propertyInfo['propertyId']
                        propertyContractId = propertyInfo['contractId']
                        propertyGroupId = propertyInfo['groupId']
                        if propertyName == property_name or propertyName == property_name + ".xml":
                            #Update the self attributes with correct values
                            self.groupId = propertyGroupId
                            self.contractId = propertyContractId
                            self.propertyId = propertyId
                            self.final_response = "SUCCESS"
                            return self
            except KeyError:
                pass
        #Return the self as it is without updated information
        self.final_response = "FAILURE"
        return self


    def getGroups(self,session):
        """
        Function to fetch all the groups under the contract

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        groupResponse : groupResponse
            (groupResponse) Object with all response details.
        """

        groupUrl = 'https://' + self.access_hostname + '/papi/v0/groups/'
        groupResponse = session.get(groupUrl)
        if groupResponse.status_code == 200:
            self.final_response = "SUCCESS"
        else:
            self.final_response = "FAILURE"
        return groupResponse

    def getAllProperties(self,session,contractId,groupId):
        """
        Function to fetch list of all properties under the group

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        allProperties : <dict>
            A dictionarty containing name, propertyId, contractId and groupId of all properties under the customer account
        """
        url = 'https://' + self.access_hostname + '/papi/v0/properties/?contractId=' + contractId +'&groupId=' + groupId
        propertiesResponse = session.get(url)
        return propertiesResponse

    def getPropertyRules(self,session,property_name,version):
        """
        Function to download rules from a property

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object
        property_name: <string>
            Property or configuration name
        version : <int>
            Property orconfiguration version number

        Returns
        -------
        rulesResponse : rulesResponse
            (rulesResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        rulesUrl = 'https://' + self.access_hostname  + '/papi/v0/properties/' + self.propertyId +'/versions/'+str(version)+'/rules/?contractId='+ self.contractId +'&groupId='+ self.groupId
        rulesResponse = session.get(rulesUrl)
        if rulesResponse.status_code == 200:
            self.final_response = "SUCCESS"
        else:
            self.final_response = rulesResponse.json()['detail']
        return rulesResponse

    def getPropertyRulesfromPropertyId(self,session,propertyId,version,contractId,groupId):
        """
        Function to download rules from a property

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object
        property_name: <string>
            Property or configuration name
        version : <int>
            Property orconfiguration version number

        Returns
        -------
        rulesResponse : rulesResponse
            (rulesResponse) Object with all response details.
        """

        rulesUrl = 'https://' + self.access_hostname  + '/papi/v0/properties/' + propertyId +'/versions/'+str(version)+'/rules/?contractId='+ contractId +'&groupId='+ groupId
        rulesResponse = session.get(rulesUrl)
        if rulesResponse.status_code == 200:
            self.final_response = "SUCCESS"
        else:
            self.final_response = rulesResponse.json()['detail']
        return rulesResponse

    def createVersion(self,session,baseVersion,property_name):
        """
        Function to create or checkout a version of property

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object
        baseVersion : <int>
            Property or configuration version number to checkout from
        property_name: <string>
            Property or configuration name

        Returns
        -------
        createVersionResponse : createVersionResponse
            (createVersionResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        newVersionData = """
        {
            "createFromVersion": %s
        }
        """ % (baseVersion)
        createVersionUrl = 'https://' + self.access_hostname + '/papi/v0/properties/' + self.propertyId + '/versions/?contractId=' + self.contractId + '&groupId=' + self.groupId
        createVersionResponse = session.post(createVersionUrl, data=newVersionData,headers=self.headers)
        if createVersionResponse.status_code == 201:
            self.final_response = "SUCCESS"
        return createVersionResponse

    def getVersion(self,session,property_name,activeOn="LATEST"):
        """
        Function to get the latest or staging or production version

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object
        activeOn : <string>
            Network Type (STAGING OR PRODUCTION) or the LATEST Version
        property_name: <string>
            Property or configuration name

        Returns
        -------
        VersionResponse : VersionResponse
            (VersionResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        if activeOn == "LATEST":
            VersionUrl = 'https://' + self.access_hostname + '/papi/v0/properties/' + self.propertyId + '/versions/latest?contractId=' + self.contractId +'&groupId=' + self.groupId
        elif activeOn == "STAGING":
            VersionUrl = 'https://' + self.access_hostname + '/papi/v0/properties/' + self.propertyId + '/versions/latest?contractId=' + self.contractId +'&groupId=' + self.groupId + '&activatedOn=STAGING'
        elif activeOn == "PRODUCTION":
            VersionUrl = 'https://' + self.access_hostname + '/papi/v0/properties/' + self.propertyId + '/versions/latest?contractId=' + self.contractId +'&groupId=' + self.groupId + '&activatedOn=PRODUCTION'
        VersionResponse = session.get(VersionUrl)
        return VersionResponse

    def uploadRules(self,session,updatedData,property_name,version):
        """
        Function to upload rules to a property

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object
        updatedData : <json>
            Complete JSON rules dataset to be uploaded
        property_name: <string>
            Property or configuration name

        Returns
        -------
        updateResponse : updateResponse
            (updateResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        updateurl = 'https://' + self.access_hostname  + '/papi/v0/properties/'+ self.propertyId + "/versions/" + str(version) + '/rules/' + '?contractId=' + self.contractId +'&groupId=' + self.groupId
        updatedData = json.dumps(updatedData)
        updateResponse = session.put(updateurl,data=updatedData,headers=self.headers)
        if updateResponse.status_code == 403:
            self.final_response == "FAILURE"
        elif updateResponse.status_code == 404:
            self.final_response == "FAILURE"
        elif updateResponse.status_code == 200:
            self.final_response == "SUCCESS"
        return updateResponse

    def activateConfiguration(self,session,property_name,version,network,emailList,notes):
        """
        Function to activate a configuration or property

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object
        property_name: <string>
            Property or configuration name
        version : <int>
            version number to be activated
        network : <string>
            network type on which configuration has to be activated on
        emailList : <string>
            List of emailIds separated by comma to be notified
        notes : <string>
            Notes that describes the activation reason

        Returns
        -------
        activationResponse : activationResponse
            (activationResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        emails = []
        emails.append(emailList)
        emails = json.dumps(emails)
        activationDetails = """
             {
                "propertyVersion": %s,
                "network": "%s",
                "note": "%s",
                "notifyEmails": %s
            } """ % (version,network,notes,emails)

        actUrl  = 'https://' + self.access_hostname + '/papi/v0/properties/'+ self.propertyId + '/activations/?contractId=' + self.contractId +'&groupId=' + self.groupId
        activationResponse = session.post(actUrl, data=activationDetails, headers=self.headers)
        try:
            if activationResponse.status_code == 400 and activationResponse.json()['detail'].find('following activation warnings must be acknowledged'):
                acknowledgeWarnings = []
                for eachWarning in activationResponse.json()['warnings']:
                    print("WARNING: " + eachWarning['detail'])
                    acknowledgeWarnings.append(eachWarning['messageId'])
                    acknowledgeWarningsJson = json.dumps(acknowledgeWarnings)
                print("\nAutomatically acknowledging the warnings.\n")
                #The details has to be within the three double quote or comment format
                updatedactivationDetails = """
                     {
                        "propertyVersion": %s,
                        "network": "%s",
                        "note": "%s",
                        "notifyEmails": %s,
                        "acknowledgeWarnings": %s
                    } """ % (version,network,notes,emails,acknowledgeWarningsJson)
                print("Please wait while we activate the config for you.. Hold on... \n")
                updatedactivationResponse = session.post(actUrl,data=updatedactivationDetails,headers=self.headers)
                if updatedactivationResponse.status_code == 201:
                    print("Here is the activation link, that can be used to track\n")
                    print(updatedactivationResponse.json()['activationLink'])
                    self.final_response = "SUCCESS"
                else:
                    self.final_response = "FAILURE"
                    print(updatedactivationResponse.json())
                return updatedactivationResponse
            elif activationResponse.status_code == 422 and activationResponse.json()['detail'].find('version already activated'):
                print("Property version already activated")
                self.final_response = "SUCCESS"
            elif activationResponse.status_code == 404 and activationResponse.json()['detail'].find('unable to locate'):
                print("The system was unable to locate the requested version of configuration")
                self.final_response = "FAILURE"
            return activationResponse
        except KeyError:
            self.final_response = "FAILURE"
            print("Looks like there is some error in configuration. Unable to activate configuration at this moment\n")
            return activationResponse

    def cloneConfig(self,session,property_name,new_property_name,version):
        """
        Function to Clone a configuration

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object
        property_name: <string>
            Property or configuration name
        new_property_name: <string>
            Destination/New Property or configuration name
        version: <int>
            Property version to refer OR base from

        Returns
        -------
        cloneResponse : cloneResponse
            (cloneResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        versionUrl = 'https://' + self.access_hostname  + '/papi/v0/properties/'+ self.propertyId + "/versions/" + '?contractId=' + self.contractId +'&groupId=' + self.groupId
        productId = ''
        versionEtag = ''
        versionResponse = session.get(versionUrl)
        for eachItem in versionResponse.json()['versions']['items']:
            if str(eachItem['propertyVersion']) == str(version):
                versionEtag = eachItem['etag']
                productId = "prd_Fresca"


        cloneData = """
        {
            "productId"    : "%s",
            "propertyName" : "%s",
            "cloneFrom": {
                "propertyId"    : "%s",
                "version"       : %s,
                "copyHostnames" : true,
                "cloneFromVersionEtag" : "%s"
            }
        }
        """ % (productId,new_property_name,self.propertyId,version,versionEtag)

        cloneUrl = 'https://' + self.access_hostname  + '/papi/v0/properties/?contractId=' + self.contractId +'&groupId=' + self.groupId
        cloneResponse = session.post(cloneUrl, data=cloneData, headers=self.headers)
        return cloneResponse

    def deleteProperty(self,session,property_name):
        """
        Function to delete a property

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object
        property_name: <string>
            Property or configuration name

        Returns
        -------
        deleteResponse : deleteResponse
            (deleteResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        deleteurl = 'https://' + self.access_hostname  + '/papi/v0/properties/'+ self.propertyId + '?contractId=' + self.contractId +'&groupId=' + self.groupId
        deleteResponse = session.delete(deleteurl)
        if deleteResponse.status_code == 403:
            self.final_response == "FAILURE"
        elif deleteResponse.status_code == 404:
            self.final_response == "FAILURE"
        elif deleteResponse.status_code == 200:
            self.final_response == "SUCCESS"
        else:
            self.final_response == "FAILURE"
        return deleteResponse

    def listProducts(self,session):
        """
        Function to fetch all products

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        Nothing: It rather prints the data
        """
        contractsResponse = self.getContracts(session)
        #print(json.dumps(contractsResponse.json()))
        for everyItem in contractsResponse.json()['contracts']['items']:
            contractId = everyItem['contractId']
            productsUrl = 'https://' + self.access_hostname + '/papi/v0/products/?contractId=' + contractId
            productsResponse = session.get(productsUrl)
            print(json.dumps(productsResponse.json()))


    def listRuleFormats(self,session):
        """
        Function to Get a list of available rule formats

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        ruleFomratResponse : ruleFomratResponse
            (ruleFomratResponse) Object with all response details.
        """
        ruleFomratUrl = 'https://' + self.access_hostname + '/papi/v0/rule-formats'
        ruleFomratResponse = session.get(ruleFomratUrl)
        return ruleFomratResponse

    def getRuleTree(self,session,property_name,version,latestTimeStamp='latest'):
        """
        Function to get the entire rule tree for a property version

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        ruleTreeResponse : ruleTreeResponse
            (ruleTreeResponse) Object with all response details.
        """
        #latestTimeStamp='latest' this is not a desired value, but can be used to fetch rule tree
        AcceptValue = "application/vnd.akamai.papirules." + latestTimeStamp + "+json"
        mime_header = {
            "Accept": AcceptValue
        }
        self.getPropertyInfo(session, property_name)
        '/papi/v0/properties/' + self.propertyId + '/versions/' + version + '/rules/?contractId=' + self.contractId + '&groupId=' + self.groupId
        ruleTreeUrl = 'https://' + self.access_hostname + '/papi/v0/properties/' + self.propertyId + '/versions/' + version + '/rules/?contractId=' + self.contractId + '&groupId=' + self.groupId
        ruleTreeResponse = session.get(ruleTreeUrl,headers=mime_header)
        return ruleTreeResponse

    def updateRuleTree(self,session,property_name,version,TimeStamp):
        """
        Function to update the entire rule tree for a property version to

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        updateruleTreeResponse : ruleTreeResponse
            (updateruleTreeResponse) Object with all response details.
        """
        mime_header = {
            "Content-Type": "application/vnd.akamai.papirules.v2016-11-15+json"
        }
        self.getPropertyInfo(session, property_name)
        '/papi/v0/properties/' + self.propertyId + '/versions/' + version + '/rules/?contractId=' + self.contractId + '&groupId=' + self.groupId
        updateruleTreeUrl = 'https://' + self.access_hostname + '/papi/v0/properties/' + self.propertyId + '/versions/' + version + '/rules/?contractId=' + self.contractId + '&groupId=' + self.groupId
        updateruleTreeResponse = session.put(updateruleTreeUrl,headers=mime_header)
        return updateruleTreeResponse
