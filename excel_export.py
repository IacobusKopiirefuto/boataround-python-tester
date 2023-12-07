"""
Module for exporting data to Excel using pandas.
Formats data in thier proper excel formats

Functions:
  -  `exc_export(data, file_name='output')`:
    Writes a list of dictionaries, each containing the information about available boats
    into an Excel file.
    Formats data into their proper Excel formats.
"""


import pandas as pd

def exc_export(data, file_name='output'):
    """
    Writes a list of dictionaries, each containing the information about available boats,
    into an Excel file. Formats data into their proper Excel formats.

    Args:
        data (list): A list of dictionaries, each containing
        the information about available boats.
        file_name (str, optional): String containing the name
        with which the Excel document should be saved.


    Returns:
        None
    """
    boat_data_frame = pd.DataFrame(data)

    # Convert 'check_in' and 'check_out' to datetime objects
    boat_data_frame['check_in'] = pd.to_datetime(boat_data_frame['check_in'])
    boat_data_frame['check_out'] = pd.to_datetime(boat_data_frame['check_out'])

    # Format 'price' as Euro currency
    euro_currency_format = '€#,##0.00'
    # Remove € and convert to float
    boat_data_frame['price'] = boat_data_frame['price'].replace(
            '[€,]', '', regex=True).astype(float)
#   boat_data_frame['price'] = boat_data_frame['price'].map('${:,.2f}'.format)

    #boat_length_format = '#,##0.00 "m"'
    # Remove m and convert to float
    boat_data_frame['price'] = boat_data_frame['price'].replace(
            ' m', '', regex=True).astype(float)

    with pd.ExcelWriter(file_name + '.xlsx', engine='xlsxwriter') as excel_writer:
        boat_data_frame.to_excel(excel_writer, index=False)

        # Get the XlsxWriter workbook and worksheet objects
        workbook = excel_writer.book
        worksheet = excel_writer.sheets['Sheet1']  # Adjust the sheet name as needed

        # Add a currency format for the 'price' column
        price_col = boat_data_frame.columns.get_loc('price')
        currency_format = workbook.add_format({'num_format': euro_currency_format})
        worksheet.set_column(price_col, price_col, None, currency_format)

        # worksheet.set_column('C:C', None, None, {'num_format': boat_length_format})

        # Add a custom date format
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})

        # Apply the custom date format to 'check_in' and 'check_out' columns
        #check_in_col = boat_data_frame.columns.get_loc('check_in')
        #check_out_col = boat_data_frame.columns.get_loc('check_out')
        worksheet.set_column('E:F', None, date_format)
