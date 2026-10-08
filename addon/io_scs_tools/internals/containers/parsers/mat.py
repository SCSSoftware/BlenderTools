from re import compile
from ast import literal_eval

from io_scs_tools.utils.printout import lprint

def parse_attributes(content, attr_pattern, print_info=False):
    """Parse attributes from content and return them as dictionary.

    :param content: content of material file
    :type content: str
    :param attr_pattern: regex pattern for matching one attribute
    :type attr_pattern: re.Pattern
    :param print_info: switch for printing parsing info
    :type print_info: bool
    :return: dictionary of mapped material attributes
    :rtype: dict
    """
    attr_dict = {}
    for i, attr_m in enumerate(attr_pattern.finditer(content)):

        attr_name = attr_m.group("attr_name")
        attr_value = attr_m.group("attr_val").replace("{", "(").replace("}", ")")

        try:
            parsed_attr_value = literal_eval(attr_value)
        except ValueError:
            parsed_attr_value = None
            lprint("W Ignoring unrecognized/malformed MAT file attribute:\n\t   Name: %r; Value: %r;", (attr_name, attr_value))

        if print_info:
            print("\tName:", attr_name, " -> Value(", type(parsed_attr_value).__name__, "):", parsed_attr_value)

        # fill successfully parsed values into dictionary
        if parsed_attr_value is not None:
            attr_dict[attr_name] = parsed_attr_value

    return attr_dict

def read_data(filepath, print_info=False):
    """Reads data from mat file and returns it's attributes as dictionary.

    :param filepath: material file path
    :type filepath: str
    :param print_info: switch for printing parsing info
    :type print_info: bool
    :return: tuple of dictionary of mapped material attributes, effect name and mat format
    :rtype: (dict, effect, mat_format)
    """
    _FORMAT_G = "mat_format"
    _EFFECT_G = "effect"
    _CONTENT_G = "content"
    _ATTR_NAME_G = "attr_name"
    _ATTR_VALUE_G = "attr_val"
    _ATTR_VALUE_NEST_G = "attr_val_nest"

    if print_info:
        print('** MAT Parser ...')
        print('   filepath: %r' % str(filepath))

    # skip any whitespace at the beginning of file (game does not care about it), then match file format (not hardcoded to later check if it's supported), ), effect name and content
    material_pattern = compile(r'(^\s*)(?P<%s>[\S]+)\W*:\W*\"(?P<%s>[\w.]+)\"\W*\{\W*(?P<%s>(.|\n)+)\W*\}' % (_FORMAT_G, _EFFECT_G, _CONTENT_G))
    """Regex pattern for matching whole material file."""
    attr_pattern = compile(r'(?P<%s>.+):(?P<%s>.+)' % (_ATTR_NAME_G, _ATTR_VALUE_G))
    """Regex pattern for matching one attribute."""
    nested_pattern = compile(r'(?P<%s>\w+):"(?P<%s>[^"]+)"\{(?P<%s>[^}]+)\}' % (_ATTR_NAME_G ,_ATTR_VALUE_G, _ATTR_VALUE_NEST_G))
    """Regex pattern for matching nested data in content."""

    with open(filepath, encoding="utf8") as f:
        f_data = f.read()
        f.close()

        # match whole file
        m = material_pattern.match(f_data)

        mat_format = m.group(_FORMAT_G)
        effect = m.group(_EFFECT_G).replace(".rfx", "")
        content = m.group(_CONTENT_G).replace(" ", "").replace("\t", "")

        if print_info:
            print("Format:", mat_format)
            print("Effect:", effect)
            print("Content:\n", content, sep='')

        if mat_format == "material":
            attr_dict = parse_attributes(content, attr_pattern, print_info)

        elif mat_format == "effect":

            nested_list = {}

            # extract nested data from content 
            for i, attr_m in enumerate(nested_pattern.finditer(content)):
                attr_name = attr_m.group(_ATTR_NAME_G)
                attr_value = attr_m.group(_ATTR_VALUE_G)
                attr_value_nest = attr_m.group(_ATTR_VALUE_NEST_G)

                if attr_name not in nested_list:
                    nested_list[attr_name] = {}

                # parse nested_attr_value into a dictionary
                nested_attr_value_dict = {}
                for i, n_attr_m in enumerate(attr_pattern.finditer(attr_value_nest)):

                    nested_attr_name = n_attr_m.group(_ATTR_NAME_G)
                    nested_attr_value = n_attr_m.group(_ATTR_VALUE_G).replace("{", "(").replace("}", ")").replace('"', '')
                    
                    if print_info:
                        print("\tName:", nested_attr_name, " -> Value(", type(nested_attr_value).__name__, "):", nested_attr_value)
                    
                    nested_attr_value_dict[nested_attr_name] = nested_attr_value

                nested_list[attr_name][attr_value] = nested_attr_value_dict

            # remove nested data from content to not broke parsing of normal attributes
            content = nested_pattern.sub('', content)

            if print_info:
                print("Nested dict:\n", nested_list, sep='')

            # parse attributes
            attr_dict = parse_attributes(content, attr_pattern, print_info)

            if print_info:
                print("Attr dict:\n", attr_dict, sep='')

            # combine nested_list with attr_dict
            for name, value in nested_list.items():
                attr_dict[name] = value

            if print_info:
                print("Combined dict:\n", attr_dict, sep='')

        else:
            lprint("E Unknown mat format: `%s`", (mat_format, ))

    return attr_dict, effect, mat_format
