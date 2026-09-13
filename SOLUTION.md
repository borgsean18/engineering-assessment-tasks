# Solution (Backend - mid)

Added an endpoint to create a change order against a project and optionally a work package.
`POST /projects/{project_id}/change-orders`

## What I did
Created a new schema called `ChangeOrderCreate` because `id` and `work_package_id` are required in `ChangeOrder`. This showed that the format of `ChangeOrder` didnt fit for creating a new ChangeOrder. 

## Validation

- Added `ConfigDict(extra="forbid")` to the new `ChangeOrderCreate` schema to reject any extra fields being sent to the endpoint
- Added *Field* funciton validation to the new `ChangeOrderCreate` schema. This provides FastAPI side validation for fields not matching the desired format.
