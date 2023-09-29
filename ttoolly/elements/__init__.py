from ttoolly.elements.common import Field
from ttoolly.utils import get_all_subclasses

elements_map = {el.type_of: el for el in get_all_subclasses(Field)}
