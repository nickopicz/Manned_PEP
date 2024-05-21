import xml.etree.ElementTree as ET
import csv

#if you get a new epf file,just change to this
# epf files are given by inmotion so you shouldnt worry unless you need help from inmotion
tree = ET.parse('69GUS222C00x05.epf')
root = tree.getroot()


def extract_parameters(group):
    parameters = []
    for param in group.findall('Parameter'):
        param_attrs = {attr: param.attrib[attr] for attr in param.attrib}

        description_element = param.find('Description')
        description = ''.join(description_element.itertext()).strip(
        ) if description_element is not None else ''
        param_attrs['Description'] = description

        parameters.append(param_attrs)
    return parameters


# Specify the CSV file name
csv_file_name = 'parameters.csv'

headers = ['SymbolName', 'Index', 'SubIndex', 'ObjectType', 'DataType', 'Visibility',
           'AccessType', 'MinimumValue', 'MaximumValue', 'DefaultValue', 'Factor', 'Unit', 'Description']

# Initialize a list to store all parameters
all_params = []

dictionary_section = root.find('.//Dictionary/Parameters')
if dictionary_section is not None:
    for group in dictionary_section.findall('Group'):
        # Extract parameters from each group and add them to the all_params list
        all_params.extend(extract_parameters(group))

with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    for param in all_params:
        # Ensure the row only contains headers that are present in this parameter
        row = {header: param.get(header, '') for header in headers}
        writer.writerow(row)
