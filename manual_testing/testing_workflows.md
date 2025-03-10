## Workflow 1: Basics

**Test Scenario**: Verify that the agent can set up a basic schema in a pre-initialized Gel project, and write an insert and a select query.

**Expected Result**: 

1. The schema is set up and contains up-to-date syntax. 
2. The database population query is verified, executed and stored in a .edgeql file.
3. The select query is verified and executed via the CLI or the specialized tool.

### Initial state

**Schema**:

```gel
# dbschema/default.gel
module default {

}
```

## Workflow 2: Embeddings 

**Test Scenario:** Verify that the agent can enable `ext::ai` to configure automatic embeddings, set up the API key, create the index and perform semantic search using the Python binding.

**Expected Result**: 

1. `ext::ai` is successfully enabled 
2. The API key is configured
3. The index is created
4. Vector search query written and executed with Python

### Initial state

**Schema**:

```gel
# dbschema/default.gel
module default {
    type Friend {
        required name: str {
            constraint exclusive;
        };

        summary: str;               # A brief description of personality and role
        relationship_to_komi: str;  # Relationship with Komi
        defining_trait: str;        # Primary character trait or quirk
    }
}
```

**Data**:

```edgeql
insert Friend {
    name := 'Tadano Hitohito',
    summary := 'An extremely average high school boy with a remarkable ability to read the atmosphere and understand others\' feelings, especially Komi\'s.',
    relationship_to_komi := 'First friend and love interest',
    defining_trait := 'Perceptiveness',
};

insert Friend {
    name := 'Osana Najimi',
    summary := 'An extremely outgoing person who claims to have been everyone\'s childhood friend. Gender: Najimi.',
    relationship_to_komi := 'Second friend and social catalyst',
    defining_trait := 'Universal childhood friend',
};

insert Friend {
    name := 'Yamai Ren',
    summary := 'An intense and sometimes obsessive classmate who is completely infatuated with Komi.',
    relationship_to_komi := 'Self-proclaimed guardian and admirer',
    defining_trait := 'Obsessive devotion',
};

insert Friend {
    name := 'Katai Makoto',
    summary := 'A intimidating-looking but shy student who shares many communication problems with Komi.',
    relationship_to_komi := 'Fellow communication-challenged friend',
    defining_trait := 'Scary appearance but gentle nature',
};

insert Friend {
    name := 'Nakanaka Omoharu',
    summary := 'A self-proclaimed wielder of dark powers who acts like an anime character and is actually just a regular gaming enthusiast.',
    relationship_to_komi := 'Gaming buddy and chuunibyou friend',
    defining_trait := 'Chuunibyou tendencies',
};
```