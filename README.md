# SAIL to CGEN - YAML to S-Expression Converter

## Overview

This program converts structured YAML data to S-expression format following Scheme/Lisp dialect conventions with proper namespace prefixing. The converter implements a well-defined transformation schema with robust error handling and comprehensive data type support.

## Requirements

- Python 3.6 or higher
- PyYAML library: `pip install PyYAML`

## Installation

```bash
# Install required dependency
pip install PyYAML
# or
pip install -r requirments.txt

# Make the script executable (Unix/Linux/macOS)
chmod +x main.py
```

## Usage

```bash
# Using default input.yaml file
python main.py

# Specifying a custom input file
python main.py input.yaml

# Direct execution (Unix/Linux/macOS)
./main.py input.yaml
```

## Target Dialect and Conventions

### S-Expression Dialect
- **Target**: Scheme-like S-expressions with custom extensions
- **Booleans**: `#t` (true) and `#f` (false) - Scheme standard
- **Null/Nil**: `nil`
- **Numbers**: Direct representation with special float handling
- **Symbols**: Bare identifiers with single quote prefix for detected symbols
- **Namespacing**: All YAML keys prefixed with `yaml:`

### Data Type Mappings

| YAML Type | S-Expression Format | Example |
|-----------|-------------------|---------|
| Dictionary | `(yaml:key value)` pairs | `(yaml:name "John")` |
| List (general) | `(item1 item2 ...)` | `(1 2 3)` |
| List of records | `(yaml:item ...)` wrapped | `(yaml:item (yaml:name "John"))` |
| String | `"escaped string"` | `"Hello World"` |
| Symbol | `'SYMBOL` | `'A4786`, `'KS` |
| Boolean | `#t` or `#f` | `#t` |
| Numbers | Direct representation | `42`, `3.14` |
| Date/DateTime | `(make-date year month day)` | `(make-date 2012 08 06)` |
| Null | `nil` | `nil` |
| Empty containers | `()` | `()` |

## Symbol Detection

The converter automatically detects and formats certain strings as symbols based on these patterns:

### Pattern Rules
1. **Part Numbers**: `A1234` to `A123456` (letter + 4-6 digits)
2. **State/Country Codes**: `AA` to `AAA` (2-3 uppercase letters)  
3. **Identifiers**: Standard programming identifiers (`[a-zA-Z_]\w*`)

### Symbol Examples
- `"A4786"` → `'A4786` (part number)
- `"KS"` → `'KS` (state code)
- `"E1628"` → `'E1628` (part number)
- `"user_id"` → `'user_id` (identifier)
- `"Dorothy"` → `"Dorothy"` (regular string - mixed case)

### Symbol Constraints
- Maximum length: 20 characters
- Must match one of the defined patterns
- Empty strings are never symbols

## String Escaping

Comprehensive escaping for all control characters and special sequences:

| Character | Escaped As | Description |
|-----------|------------|-------------|
| `"` | `\"` | Double quote |
| `\` | `\\` | Backslash |
| Newline | `\n` | Line break |
| Tab | `\t` | Tab character |
| Carriage return | `\r` | CR character |
| Control chars | `\x##` | Hex escape for chars 0x00-0x1F, 0x7F |

## Special Features

### List of Records Detection
The converter automatically detects when a list contains only dictionary/mapping objects and wraps each record:

**Input YAML:**
```yaml
items:
  - name: Widget
    price: 10.99
  - name: Gadget
    price: 5.50
```

**Output S-Expression:**
```lisp
(yaml:items (yaml:item (yaml:name "Widget") (yaml:price 10.99))
            (yaml:item (yaml:name "Gadget") (yaml:price 5.50)))
```

### Date/DateTime Handling
- YAML date scalars automatically converted to `(make-date year month day)` format
- DateTime objects converted to date (time component ignored)
- Month and day are zero-padded to 2 digits

### Special Float Values
- `NaN` → `+nan.0`
- `Infinity` → `+inf.0`  
- `-Infinity` → `-inf.0`

### Empty Container Handling
- Empty dictionaries: `{} → ()`
- Empty lists: `[] → ()`

## Example Conversion

### Input (input.yaml):
```yaml
---
receipt: Oz-Ware Purchase Invoice
date: 2012-08-06
customer:
    first_name: Dorothy
    family_name: Gale
items:
    - part_no: A4786
      descrip: Water Bucket (Filled)
      price: 1.47
      quantity: 4
    - part_no: E1628
      descrip: High Heeled "Ruby" Slippers
      size: 8
      price: 133.7
      quantity: 1
bill-to:
    street: |
        123 Tornado Alley
        Suite 16
    city: East Centerville
    state: KS
active: true
special_price: null
```

### Output S-Expression:
```lisp
((yaml:receipt "Oz-Ware Purchase Invoice")
 (yaml:date (make-date 2012 08 06))
 (yaml:customer (yaml:first_name "Dorothy") (yaml:family_name "Gale"))
 (yaml:items (yaml:item (yaml:part_no 'A4786) (yaml:descrip "Water Bucket (Filled)") 
                        (yaml:price 1.47) (yaml:quantity 4))
             (yaml:item (yaml:part_no 'E1628) (yaml:descrip "High Heeled \"Ruby\" Slippers") 
                        (yaml:size 8) (yaml:price 133.7) (yaml:quantity 1)))
 (yaml:bill-to (yaml:street "123 Tornado Alley\\nSuite 16\\n")
               (yaml:city "East Centerville")
               (yaml:state 'KS))
 (yaml:active #t)
 (yaml:special_price nil))
```

## Customization

### Namespace Prefix
The default namespace prefix `yaml:` can be changed by modifying the `key_prefix` parameter:

```python
converter = YAMLToSExpConverter(key_prefix="custom")
# Results in: (custom:key value)
```

## Limitations

### Known Constraints
1. **File Size**: Limited by available system memory
2. **Depth**: Limited by Python's recursion limit (default ~1000 levels)
3. **Symbol Length**: Maximum 20 characters for symbol detection
4. **Encoding**: Input files must be UTF-8 encoded
5. **Key Format**: All YAML keys become `yaml:<key>` - no key transformation

### Non-Supported Features
- YAML tags and custom types
- Preservation of YAML comments  
- Binary data (will be string-converted)
- Complex number types
- Circular references (not applicable to YAML)

### Debugging Tips
1. Verify YAML syntax with `python -c "import yaml; yaml.safe_load(open('file.yaml'))"`
2. Check file encoding with `file -bi filename.yaml`
3. Test with minimal YAML examples to isolate issues
4. Use Python's traceback for detailed error information