# Solution (Backend - mid)

Added an endpoint to create a change order against a project and optionally a work package.
`POST /projects/{project_id}/change-orders`

## What I did
Created a new schema called `ChangeOrderCreate` because `id` and `work_package_id` are required in `ChangeOrder`. This showed that the format of `ChangeOrder` didnt fit for creating a new ChangeOrder.
If the date raised is not supplied, then I am defaulting it to today (the day the `ChangeOrder` is being created). I did this because a planner raising a change order is raising it now. I didnt want to add friction to creating a ChangeOrder when it does make sense to default it to the date of creation.

## Validation

- Added `ConfigDict(extra="forbid")` to the new `ChangeOrderCreate` schema to reject any extra fields being sent to the endpoint
- Added *Field* funciton validation to the new `ChangeOrderCreate` schema. This provides FastAPI side validation for fields not matching the desired format.
- Validation in the router - these validation errors depend on results returned from the database.
- - 404: Unknown project
- - 409: Dupplicate reference on the same project
- - 422: A work package code does not resolve in this project.

## AI and tooling disclosure
I used Claude to ask questions on improving validation (including the error codes as I dont know them all, and always default to searching them when needed), and to generate tests. I iterated over the tests with Claude till I felt they were comprehensive.