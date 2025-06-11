---
description: Working with Gel in TypeScript
globs: 
alwaysApply: false
---

# Gel TypeScript Query Builder Guide

Gel TypeScript query builder provides type safety and IntelliSense for EdgeQL.

## Setup & Connection

```typescript
import { createClient } from "gel";
import e from "@/dbschema/edgeql-js"; // Generated query builder

const client = createClient(); // Auto-detects connection
```

## Schema Example

```gel
module default {
  type User {
    required name: str;
    email: str;
    posts: multi link Post;
    created_at: datetime { default := datetime_current(); };
    metadata: json;
  }
  
  type Post {
    required title: str;
    content: str;
    required author: link User;
    tags: multi link Tag;
    published: bool { default := false; };
    created_at: datetime { default := datetime_current(); };
  }
  
  type Tag {
    required name: str { constraint exclusive; };
  }
}
```

## Core Operations

### Insert

```typescript
// Simple insert
const user = await e.insert(e.User, {
  name: "Alice",
  email: "alice@example.com"
}).run(client);

// Insert with relations
const post = await e.insert(e.Post, {
  title: "My Post",
  content: "Content here",
  author: e.select(e.User, (u) => ({
    filter_single: e.op(u.email, "=", "alice@example.com")
  })),
  tags: e.select(e.Tag, (t) => ({
    filter: e.op(t.name, "in", e.set("tech", "typescript"))
  }))
}).run(client);

// Upsert with conflict handling
const tag = await e.insert(e.Tag, {
  name: "typescript"
}).unlessConflict((tag) => ({
  on: tag.name,
  else: e.select(tag)
})).run(client);

// Bulk insert
const users = await e.for(
  e.set(
    { name: "Alice", email: "alice@example.com" },
    { name: "Bob", email: "bob@example.com" }
  ),
  (userData) => e.insert(e.User, userData)
).run(client);
```

### Select

```typescript
// Basic select with relations
const posts = await e.select(e.Post, (p) => ({
  title: true,
  author: { name: true },
  tags: { name: true },
  filter: e.op(p.published, "=", true),
  order_by: e.desc(p.created_at),
  limit: 10
})).run(client);

// Parameterized queries
const searchPosts = await e.params({
  term: e.optional(e.str),
  authorId: e.optional(e.uuid)
}, (params) => 
  e.select(e.Post, (p) => ({
    title: true,
    author: { name: true },
    filter: e.all(e.set(
      params.term ? e.op(p.title, "ilike", e.op("%", "++", params.term, "++", "%")) : e.bool(true),
      params.authorId ? e.op(p.author.id, "=", params.authorId) : e.bool(true)
    ))
  }))
).run(client, { term: "typescript" });

// Computed properties
const enrichedPosts = await e.select(e.Post, (p) => ({
  title: true,
  word_count: e.len(e.str_split(p.content, " ")),
  author_post_count: e.count(p.author.posts),
  tag_names: e.array_agg(p.tags.name),
  is_recent: e.op(p.created_at, ">", e.datetime("2024-01-01T00:00:00Z"))
})).run(client);

// Nested filtering - posts by active authors
const activePosts = await e.select(e.Post, (p) => ({
  title: true,
  author: { name: true },
  filter: e.op(e.count(p.author.posts), ">", 5)
})).run(client);

// Pagination
const paginatedPosts = await e.select(e.Post, (p) => ({
  title: true,
  created_at: true,
  order_by: e.desc(p.created_at),
  offset: 20,
  limit: 10
})).run(client);
```

### Update

```typescript
// Update with relations
await e.update(e.Post, (p) => ({
  filter_single: e.op(p.id, "=", e.uuid(postId)),
  set: {
    title: "New Title",
    published: true,
    tags: { "+=": e.select(e.Tag, t => ({ filter: e.op(t.name, "=", "featured") })) }
  }
})).run(client);

// Bulk update
await e.update(e.Post, (p) => ({
  filter: e.op(p.created_at, "<", e.datetime("2023-01-01T00:00:00Z")),
  set: {
    tags: { "+=": e.select(e.Tag, t => ({ filter: e.op(t.name, "=", "archived") })) }
  }
})).run(client);
```

### Delete

```typescript
await e.delete(e.Post, (p) => ({
  filter: e.op(p.published, "=", false)
})).run(client);
```

## Advanced Patterns

### Transactions
```typescript
await client.transaction(async (tx) => {
  const user = await e.insert(e.User, { name: "Bob" }).run(tx);
  await e.insert(e.Post, { title: "Bob's Post", author: user }).run(tx);
});
```

### Aggregations
```typescript
const userStats = await e.select(e.User, (u) => ({
  name: true,
  post_count: e.count(u.posts),
  published_count: e.count(e.select(u.posts, p => ({ filter: p.published }))),
  latest_post_date: e.max(u.posts.created_at),
  order_by: e.desc(e.count(u.posts))
})).run(client);
```

### Grouping
```typescript
const postsByAuthor = await e.group(e.Post, (p) => ({
  post_count: e.count(e.set()),
  latest_post: e.max(p.created_at),
  titles: e.array_agg(p.title),
  by: { author_name: p.author.name }
})).run(client);
```

### For Loops
```typescript
// Transform data with for loops
const userEmails = await e.for(
  e.select(e.User, (u) => ({ filter: e.op(u.email, "!=", e.str("")) })),
  (user) => e.str_upper(user.email)
).run(client);
```

### JSON Handling
```typescript
// Work with JSON fields
const userWithMetadata = await e.select(e.User, (u) => ({
  name: true,
  metadata: u.metadata,
  setting_value: e.json_get(u.metadata, "settings", "theme"),
  filter_single: e.op(u.id, "=", e.uuid(userId))
})).run(client);
```

### Complex Filtering
```typescript
// Multiple OR conditions
const posts = await e.select(e.Post, (p) => ({
  title: true,
  filter: e.any(e.set(
    e.op(p.title, "ilike", "%typescript%"),
    e.op(p.title, "ilike", "%javascript%"),
    e.all(e.set(
      e.op(p.published, "=", true),
      e.op(p.author.name, "=", "Alice")
    ))
  ))
})).run(client);

// Filter by related object properties
const postsWithTags = await e.select(e.Post, (p) => ({
  title: true,
  tags: { name: true },
  filter: e.any(p.tags, (tag) => e.op(tag.name, "in", e.set("featured", "popular")))
})).run(client);

// Date range filtering
const recentPosts = await e.select(e.Post, (p) => ({
  title: true,
  created_at: true,
  filter: e.all(e.set(
    e.op(p.created_at, ">=", e.datetime("2024-01-01T00:00:00Z")),
    e.op(p.created_at, "<", e.datetime_current())
  ))
})).run(client);
```

### Error Handling
```typescript
// Handle optional single results
try {
  const user = await e.select(e.User, (u) => ({
    name: true,
    filter_single: e.op(u.email, "=", email)
  })).run(client);
} catch (error) {
  if (error instanceof e.NoDataError) {
    console.log("User not found");
  }
}

// Safe optional access
const users = await e.select(e.User, (u) => ({
  name: true,
  filter: e.op(u.email, "=", email),
  limit: 1
})).run(client);
const user = users[0] ?? null;
```

## Key Patterns

- **Type Safety**: All queries typed from schema
- **Relations**: Navigate with dot notation (`u.posts`, `p.author.name`)
- **Filtering**: Use `e.op()` for comparisons, `e.all()`/`e.any()` for logic
- **Parameters**: Use `e.params()` for safe parameterization
- **Transactions**: Wrap operations in `client.transaction()`
- **Upserts**: Use `.unlessConflict()` for conflict resolution
- **Bulk Operations**: Use `e.for()` for iterations and bulk processing
- **Grouping**: Use `e.group()` for aggregations with `by` clause
- **Arrays**: Use `e.array_agg()` for collecting related data
- **JSON**: Use `e.json_get()` to access JSON field properties
- **Dates**: Use `e.datetime()` for literals, `e.datetime_current()` for now
- **Error Handling**: Handle `NoDataError` for missing single results
- **Computed Fields**: Add calculated properties directly in queries
- **Pagination**: Use `offset`/`limit` for paging

The query builder provides a fluent, type-safe interface that prevents runtime errors and enables powerful IntelliSense support while maintaining the full expressiveness of EdgeQL.




