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


__author__ = 'api.laurabeth@gmail.com (Laura Beth Lincoln)'


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

  def __init__(self, email, password):
    self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
    self.gd_client.email = email
    self.gd_client.password = password
    self.gd_client.source = 'Import Google SpreadSheet to Database'
    self.gd_client.ProgrammaticLogin()
    self.curr_key = ''
    self.curr_wksht_id = ''
    self.list_feed = None
    
  def getSpreadsheet(self, doc_name):
    """Query the spreadsheet by name, and extract the unique spreadsheet ID."""
    self.doc_name = doc_name
    q = gdata.spreadsheet.service.DocumentQuery()
    q['title'] = self.doc_name
    q['title-exact'] = 'true'
    feed = self.gd_client.GetSpreadsheetsFeed(query=q)
    self.curr_key = feed.entry[0].id.text.rsplit('/',1)[1]
       
       
  def getWorksheets(self):
    """Acess the enrol and current month's worksheets of the current spread sheet."""
    #print 'Inside getWorksheet current key is: %s\n' % self.curr_key
    month_worksheet = {}
    #months tuple
    months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
    #get current month
    curr_month = datetime.date.today().month  
    curr_month = int(curr_month)
    # Get the list of worksheets in the spreadsheet
    feed = self.gd_client.GetWorksheetsFeed(self.curr_key)
        
    for i, entry in enumerate(feed.entry):
        #check for this month's worksheet
        if entry.title.text == 'enrollment sheet':
            select = i
            #select the worksheet to be accessed
            id_parts = feed.entry[select].id.text.split('/')
            #stores the unique ID used to access the spreadsheet
            self.wksht_id = id_parts[len(id_parts) - 1]
            #get the enrollment data use list
            enrol_worksheet = self._PromptForListAction('enrol') 
        #if the date is end of the month get next months spreadsheet   
        elif datetime.date.today().day >= 28 and (months[curr_month-1] == entry.title.text or months[curr_month] == entry.title.text):
            select = i
            id_parts = feed.entry[select].id.text.split('/')
            self.wksht_id = id_parts[len(id_parts) - 1]
            month_sheet = self._PromptForListAction('appointment')
            month_worksheet.update(mont_sheet)
        #if not end of the month get the current month worksheet    
        elif datetime.date.today().day < 28 and months[curr_month-1] == entry.title.text:
            select = i
            id_parts = feed.entry[select].id.text.split('/')
            self.wksht_id = id_parts[len(id_parts) - 1]
            month_worksheet = self._PromptForListAction('appointment')
                
    return (enrol_worksheet, month_worksheet)  
           
  def _PromptForListAction(self, worksheet):
    """Calls method that gets a list feed from the given worksheet."""
    sheet = self._ListGetAction(worksheet)
    return sheet
    
  def _ListGetAction(self, worksheet):
    """Gets the list feed for the worksheet and sends it to be processed"""
    # Get the list feed
    list_feed = self.gd_client.GetListFeed(self.curr_key, self.wksht_id)
    #get the enrollment worksheet
    sheet = self.processFile(feed=list_feed, worksheet=worksheet)
    return sheet
    
    
  def processFile(self, feed, worksheet):  
    """Gets the data from the list feed and process it. Loop through the worksheet and make the data avaliable. """     
    #process enrollment worksheet        
    if isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
        print 'worksheet inside processFile: %s\n' % worksheet
        #feed_type = 'list'
        worksheet_data = {}
        proper_worksheet = {}
        temp_dic = {}
        rowdic = {}
        copydic = {}
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
        
        #for each row get proper type for each one of its contents
        for k in worksheet_data:
            row_no = k + 2
            #print worksheet_data[k]
            #get proper values for each key in row dictionary
            enrol_p = self.databaseRecord(dic=worksheet_data[k], worksheet=worksheet)
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
 
  def databaseRecord(self, dic, worksheet):
      """Accepts a dictionary from a worksheet and converts the contents into the proper type"""
      if worksheet == 'enrol':
          enrol_dic = dic
          enrolDic = {}          
          for key in enrol_dic:
              if key == 'patientid':
                  try:
                      temp_dic = {key:int(enrol_dic[key])}
                      enrolDic.update(temp_dic) 
                      temp_dic = {}
                  except TypeError:
                      temp_dic = {key:TypeError}
                      enrolDic.update(temp_dic) 
                      temp_dic = {}                 
              elif key == 'patientfileno':
                  try:
                      temp_dic = {key:int(enrol_dic[key])}
                      enrolDic.update(temp_dic) 
                      temp_dic = {}
                  except TypeError:
                      temp_dic = {key:TypeError}
                      enrolDic.update(temp_dic) 
                      temp_dic = {} 
              elif key == 'patientphonenumber':
                  try:
                      temp_dic = {key:int(enrol_dic[key])}
                      enrolDic.update(temp_dic) 
                      temp_dic = {}
                  except ValueError:
                      temp_dic = {key:ValueError}
                      enrolDic.update(temp_dic) 
                      temp_dic = {} 
              elif key == 'dateofenrollment':
                  enrol_date = self.dateObjectCreator(enrol_dic[key])
                  temp_dic = {key:enrol_date}
                  enrolDic.update(temp_dic)
                  temp_dic = {}
                  
          return enrolDic       
      
      elif worksheet == 'appointment':
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
    
    
                  
  def Run(self, doc_name='ByteOrbit copy of WrHI spreadsheet for Praekelt TxtAlert'):
    """Expects the name of the spreadsheet to be imported as well as the row numnber to start exxporting from."""
    #get the spread sheet to be worked on
    self.getSpreadsheet(doc_name)
    #get the worksheets on the spreadsheet
    self.getWorksheets()
   

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
        
  sample = SimpleCRUD(user, pw)
  sample.Run()


if __name__ == '__main__':
  main()
