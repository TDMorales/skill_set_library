# Examples

These examples show how the prompt-optimizer should ask clarifying questions
and then produce a Task Spec once critical details are provided.

## Example 1: Clarifying questions first

User input:
Create a pivot table using AG Grid.

Agent questions (ask up to 3):
1) What version of AG Grid are you using or expecting to use?
2) Will your data be hydrated from a REST endpoint or using SSRM?
3) What baseline functionality do you expect from the pivot table (row/column grouping, aggregation types, export)?

## Example 2: Task Spec after answers are provided

Assume the user answers:
- AG Grid v32, enterprise enabled
- Data comes from a REST endpoint (client-side row model)
- Needs row grouping, sum aggregation, and CSV export

Task Spec
### Goal
- Implement an AG Grid pivot table with row grouping, sum aggregation, and CSV export using AG Grid v32 enterprise.

### Context (what we know)
- Target is AG Grid v32 with enterprise features enabled.
- Data is loaded from a REST endpoint using the client-side row model.
- Required features: row grouping, sum aggregation, CSV export.

### Assumptions (what we are inferring)
- Project is a frontend web app already using AG Grid.
- REST data is available in a JSON array suitable for AG Grid rows.

### Constraints
- Languages/frameworks/versions: AG Grid v32
- Do not change: Existing data-fetching endpoint or server API
- Performance/latency targets: No specific target provided
- Security/compliance constraints: No special constraints provided

### Deliverables
- Implementation steps and sample code to configure pivoting, grouping, and CSV export.
- Clear instructions on required AG Grid enterprise modules.

### Execution Plan (agent steps)
1) Confirm required AG Grid enterprise modules and imports for pivoting and row grouping.
2) Define column definitions with pivot and aggregation settings.
3) Configure grid options for pivot mode and enable CSV export.
4) Provide example data fetch and grid initialization snippet.

### Acceptance Criteria
- Grid renders with pivoting enabled and row grouping functional.
- Sum aggregation works on numeric columns.
- CSV export produces a file with the grouped/pivoted data.

### Required Inputs (from user, if any)
- Existing project structure or preferred framework (React, Angular, Vue, vanilla).
- Column schema for the dataset.
