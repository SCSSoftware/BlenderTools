from re import compile
from ast import literal_eval

from io_scs_tools.utils.printout import lprint


def read_data(filepath, print_info=False):
    """Reads data from mat file and returns it's attributes as dictionary.

    :param filepath: material file path
    :type filepath: str
    :param print_info: switch for printing parsing info
    :type print_info: bool
    :return: tuple of dictionary of mapped material attributes and effect name
    :rtype: (dict, effect)
    """
    _EFFECT_G = "effect"
    _CONTENT_G = "content"
    _ATTR_NAME_G = "attr_name"
    _ATTR_VALUE_G = "attr_val"

    if print_info:
        print('** MAT Parser ...')
        print('   filepath: %r' % str(filepath))

    material_pattern = compile(r'material\W*:\W*\"(?P<%s>(.|\n)+)\"\W*\{\W*(?P<%s>(.|\n)+)\W*\}' % (_EFFECT_G, _CONTENT_G))
    """Regex pattern for matching whole material file."""
    attr_pattern = compile(r'(?P<%s>.+):(?P<%s>.+)' % (_ATTR_NAME_G, _ATTR_VALUE_G))
    """Regex pattern for matching one attribute."""

    attr_dict = {}

    with open(filepath) as f:
        f_data = f.read()
        f.close()

        # match whole file
        m = material_pattern.match(f_data)

        effect = m.group(_EFFECT_G)
        content = m.group(_CONTENT_G).replace(" ", "").replace("\t", "")

        if print_info:
            print("Effect:", effect)
            print("Content:", content)

        for i, attr_m in enumerate(attr_pattern.finditer(content)):

            attr_name = attr_m.group(_ATTR_NAME_G)
            attr_value = attr_m.group(_ATTR_VALUE_G).replace("{", "(").replace("}", ")")

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

    return attr_dict, effect
