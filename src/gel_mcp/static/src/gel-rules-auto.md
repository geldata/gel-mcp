---
description: Working with Gel database
globs: 
alwaysApply: false
---

# Working with Gel (ex EdgeDB)

## General

1. Gel is rebranded EdgeDB. It uses SDL for schemas and EdgeQL for queries. Same syntax and usage apply.
2. **ALWAYS** consult the Gel MCP server for code examples.
3. Run CLI commands with `--non-interactive` flag where available to avoid getting the tool call.
4. Search docs at docs.geldata.com.

## CLI

Key Commands:

```bash
gel project init --non-interactive     # Initialize project  
gel migration create --non-interactive # Create migration
gel migrate                            # Apply migrations
gel branch                             # Manage database branches for safe development
gel query                              # Run a query (no support for args and globals)
```

## MCP server

1. `execute_query`: execute a Gel query **with args and globals** against the current project's instance.
2. `try_query`: test query in a rolled-back transaction.
3. `list_examples`: browse code examples for advanced features.
4. `fetch_example`: get specific example by slug.

## Schema

Modern syntax (.gel files, v6+):

```sdl
# Core types with inheritance, multi-links, constraints, computeds
abstract type Content {
    required title: str {
        constraint exclusive;
    };
    created_at: datetime {
        default := datetime_current();
    };
}

type User {
    required name: str {
        constraint exclusive;
    };
    email: str;
    multi authored_posts := .<author[is Post];
}

type Post extending Content {
    content: str;
    author: User {
        on target delete delete source;  # Delete post when author is deleted
    };
    multi tags: Tag;
    uppercase_title := str_upper(.title);
    
    index on (.title);
    index on ((.author, .created_at));  # Note that the argument is a tuple
}

type Tag {
    required name: str {
        constraint exclusive;
    };
    multi posts := .<tags[is Post];
}
```

## Query Language (EdgeQL)

Use `select` for retrieving data, `insert` for creating, `update` for modifying, and `delete` for removing data.
Use shape expressions ({ ... }) to specify which properties to include in the result.

### Select

```edgeql

select Movie {
    id,
    title,
    year,
    actors: { id, full_name },
    reviews := .<movie[is Review] {
        id, rating,
        author: { id, name }
    },
}
filter .id = <uuid>'09c34154-4148-11ea-9c68-5375ca908326'
```

Filter by nested property and use of `detached` for comparing objects of the same type:
```edgeql
# Filter by nested property
select Movie { id, title, year }
filter .actors.full_name = 'Keanu Reeves'

# With blocks for complex queries (top-level preferred)
select Person {
    id, full_name,
    same_last_name := (
        with
            P := detached Person
        select P { id, full_name }
        filter P.last_name = Person.last_name and P != Person
    ),
}
filter exists .same_last_name
```

Set operations and ordering:

```edgeql
# Set intersection
with Actor := Movie.actors, Director := Movie.director,
select Actor filter Actor in Director;

# Order scalar sets
select numbers := {3, 1, 2} order by numbers;
```

Free objects for data packaging:

```edgeql
with U := (select User filter .name like '%user%')
select {
    matches := U {name},
    total := count(U),
    total_users := count(User),
};
```

### Insert

Basic and JSON input:
```edgeql
# Basic insert with mixed literals and parameters
insert Movie {
    title := 'Dune',
    year := $year,
    image := 'dune2020.jpg',
    directors := (select Person filter .full_name = $director_name)
}

# Complex insert with parameters in with block
with
    movie_data := <tuple<title: str, year: int64, directors: array<str>>> <json>$input,
    default_image := 'default_movie.jpg'
insert Movie {
    title := movie_data.title,
    year := movie_data.year,
    image := default_image,
    directors := (select Person filter .full_name in array_unpack(movie_data.directors))
}
```

Nested insert and conflict handling:
```edgeql
# Nested insert with mixed approach
insert Review {
    body := $review_body,
    rating := $rating,
    movie := (select Movie filter .title = 'Dune' and .year = 2020 limit 1),
    author := (insert User { name := $username, image := 'default_avatar.jpg' })
}

# Conflict handling patterns
insert User { name := $username, image := 'default_avatar.jpg' }
unless conflict on .name  # Do nothing if exists

# Upsert pattern
insert User { name := $username, image := $new_image }
unless conflict on .name
else (update User set { image := $new_image })

# Insert or select existing
insert User { name := 'dune_fan_2020', image := 'default_avatar.jpg' }
unless conflict on .name else User
```

Bulk insert with `for` loops:
```edgeql
# Bulk insert from JSON parameter
with raw_data := <json>$data
for item in json_array_unpack(raw_data) union (
    insert Movie {
        title := <str>item['title'],
        year := <int64>item['year']
    }
)
```

### Update & Delete

```edgeql
# Update with parameters
update User filter .id = <uuid>$user_id set { name := $new_name };

# Delete operations
delete User filter .id = <uuid>'09c34154-4148-11ea-9c68-5375ca908326';
delete Review filter .author.name = $author_name;

# Bulk operations with conditions
delete Review 
filter .rating < $min_rating and .author.name = 'trouble2020'
```

### Complex Operations

```edgeql
# Complex query with organized parameters (optional param with default)
with
    min_year := <int64>$min_year,
    max_year := <int64>$max_year,
    title_pattern := <optional str>$title_pattern ?? '%',
    actor_names := <array<str>>$actor_names
select Movie { 
    title, year,
    matching_actors := .actors[.full_name in array_unpack(actor_names)]
}
filter .year >= min_year and .year <= max_year
  and .title ilike title_pattern
```

## Advanced Schema

```sdl
# Functions, triggers, mutation rewrites, link props, access policies

global current_user_id  # set at query time by the querying side

function get_current_user() -> optional User using (
    select User filter .id = global current_user_id 
);

type User {
    required name: str;
    required email: str { constraint exclusive; };
    
    access policy own_records 
        allow all 
        using (exists global current_user_id and .id ?= global current_user_id);
}

type Post {
    required title: str;
    content: str;
    author: User;
    
    # Triggers for validation/logging
    trigger validate_content after insert, update for each do (
        assert(len(__new__.title) > 0, message := "Title required")
    );
    
    # Mutation rewrites on properties
    created_at: datetime {
        rewrite insert using (datetime_of_statement());
    };
    modified_at: datetime {
        rewrite update using (datetime_of_statement());
    };
    
    access policy author_only allow update, delete using (.author.id = global current_user_id);
}
```

```sdl
# Link properties are always single and optional
type BlogPost {
    multi editors: User {
        added_at: datetime { default := datetime_current(); };
        role: str;
    };
}
```

```edgeql
# Inserting with link properties
insert BlogPost {
    title := 'Test',
    editors := (select User filter .name = 'Bob') { 
        @added_at := datetime_current(), 
        @role := 'reviewer' 
    }
}

# Querying link properties (note the @ syntax)
select BlogPost {
    title,
    editors: { name, @added_at, @role }
}
```

## Critical Gotchas

**ALWAYS check before schema changes**

### Delegated Constraints
When moving exclusive properties to parent types, use `delegated constraint exclusive` to maintain per-type uniqueness:

```sdl
abstract type BaseType {
    required some_prop: str {
        delegated constraint exclusive;  # Unique per extending type
    }
}

type Foo extending BaseType { }  # some_prop unique among Foo instances
type Bar extending BaseType { }  # some_prop unique among Bar instances
```

**Never refactor inheritance without considering delegated constraints.**

## AI Agent Guidelines

1. **Always check delegated constraints** when refactoring schemas
2. Use parameters (`$var`) instead of hardcoded values
3. Gel has no NULL - use `exists` or `?=` operators
4. Use `limit 1` for single link requirements
5. Organize complex queries with `with` blocks at top
6. Consult MCP server examples for advanced patterns
7. Check docs.geldata.com for syntax questions
