# Test Markdown Document

This is a comprehensive test document for the markdown parser and SCM queries.

## Headings

### ATX Headings
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

### Setext Headings
Heading Level 1
================

Heading Level 2
--------------

## Lists

### Unordered Lists
- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3

### Ordered Lists
1. First item
2. Second item
   1. Nested ordered item 2.1
   2. Nested ordered item 2.2
3. Third item

### Task Lists
- [ ] Unchecked task
- [x] Checked task
- [X] Checked task (uppercase)
  - [ ] Nested unchecked task
  - [x] Nested checked task

## Code Blocks

### Fenced Code Blocks
```python
def hello_world():
    print("Hello, World!")
    return True
```

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```

```bash
#!/bin/bash
echo "Hello from bash"
```

### Indented Code Blocks
    This is an indented code block
    with multiple lines
    of code content

## Tables

### Basic Table
| Name | Age | City |
|------|-----|------|
| Alice | 25 | New York |
| Bob | 30 | London |
| Charlie | 35 | Paris |

### Table with Alignment
| Left | Center | Right |
|:-----|:------:|------:|
| Left aligned | Center aligned | Right aligned |
| More content | More content | More content |

### Table with Escaped Pipes
| Column with \| pipe | Another column |
|-------------------|----------------|
| Content with \| pipe | More content |

## Blockquotes

> This is a blockquote
> with multiple lines
> of quoted content

> > This is a nested blockquote
> > within another blockquote

> Blockquote with **bold** and *italic* text

## Links and References

### Inline Links
[GitHub](https://github.com)
[Stack Overflow](https://stackoverflow.com "Visit Stack Overflow")

### Reference Links
[GitHub][github-link]
[Stack Overflow][so-link]

[github-link]: https://github.com "GitHub Homepage"
[so-link]: https://stackoverflow.com "Stack Overflow"

## Thematic Breaks

Content above the break

---

Content below the break

***

More content

___

Final content

## HTML Blocks

<div class="custom-block">
  <p>This is an HTML block with custom content.</p>
  <ul>
    <li>HTML list item 1</li>
    <li>HTML list item 2</li>
  </ul>
</div>

## Escapes and Entities

### Backslash Escapes
\*This is not italic\*
\[This is not a link\]
\`This is not code\`

### Entity References
&copy; Copyright symbol
&trade; Trademark symbol
&reg; Registered trademark
&nbsp; Non-breaking space

### Numeric Character References
&#169; Copyright (decimal)
&#x00A9; Copyright (hexadecimal)

## Mixed Content

### Paragraph with Inline Elements
This paragraph contains **bold text**, *italic text*, `inline code`, and a [link](https://example.com).

### Lists with Mixed Content
- **Bold list item**
- *Italic list item*
- `Code list item`
- [Link list item](https://example.com)

### Code Blocks with Language
```python
# Python code with comments
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

```javascript
// JavaScript code with comments
function factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
```

## Complex Nested Structures

### Nested Lists with Different Types
1. Ordered item 1
   - Unordered nested item
   - [ ] Task list item
   - [x] Completed task
2. Ordered item 2
   ```python
   # Code block in list
   print("Hello from list")
   ```
3. Ordered item 3
   > Blockquote in list
   > with multiple lines

### Section with All Elements
# Complete Section

This section contains all major markdown elements:

**Bold text** and *italic text* with `inline code`.

- List item 1
- List item 2

> Blockquote content

```bash
echo "Code block"
```

| Table | Header |
|-------|--------|
| Data  | Cell   |

---

## Metadata

### YAML Front Matter
---
title: "Test Document"
author: "Test Author"
date: 2024-01-01
tags: [test, markdown, parser]
---

### TOML Front Matter
+++
title = "Test Document"
author = "Test Author"
date = 2024-01-01
tags = ["test", "markdown", "parser"]
+++

## Edge Cases

### Empty Elements
#### 

### Elements with Special Characters
# Heading with `backticks`
## Heading with **bold**
### Heading with [links](https://example.com)

### Very Long Content
This is a very long paragraph that contains a lot of text to test how the parser handles long content. It includes various elements like **bold text**, *italic text*, `inline code`, and [links](https://example.com). The content continues for multiple sentences to ensure that the parser can handle substantial amounts of text without issues.

### Code Blocks with Special Characters
```bash
#!/bin/bash
echo "Hello, World!"
echo "Special chars: $PATH, ~/home, &amp;, &lt;, &gt;"
```

```python
# Python with special characters
import re
pattern = r'[a-zA-Z0-9_]+'
text = "Hello_World123"
matches = re.findall(pattern, text)
print(f"Matches: {matches}")
```

## Final Section

This concludes our comprehensive test of markdown parsing capabilities.

> **Note**: This document tests all major markdown constructs supported by the tree-sitter markdown grammar.

---

*End of test document* 