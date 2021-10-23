"""
DSCI-633 Lab 2: Data Cleansing Python

This is an individual assignment to investigate data cleansing in python

:author:    Stephen Cook <sjc5897@rit.edu>
:language:  Python 3
:created:   9/10/21
:last_edit: 9/17/21
"""
import pandas as pd
import numpy as np
import random

"""
Helper function for clean_patientNo. This function is used to generate a unique ID
It is inefficient, using guess and check
"""
def generate_new_unique_id(count, patientID_data):
    # get the patient ID
    patient_id = patientID_data.loc[count]

    # this while loop ensures unique values.
    # it will generate a random id until one is found not in the data
    # this leads to a potential major inefficiency that in a real system would probably be different
    while patient_id in patientID_data.values:
        # gets new random id within range
        new_id = random.randint(1, 999)

        # format it in the three digit string form
        if new_id < 10:
            patient_id = "00" + str(new_id)
        elif 10 <= new_id < 100:
            patient_id = "0" + str(new_id)
        else:
            patient_id = str(new_id)

    # Once a unique id is found return
    return patient_id

"""
This function is used in the cleaning of the patientNo column
Length:         3 
Data Type:      Char
Valid Values:   Numbers only; if missing, duplicated or none alpha, assign a unique number
"""
def clean_patientNo(patientNo_data):
    # get duplicated boolean list
    duplicated = patientNo_data.duplicated()

    # this is a cheat as the generation algorithm doesn't work with NaN
    patientNo_data = patientNo_data.fillna('XXX')
    count = 0
    # iterate through the data
    for row in patientNo_data:
        try:
            int(row)           # if throws value error exception, it is an invalid patient no
            # check the duplicated list
            if duplicated.loc[count]:
                # if value is duplicated, get the new id
                patientNo_data[count] = generate_new_unique_id(count,patientNo_data)

        except ValueError:
            # if value is invalid, get a new id
            patientNo_data[count] = generate_new_unique_id(count,patientNo_data)
        count += 1

    return patientNo_data


"""
This function is used in the cleaning of the visit column
Length:         8
Data Type:      Char (MMDDYYYY)
Valid Values:   Any Valid Date; If missing 1/1/1900; 
                                if month>12, 12; 
                                if day>31, 31;
                                if year>1999, 1999;
                                if non-digit, 1/1/1990  
"""
def clean_visit(visit_data):
    count = 0
    # iterate through the column
    for row in visit_data:
        try:
            # split the row up into month, day, year
            month = int(row[0:2])
            day = int(row [2:4])
            year = int(row[4:8])

            # verify the data
            if month > 12:
                month = 12
            if day > 31:
                day = 31
            if year > 1999 or year < 1900:
                year = 1999

            # reassembles the date
            visit_data.loc[count] = str(month).zfill(2) + str(day).zfill(2) + str(year)
        except:
            # if error is thrown, it is assumed the data is invalid and set to na
            visit_data.loc[count] = np.nan
        count += 1

    # Fills empty values
    visit_data = visit_data.fillna("01011900")
    return visit_data


"""
This function assists in the cleaning of numeric data in the data sheet
This is for HR, SBP and DBP

The write up is ambitious on how to handle outliers, so I decided to set low outliers to min values
and high outliers to max values

:numeric_data:      The actual data column
:min_value:         The minimum acceptable value for the data; min_value also acts as a replacement value
:max_value:         the maximum acceptable value for the data
"""
def clean_numeric(numeric_data, min_value,max_value):
    count = 0
    # Iterate through numeric data
    for row in numeric_data:
        try:
            # get the value as int
            row = int(row)

            # verify if it is within specified range
            if row <= min_value:
                numeric_data.loc[count] = min_value
            elif row >= max_value:
                numeric_data.loc[count] = max_value

        except ValueError:
            # if value error, row is invalid and replaced with none
            numeric_data.loc[count] = np.nan
        count += 1

    # fill all invalids with the minimum value
    numeric_data = numeric_data.fillna(min_value)
    return numeric_data

"""
Used in the cleaning of the dx column
Length:         3
Data Type:      Char
Valid Values:   1 to 3 digit number;
                if missing, 999
                if non-digit, 999
"""
def clean_dx(dx_data):
    count = 0           # counter var to keep track of place in below iteration

    # look at each item in the column
    for row in dx_data:
        try:
            # Convert to integer, if not int Value Error is thrown
            row = int(row)
            # Check if value is less than 0 or greater than 999
            if row < 0 or row > 999:
                # if yes set value to invalid
                dx_data.loc[count] = np.nan
        except ValueError:
            # If row is not int, it is invalid and set to na
            dx_data.loc[count] = np.nan
        count += 1

    # fill empties with 999 and return
    dx_data = dx_data.fillna('999')
    return dx_data


"""
Used in the cleaning of Adverse Advents
Length:         1
Data Type:      Char (Boolean)
Valid Values:   '0' or '1'; if missing or invalid 0; 
"""
def clean_ae(ae_data):
    count = 0           # counter variable to keep track of place in below iteration

    # look at each item in the column
    for row in ae_data:
        # if row does not == '0' and '1'
        if row != '0' and row != '1':
            # set to none
            ae_data.loc[count] = np.nan
        count += 1

    # fill all nones with '0' and return
    ae_data = ae_data.fillna('0')
    return ae_data


"""
Main, runs the function
"""
if __name__ == '__main__':
    # pandas module = pd; numpy = np

    # read in the data file
    data = pd.read_csv('patients.txt', sep=";", header=None)

    """
    Set table headers, 
        patientNo:  Patient ID
        gender:     Patient Gender 
        visit:      Date of Visit (MMDDYYYY)
        hr:         Heart rate
        sbp:        Systolic blood pressure
        dbp:        Diastolic blood pressure
        dx:         Diagnosis code 
        ae:         Adverse Event
    """
    data.columns = ['patientNo', 'gender', 'visit', 'hr', 'sbp', 'dbp', 'dx', 'ae']

    # set all blank entries with NaN
    data = data.replace(r'^\s*$', np.nan, regex=True)

    # # clean patientNo
    data['patientNo'] = clean_patientNo(data['patientNo'])
    # clean visit
    data['visit'] = clean_visit(data['visit'])
    # clean hr, min = 40, max = 100
    data['hr'] = clean_numeric(data['hr'], 40, 100)
    # clean sbp, min = 80 , max = 200
    data['sbp'] = clean_numeric(data['sbp'], 80, 200)
    # clean dbp, min = 80 , max = 200
    data['dbp'] = clean_numeric(data['dbp'], 60, 120)
    # clean dx
    data['dx'] = clean_dx(data['dx'])
    # clean ae
    data['ae'] = clean_ae(data['ae'])

    # print the cleaned data to an output file with similar characteristics as the text file
    data.to_csv('output_patients.txt', sep=";", header=None, index=False)
