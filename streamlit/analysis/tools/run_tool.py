import argparse
import xml.etree.ElementTree as ET
import os
import subprocess

def parse_xml_for_command(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extraction de la commande
    command = root.find('.//command').text.strip()

    # Extraction des paramètres d'entrée
    inputs = {param.get('name'): param.get('value', None) for param in root.findall('.//inputs/param')}

    # Extraction des paramètres de sortie
    outputs = {data.get('name'): None for data in root.findall('.//outputs/data')}  # Les chemins de sortie seront définis plus tard

    return command, inputs, outputs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--xml', required=True,
                        help='Galaxy Tool XML Filepath.')
    args = parser.parse_args()

    os.environ['__tool_directory__'] = os.path.dirname(args.xml)

    command_template, inputs, outputs = parse_xml_for_command(args.xml)

    print("Commande :", command_template)
    print("Inputs :", inputs)
    print("Outputs :", outputs)

    subprocess.Popen(command_template, shell=True)

if __name__ == "__main__":
    main()