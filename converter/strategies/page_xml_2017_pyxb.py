import functools
import re
from datetime import date
from typing import Sequence, Tuple, Optional

from loguru import logger
# noinspection PyProtectedMember
from pyxb.binding.content import _PluralBinding

from converter.elements import PageConversionStrategy, ConverterDocument
from converter.strategies.generated.page_xml.py_xb_2017 import PcGtsType, UserDefinedType, TextRegionType, CoordsType, \
    PointsType, TextLineType, BaselineType, TextEquivType, TextStyleType
from docrecjson.elements import Document, Region, PolygonRegion, GroupRef


def execute_if_present(func):
    """
    Wraps a function call into a presence check. This is intended for a presence detection for pyXB objects.
    requires to argument to be default returned as first position argument and the argument to check presence as the
    second argument.
    :param func:
    :return: returns the second argument (first argument after self) of the function to allow usage in direct
    assignments.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if type(args[2]) == _PluralBinding:
            if len(args[2]) != 0:
                return func(*args, **kwargs)
            else:
                return args[1]
        elif args[2]:
            return func(*args, **kwargs)
        else:
            return args[1]

    return wrapper


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

    def _warn_if_present(self, obj, property_name: str):
        if obj:
            logger.warning(property_name + "= [" + str(obj) + "] is not further processed.")

    # noinspection PyMethodMayBeStatic
    def _create_user_defined_metadata(self, user_defined_metadata: UserDefinedType) -> dict:
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

        document = self.handle_text_regions(document, pyxb_object.Page.TextRegion)

        original.shared_file_format_document = document
        return original

    """
    Text Region Handling
    """

    @execute_if_present
    def handle_text_regions(self, document: Document, text_regions) -> Document:
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

            self._warn_simple_text_region_root(text_region)

        return document

    def _handle_simple_text_region_type(self, document: Document, text_region: TextRegionType) -> Document:
        coordinates = self.handle_coords_type(text_region.Coords)
        region_type: str = "text"
        region_subtype = text_region.type
        document.add_region(coordinates, region_type, region_subtype)
        document = self.handle_text_style(document, text_region.TextStyle)
        return document

    def _handle_complex_text_region_type(self, document: Document, text_region: TextRegionType) -> Document:
        coordinates = self.handle_coords_type(text_region.Coords)
        region_type: str = "text"
        region_subtype = text_region.type
        region_identification: PolygonRegion = document.add_region(coordinates, region_type, region_subtype)

        document = self.handle_text_lines(document, text_region.TextLine, region_identification)
        document = self.handle_text_equiv(document, text_region.TextEquiv, region_identification)
        document = self.handle_text_style(document, text_region.TextStyle)

        return document

    def _warn_simple_text_region_root(self, text_region):
        self._warn_if_present(text_region.align, "align")
        self._warn_if_present(text_region.comments, "comments")
        self._warn_if_present(text_region.continuation, "continuation")
        self._warn_if_present(text_region.custom, "custom")
        self._warn_if_present(text_region.indented, "indented")
        self._warn_if_present(text_region.leading, "leading")
        self._warn_if_present(text_region.orientation, "orientation")
        self._warn_if_present(text_region.primaryLanguage, "primaryLanguage")
        self._warn_if_present(text_region.primaryScript, "primaryScript")
        self._warn_if_present(text_region.production, "production")
        self._warn_if_present(text_region.readingDirection, "readingDirection")
        self._warn_if_present(text_region.readingOrientation, "readingOrientation")
        self._warn_if_present(text_region.secondaryLanguage, "secondaryLanguage")
        self._warn_if_present(text_region.textLineOrder, "textLineOrder")

    def _len_plural_binding(self, _plural_binding_object: _PluralBinding) -> int:
        return len(_plural_binding_object)

    def _has_complex_subtype(self, text_region: TextRegionType) -> bool:
        length_of_all_types: int = self._len_plural_binding(
            text_region.AdvertRegion) + self._len_plural_binding(
            text_region.ChartRegion) + self._len_plural_binding(
            text_region.ChemRegion) + self._len_plural_binding(
            text_region.GraphicRegion) + self._len_plural_binding(
            text_region.ImageRegion) + self._len_plural_binding(
            text_region.LineDrawingRegion) + self._len_plural_binding(
            text_region.MathsRegion) + self._len_plural_binding(
            text_region.MusicRegion) + self._len_plural_binding(
            text_region.NoiseRegion) + self._len_plural_binding(
            text_region.SeparatorRegion) + self._len_plural_binding(
            text_region.TableRegion) + self._len_plural_binding(
            text_region.TextEquiv) + self._len_plural_binding(
            text_region.TextLine) + self._len_plural_binding(
            text_region.TextRegion) + self._len_plural_binding(
            text_region.UnknownRegion)
        return True if length_of_all_types != 0 else False

    @execute_if_present
    def handle_text_lines(self, document: Document, text_lines: _PluralBinding,
                          group_ref: Optional[GroupRef] = None) -> Document:
        text_line: TextLineType
        for text_line in text_lines:
            points = self.handle_coords_type(text_line.Coords)
            baseline_points = self.handle_baseline_type([], text_line.Baseline)

            if len(points) != 0:
                document.add_line_polygon(points, group_ref)
            if len(baseline_points) != 0:
                document.add_baseline(points, group_ref)

            self._warn_if_present(text_line.id, "id")
            self._warn_if_present(text_line.primaryLanguage, "primaryLanguage")
            self._warn_if_present(text_line.primaryScript, "primaryScript")
            self._warn_if_present(text_line.secondaryScript, "secondaryScript")
            self._warn_if_present(text_line.readingDirection, "readingdirection")
            self._warn_if_present(text_line.production, "production")
            self._warn_if_present(text_line.custom, "custom")
            self._warn_if_present(text_line.comments, "comments")

            self._warn_if_present(text_line.Word, "word")
            self._warn_if_present(text_line.TextEquiv, "textEquiv")
            self._warn_if_present(text_line.TextStyle, "textStyle")
            self._warn_if_present(text_line.UserDefined, "userDefined")

        return document

    @execute_if_present
    def handle_text_equiv(self, document: Document, text_equivs: _PluralBinding,
                          group_ref: Optional[GroupRef] = None) -> Document:
        text_equiv: TextEquivType
        for text_equiv in text_equivs:
            unicode: str = text_equiv.Unicode
            document.add_text(unicode, group_ref)

            self._warn_if_present(text_equiv.index, "index")
            self._warn_if_present(text_equiv.conf, "confidence")
            self._warn_if_present(text_equiv.dataType, "dataType")
            self._warn_if_present(text_equiv.dataTypeDetails, "dataTypeDetails")
            self._warn_if_present(text_equiv.comments, "comments")

        return document

    @execute_if_present
    def handle_text_style(self, document: Document, text_style: TextStyleType) -> Document:
        self._warn_if_present(text_style.fontFamily, "fontFamily")
        self._warn_if_present(text_style.serif, "serif")
        self._warn_if_present(text_style.monospace, "monospace")
        self._warn_if_present(text_style.fontSize, "fontSize")
        self._warn_if_present(text_style.xHeight, "xHeight")
        self._warn_if_present(text_style.kerning, "kerning")
        self._warn_if_present(text_style.textColour, "textColour")
        self._warn_if_present(text_style.textColourRgb, "textColourRgb")
        self._warn_if_present(text_style.bgColour, "bgColour")
        self._warn_if_present(text_style.bgColourRgb, "bgColourRgb")
        self._warn_if_present(text_style.reverseVideo, "reverseVideo")
        self._warn_if_present(text_style.bold, "bold")
        self._warn_if_present(text_style.italic, "italic")
        self._warn_if_present(text_style.underlined, "underlined")
        self._warn_if_present(text_style.subscript, "subscript")
        self._warn_if_present(text_style.superscript, "superscript")
        self._warn_if_present(text_style.strikethrough, "strikethrough")
        self._warn_if_present(text_style.smallCaps, "smallCaps")
        self._warn_if_present(text_style.letterSpaced, "letterSpaced")
        return document

    def handle_coords_type(self, coords: CoordsType) -> Sequence[Tuple[int, int]]:
        """
        the coords entries have been previously xsd-validated using: ([0-9]+,[0-9]+ )+([0-9]+,[0-9]+)
        :param coords:
        :return:
        """
        return self.handle_points_type(coords.points)

    @execute_if_present
    def handle_baseline_type(self, default_return, baseline: BaselineType):
        return self.handle_points_type(baseline.points)

    def handle_points_type(self, points: PointsType) -> Sequence[Tuple[int, int]]:
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

    """
    Top Level Region handling
    """

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
