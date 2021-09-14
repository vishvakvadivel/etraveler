import time  # imports time module

# import serial  # imports serial module to read values from arduino
import pandas as pd
import sqlalchemy as sql
import json
import datetime

# dictionary for operator training matrix
operatortrainingdict = {
    "Preclean": [
        "Leo McGuire",
        "Rith Phal",
        "Tony Inthirath",
        "Heather Tragash",
        "Liz Hernandez",
        "Chance Souvannadeth",
        "Bob Halliday",
    ],
    "Spin": [
        "Leo McGuire",
        "Rith Phal",
        "Melinda Clemens",
        "Chance Souvannadeth",
        "Bob Halliday",
    ],
    "PR Application": [
        "Leo McGuire",
        "Rith Phal",
        "Melinda Clemens",
        "Chance Souvannadeth",
        "Bob Halliday",
    ],
    "Antihalation": [
        "Rith Phal",
        "Tony Inthirath",
        "Heather Tragash",
        "Bob Halliday",
    ],
    "Softbake": [
        "Leo McGuire",
        "Rith Phal",
        "Tony Inthirath",
        "Melinda Clemens",
        "Heather Tragash",
        "Chance Souvannadeth",
        "Bob Halliday",
    ],
    "Hardbake": [
        "Leo McGuire",
        "Rith Phal",
        "Tony Inthirath",
        "Melinda Clemens",
        "Heather Tragash",
        "Chance Souvannadeth",
        "Bob Halliday",
    ],
    "Setup for Exposure": [
        "Rith Phal",
        "Tony Inthirath",
        "Chance Souvannadeth",
        "Bob Halliday",
    ],
    "Exposure": [
        "Rith Phal",
        "Tony Inthirath",
        "Chance Souvannadeth",
        "Bob Halliday",
    ],
    "Flatness": ["Leo McGuire", "Heather Tragash", "Bob Halliday"],
    "Metalization": [
        "Leo McGuire",
        "Heather Tragash",
        "Chance Souvannadeth",
        "Bob Halliday",
    ],
    "Packaging": [
        "Rith Phal",
        "Heather Tragash",
        "Liz Hernandez",
        "Bob Halliday",
    ],
    "Preliminary Cosmetic Inspection": [
        "Leo McGuire",
        "Rith Phal",
        "Tony Inthirath",
        "Heather Tragash",
        "Chance Souvannadeth",
        "Bob Halliday",
    ],
    "Pretest Cosmetic Inspection": [
        "Leo McGuire",
        "Rith Phal",
        "Tony Inthirath",
        "Heather Tragash",
        "Chance Souvannadeth",
        "Bob Halliday",
    ],
    "Stray Light": ["Leo McGuire", "Rith Phal", "Heather Tragash"],
    "Final Efficiency Test": [
        "Leo McGuire",
        "Rith Phal",
        "Tony Inthirath",
        "Heather Tragash",
        "Bob Halliday",
    ],
    "Final Visual Inspection": [
        "Leo McGuire",
        "Rith Phal",
        "Tony Inthirath",
        "Heather Tragash",
        "Bob Halliday",
    ],
}


class Tools:
    def __init__(self):
        self.db_connection_str = "mysql+pymysql://vishvak:vishvakshaya05@45.33.72.29/processdb"  # database connection string

    def isoperator(
        self, operator, processstep
    ):  # function checks if operator is trained for the step in the training matrix

        with open(
            "operatordict.txt"
        ) as file:  # opens the text file with the dictionary for training matrix
            data = json.load(file)  # grabs the data using json

        file.close()  # closes file

        if (
            operator in data[processstep]
        ):  # sees if operator submitted is in the list of the corresponding process step key in the dict
            return operator  # returns operator

    def processpdf(self, table):  # function to create pandas dataframe from sql table

        db_connection = sql.create_engine(
            self.db_connection_str
        )  # creates actual connection

        query = "SELECT * FROM {}".format(
            table
        )  # sql query to select all data for the table passed in the function

        df = pd.read_sql(query, con=db_connection)  # creates dataframe

        return df

    # def getvalues():
    #  arduino = serial.Serial("COM6", baudrate=9600, timeout=1)
    # time.sleep(3)
    # data = arduino.readline().decode().strip("\r\n").split(",")

    # return data

    def newop(
        self, op, addstep
    ):  # function takes in new operator and step operator is being added to

        with open("operatordict.txt") as file:  # opens file with operator dict
            data = json.load(file)  # loads the data with json

        file.close()  # cloases file

        data[addstep].append(
            op
        )  # appends new operator to the step desired from the dictionary

        with open("operatordict.txt", "w") as file:
            file.write(json.dumps(data))  # rewrites the data in the txt file
        file.close()  # closes file

    def lessop(
        self, op, remstep
    ):  # function takes in old operator and step operator is being removed from
        with open("operatordict.txt") as file:  # opens file with operator dict
            data = json.load(file)  # loads dictionary

        file.close()  # closes file

        data[remstep].remove(
            op
        )  # removes operator from desired step from the coreresponding process key value in the dictionary

        with open("operatordict.txt", "w") as file:
            file.write(json.dumps(data))  # rewrites data
        file.close()  # closes file

    # def arduinoconnect():  # may not use arduino now and use DicksonOne

    # try:

    # arduino = serial.Serial("COM6", baudrate=9600, timeout=1)

    # return True

    # except serial.serialutil.SerialException:

    # return False

    def propdfilter(self, x, y, z, m, v):  # filter for process talble

        db_connection = sql.create_engine(
            self.db_connection_str
        )  # creates actual connection to server and database

        query = "SELECT * FROM {}".format(
            z
        )  # sql query to grab all records of desired table

        df = pd.read_sql(query, con=db_connection)  # creates dataframe for sql table

        if x == "in process":  # sees if in process was selected from the filter options

            profiltereddf = df.drop(
                df.index[df["Step"] == "Packaging"]
            )  # creates a dataframe that drops all of the work orders that have finsihed the packaging step, as all orders that have not reaches this step are in process

        else:

            profilterdict = {  # dictionary for filter category and value selection
                "work order": df.WorkOrder == y,
                "part number": df.P_N == y,
                "operator": df.Operator == y,
                # user selects one of the filter options from the drop down menu and inputs a value, then the corresponding key in the dictionary will pick the proper pandas search query
                "step": df.Step == y,
            }

            profilterdict2 = {
                "work order": df.WorkOrder == v,  # second category
                "part number": df.P_N == v,
                # user selects one of the filter options from the drop down menu and inputs a value, then the corresponding key in the dictionary will pick the proper pandas search query
                "operator": df.Operator == v,
                "step": df.Step == v,
            }

            profiltereddf = df[
                (profilterdict[x]) & (profilterdict2[m])
            ]  # creates a dataframe with the combined pandas search queries

        return profiltereddf  # returns the dataframe

    def rejpdfilter(self, x, y, z, m, v):  # filter for rejection table

        db_connection = sql.create_engine(
            self.db_connection_str
        )  # creates actual connection to server and database

        query = "SELECT * FROM {}".format(z)  # sql query to select all records

        df = pd.read_sql(query, con=db_connection)  # creates dataframe from sql table

        rejfilterdict = {  # dictionary for filter category and value selection
            "part number": df.P_N == y,
            "code": df.RejCode == y,
            "operator": df.Operator == y,
            # user selects one of the filter options from the drop down menu and inputs a value, then the corresponding key in the dictionary will pick the proper pandas search query
            "step": df.ProcessStep == y,
        }
        rejfilterdict2 = {
            "part number": df.P_N == v,  # second category
            "code": df.RejCode == v,
            "operator": df.Operator == v,
            # user selects one of the filter options from the drop down menu and inputs a value, then the corresponding key in the dictionary will pick the proper pandas search query
            "step": df.ProcessStep == v,
        }

        rejfiltereddf = df[
            (rejfilterdict[x]) & (rejfilterdict2[m])
        ]  # creates dataframe with combined pandas search queries

        return rejfiltereddf  # function returns dataframe

    def get_current_qty(self, work_order):

        try:
            db_connection = sql.create_engine(
                self.db_connection_str
            )  # creates actual connection

            process_query = "SELECT * FROM {}".format(
                "processstep"
            )  # sql query to select all records for the table

            rejection_query = "SELECT * FROM {}".format("rejectiondata")

            process_df = pd.read_sql(
                process_query, con=db_connection
            )  # creates df for process data

            rejection_df = pd.read_sql(
                rejection_query, con=db_connection
            )  # creates df for rejection data

            original_quantity = process_df.loc[
                process_df["WorkOrder"] == work_order, "OriginalTrayQty"
            ].iloc[0]

            total_rejections = rejection_df.loc[
                rejection_df["WorkOrder"] == work_order, "Quantity"
            ].sum()

            current_quantity = original_quantity - total_rejections

            return current_quantity

        except IndexError:

            return None

    def processautofill(
        self, workorder
    ):  # function for autofill data, it recieves a work order

        try:
            db_connection = sql.create_engine(
                self.db_connection_str
            )  # creates actual connection

            query = "SELECT * FROM {}".format(
                "processstep"
            )  # sql query to select all records for the table

            processdf = pd.read_sql(query, con=db_connection)  # creates df

            prodf = processdf["OriginalTrayQty"].where(
                processdf["WorkOrder"] == workorder
            )  # creates df where it only has the orginal tray qwuantity for the desired work order

            partnumdf = processdf["P_N"].where(
                processdf["WorkOrder"] == workorder
            )  # creates a df for the P_N of the desired work order
            partnumlist = (
                partnumdf.dropna().tolist()
            )  # turns the df into a list and drops null values

            duedf = processdf["Due_Date"].where(
                processdf["WorkOrder"] == workorder
            )  # creates a df with only the due date of the desired work order

            duelist = (
                duedf.dropna().tolist()
            )  # turns df into a list and drops null values

            due_date = duelist[
                0
            ]  # index the first value in the due date list to get due date as all the values in the list will be the same anyway

            p_n = partnumlist[0]  # gets part number
            return p_n, due_date  # returns values

        except IndexError:  # catches indexverror

            p_n = None  # sets part number to none

            due_date = None  # sets due date to none

            return p_n, due_date

    def reject_check(self, workorder):
        try:
            db_connection = sql.create_engine(
                self.db_connection_str
            )  # creates actual connection

            query = "SELECT * FROM {}".format(
                "processstep"
            )  # sql query to select all records for the table

            processdf = pd.read_sql(query, con=db_connection)  # creates df

            prodf = processdf["OriginalTrayQty"].where(
                processdf["WorkOrder"] == workorder
            )  # creates df where it only has the orginal tray quantity for the desired work order
            qtylist = (
                prodf.dropna().tolist()
            )  # creates a list of the orignal tray quantities and drops null values

            query = "SELECT * FROM {}".format(
                "rejectiondata"
            )  # sql query to select all records for the table

            rejectdf = pd.read_sql(query, con=db_connection)  # creates df

            reject_total = rejectdf.loc[
                rejectdf["WorkOrder"] == workorder, "Quantity"
            ].sum()  # sums the rejections for the workorder

            final_qty = qtylist[0] - reject_total  # finds what final tray qty should be

            return final_qty

        except IndexError:  # catches index error

            pass
