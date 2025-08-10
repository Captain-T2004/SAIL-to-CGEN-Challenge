# YAML to S-Expression Conversion Schema

## Input Schema (YAML)

### Supported YAML Features

#### Data Types
- **Scalars**: strings, numbers, booleans, null, dates
- **Collections**: sequences (lists), mappings (dictionaries)
- **Multi-line strings**: literal (`|`) and folded (`>`) styles
- **References**: anchors (`&`) and aliases (`*`) - expanded in output

#### YAML Constructs
```yaml
# Supported YAML syntax examples
string_value: "Hello World"
number_value: 42
float_value: 3.14159
boolean_true: true
boolean_false: false
null_value: null
date_value: 2012-08-06

# Collections
list_example:
  - item1
  - item2
  - item3

mapping_example:
  key1: value1
  key2: value2

# Multi-line strings
literal_string: |
  Line 1
  Line 2
  Line 3

folded_string: >
  This is a long
  line that will be
  folded into one line

# References (expanded in output)
shared_config: &config
  timeout: 30
  retries: 3

service_a:
  <<: *config
  name: "Service A"
```

### Expected Input Structure

#### Wikipedia Example Schema
```yaml
---
# Document metadata
receipt: string                    # Invoice/document title
date: YYYY-MM-DD                  # ISO date or YAML date scalar

# Customer information
customer:
  first_name: string              # Customer's first name  
  family_name: string             # Customer's family name

# Items list (special handling)
items:
  - part_no: string               # Part number (symbol candidate)
    descrip: string               # Item description
    price: number                 # Unit price
    quantity: integer             # Quantity
    size: number                  # Optional: size specification
  # Additional items...

# Address structures  
bill-to:
  street: string                  # May be multi-line
  city: string                    # City name
  state: string                   # State code (symbol candidate)

ship-to:                          # Can be reference to bill-to
  street: string
  city: string  
  state: string

# Special instructions
specialDelivery: string           # Multi-line allowed

# Additional optional fields allowed
...
```

#### Data Type Constraints

##### Strings
- **Encoding**: Must be UTF-8
- **Length**: No practical limit (memory dependent)
- **Content**: All Unicode characters supported
- **Special handling**: Symbol detection for specific patterns

##### Numbers
- **Integers**: Standard YAML integers
- **Floats**: IEEE 754 double precision
- **Special values**: `inf`, `-inf`, `nan` supported
- **Scientific notation**: Supported (`1.23e-4`)

##### Dates
- **YAML dates**: Unquoted dates (`2012-08-06`)
- **String dates**: Quoted ISO-8601 format (`"2012-08-06"`)
- **DateTime**: Time component ignored, converted to date

##### Collections
- **Lists**: Homogeneous or heterogeneous elements
- **Mappings**: String keys required (non-string keys cause error)
- **Empty collections**: `[]` and `{}` supported
- **Nesting**: Unlimited depth (recursion limit dependent)

## Output Schema (S-Expression)

### Format Specification

#### Overall Structure
```lisp
(<top-level-forms>)
```

Where `<top-level-forms>` is a space-separated sequence of S-expressions.

#### Form Types

##### Key-Value Pairs
```lisp
(yaml:<key> <value>)
```

##### Nested Mappings
```lisp
(yaml:<key> (yaml:<nested-key> <nested-value>) ...)
```

##### Regular Lists
```lisp
(yaml:<key> (<item1> <item2> <item3> ...))
```

##### Record Lists (Special)
```lisp
(yaml:<key> (yaml:item (yaml:<field1> <value1>) (yaml:<field2> <value2>))
            (yaml:item (yaml:<field3> <value3>) (yaml:<field4> <value4>)))
```

### Data Type Conversion Rules

#### Scalars

| Input Type | Output Format | Example Input | Example Output |
|------------|---------------|---------------|----------------|
| String (regular) | `"escaped"` | `"Hello"` | `"Hello"` |
| String (symbol) | `'SYMBOL` | `"A4786"` | `'A4786` |
| Integer | `number` | `42` | `42` |
| Float | `number` | `3.14` | `3.14` |
| Boolean true | `#t` | `true` | `#t` |
| Boolean false | `#f` | `false` | `#f` |
| Null | `nil` | `null` | `nil` |
| Date | `(make-date y m d)` | `2012-08-06` | `(make-date 2012 08 06)` |
| Special float | Special form | `inf` | `+inf.0` |

#### Special Float Handling
```yaml
# Input YAML
positive_infinity: .inf
negative_infinity: -.inf
not_a_number: .nan
```

```lisp
; Output S-Expression
(yaml:positive_infinity +inf.0)
(yaml:negative_infinity -inf.0)  
(yaml:not_a_number +nan.0)
```

#### Collections

##### Empty Collections
```yaml
empty_list: []
empty_dict: {}
```

```lisp
(yaml:empty_list ())
(yaml:empty_dict ())
```

##### Regular Lists
```yaml
numbers: [1, 2, 3, 4]
mixed: ["a", 1, true, null]
```

```lisp
(yaml:numbers (1 2 3 4))
(yaml:mixed ("a" 1 #t nil))
```

##### Record Lists (Auto-detected)
```yaml
products:
  - id: P001
    name: Widget
    price: 9.99
  - id: P002
    name: Gadget  
    price: 14.99
```

```lisp
(yaml:products (yaml:item (yaml:id 'P001) (yaml:name "Widget") (yaml:price 9.99))
               (yaml:item (yaml:id 'P002) (yaml:name "Gadget") (yaml:price 14.99)))
```