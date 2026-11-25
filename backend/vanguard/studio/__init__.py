"""The configuration studio: personas, sites and tasks that users create without code.

Custom items are stored in three tables (`models`), read and written through
`repository`, and reach the catalog through `source` (the hook vanguard.catalog calls),
so they appear in the lobby, runs, the checker and the results like built-in items.
"""
