#!/usr/bin/python
#
# Copyright (C) 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


__author__ = 'olwethu@byteorbit.com'


import gdata.spreadsheet.service
from gdata.service import BadAuthentication, CaptchaRequired
import gdata.service
import gdata.spreadsheet
import datetime
import logging

class SimpleCRUD:

    def __init__(self, email, password):
        """
        @rguments:
        email: google email account username.
        password: google email account password.
        
        Authenticates the user and sets the
        Gdata Auth token.
        """
        
        self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        self.gd_client.email = email
        self.gd_client.password = password
        self.gd_client.source = 'Import Google SpreadSheet to Database'
        try:
            self.gd_client.ProgrammaticLogin()
        except BadAuthentication, CaptchaRequired:
            logging.exception("Error Logging in invalid loggin values or captcha error.")
            raise
        self.curr_key = ''
        self.wksht_id = ''
        self.list_feed = None
    
    def get_spreadsheet(self, doc_name):
        """
        @arguments:
        doc_name: The spreadsheet's name.
        
        Use Auth token to get the spreadsheet
        specified by doc_name. Gets a key which
        is used as a unique idenfier for the
        spreadsheet.        
        """
        q = gdata.spreadsheet.service.DocumentQuery()
        q['title'] = doc_name
        q['title-exact'] = 'true'
        feed = self.gd_client.GetSpreadsheetsFeed(query=q)
        try:
            self.curr_key = feed.entry[0].id.text.rsplit('/', 1)[1]
            found = True
            return found
        except IndexError:
            logging.exception("Spreadsheet name is invalid")
            found = False
            return found
       
    def get_worksheet_data(self, worksheet_type, start, until):
        """
        @rguments:
        worksheet_type: The name of a worksheet in the spreadsheet.
        start: indicates the date to start import data from.
        until: indicates the date import data function must stop at.
        
        Appointment worksheet are processed to accessed the
        patient updates that fall with the start and until date.
        Uses until date to determine the appointment worksheets
        that must be accessed. For enrollemnt get the worksheet
        name in the spreadsheet.
        
        @returns:
        app_worksheets: Used to store two worksheets.
        app_worksheet: Used to store a worksheet.
        """
        #store the worksheet which have appointment data to be imported
        app_worksheets = {}
        #months tuple
        months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
        #get current month, returns an integer value
        curr_month = datetime.date.today().month 
        #get the name of the month 
        curr_month = int(curr_month)
        #use the month's name as worksheet name
        worksheet_name = months[curr_month - 1]

        #check if the worksheet requested is for making appointments
        if worksheet_type == 'appointment worksheet':
            #check if all the appointment data is from the same worksheet
            if until.month == curr_month:
                #get all the rows in the worksheet and process them
                app_worksheet = self.get_worksheet(worksheet_name, start, until)
                #check if the worksheet was found
                if app_worksheet is False:
                    return False
                #get the rows that fall with the start and until date(s)
                app_worksheet = self.appointmentRows(app_worksheet, start, until)
                #send to program that updates the apppointments
                return app_worksheet
            
            #if the appointment are on two worksheets process each 
            elif until.month > curr_month:
                #process the first worksheet
                app_worksheet = self.get_worksheet(worksheet_name, start, until)
                #check if the worksheet was found
                if app_worksheet is False:
                    return False
                #get the rows that fall with the start and until date(s)
                app_worksheet = self.appointmentRows(app_worksheet, start, until)
                #worksheet name is the key and value is worksheet
                holder = {worksheet_name: app_worksheet}
                #store it in the dictionary to be returned
                app_worksheets.update(holder)
                #clear for next use
                app_worksheet = {}
                holder = {}
                #process the second worksheet
                app_worksheet = self.get_worksheet(months[curr_month], start, until)
                #check if the worksheet was found
                if app_worksheet is False:
                    return False
                app_worksheet = self.appointmentRows(app_worksheet, start, until)
                holder = {months[curr_month]: app_worksheet}
                app_worksheet = {}
                app_worksheets.update(holder)
                holder = {}
                #return both worksheets in a single dictionary
                return app_worksheets
                
        #check if the requested worksheet is the enrollment sheet
        elif worksheet_type == 'enrollment worksheet':
            #get the name of the worksheet used for patient enrollment in spreadsheet
            self.get_worksheet('enrollment sheet', start, until)
                            
    def get_worksheet(self, worksheet_name, start, until):
        """
        @arguments:
        worksheet_name: The name of the worksheet on the spreadsheet.
        start: indicates the date to start import data from.
        until: indicates the date import data function must stop at.
        
        Send a query using worksheet_name to get a worksheet feed.
        Get wksht_id which is the permanent unique ID for the 
        worksheet within the spreadsheet. If the worksheet 
        contains appointment data call method to access this data.
        
        @returns:
        app_worksheet: Stores the worksheet contents.
        """
        
        q = gdata.spreadsheet.service.DocumentQuery()
        q['title'] = worksheet_name
        q['title-exact'] = 'true'
        feed = self.gd_client.GetWorksheetsFeed(self.curr_key, query=q)
        try:
            self.wksht_id = feed.entry[0].id.text.rsplit('/', 1)[1]
            #check if the retrieved worksheet is not an enrollment worksheet if not process the data 
            if worksheet_name != 'enrollment sheet':
                app_worksheet = self.prompt_for_list_action()
                return app_worksheet      
            
        except IndexError:
            worksheet_found = False
            return worksheet_found
       
     
    def appointmentRows(self, worksheet, start, until):
        """
        @arguments: 
        worksheet: the worksheet contents to get data from.
        start: indicates the date to start import data from.
        until: indicates the date import data function must stop at.
        
        Looks at data from the provideed worksheet that falls 
        within the start and until date. Creates a loop of dates from 
        start to until, for each day search the worksheet to see if
        the is a patient record with the same date if true get it.
        
        @returns:
        patients_worksheet: store the patient rows that are within start and until.
        """
        #stores the rows in the worksheet that are with the period date
        patients_worksheet = {}
        #Used to indicate the days to get patient data from
        period = until - start
        #get patient info for each day in period
        for day in range(period.days + 1):
            #the day to check from the worksheet
            curr_date = start + datetime.timedelta(days=day)
            #access the rows inside the worksheet
            for row in worksheet:
                #check if the worksheet has a patient with this date
                if worksheet[row]['appointmentdate1'] == curr_date:
                    #row for final worksheet
                    patient_row = {row: worksheet[row]}
                    #update the new worksheet
                    patients_worksheet.update(patient_row)
                    #clear temp locations
                    patient_row = {}
        return patients_worksheet             
           
    def enrolQuery(self, file_no):
        """
        @arguments:
        file_no: A patient file number.
        
        Sends a query to a enrollment worksheet to
        check if the patient has enrolled to use 
        appointment service. Check if the query returned
        a patient row and if True then patient has 
        enrolled if False the patient needs to enrol.
        
        @returns:
        enrolled: Flag to indicate if the patient was 
                  found int the enrollment worksheet.
        """
        q = gdata.spreadsheet.service.ListQuery(text_query=str(file_no))
        feed = self.gd_client.GetListFeed(self.curr_key, self.wksht_id, query=q)
        #patient was found in the enrollment worksheet
        if feed.entry:
            enrolled = True
            return enrolled
        #patient needs to enrol first
        if not feed.entry is None:
            enrolled = False
            return enrolled
          
    def prompt_for_list_action(self):
        """Calls method that gets a list feed from the given worksheet."""
        sheet = self.list_get_action()
        return sheet
    
    def list_get_action(self):
        """Gets the list feed for the worksheet and sends it to be processed"""
        list_feed = self.gd_client.GetListFeed(self.curr_key, self.wksht_id)
        #get the enrollment worksheet
        sheet = self.processFile(feed=list_feed)
        return sheet
       
    def processFile(self, feed):
        """
        @rguments:
        feed: the feed that contains the row(s) from a worksheet.
        
        Checks if the incoming feed is a list feed.
        if True access the contents of a row and 
        construct a dictionary to store it in. 
        Use the row number of the row in the
        worksheet as the key. Send the row to a
        method that ensures the contents of the
        row a proper for database storage.
        Use rows to construct a dictionary
        to store the entire worksheet.
        
        @returns:
        proper_worksheet: contains entire worksheet in a proper format.
        """      
        #process enrollment worksheet        
        if isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
            worksheet_data = {}
            proper_worksheet = {}
            temp_dic = {}
            rowdic = {}
            copydic = {}
            #loop through all the rows in the datak
            for i, entry in enumerate(feed.entry):
                row_no = i
                for key in entry.custom:
                    #dictionary to store a single column from row
                    temp_dic = {key: entry.custom[key].text}
                    #create a dictionary to store a row in worksheet and store to temp dictionary
                    rowdic.update(temp_dic)
                    #clear column dictionary for next usage
                    temp_dic = {}                     
                #creates a dictionary with the row number as the key and row dictionary as the value
                copydic = {row_no: rowdic}
                #dictionary to store the contents of a spreadsheet (stores copydic)
                worksheet_data.update(copydic)
                #clear for next worksheet row
                copydic = {}
                rowdic = {}   
            #for each row get proper type for each one of its contents
            for k in worksheet_data:
                row_no = k + 2
                #get proper values for each key in row dictionary
                enrol_p = self.databaseRecord(dic=worksheet_data[k])
                #creates a dictionary with the row number as the key and row dictionary as the value
                enroltemp = {row_no: enrol_p} 
                #clear for next row excess
                enrol_p = {}
                #dictionary that stores a row number as a key to the row data  
                proper_worksheet.update(enroltemp)
                enroltemp = {}
                row_no = 0
            return proper_worksheet
           
    def dateObjectCreator(self, datestring):
        """
        @arguments:
        datestring: the date abtained from the worksheet.
        
        convert the date that was obtained in the worksheet 
        to a real date object. The date string must use the
        format specified by the variable 'dateformat'.
        
        @returns:
        real_date: contains the date object.
        Exception: if an error occured during convertion
                   return the error.
        """
        #date must be in this format
        dateformat = '%d/%m/%Y'
        try:
            real_date = datetime.datetime.strptime(datestring, dateformat)
            real_date = real_date.date()
            return real_date
        except ValueError, exceptions:
            return ValueError
 
    def databaseRecord(self, dic):
        """
        @arguments:
        dic: The row from worksheet that must be processed.
        
        Get a row from a worksheet and convert its contents
        into their proper type (ie., string date -->  real date).
        If any of the contents raised an error during their
        convertion store it.
        
        @returns:
        appDic: The row with proper contents.        
        """
        app_dic = dic
        appDic = {}
        for key in app_dic:
            if key == 'fileno':
                try:
                    temp_dic = {key: int(app_dic[key])}
                    appDic.update(temp_dic)
                    temp_dic = {} 
                except TypeError:
                    temp_dic = {key: TypeError}
                    appDic.update(key=TypeError)
                    temp_dic = {}
            elif key == 'phonenumber':
                try:
                    temp_dic = {key: int(app_dic[key])}
                    appDic.update(temp_dic)
                    temp_dic = {}
                except ValueError:
                    temp_dic = {key: TypeError}
                    appDic.update(temp_dic)
                    temp_dic = {}
            elif key == 'appointmentdate1':
                app_date = self.dateObjectCreator(app_dic[key])
                temp_dic = {key: app_date}
                appDic.update(temp_dic)
                temp_dic = {}   
            elif key == 'appointmentstatus1':
                try:
                    temp_dic = {key: app_dic[key]}
                    appDic.update(temp_dic) 
                except TypeError:
                    temp_dic = {key: TypeError}
                    appDic.update(temp_dic)
                    temp_dic = {}
        return appDic
    
    def dateFormat(self, d):
      str_date = str(d)
      (y, m, d) = str_date.split('-')
      new_date = d+'/'+m+'/'+y
      return new_date
      
    def RunAppointment(self, doc_name, start, until):
        """
        @arguments:
        doc_name: the name of spreadsheet to import data from.
        start: indicates the date to start import data from.
        until: indicates the date import data function must stop at.
        
        Calls all the methods that access a users spreadssheet.
        
        @returns:
        app_worksheet: Contains worksheet(s) with appointment data.
        """
        #get the spread sheet to be worked on
        found = self.get_spreadsheet(doc_name)
        #check if a spreadsheet to work on was found if not return
        if found:
            #get the worksheets on the spreadsheet
            app_worksheet = self.get_worksheet_data('appointment worksheet', start, until)
            #check if the worksheet was found
            if app_worksheet is False:
                    return False
                
            return app_worksheet
        else:
            return False
  
    def RunEnrollmentCheck(self, doc_name, file_no, start, until):
        """
        @arguments:
        doc_name: the name of spreadsheet to import data from.
        file_no: patient file number. 
        start: indicates the date to start import data from.
        until: indicates the date import data function must stop at.
        """
        #get the spread sheet to be worked on
        self.get_spreadsheet(doc_name)
        #get the worksheets on the spreadsheet
        self.get_worksheet_data('enrollment worksheet', start, until)
        #send structured query to check if the patient is enrolled to use service
        exists = self.enrolQuery(file_no)
        return exists
