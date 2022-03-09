import re
from datetime import date
from typing import Sequence, Tuple

from loguru import logger

from converter.elements import PageConversionStrategy, ConverterDocument
from converter.strategies.generated.page_xml.py_xb_2017 import PcGtsType, UserDefinedType, TextRegionType, CoordsType, \
    PointsType
from docrecjson.elements import Document, Region


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
        if py_xb_object_condition:
            func(*args)

    def _log_warning_not_processed_if_present(self, obj, property_name: str):
        if obj:
            logger.warning(property_name + "= [" + str(obj) + "] is not further processed.")

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

        # self._execute_if_present(pyxb_object.Page.TextRegion, document.add_region,
        #                          self.handle_text_region(pyxb_object.Page.TextRegion), "text")
        if self._is_present(pyxb_object.Page.TextRegion):
            document = self.handle_text_region(pyxb_object.Page.TextRegion, document)

        original.shared_file_format_document = document
        return original

    def handle_text_region(self, text_regions, document: Document) -> Document:
        """
        Problem: Text Regions in PageXML sind nicht eindeutig
        -> können ein Wrapper für mehrere TextLines sein -> eigentlich eher als group id für baselines/andere text objects zu verstehen
        -> können ein Wrapper für mehrere TextEquiv sein -> eigentlich eher als group id für andere Text objects
        -> stehen für sich alleine -> realer Region type ohne andere sachen

        :param document:
        :param text_regions:
        :return:
        """

        text_region: TextRegionType
        for text_region in text_regions:
            if self._has_complex_subtype(text_region):
                # this text regions has subtypes
                # -> it only serves the purpose of beeing a group id for it's subtypes
                document = self._handle_complex_text_region_type(document, text_region)
            else:
                # this text region stands for itself without any further information
                # -> it's added to document engine as text content
                document = self._handle_simple_text_region_type(document, text_region)

            self._log_warn_missing_simple_root_text_region_attributes(text_region)

        return document

    def _handle_simple_text_region_type(self, document: Document, text_region: TextRegionType) -> Document:
        coordinates = self.handle_coords_type(text_region.Coords)
        region_type: str = "text"
        region_subtype = text_region.type
        document.add_region(coordinates, region_type, region_subtype)
        return document

    def _handle_complex_text_region_type(self, document: Document, text_region: TextRegionType) -> Document:
        # text_lines = text_region.TextLine
        # text_line: TextLineType
        # for text_line in text_lines:
        #     points = self.handle_coords_type(text_line.Coords)
        logger.error("not implemented")
        return document

    def _log_warn_missing_simple_root_text_region_attributes(self, text_region):
        self._log_warning_not_processed_if_present(text_region.align, "align")
        self._log_warning_not_processed_if_present(text_region.comments, "comments")
        self._log_warning_not_processed_if_present(text_region.continuation, "continuation")
        self._log_warning_not_processed_if_present(text_region.custom, "custom")
        self._log_warning_not_processed_if_present(text_region.indented, "indented")
        self._log_warning_not_processed_if_present(text_region.leading, "leading")
        self._log_warning_not_processed_if_present(text_region.orientation, "orientation")
        self._log_warning_not_processed_if_present(text_region.primaryLanguage, "primaryLanguage")
        self._log_warning_not_processed_if_present(text_region.primaryScript, "primaryScript")
        self._log_warning_not_processed_if_present(text_region.production, "production")
        self._log_warning_not_processed_if_present(text_region.readingDirection, "readingDirection")
        self._log_warning_not_processed_if_present(text_region.readingOrientation, "readingOrientation")
        self._log_warning_not_processed_if_present(text_region.secondaryLanguage, "secondaryLanguage")
        self._log_warning_not_processed_if_present(text_region.textLineOrder, "textLineOrder")

    def _check_plural_binding_length(self, _plural_binding_object) -> int:
        return len(_plural_binding_object)

    def _has_complex_subtype(self, text_region: TextRegionType) -> bool:
        length_of_all_types: int = self._check_plural_binding_length(
            text_region.AdvertRegion) + self._check_plural_binding_length(
            text_region.ChartRegion) + self._check_plural_binding_length(
            text_region.ChemRegion) + self._check_plural_binding_length(
            text_region.GraphicRegion) + self._check_plural_binding_length(
            text_region.ImageRegion) + self._check_plural_binding_length(
            text_region.LineDrawingRegion) + self._check_plural_binding_length(
            text_region.MathsRegion) + self._check_plural_binding_length(
            text_region.MusicRegion) + self._check_plural_binding_length(
            text_region.NoiseRegion) + self._check_plural_binding_length(
            text_region.SeparatorRegion) + self._check_plural_binding_length(
            text_region.TableRegion) + self._check_plural_binding_length(
            text_region.TextEquiv) + self._check_plural_binding_length(
            text_region.TextLine) + self._check_plural_binding_length(
            text_region.TextRegion) + self._check_plural_binding_length(
            text_region.UnknownRegion)
        return True if length_of_all_types != 0 else False

    def _is_present(self, _plural_binding_object) -> bool:
        return True if len(_plural_binding_object) != 0 else False

    def handle_text_line(self):
        pass

    def handle_text_equiv(self):
        pass

    def handle_text_style(self):
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
        points_shared_file_format = []
        for pair in coords_pairs:
            pair_tuple = pair.split(",")
            x = int(pair_tuple[0])
            y = int(pair_tuple[1])
            point = (x, y)
            points_shared_file_format.append(point)
        return points_shared_file_format

    def handle_image_region(self, image_region_type) -> Region:
        pass

    def handle_line_drawing_region(self, line_drawing_region_type) -> Region:
        pass

    def handle_graphic_region(self, graphic_region_type) -> Region:
        pass

    def handle_table_region(self, table_region_type) -> Region:
        pass

    def handle_chart_region(self, chart_region_type) -> Region:
        pass

    def handle_separator_region(self, separator_region_type) -> Region:
        pass

    def handle_maths_region(self, maths_region_type) -> Region:
        pass

    def handle_chem_region(self, chem_region_type) -> Region:
        pass

    def handle_music_region(self, music_region_type) -> Region:
        pass

    def handle_advert_region(self, advert_region_type) -> Region:
        pass

    def handle_noise_region(self, noise_region_type) -> Region:
        pass

    def handle_unknown_region(self, unknown_region_type) -> Region:
        pass
