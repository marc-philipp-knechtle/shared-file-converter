import xmltodict


def read_xml(filepath: str) -> str:
    with open(filepath, "r") as file:
        content: str = file.read()
        return content


def read_and_convert_to_dict(filepath: str) -> dict:
    return xmltodict.parse(read_xml(filepath))
