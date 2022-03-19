import functools
import re
from datetime import date
from typing import Sequence, Tuple, Optional

from loguru import logger
# noinspection PyProtectedMember
from pyxb.binding.content import _PluralBinding
from pyxb.binding.datatypes import boolean

from converter.elements import PageConversionStrategy, ConverterDocument
from converter.strategies.generated.page_xml.py_xb_2017 import PcGtsType, UserDefinedType, TextRegionType, CoordsType, \
    PointsType, TextLineType, BaselineType, TextEquivType, TextStyleType, PageType, LineDrawingRegionType, \
    GraphicRegionType, TableRegionType, ChartRegionType, SeparatorRegionType, MathsRegionType, \
    ChemRegionType, MusicRegionType, AdvertRegionType, NoiseRegionType, UnknownRegionType, RegionType, \
    ImageRegionType, UserAttributeType, WordType
from docrecjson.elements import Document, PolygonRegion, GroupRef, DocumentElement


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


def recursive(func):
    """
    the add_xyz methods annotated with this will call their children or themselves recursively until there are no more
    children elements.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        document: Document = func(*args, **kwargs)
        parent: DocumentElement = document.content[-1]
        # add a group to the parent object if the group is not already present
        if parent.group is None:
            document.add_group(parent)

        document.use_group_of(parent)

        plural_binding_parent = args[2]
        for element in plural_binding_parent:
            document = PageXML2017StrategyPyXB.add_region_content(PageXML2017StrategyPyXB(), document, element)
        document.use_new_group()

        return document

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

    # The next methods are not static-inspected inspected because moving this out of the strategy may be very confusing
    # Furthermore this may be necessary to implement for each strategy and be moved therefore into ConversionStrategy
    #   or a page subclass.
    # noinspection PyMethodMayBeStatic
    def _execute_if_present(self, condition, func, *args):
        if self._is_present(condition):
            func(*args)

    # noinspection PyMethodMayBeStatic
    def _is_present(self, condition) -> bool:
        if type(condition) == dict:
            if len(condition) > 0:
                return True
            else:
                return False
        # At this point, it's assumed that the condition object is one of the PyXb objects.
        if condition:
            return True
        return False

    def _create_dict_if_present(self, **kwargs) -> dict:
        dct: dict = {}
        for name, value in kwargs.items():
            if self._is_present(value):
                dct[name] = value
        return dct

    # noinspection PyMethodMayBeStatic
    def _warn_if_present(self, obj, property_name: str):
        if type(obj) == boolean or obj:
            logger.warning(property_name + "= [" + str(obj) + "] is not further processed.")

    # noinspection PyMethodMayBeStatic
    def _create_user_defined_metadata(self, user_defined_metadata: UserDefinedType) -> dict:
        if user_defined_metadata is None:
            return {}
        dct = {}
        for attribute in user_defined_metadata.UserAttribute:
            dct[str(attribute.name)] = str(attribute.value_)
        return dct

    # noinspection PyMethodMayBeStatic
    def _handle_points_type(self, points: PointsType) -> Sequence[Tuple[int, int]]:
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

    def add_region_content(self, document, parent) -> Document:
        document = self.handle_text_regions(document, parent.TextRegion)
        document = self.handle_image_region(document, parent.ImageRegion)
        document = self.handle_line_drawing_region(document, parent.LineDrawingRegion)
        document = self.handle_graphic_region(document, parent.GraphicRegion)
        document = self.handle_table_region(document, parent.TableRegion)
        document = self.handle_chart_region(document, parent.ChartRegion)
        document = self.handle_separator_region(document, parent.SeparatorRegion)
        document = self.handle_maths_region(document, parent.MathsRegion)
        document = self.handle_chem_region(document, parent.ChemRegion)
        document = self.handle_music_region(document, parent.MusicRegion)
        document = self.handle_advert_region(document, parent.AdvertRegion)
        document = self.handle_noise_region(document, parent.NoiseRegion)
        document = self.handle_unknown_region(document, parent.UnknownRegion)
        return document

    def initialize(self, original: ConverterDocument) -> ConverterDocument:
        pyxb_object: PcGtsType = original.tmp_type
        document: Document = Document.empty(pyxb_object.Page.imageFilename,
                                            (pyxb_object.Page.imageHeight, pyxb_object.Page.imageWidth))
        document.add_creator(pyxb_object.Metadata.Creator, "2017-07-15")
        document.add_creator("shared-file-converter", str(date.today()))
        original.shared_file_format_document = document

        # todo add Page root types e.g. pyxb_object.Page.<xyz> (maybe this is more appropriate in add_metadate)
        # missing: custom, type, primaryLanguage, secondaryLanguage, primaryScript, secondaryScript, readingOrder
        #          textLineOrder

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
        page: PageType = pyxb_object.Page
        document: Document = original.shared_file_format_document

        document = self.add_region_content(document, page)

        original.shared_file_format_document = document
        return original

    """
    page xml element handling = type handling
    """

    def handle_alternative_image_type(self, document: Document, alternative_image) -> Document:
        pass

    def handle_border_type(self, document: Document, border) -> Document:
        pass

    def handle_print_space_type(self, document: Document, print_space) -> Document:
        pass

    def handle_reading_order_type(self, document: Document, reading_order) -> Document:
        pass

    def handle_layers_type(self, document: Document, layers) -> Document:
        pass

    @execute_if_present
    def handle_user_defined_type(self, document: Document, user_defined: UserDefinedType,
                                 group_ref: Optional[GroupRef] = None) -> Document:
        user_attribute: UserAttributeType
        for user_attribute in user_defined.UserAttribute:
            metadata: dict = self._create_dict_if_present(name=user_attribute.name,
                                                          description=user_attribute.description,
                                                          type=user_attribute.type,
                                                          value=user_attribute.value_)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, group_ref)

        return document

    @execute_if_present
    def handle_word_type(self, document: Document, words: _PluralBinding) -> Document:
        word: WordType
        for _ in words:
            logger.warning("This conversion is currently not implemented.")
            # todo: call: handle_glyph, handle_text_equiv, handle_text_style, handle_user_defined
        return document

    def handle_glyph_type(self):
        # todo: call: handle_coords, handle_graphemes, handle_text_equiv, handle_text_style, handle_user_defined
        pass

    """
    Text Region Handling
    """

    @execute_if_present
    @recursive
    def handle_text_regions(self, document: Document, text_regions) -> Document:
        text_region: TextRegionType
        for text_region in text_regions:
            region: GroupRef
            if self._has_complex_subtype(text_region):
                # this text regions has subtypes
                # -> it only serves the purpose of beeing a group id for it's subtypes
                document = self._handle_complex_text_region_type(document, text_region)
            else:
                # this text region stands for itself without any further information
                # -> it's added to document engine as text content
                document = self._handle_simple_text_region_type(document, text_region)

            metadata: dict = self._create_dict_if_present(align=text_region.align,
                                                          comments=text_region.comments,
                                                          continuation=text_region.continuation,
                                                          custom=text_region.custom,
                                                          indented=text_region.indented,
                                                          leading=text_region.leading,
                                                          orientation=text_region.orientation,
                                                          primaryLanguage=text_region.primaryLanguage,
                                                          primaryScript=text_region.primaryScript,
                                                          production=text_region.production,
                                                          readingDirection=text_region.readingDirection,
                                                          readingOrientation=text_region.readingOrientation,
                                                          secondaryLanguage=text_region.secondaryLanguage,
                                                          textLineOrder=text_region.textLineOrder)
            if document.content[-1].group is None:
                document.add_group(document.content[-1])
            self._execute_if_present(metadata, document.add_content_metadata, metadata, document.content[-1].group)

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
        document = self.handle_text_style(document, text_region.TextStyle, region_identification)

        return document

    # noinspection PyMethodMayBeStatic
    def _len_plural_binding(self, _plural_binding_object: _PluralBinding) -> int:
        return len(_plural_binding_object)

    def _has_complex_subtype(self, text_region: TextRegionType) -> bool:
        length_of_all_types: int = self._len_plural_binding(
            text_region.TextEquiv) + self._len_plural_binding(
            text_region.TextLine)
        return True if length_of_all_types != 0 else False

    @execute_if_present
    def handle_text_lines(self, document: Document, text_lines: _PluralBinding,
                          group_ref: Optional[GroupRef] = None) -> Document:
        text_line: TextLineType
        for text_line in text_lines:
            points = self.handle_coords_type(text_line.Coords)
            baseline_points = self.handle_baseline_type([], text_line.Baseline)

            docobject: DocumentElement = document.content[-1]
            if len(points) != 0:
                docobject = document.add_line_polygon(points, group_ref)
            if len(baseline_points) != 0:
                docobject = document.add_baseline(points, group_ref)

            metadata: dict = self._create_dict_if_present(primaryLanguage=text_line.primaryLanguage,
                                                          primaryScript=text_line.primaryScript,
                                                          secondaryScript=text_line.secondaryScript,
                                                          readingDirection=text_line.readingDirection,
                                                          production=text_line.production,
                                                          custom=text_line.custom,
                                                          comments=text_line.comments)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, docobject)

            self.handle_word_type(document, text_line.Word)
            self.handle_text_equiv(document, text_line.TextEquiv, docobject)
            self.handle_text_style(document, text_line.TextStyle, document)
            self.handle_user_defined_type(document, text_line.UserDefined, docobject)

        return document

    @execute_if_present
    def handle_text_equiv(self, document: Document, text_equivs: _PluralBinding,
                          group_ref: Optional[GroupRef] = None) -> Document:
        text_equiv: TextEquivType
        for text_equiv in text_equivs:
            unicode: str = text_equiv.Unicode
            region = document.add_text(unicode, group_ref)

            metadata: dict = self._create_dict_if_present(index=text_equiv.index,
                                                          confidence=text_equiv.conf,
                                                          dataType=text_equiv.dataType,
                                                          dataTypeDetails=text_equiv.dataTypeDetails,
                                                          comments=text_equiv.comments)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, region)

        return document

    @execute_if_present
    def handle_text_style(self, document: Document, text_style: TextStyleType,
                          group_ref: Optional[GroupRef] = None) -> Document:
        metadata: dict = self._create_dict_if_present(fontFamily=text_style.fontFamily,
                                                      serif=text_style.serif,
                                                      monospace=text_style.monospace,
                                                      fontSize=text_style.fontSize,
                                                      xHeight=text_style.xHeight,
                                                      kerning=text_style.kerning,
                                                      textColour=text_style.textColour,
                                                      textColourRgb=text_style.textColourRgb,
                                                      bgColour=text_style.bgColour,
                                                      bgColourRgb=text_style.bgColourRgb,
                                                      reverseVideo=text_style.reverseVideo,
                                                      bold=text_style.bold,
                                                      italic=text_style.italic,
                                                      underlined=text_style.underlined,
                                                      subscript=text_style.subscript,
                                                      superscript=text_style.superscript,
                                                      strikethrough=text_style.strikethrough,
                                                      smallCaps=text_style.smallCaps,
                                                      letterSpaced=text_style.letterSpaced)
        self._execute_if_present(metadata, document.add_content_metadata, metadata, group_ref)
        return document

    def handle_coords_type(self, coords: CoordsType) -> Sequence[Tuple[int, int]]:
        """
        the coords entries have been previously xsd-validated using: ([0-9]+,[0-9]+ )+([0-9]+,[0-9]+)
        :param coords:
        :return:
        """
        return self._handle_points_type(coords.points)

    @execute_if_present
    def handle_baseline_type(self, default_return, baseline: BaselineType) -> Sequence[Tuple[int, int]]:
        return self._handle_points_type(baseline.points)

    """
    Top Level Region handling
    """

    def _warn_region_parent_elements(self, region_child_element: RegionType):
        """
        This method is used to warn if there are complex subregions in another region (except text_region).
        This Conversion is currently not supported.
        :param region_child_element: the Region to check for certain Region elements
        """
        self._warn_if_present(region_child_element.custom, "custom")
        self._warn_if_present(region_child_element.comments, "comments")
        self._warn_if_present(region_child_element.continuation, "continuation")

        self._warn_if_present(region_child_element.UserDefined, "UserDefined")
        self._warn_if_present(region_child_element.Roles, "Roles")
        self._warn_if_present(region_child_element.TextRegion, "TextRegion")
        self._warn_if_present(region_child_element.ImageRegion, "ImageRegion")
        self._warn_if_present(region_child_element.LineDrawingRegion, "LineDrawingRegion")
        self._warn_if_present(region_child_element.GraphicRegion, "GraphicRegion")
        self._warn_if_present(region_child_element.TableRegion, "TableRegion")
        self._warn_if_present(region_child_element.ChartRegion, "ChartRegion")
        self._warn_if_present(region_child_element.SeparatorRegion, "SeparatorRegion")
        self._warn_if_present(region_child_element.MathsRegion, "MathsRegion")
        self._warn_if_present(region_child_element.ChemRegion, "ChemRegion")
        self._warn_if_present(region_child_element.MusicRegion, "MusicRegion")
        self._warn_if_present(region_child_element.AdvertRegion, "AdvertRegion")
        self._warn_if_present(region_child_element.NoiseRegion, "NoiseRegion")
        self._warn_if_present(region_child_element.UnknownRegion, "UnknownRegion")

    @execute_if_present
    @recursive
    def handle_image_region(self, document: Document, image_regions: _PluralBinding) -> Document:
        image_region: ImageRegionType
        for image_region in image_regions:
            coordinates = self._handle_points_type(image_region.Coords.points)
            region = document.add_region(area=coordinates, region_type="image")

            metadata: dict = self._create_dict_if_present(orientation=image_region.orientation,
                                                          colourDepth=image_region.colourDepth,
                                                          bgColour=image_region.bgColour,
                                                          embText=image_region.embText)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, region)

            # todo what elements need to be added to the recursive functionality to remove this behaviour
            self._warn_region_parent_elements(image_region)

        return document

    @execute_if_present
    @recursive
    def handle_line_drawing_region(self, document: Document, line_drawing_regions: _PluralBinding) -> Document:
        line_drawing_region: LineDrawingRegionType
        for line_drawing_region in line_drawing_regions:
            coordinates = self._handle_points_type(line_drawing_region.Coords.points)
            region = document.add_region(area=coordinates, region_type="line_drawing")

            metadata: dict = self._create_dict_if_present(orientation=line_drawing_region.orientation,
                                                          penColour=line_drawing_region.penColour,
                                                          bgColour=line_drawing_region.bgColour,
                                                          embText=line_drawing_region.embText)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, region)

            self._warn_region_parent_elements(line_drawing_region)

        return document

    @execute_if_present
    @recursive
    def handle_graphic_region(self, document: Document, graphic_regions: _PluralBinding) -> Document:
        graphic_region: GraphicRegionType
        for graphic_region in graphic_regions:
            coordinates = self._handle_points_type(graphic_region.Coords.points)
            region = document.add_region(area=coordinates, region_type="graphic")

            metadata: dict = self._create_dict_if_present(orientation=graphic_region.orientation,
                                                          type=graphic_region.type,
                                                          numColours=graphic_region.numColours,
                                                          embText=graphic_region.embText)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, region)

            self._warn_region_parent_elements(graphic_region)

        return document

    @execute_if_present
    @recursive
    def handle_table_region(self, document: Document, table_regions: _PluralBinding) -> Document:
        table_region: TableRegionType
        for table_region in table_regions:
            coordinates = self._handle_points_type(table_region.Coords.points)
            region = document.add_region(area=coordinates, region_type="table")

            metadata: dict = self._create_dict_if_present(orientation=table_region.orientation,
                                                          rows=table_region.rows,
                                                          columns=table_region.columns,
                                                          lineColour=table_region.lineColour,
                                                          bgColour=table_region.bgColour,
                                                          lineSeparators=table_region.lineSeparators,
                                                          embText=table_region.embText)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, region)

            self._warn_region_parent_elements(table_region)
        return document

    @execute_if_present
    @recursive
    def handle_chart_region(self, document: Document, chart_regions: _PluralBinding) -> Document:
        chart_region: ChartRegionType
        for chart_region in chart_regions:
            coordinates = self._handle_points_type(chart_region.Coords.points)
            region = document.add_region(area=coordinates, region_type="chart")

            metadata: dict = self._create_dict_if_present(orientation=chart_region.orientation,
                                                          type=chart_region.type,
                                                          numColours=chart_region.numColours,
                                                          bgColour=chart_region.bgColour,
                                                          embText=chart_region.embText)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, region)

            self._warn_region_parent_elements(chart_region)

        return document

    @execute_if_present
    @recursive
    def handle_separator_region(self, document: Document, separator_regions: _PluralBinding) -> Document:
        separator_region: SeparatorRegionType
        for separator_region in separator_regions:
            coordinates = self._handle_points_type(separator_region.Coords.points)
            region = document.add_region(area=coordinates, region_type="separator")

            metadata: dict = self._create_dict_if_present(orientation=separator_region.orientation,
                                                          colour=separator_region.colour)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, region)

            self._warn_region_parent_elements(separator_region)
        return document

    @execute_if_present
    @recursive
    def handle_maths_region(self, document: Document, maths_regions: _PluralBinding) -> Document:
        maths_region: MathsRegionType
        for maths_region in maths_regions:
            coordinates = self._handle_points_type(maths_region.Coords.points)
            region = document.add_region(area=coordinates, region_type="maths")

            metadata: dict = self._create_dict_if_present(orientation=maths_region.orientation,
                                                          bgColour=maths_region.bgColour)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, region)

            self._warn_region_parent_elements(maths_region)
        return document

    @execute_if_present
    @recursive
    def handle_chem_region(self, document: Document, chem_regions: _PluralBinding) -> Document:
        chem_region: ChemRegionType
        for chem_region in chem_regions:
            coordinates = self._handle_points_type(chem_region.Coords.points)
            region = document.add_region(area=coordinates, region_type="chem")

            metadata: dict = self._create_dict_if_present(orientation=chem_region.orientation,
                                                          bgColour=chem_region.bgColour)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, region)

            self._warn_region_parent_elements(chem_region)
        return document

    @execute_if_present
    @recursive
    def handle_music_region(self, document: Document, music_regions: _PluralBinding) -> Document:
        music_region: MusicRegionType
        for music_region in music_regions:
            coordinates = self._handle_points_type(music_region.Coords.points)
            region = document.add_region(area=coordinates, region_type="music")

            metadata: dict = self._create_dict_if_present(orientation=music_region.orientation,
                                                          bgColour=music_region.bgColour)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, region)

            self._warn_region_parent_elements(music_region)
        return document

    @execute_if_present
    @recursive
    def handle_advert_region(self, document: Document, advert_regions: _PluralBinding) -> Document:
        advert_region: AdvertRegionType
        for advert_region in advert_regions:
            coordinates = self._handle_points_type(advert_region.Coords.points)
            region = document.add_region(area=coordinates, region_type="advert")

            metadata: dict = self._create_dict_if_present(orientation=advert_region.orientation,
                                                          bgColour=advert_region.bgColour)
            self._execute_if_present(metadata, document.add_content_metadata, metadata, region)

            self._warn_region_parent_elements(advert_region)
        return document

    @execute_if_present
    @recursive
    def handle_noise_region(self, document: Document, noise_regions: _PluralBinding) -> Document:
        noise_region: NoiseRegionType
        for noise_region in noise_regions:
            coordinates = self._handle_points_type(noise_region.Coords.points)
            document.add_region(area=coordinates, region_type="noise")

            self._warn_region_parent_elements(noise_region)
        return document

    @execute_if_present
    @recursive
    def handle_unknown_region(self, document: Document, unknown_regions: _PluralBinding) -> Document:
        unknown_region: UnknownRegionType
        for unknown_region in unknown_regions:
            coordinates = self._handle_points_type(unknown_region.Coords.points)
            document.add_region(area=coordinates, region_type="unknown")

            self._warn_region_parent_elements(unknown_region)
        return document
