import re
from datetime import date
from typing import Sequence, Tuple

from loguru import logger

from converter.elements import PageConversionStrategy, ConverterDocument
from converter.strategies.generated.page_xml.py_xb_2017 import PcGtsType, UserDefinedType, TextRegionType, TextLineType, \
    CoordsType, PointsType
from docrecjson.commontypes import Points, Point
from docrecjson.elements import Document


class PageXML2017StrategyPyXB(PageConversionStrategy):
    """
    assumptions:
        *   each region is a group -> top level regions of any type will always share a common group id
        *   Nested xml objects are currently not allowed
            In this PageXML version, there are the following complex base Regions:
                - TextRegion
                - ImageRegion
                - LineDrawingRegion
                - GraphicRegion
                - TableRegion
                - ChartRegion
                - SeparatorRegion
                - MathsRegion
                - ChemRegion
                - MusicRegion
                - AdvertRegion
                - NoiseRegion
                - UnknownRegion
            Theoretically, each Region could have any other Region as subtype. This subtyping is not processed.
            I don't know whether it's intended that you could theoretically have a ImageRegion as Subtype of an
            TextRegion, but the xsd schema would allow it.
            It originates from the dependency of each ...Type to RegionType, which includes the other ...Types.
            The dependency to RegionType is necessary to include basic properties e.g. Coordinates.
    """

    # This is not inspected because moving this out of the strategy may be very confusing
    # Furthermore this may be necessary to implement for each strategy and be moved therefore into ConversionStrategy
    #   or a page subclass.
    # noinspection PyMethodMayBeStatic
    def _execute_if_present(self, py_xb_object_condition, func, *args):
        if not py_xb_object_condition:
            logger.debug("[" + str(type(py_xb_object_condition)) + "] is not present in the currently created object.")
        else:
            func(*args)

    # noinspection PyMethodMayBeStatic
    def _create_user_defined_metadata(self, user_defined_metadata: UserDefinedType) -> dict:
        # todo mitigate the necessity for this behaviour or create an abstract function which performs this check
        if user_defined_metadata is None:
            return {}
        dct = {}
        for attribute in user_defined_metadata.UserAttribute:
            dct[str(attribute.name)] = str(attribute.value_)
        return dct

    def initialize(self, original: ConverterDocument) -> ConverterDocument:
        pyxb_object: PcGtsType = original.tmp_type
        document: Document = Document.empty(pyxb_object.Page.imageFilename,
                                            (pyxb_object.Page.imageHeight, pyxb_object.Page.imageWidth))
        document.add_creator(pyxb_object.Metadata.Creator, "2017-07-15")
        document.add_creator("shared-file-converter", str(date.today()))
        original.shared_file_format_document = document
        return original

    def add_metadata(self, original: ConverterDocument) -> ConverterDocument:
        pyxb_object: PcGtsType = original.tmp_type
        document: Document = original.shared_file_format_document

        document.add_metadata({"LastChange": str(pyxb_object.Metadata.LastChange)})
        self._execute_if_present(pyxb_object.Metadata.Comments, document.add_metadata,
                                 {"Comments": str(pyxb_object.Metadata.Comments)})
        self._execute_if_present(pyxb_object.Metadata.UserDefined, document.add_metadata,
                                 self._create_user_defined_metadata(pyxb_object.Metadata.UserDefined))
        self._execute_if_present(pyxb_object.Metadata.externalRef, document.add_metadata,
                                 {"externalRef": str(pyxb_object.Metadata.externalRef)})

        original.shared_file_format_document = document
        return original

    def add_regions(self, original: ConverterDocument) -> ConverterDocument:
        pyxb_object: PcGtsType = original.tmp_type
        document: Document = original.shared_file_format_document

        self._execute_if_present(pyxb_object.Page.TextRegion, document.add_region,
                                 self.handle_text_region(pyxb_object.Page.TextRegion), "text")

        original.shared_file_format_document = document
        return original

    def handle_text_region(self, text_regions):

        print(str(type(text_regions)))
        text_region: TextRegionType
        for text_region in text_regions:
            text_lines = text_region.TextLine
            text_line: TextLineType
            for text_line in text_lines:
                points = self.handle_coords_type(text_line.Coords)
                print("asdf")
            # points = text_line.Coords.points
            # baseline = text_line.Baseline.points
            # text_equiv = text_line.TextEquiv.Unicode
            print("asdf")
        pass

    def handle_coords_type(self, coords: CoordsType) -> Sequence[Tuple[int, int]]:
        """
        the coords entries have been previously xsd-validated using: ([0-9]+,[0-9]+ )+([0-9]+,[0-9]+)
        :param coords:
        :return:
        """
        points: PointsType = coords.points
        coords_pairs = re.findall("([0-9]+,[0-9]+ )", str(points))
        pair: str
        points = []
        for pair in coords_pairs:
            pair_tuple = pair.split(",")
            x = int(pair_tuple[0])
            y = int(pair_tuple[1])
            point = (x, y)
            points.append(point)
        return points

    def handle_image_region(self, image_region_type) -> dict:
        pass

    def handle_line_drawing_region(self, line_drawing_region_type) -> dict:
        pass
