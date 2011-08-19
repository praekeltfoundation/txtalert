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


try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.spreadsheet
import atom
import getopt
import sys
import string
import datetime
import re


class SimpleCRUD:

  def __init__(self, email, password, spreadsheet_name):
    self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    self.gd_client.email = email
    self.gd_client.password = password
    self.spreadsheet_name = spreadsheet_name
    self.gd_client.source = 'Import Google SpreadSheet to Database'
    self.gd_client.ProgrammaticLogin()
    self.curr_key = ''
    self.curr_wksht_id = ''
    self.list_feed = None
    
  def getSpreadsheet(self):
    """Query the spreadsheet by name, and extract the unique spreadsheet ID."""
    q = gdata.spreadsheet.service.DocumentQuery()
    q['title'] = self.spreadsheet_name
    q['title-exact'] = 'true'
    feed = self.gd_client.GetSpreadsheetsFeed(query=q)
    self.curr_key = feed.entry[0].id.text.rsplit('/',1)[1]
    return self.curr_key
       
       
  def getWorksheetData(self, worksheet_type):
    """Acess the enrol and current month's worksheets of the current spread sheet."""
    #print 'Inside getWorksheet current key is: %s\n' % self.curr_key
    month_worksheet = {}
    #months tuple
    months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
    #get current month
    curr_month = datetime.date.today().month  
    curr_month = int(curr_month)
    worksheet_name = months[curr_month-1]
    
    #check if the worksheet requested is for making appointments
    if worksheet_type == 'appointment worksheet':
         app_worksheet = self.getWorkSheet(worksheet_name)
         #self.getWorkSheet(app_worksheet)
         #app_worksheet = self.appointmentQuery(start, until)
         return app_worksheet
        
    #check if the requested worksheet is the enrollment sheet
    elif worksheet_type == 'enrollment worksheet':
        exists = self.getWorkSheet('enrollment sheet')
        return exists
                     
   
  def getWorkSheet(self, worksheet_name):
      q = gdata.spreadsheet.service.DocumentQuery()
      q['title'] = worksheet_name
      q['title-exact'] = 'true'
      feed = self.gd_client.GetWorksheetsFeed(self.curr_key, query=q)
      self.wksht_id = feed.entry[0].id.text.rsplit('/',1)[1] 
      #check if the retrieved worksheet is not an enrollment worksheet if not process the data 
      if worksheet_name is not 'enrollment sheet':
           app_worksheet = self._PromptForListAction()
           return app_worksheet
  
  def appointmentQuery(self, start, until):
    str_start = str(start)
    str_start = str_start.replace('-', '/')
    q = gdata.spreadsheet.service.ListQuery(text_query='1/8/2011')
    print str_start
    feed = self.gd_client.GetListFeed(self.curr_key, self.wksht_id, query=q)
    #patient was found in the enrollment worksheet
    if feed:
        enrolled = True
        print 'patient with this date was found'
    #patient needs to enrol first
    if not feed:
        enrolled = False
        print 'no patient with this date'
    date_diff = until - start
    for d in range(date_diff.days):
        day_query = start + datetime.timedelta(days=d)
                
           
  def enrolQuery(self, file_no):
      q = gdata.spreadsheet.service.ListQuery(text_query=str(file_no))
      feed = self.gd_client.GetListFeed(self.curr_key, self.wksht_id, query=q)
      #patient was found in the enrollment worksheet
      if feed:
          enrolled = True
          return enrolled
      #patient needs to enrol first
      if not feed:
          enrolled = False
          return enrolled
          
                  
  def _PromptForListAction(self):
    """Calls method that gets a list feed from the given worksheet."""
    sheet = self._ListGetAction()
    return sheet
    
  def _ListGetAction(self):
    """Gets the list feed for the worksheet and sends it to be processed"""
    list_feed = self.gd_client.GetListFeed(self.curr_key, self.wksht_id)
    #get the enrollment worksheet
    sheet = self.processFile(feed=list_feed)
    return sheet
       
    
  def processFile(self, feed):  
    """Gets the data from the list feed and process it. Loop through the worksheet and make the data avaliable. """     
    #process enrollment worksheet        
    if isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
        worksheet_data = {}
        proper_worksheet = {}
        temp_dic = {}
        rowdic = {}
        copydic = {}
        enrolled = False
        #loop through all the rows in the data
        for i, entry in enumerate(feed.entry):
            
            row_no = i
            for key in entry.custom:
                #dictionary to store a single column from row
                temp_dic = {key:entry.custom[key].text}
                #create a dictionary to store a row in worksheet and store to temp dictionary
                rowdic.update(temp_dic)
                #clear column dictionary for next usage
                temp_dic = {}
                                        
            #creates a dictionary with the row number as the key and row dictionary as the value
            copydic = {row_no:rowdic}
            #dictionary to store the contents of a spreadsheet (stores copydic)
            worksheet_data.update(copydic)
            #clear for next worksheet row
            copydic = {}
            rowdic ={}
                
        #print worksheet_data
        #for each row get proper type for each one of its contents
        for k in worksheet_data:
            row_no = k + 2
            #print worksheet_data[k]
            #get proper values for each key in row dictionary
            enrol_p = self.databaseRecord(dic=worksheet_data[k])
            #creates a dictionary with the row number as the key and row dictionary as the value
            enroltemp = {k:enrol_p} 
            #clear for next row excess
            enrol_p = {}
            #dictionary that stores a row number as a key to the row data  
            proper_worksheet.update(enroltemp)
            enroltemp = {}
             
            row_no = 0
        return proper_worksheet
           
  def dateObjectCreator(self, datestring):
      """Used to convert a string type date into a datetime object."""
      dateformat = '%d/%m/%Y'
      try:
          real_date = datetime.datetime.strptime(datestring, dateformat)
          real_date = real_date.date()
          return real_date
      except TypeError:
          return TypeError
 
  def databaseRecord(self, dic):
      """Accepts a dictionary from a worksheet and converts the contents into the proper type"""
      app_dic = dic
      appDic = {}
      for key in app_dic:
          if key == 'fileno':
              try:
                  temp_dic = {key:int(app_dic[key])}
                  appDic.update(temp_dic)
                  temp_dic = {} 
              except TypeError:
                  temp_dic = {key:TypeError}
                  appDic.update(key=TypeError)
                  temp_dic = {}
                  
          elif key == 'phonenumber':
              try:
                  temp_dic = {key:int(app_dic[key])}
                  appDic.update(temp_dic)
                  temp_dic = {}
              except ValueError:
                  temp_dic = {key:TypeError}
                  appDic.update(temp_dic)
                  temp_dic = {}
            
          elif key == 'appointmentdate1':
              app_date = self.dateObjectCreator(app_dic[key])
              temp_dic = {key:app_date}
              appDic.update(temp_dic)
              temp_dic = {}   
                
          elif key == 'appointmentstatus1':
              try:
                  temp_dic = {key:app_dic[key]}
                  appDic.update(temp_dic) 
              except TypeError:
                  temp_dic = {key:TypeError}
                  appDic.update(temp_dic)
                  temp_dic = {}
         
      return appDic
      
  def RunAppointment(self):
      #get the spread sheet to be worked on
      self.getSpreadsheet()
      #get the worksheets on the spreadsheet
      app_worksheet = self.getWorksheetData('appointment worksheet')
      return app_worksheet
  
  def RunEnrollmentCheck(self, file_no):
      #get the spread sheet to be worked on
      self.getSpreadsheet()
      #get the worksheets on the spreadsheet
      self.getWorksheetData('enrollment worksheet')
      #send structured query to check if the patient is enrolled to use service
      exists = self.enrolQuery(file_no)
      return exists
       
  '''def RunEnrollmentCheck(self, doc_name, worksheet_type, file_no, start, until):
      #get the spread sheet to be worked on
      self.getSpreadsheet(doc_name)
      #get the worksheets on the spreadsheet
      self.getWorksheetData(worksheet_type, start, until)
      #send structured query to check if the patient is enrolled to use service
      exists = self.enrolQuery(file_no)
      return exists'''
       

def main():
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["user=", "pw="])
  except getopt.error, msg:
    print 'python spreadsheetReader.py --user [username] --pw [password] '
    sys.exit(2)
  
  user = ''
  pw = ''
  key = ''
  # Process options
  for o, a in opts:
    if o == "--user":
      user = a
    elif o == "--pw":
      pw = a
     
 
  if user == '' or pw == '':
    print 'python spreadsheetExample.py --user [username] --pw [password]'
    sys.exit(2)
        
  sample = SimpleCRUD(user, pw, 'ByteOrbit copy of WrHI spreadsheet for Praekelt TxtAlert')
  sample.RunAppointment()
  sample.RunEnrollmentCheck(1932)
  

if __name__ == '__main__':
  main()

