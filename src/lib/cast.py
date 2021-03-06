# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import datetime
import warnings
import pandas
from typing import Any, Dict, Callable, Optional


def safe_float_cast(value: Any) -> Optional[float]:
    if value is None:
        return None
    if pandas.isna(value):
        return None
    if isinstance(value, int):
        return float(value)
    if isinstance(value, float):
        return value
    if value == "":
        return None
    try:
        value = str(value)
        value = re.sub(r",", "", value)
        value = re.sub(r"−", "-", value)
        return float(value)
    except:
        return None


def safe_int_cast(value: Any, round_function: Callable[[float], int] = round) -> Optional[int]:
    value = safe_float_cast(value)
    if value is None:
        return None
    try:
        value = round_function(value)
        return value
    except:
        return None


def safe_str_cast(value: Any) -> Optional[str]:
    if pandas.isna(value):
        return None
    try:
        value = str(value)
        return value
    except:
        return None


def safe_datetime_parse(
    value: str, date_format: str = None, warn: bool = False
) -> Optional[datetime.datetime]:
    try:
        return (
            datetime.datetime.fromisoformat(str(value))
            if not date_format
            else datetime.datetime.strptime(str(value), date_format)
        )
    except ValueError as exc:
        if warn:
            warnings.warn("Could not parse date {} using format {}".format(value, date_format))
        return None


def column_converters(schema: Dict[str, Any]) -> Dict[str, Callable]:
    converters: Dict[str, Callable] = {}
    for column, dtype in schema.items():
        if dtype == "int" or dtype == pandas.Int64Dtype():
            converters[column] = safe_int_cast
        elif dtype == "float":
            converters[column] = safe_float_cast
        elif dtype == "str":
            converters[column] = safe_str_cast
        else:
            raise ValueError(f"Unsupported dtype {dtype} for column {column}")
    return converters


def age_group(age: int, bin_count: int = 10, age_cutoff: int = 90) -> str:
    """
    Categorical age group given a specific age, codified into a function to enforce consistency.
    """
    if pandas.isna(age) or age < 0:
        return None

    bin_size = age_cutoff // bin_count + 1
    if age >= age_cutoff:
        return f"{age_cutoff}-"

    bin_idx = age // bin_size
    lo = int(bin_idx * bin_size)
    hi = lo + bin_size - 1
    return f"{lo}-{hi}"


def numeric_code_as_string(code: Any, digits: int = 0) -> str:
    """
    Converts a code, which is typically a (potentially null) number, into its integer string
    representation. This is very convenient to parse things like FIPS codes.

    Arguments:
        code: The input to cast into a string.
        digits: The number of digits to force on the output, left-padding with zeroes. If this
            argument is <= 0 then the output is unpadded.
    Returns:
        str: The input cast as a string, or None if it could not be converted into an integer.
    """
    code = safe_int_cast(code)
    if code is None:
        return code
    else:
        fmt = f"%0{digits}d" if digits > 0 else "%d"
        return fmt % code
