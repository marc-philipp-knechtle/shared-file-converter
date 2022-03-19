import json
import os
from unittest import TestCase

from bson import json_util
from deepdiff import DeepDiff

from converter.validator import reader
from docrecjson.elements import Document

script_dir = os.path.dirname(__file__)


def read_json(filepath: str):
    with open(filepath) as simple_image_region:
        return json.loads(simple_image_region.read(), object_hook=json_util.object_hook)


def run_end_to_end_conversion(xml_path: str, json_path: str):
    """
    :param xml_path: path to your xml file as seen from /tests/fixtures/page-xml/2017-07-15/ e.g.
    /image-region/simple-image-region.xml
    :param json_path:
    :return:
    """
    local_fixture_path: str = "/fixtures/page-xml/2017-07-15/region"
    document: Document = reader.handle_incoming_file(script_dir + local_fixture_path + xml_path)
    manual_json = read_json(script_dir + local_fixture_path + json_path)
    ddiff = DeepDiff(document.to_dict(), manual_json)
    assert ddiff == {}


class TestImageRegion(TestCase):

    def test_simple_image_region(self):
        xml_filepath: str = "/image-region/simple-image-region.xml"
        run_end_to_end_conversion(xml_filepath, xml_filepath + ".json")

    def test_nested_image_region(self):
        xml_filepath: str = "/image-region/nested-image-region.xml"
        run_end_to_end_conversion(xml_filepath, xml_filepath + ".json")


class TestTextRegion(TestCase):
    def test_simple_text_region(self):
        xml_filepath: str = "/text-region/simple-text-region.xml"
        run_end_to_end_conversion(xml_filepath, xml_filepath + ".json")

    def test_text_region_with_text_equiv(self):
        xml_filepath: str = "/text-region/text-region-with-text-equiv.xml"
        run_end_to_end_conversion(xml_filepath, xml_filepath + ".json")

    def test_text_region_with_text_line(self):
        xml_filepath: str = "/text-region/text-region-with-text-line.xml"
        run_end_to_end_conversion(xml_filepath, xml_filepath + ".json")

    def test_text_region_with_text_style(self):
        xml_filepath: str = "/text-region/text-region-with-text-style.xml"
        run_end_to_end_conversion(xml_filepath, xml_filepath + ".json")
