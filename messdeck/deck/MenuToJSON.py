import pandas as pd
import json
import math
import os

class MenuParser:
    
    # This is a simple linear search function to get the nth occurrence of a string in a column
    def get_nth_index_of_value(self, name, column, n):
        i = 0
        for index, item in column.items():
            if(item == name):
                i += 1
                if(i == n):
                    return index      
        
        return -1

    # Checking if an item in the column is a valid food item, some condition could be missing
    def is_valid_menu_item(self, in_str):
        # In case NaN or some other numeric value turns up in the column
        null_check = not pd.isnull(in_str)
        condition = null_check and len(in_str) > 1 and in_str[0] != '*'
        return condition

    def create_menu_structure(self):
        # Loading up the excel file into a python object
        path_to_file = os.path.abspath("media/MessMenu.xlsx")
        menu = pd.read_excel(path_to_file)

        # len of menu is equal to number of rows
        last_row = len(menu)

        # Using the first column as an example to find the range of indices where the menu items are located in the column
        first_column = menu[menu.columns[0]]
        # Ending index is exclusive
        breakfast_range = (self.get_nth_index_of_value("BREAKFAST", first_column, 1) + 1, self.get_nth_index_of_value("LUNCH", first_column, 1) - 1)
        lunch_range = (self.get_nth_index_of_value("LUNCH", first_column, 1) + 1, self.get_nth_index_of_value("DINNER", first_column, 1) - 1)
        dinner_range = (self.get_nth_index_of_value("DINNER", first_column, 1) + 1, last_row)

        # This dict will store the final values for the JSON dump
        dict_for_days = dict()

        for index, column in menu.items():
            # Grabbing the date from the current column
            date_string = column.iat[0].strftime("%Y-%m-%d")
            column_values = column.values
            
            # Simply picking up the items for each meal using the range we stored earlier and using the check function
            list_of_breakfast_items = []
            
            for x in range(breakfast_range[0], breakfast_range[1]):
                if(self.is_valid_menu_item(column_values[x])):
                    list_of_breakfast_items.append(column_values[x])
            
            list_of_lunch_items = []
            
            for x in range(lunch_range[0], lunch_range[1]):
                if(self.is_valid_menu_item(column_values[x])):
                    list_of_lunch_items.append(column_values[x])
                    
            list_of_dinner_items = []
            
            for x in range(dinner_range[0], dinner_range[1]):
                if(self.is_valid_menu_item(column_values[x])):
                    list_of_dinner_items.append(column_values[x])
            
            # Add the entry for the current date into the string
            dict_for_days[date_string] = {'BREAKFAST' : list_of_breakfast_items, 'LUNCH': list_of_lunch_items, 'DINNER': list_of_dinner_items}

        return dict_for_days
    
        # Opening up a new file and serializing the data as JSON
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(dict_for_days, f, ensure_ascii=False, indent=4)
