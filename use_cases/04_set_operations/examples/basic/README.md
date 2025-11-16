# Basic Examples

Simple example files to test and learn the set operations utility.

## Files

### list_a.txt
Columnar format with 7 fruit items:
- apple, banana, cherry, date, elderberry, fig, grape

### list_b.txt
Columnar format with 4 fruit items:
- banana, date, grape, kiwi

### list_c.txt
Columnar format with 4 fruit items:
- honeydew, kiwi, lemon, mango

### comma_list.txt
Comma-separated format:
- apple, banana, cherry, date, elderberry

## Example Operations

### Basic A - B + C
```bash
python ../../bin/set_operations.py \
  -a list_a.txt \
  -b list_b.txt \
  -c list_c.txt
```
**Result:** apple, cherry, elderberry, fig, honeydew, kiwi, lemon, mango

### Find Common Items (Intersection)
```bash
python ../../bin/set_operations.py \
  -a list_a.txt \
  -b list_b.txt \
  --operation "A&B"
```
**Result:** banana, date, grape

### Combine All Lists (Union)
```bash
python ../../bin/set_operations.py \
  -a list_a.txt \
  -b list_b.txt \
  -c list_c.txt \
  --operation "A+B+C"
```
**Result:** All unique fruits from all lists

### Items Unique to List A
```bash
python ../../bin/set_operations.py \
  -a list_a.txt \
  -b list_b.txt \
  -c list_c.txt \
  --operation "A-(B+C)"
```
**Result:** apple, cherry, elderberry, fig

## Testing Different Formats

### Mixed Input Formats
```bash
# Columnar file + comma-separated direct input
python ../../bin/set_operations.py \
  -a list_a.txt \
  -b "banana,kiwi" \
  --operation "A-B"
```

### Using the Comma File
```bash
python ../../bin/set_operations.py \
  -a comma_list.txt \
  -b list_b.txt \
  --operation "A-B"
```

## Output Format Examples

### Columnar Output
```bash
python ../../bin/set_operations.py \
  -a list_a.txt -b list_b.txt \
  --operation "A-B" \
  --output-format columnar
```

### JSON Output
```bash
python ../../bin/set_operations.py \
  -a list_a.txt -b list_b.txt \
  --operation "A-B" \
  --output-format json
```

## Tips
- These examples use simple, memorable data (fruits)
- Great for understanding how operations work
- Test your understanding before using with real data
- All files are in columnar format except comma_list.txt