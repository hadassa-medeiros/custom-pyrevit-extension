# from pyrevit import forms
import csv 

def get_frames_category_info(csv_rows):
  for row in csv_rows:
    try:
      col_1 = row[0]
      col_2 = row[1]
      col_3 = row[2].split(' ')
      col_4 = row[3].split(';')[1]

      elem_codigo_sigla = col_1.split(' ')[0]
      elem_codigo_num = col_1.split(' ')[1].split(';')[0]
      door_type_quant = col_4.split('"')[1]
      # largura = col_1.split(' ')[1].split(';')[0] + col_2.split(' ')[0]
      elem_largura = col_1.split(' ')[1].split(';')[-1].split('"')[-1] + '.' + col_2.split(';')[0].split('"')[0]
      # elem_altura = col_2.split(' ')[0].split('"') + '.' + col_3
      # print(elem_altura)

      # print(elem_codigo_sigla, elem_codigo_num, door_type_quant)
      # print(col_2, '--', col_3)
      return elem_codigo_sigla
    except IndexError as e:
      print(e)

def get_frames_table_info(csv_reader, identifiers):
  frames_table_info = [row for row in csv_reader if any(identifier in ' '.join(row).lower() for identifier in identifiers)]
  return frames_table_info

# Open the CSV file in read mode 
with open("C:/Users/Hadassa/Documents/UFPE-SPO-CCBI/CCS Bloco F/Table1.csv", mode='r', encoding='utf-8') as file: 
  # Create a CSV reader object 
  csv_reader = csv.reader(file)

# Skip the header row (if there is one) 
  next(csv_reader, None) 

# Iterate over each row in the CSV file 
#   for row in csv_reader: 
#     print(row) 
  window_identifiers = ['JA'.lower()]
  door_identifiers = ['PF'.lower(), 'PA'.lower(), 'PM'.lower()]

  doors_info = [row for row in csv_reader if any(door_identifier in ' '.join(row).lower() for door_identifier in door_identifiers)]
  doors_info = [row for row in csv_reader if any(door_identifier in ' '.join(row).lower() for door_identifier in door_identifiers)]

  windows_table = get_frames_table_info(csv_reader, window_identifiers)
  print(windows_table)
# Display the filtered data 
  # for door_info in doors_info:
  #     door_type_code = row[0].split(' ')[0]
  #     door_type_num = row[0].split(' ')[1].split(';')[0]
  #     door_type_quant = row[0].split(' ')[1].split(';')[-1][-1]
  #     print(door_type_quant)
