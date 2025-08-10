import yaml
import sys
import re
from datetime import datetime, date
from pathlib import Path
from typing import Any

class YAMLToSExpConverter:
    def __init__(self, key_prefix: str = "yaml"):
        self.key_prefix = key_prefix
        
        self.escape_pattern = re.compile(r'(["\\]|[\x00-\x1f\x7f])')
        
        # TODO: Symbol patterns are currently not robust enough.
        self.symbol_patterns = [
            r'^[A-Z]\d{4,6}$',
            r'^[A-Z]{2,3}$',
            r'^[a-zA-Z_]\w*$',
        ]
        self.symbol_regex = re.compile('|'.join(f'({pattern})' for pattern in self.symbol_patterns))

    def escape_char(self, match):
        char = match.group(0)
        if char == '"':
            return '\\"'
        elif char == '\\':
            return '\\\\'
        elif char == '\n':
            return '\\n'
        elif char == '\r':
            return '\\r'
        elif char == '\t':
            return '\\t'
        else:
            return f'\\x{ord(char):02x}'

    def escape_string(self, s: str) -> str:
        return self.escape_pattern.sub(self.escape_char, s)

    def is_symbol(self, s: str) -> bool:
        if not s or len(s) > 20:
            return False
        
        return bool(self.symbol_regex.match(s))

    def format_date(self, date_obj: date) -> str:
        return f'(make-date {date_obj.year} {date_obj.month:02d} {date_obj.day:02d})'

    def is_list_of_records(self, data: list) -> bool:
        if not data:
            return False
        return all(isinstance(item, dict) for item in data)

    def to_sexp(self, data: Any) -> str:
        if isinstance(data, dict):
            if not data:
                return '()'
            
            parts = []
            for key, value in data.items():
                prefixed_key = f'{self.key_prefix}:{key}'
                converted_value = self.to_sexp(value)
                parts.append(f'({prefixed_key} {converted_value})')
            
            return ' '.join(parts)
        
        elif isinstance(data, list):
            if not data:
                return '()'

            if self.is_list_of_records(data):
                item_parts = []
                for record in data:
                    record_sexp = self.to_sexp(record)
                    item_parts.append(f'({self.key_prefix}:item {record_sexp})')
                return ' '.join(item_parts)
            else:
                elements = [self.to_sexp(item) for item in data]
                return f'({" ".join(elements)})'
        
        elif isinstance(data, str):
            if self.is_symbol(data):
                return f"'{data}"
            else:
                return f'"{self.escape_string(data)}"'
        
        elif isinstance(data, bool):
            return '#t' if data else '#f'
        
        elif isinstance(data, (int, float)):
            if isinstance(data, float):
                if data != data:
                    return '+nan.0'
                elif data == float('inf'):
                    return '+inf.0'
                elif data == float('-inf'):
                    return '-inf.0'
            return str(data)
        
        elif isinstance(data, (date, datetime)):
            if isinstance(data, datetime):
                data = data.date()
            return self.format_date(data)
        
        elif data is None:
            return 'nil'
        
        else:
            if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                return self.to_sexp(list(data))
            else:
                return f'"{self.escape_string(str(data))}"'

def validate_yaml_structure(data: Any) -> bool:
    if data is None:
        raise ValueError("YAML file is empty or contains only null values")
    return True

def main():
    input_file = 'input.yaml'
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    
    try:
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
            print(f"Usage: {sys.argv[0]} [input_file]", file=sys.stderr)
            return 1
        
        with open(input_file, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        validate_yaml_structure(data)
        
        converter = YAMLToSExpConverter()
        s_expression = converter.to_sexp(data)
        
        print(f'({s_expression})')
        
        return 0
    
    except FileNotFoundError:
        print(f"Error: Could not find file '{input_file}'", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())