# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re

import pyparsing as pp

from . import imcgenutils
from . import imccoreutils
from .imcfiltertype import OrFilter, AndFilter, NotFilter
from .imcbasetype import FilterFilter

types = {"eq": "EqFilter",
         "ne": "NeFilter",
         "ge": "GeFilter",
         "gt": "GtFilter",
         "le": "LeFilter",
         "lt": "LtFilter",
         "re": "WcardFilter"
         }


class ParseFilter(object):
    """
    Supporting class to parse filter expression.
    """

    class_id = None
    is_meta_classid = None

    @staticmethod
    def parse_filter_obj(sstr, loc, toks):
        """
        Supporting class to parse filter expression.
        """

        # print toks[0] #logger

        prop_ = toks[0]["prop"]
        value_ = toks[0]["value"]

        type_ = "re"
        if "type_exp" in toks[0]:
            type_ = toks[0]["type_exp"]["types"]

        flag_ = "C"
        if "flag_exp" in toks[0]:
            flag_ = toks[0]["flag_exp"]["flags"]

        # print prop_, value_, type_, flag_ #logger

        if flag_ == "I":
            value_ = re.sub(r"[a-zA-Z]", lambda x: "[" + x.group().upper() +
                                                   x.group().lower() +
                                                   "]", value_)

        if ParseFilter.is_meta_classid:
            class_obj = imccoreutils.load_class(ParseFilter.class_id)
            prop_mo_meta = class_obj.prop_meta[prop_]
            if prop_mo_meta:
                prop_ = prop_mo_meta.xml_attribute

        sub_filter = create_basic_filter(types[type_],
                                         class_=imcgenutils.word_l(
                                             ParseFilter.class_id),
                                         property=prop_,
                                         value=value_)

        return sub_filter

    @staticmethod
    def and_operator(str, loc, toks):
        """
        method to support logical 'and' operator expression
        """

        # print  str, loc, toks
        # print toks[0][0::2]
        and_filter = AndFilter()
        for op_filter in toks[0][0::2]:
            and_filter.child_add(op_filter)
        return and_filter

    @staticmethod
    def or_operator(str, loc, toks):
        """
        method to support logical 'or' operator expression
        """

        # print  str, loc, toks
        # print toks[0][0::2]
        or_filter = OrFilter()
        for op_filter in toks[0][0::2]:
            or_filter.child_add(op_filter)
        return or_filter

    @staticmethod
    def not_operator(str_, loc, toks):
        """
        method to support logical 'and' operator expression
        """

        not_filter = NotFilter()

        for op_filter in toks[0][1:]:
            not_filter.child_add(op_filter)
        return not_filter


prop = pp.WordStart(pp.alphas) + pp.Word(pp.alphanums +
                                         "_").setResultsName("prop")
value = (pp.QuotedString("'") | pp.QuotedString('"') | pp.Word(
    pp.printables, excludeChars=",")).setResultsName("value")
types_ = pp.oneOf("re eq ne gt ge lt le").setResultsName("types")
flags = pp.oneOf("C I").setResultsName("flags")
comma = pp.Literal(',')
quote = (pp.Literal("'") | pp.Literal('"')).setResultsName("quote")

type_exp = pp.Group(pp.Literal("type") + pp.Literal(
    "=") + quote + types_ + quote).setResultsName("type_exp")
flag_exp = pp.Group(pp.Literal("flag") + pp.Literal(
    "=") + quote + flags + quote).setResultsName("flag_exp")

semi_expression = pp.Forward()
semi_expression << pp.Group(pp.Literal("(") +
                            prop + comma + value +
                            pp.Optional(comma + type_exp) +
                            pp.Optional(comma + flag_exp) +
                            pp.Literal(")")
                            ).setParseAction(
    ParseFilter.parse_filter_obj).setResultsName("semi_expression")

expr = pp.Forward()
expr << pp.operatorPrecedence(semi_expression, [
    ("not", 1, pp.opAssoc.RIGHT, ParseFilter.not_operator),
    ("and", 2, pp.opAssoc.LEFT, ParseFilter.and_operator),
    ("or", 2, pp.opAssoc.LEFT, ParseFilter.or_operator)
])


def generate_infilter(class_id, filter_str, is_meta_class_id):
    """
    Create FilterFilter object

    Args:
        class_id (str): class_id
        filter_str (str): filter expression
        is_meta_class_id (bool)

    Returns:
        True on successful connect

    Example:
        generate_infilter("LsServer", '("usr_lbl, "mysp", type="eq",
        flag="I)', True)
    """

    ParseFilter.class_id = class_id
    ParseFilter.is_meta_classid = is_meta_class_id
    result = expr.parseString(filter_str)
    in_filter = FilterFilter()
    in_filter.child_add(result[0])
    return in_filter


def handle_filter_max_component_limit(handle, l_filter):
    """
    Method checks the filter count and if the filter count exceeds
    the max_components(number of filters), then the given filter
    objects get distributed among small groups and then again binded
    together in complex filters(like and , or) so that the
    count of filters can be reduced.
    """

    from .imccore import AbstractFilter
    from .imcfiltertype import AndFilter, OrFilter

    max_components = 10
    if l_filter is None or l_filter.child_count() <= max_components:
        return l_filter

    if not isinstance(l_filter, AndFilter) and not isinstance(l_filter,
                                                              OrFilter):
        return l_filter

    result_filter = None
    if isinstance(l_filter, AndFilter):
        parent_filter = AndFilter()
        child_filter = AndFilter()
        parent_filter.child_add(child_filter)
        for childf in l_filter.child:
            if isinstance(childf, AbstractFilter):
                if child_filter.child_count() == max_components:
                    child_filter = AndFilter()
                    parent_filter.child_add(child_filter)
                child_filter.child_add(childf)
        result_filter = parent_filter
    else:
        parent_filter = OrFilter()
        child_filter = OrFilter()
        parent_filter.child_add(child_filter)
        for childf in l_filter.child:
            if isinstance(childf, AbstractFilter):
                if child_filter.child_count() == max_components:
                    child_filter = OrFilter()
                    parent_filter.child_add(child_filter)
                child_filter.child_add(childf)
        result_filter = parent_filter
    return handle_filter_max_component_limit(handle, result_filter)


def create_basic_filter(filter_name, **kwargs):
    """
    Loads filter class
    """

    from . import imcmeta
    fq_module_name = imcmeta.OTHER_TYPE_CLASS_ID[filter_name]
    module_import = __import__(fq_module_name, globals(), locals(),
                               [filter_name], level=1)
    filter_obj = getattr(module_import, filter_name)()
    filter_obj.create(**kwargs)
    return filter_obj
