---
description: Working with Gel in Python
globs: 
alwaysApply: false
---

# Working with Gel in Python

For general information please request a general Gel rules document.
This one is specifically for the new Python API.

## Core Concepts

**Gel Python API** consists of a query builder and an ORM.
Both work via generated Pydantic reflections of the schema.

```bash
gel-generate-py models
```

This creates a `models` package with Pydantic models corresponding to your schema modules.
You don't need to go deep into the type hierarchies, only the contents of `default.py` that contain your reflected Pydantic models.

1. Query builder is for building queries in a typesafe way. Use for general querying and bulk ops.
2. ORM is for managing objects and syncing their state with the database. Use for working with individual objects.

Leverage both components and their mutual integration for maximum code prettiness and typesafety.

## Database Connection

```python
import gel
from models import default, std

# Create database client
db = gel.create_async_client()
```

**Note**: the Python API works both with sync and async client.


## ORM: create and save objects

```python
# Create individual objects
alice = default.User(name='Alice')
billie = default.User(name='Billie')
cameron = default.User(name='Cameron')

# Save single or multiple objects
await db.save(alice, billie, cameron)
```

```python
# Create and save nested structures
await db.save(
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

## QB basics

Use `db.get` to fetch a single object or return default value like `dict.get`.
Unlike `dict`, `db.get` will throw an error if you don't specify a default and nothing is found.

Use `db.query` for all other querying purposes.

Use `query.__edgeql__[1]` before calling `.get()` or `.query()` to see the generated EdgeQL query for debugging.  

### Basic Queries

```python
# Fetch all objects of a type
q = default.User
await everyone = db.query(q)

# Get single object with filter
q = default.User.filter(name='Alice')
await alice = db.get(q, None)

# Query multiple objects with filter
q = default.Post.filter(body='Hello')
await posts = db.query(q)
```

### Advanced Filtering

```python
# Using lambda functions for complex filters
q = default.User.filter(
    lambda u: std.len(u.name) > 5
)
await users = db.query(q)

# Following links in filters
q = default.Post.filter(
    lambda p: p.author.name == 'Alice'
)
await posts = db.query(q)
```

### Shapes

You specify what properties to fetch by using:

```python
Type.select(
    prop_1=True,  # fetch prop_1
    prop_3=True   # fetch prop_3
)
# No other props will be fetched.
```

```python
# Include all fields and specific links
q = default.Post.select(
    '*',
    author=True,
).filter(
    lambda p: p.author.name == 'Alice'
)
await posts = db.query(q)

# Cherry-pick specific fields
q = default.Post.select(
    title=True,
    body=True,
    author=True,
).filter(
    lambda p: p.author.name == 'Alice'
)
await posts = db.query(q)
```

### Ordering Results
```python
# Simple ordering
q = default.Post.select(
    '*',
    author=True,
).order_by(created_at=True)
await posts = db.query(q)

# Multiple ordering criteria with direction
q = default.Post.select(
    '*',
    author=True,
).order_by(
    created_at='desc',
    title='asc',
)
await posts = db.query(q)
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
await user = db.get(q)
```

## ORM: updating data

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
await db.save(posts[0], new_post)
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

- Use `db.save()` for ORM persistence (creation and updates)
- Use `db.get()` for QB fetching single objects, `db.query()` for multiple objects
- Chain `.filter()`, `.select()`, `.order_by()` methods for complex queries, use `.__edgeql__` to verify the query.
- Use lambda functions for advanced filtering with `std` module functions
- Leverage object references to maintain relationships between data




