---
description: Working with Gel in Python
globs: 
alwaysApply: false
---

# Working with Gel in Python

For general information please request a general Gel rules document.
This one is specifically for the new Python API that leverages Pydantic models.

## Core Concepts

**Gel Python API** provides typesafe query building through generated Pydantic models. It offers a pythonic way to interact with Gel databases using familiar object-oriented patterns.

## Setup & Code Generation

```bash
# Generate typesafe Python models from schema
gel-generate-py models
```

This creates a `models` package with Pydantic models corresponding to your schema modules.

## Database Connection

```python
import gel
from models import default, std

# Create database client
db = gel.create_client()
```

## Object Creation & Saving

### Simple Object Creation
```python
# Create individual objects
alice = default.User(name='Alice')
billie = default.User(name='Billie')
cameron = default.User(name='Cameron')

# Save single or multiple objects
db.save(alice, billie, cameron)
```

### Nested Object Creation
```python
# Create and save nested structures
db.save(
    default.Post(
        title='New here',
        body='Hello',
        author=alice,
    ),
    default.Post(
        title='First time', 
        body='Hello',
        author=billie,
    ),
)
```

## Querying Data

### Basic Queries
```python
# Fetch all objects of a type
q = default.User
everyone = db.query(q)

# Get single object with filter
q = default.User.filter(name='Alice')
alice = db.get(q)

# Query multiple objects with filter
q = default.Post.filter(body='Hello')
posts = db.query(q)
```

### Advanced Filtering
```python
# Using lambda functions for complex filters
q = default.User.filter(
    lambda u: std.len(u.name) > 5
)
users = db.query(q)

# Following links in filters
q = default.Post.filter(
    lambda p: p.author.name == 'Alice'
)
posts = db.query(q)
```

### Field Selection
```python
# Include all fields and specific links
q = default.Post.select(
    '*',
    author=True,
).filter(
    lambda p: p.author.name == 'Alice'
)
posts = db.query(q)

# Cherry-pick specific fields
q = default.Post.select(
    title=True,
    body=True,
    author=True,
).filter(
    lambda p: p.author.name == 'Alice'
)
posts = db.query(q)
```

### Ordering Results
```python
# Simple ordering
q = default.Post.select(
    '*',
    author=True,
).order_by(created_at=True)
posts = db.query(q)

# Multiple ordering criteria with direction
q = default.Post.select(
    '*',
    author=True,
).order_by(
    created_at='desc',
    title='asc',
)
posts = db.query(q)
```

### Nested Queries
```python
# Nested sub-queries with filtering and ordering
q = default.User.select(
    '*',
    posts=lambda u: u.posts.order_by(
        created_at='desc',
        title='asc',
    ),
).filter(name='Alice')
user = db.get(q)
```

## Updating Data

```python
# Modify existing objects and save changes
posts = db.query(default.Post.filter(lambda p: p.author.name == 'Alice'))
posts[0].body = 'Hello world!'

# Create new objects using existing ones as references
new_post = default.Post(
    title='Question',
    body='How do I insert data?',
    author=posts[0].author,  # Reference existing user
)

# Save both updated and new objects
db.save(posts[0], new_post)
```

## Key Features Summary

1. **Type Safety**: Generated Pydantic models provide compile-time type checking
2. **Pythonic API**: Object-oriented approach familiar to Python developers  
3. **Flexible Querying**: Support for filtering, field selection, ordering, and nested queries
4. **Lambda Expressions**: Complex filtering with lambda functions and link traversal
5. **Batch Operations**: Save multiple objects in single transactions
6. **Object References**: Use fetched objects as references when creating new data
7. **Nested Structures**: Build and query complex nested object relationships

## Common Patterns

- Always use `db.save()` for persistence (creation and updates)
- Use `db.get()` for single objects, `db.query()` for multiple objects
- Chain `.filter()`, `.select()`, `.order_by()` methods for complex queries
- Use lambda functions for advanced filtering with `std` module functions
- Leverage object references to maintain relationships between data




