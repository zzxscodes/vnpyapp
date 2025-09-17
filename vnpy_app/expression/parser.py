import re

# noinspection PyUnresolvedReferences
from .base import Feature
# noinspection PyUnresolvedReferences
from .ops import Operators
from .base import Expression


def parse_field(field):
    # Following patterns will be matched:
    # - $close -> Feature("close")
    # - $close5 -> Feature("close5")
    # - $open+$close -> Feature("open")+Feature("close")
    if not isinstance(field, str):
        field = str(field)
    return re.sub(r"\$(\w+)", r'Feature("\1")', re.sub(r"(\w+\s*)\(", r"Operators.\1(", field))


def parser_expression(field):
    expression = eval(parse_field(field))
    return expression


def calculate_expression(df, expression):
    if not isinstance(expression, Expression):
        return expression
    elif expression.is_root():
        return expression(df)
    else:
        if hasattr(expression, 'feature'):
            expression.feature = calculate_expression(df, expression.feature)
        if hasattr(expression, 'feature_left'):
            expression.feature_left = calculate_expression(df, expression.feature_left)
        if hasattr(expression, 'feature_right'):
            expression.feature_right = calculate_expression(df, expression.feature_right)
        return expression(df)


def calculate_field(df, field):
    expression = parser_expression(field)
    return calculate_expression(df, expression)
