import zipfile
import csv
import xml.etree.ElementTree as ET
import boto3

url = "http://firds.esma.europa.eu/firds/DLTINS_20210117_01of01.zip"
response = requests.get(url)

zip_file = zipfile.ZipFile(io.BytesIO(response.content))
xml_content = zip_file.read("DLTINS_20220131_01of01.xml").decode("utf-8")

root = ET.fromstring(xml_content)

ns = {'ns': 'urn:iso:std:iso:20022:tech:xsd:head.003.001.01'}

header = [
    'FinInstrmGnlAttrbts.Id',
    'FinInstrmGnlAttrbts.FullNm',
    'FinInstrmGnlAttrbts.ClssfctnTp',
    'FinInstrmGnlAttrbts.CmmdtyDerivInd',
    'FinInstrmGnlAttrbts.NtnlCcy',
    'Issr',
]

s3 = boto3.client('s3')

with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()

    for instr in root.findall('.//ns:FinInstrmGnlAttrbts', ns):
        row = {
            'FinInstrmGnlAttrbts.Id': instr.find('ns:Id', ns).text,
            'FinInstrmGnlAttrbts.FullNm': instr.find('ns:FullNm', ns).text,
            'FinInstrmGnlAttrbts.ClssfctnTp': instr.find('ns:ClssfctnTp', ns).text,
            'FinInstrmGnlAttrbts.CmmdtyDerivInd': instr.find('ns:CmmdtyDerivInd', ns).text,
            'FinInstrmGnlAttrbts.NtnlCcy': instr.find('ns:NtnlCcy', ns).text,
            'Issr': instr.find('ns:Issr', ns).text,
        }
        writer.writerow(row)

with open('output.csv', 'rb') as csvfile:
    s3.upload_fileobj(csvfile, 'your-bucket-pythim', 'output.csv')