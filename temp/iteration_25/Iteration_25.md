# Executive Summary — Iteration 25

• Added APR calculation and management to Labor Agreements  [Issue #4063](https://github.com/semanticarts/dca/issues/4063) · [PR #4127](https://github.com/semanticarts/dca/pull/4127) · [PR #4631](https://github.com/semanticarts/dca/pull/4631)
  - Automatically closes out old APR when new one is created due to higher pay rate
  - Introduced queries to retroactively update paystub APRs with correct records
  - Enhanced payroll processing workflow
    - Integrated actual pay rates into labor agreements for accurate tracking

• Burnchart views updated to more descriptive names  [Issue #4311](https://github.com/semanticarts/dca/issues/4311) · [PR #4651](https://github.com/semanticarts/dca/pull/4651)
  - "Burnchart Details" renamed to "Time Charge Details" with new description: "A detailed view of all time charges submitted by SA employees."
  - "Burnchart Hours Summary" renamed to "Hours by Week and Category" with new description: "Group the hours by week and category for easier analysis."

• Burn chart query now supports optional time card charging to projects    [Issue #4338](https://github.com/semanticarts/dca/issues/4338)
  - Updated `sa-view:_burn_chart` to include an optional selection of time cards
  - Projects with no time entries will now still display in burn charts

• Employee EER vs AER view with pay period breakdown sub-view added    [Issue #4443](https://github.com/semanticarts/dca/issues/4443) · [PR #4428](https://github.com/semanticarts/dca/pull/4428) · [PR #4648](https://github.com/semanticarts/dca/pull/4648) · [PR #4672](https://github.com/semanticarts/dca/pull/4672)
  - Closes #4309
  - PR #4428 (Merged)
  - EER vs AER view now includes all matching active employees and tasks
    - PR #4648 (Merged)
    - Removes employee and task filters
  - Exclude advisory work from earned revenue totals
    - PR #4672 (Merged)
    - Subtracts time cards tied to advisory assignments from total

• Resolved duplicate predicate issues in ontology mappings  [Issue #4468](https://github.com/semanticarts/dca/issues/4468)
  - Identified and corrected 715 instances across multiple namespaces
  - Enhanced data consistency for properties like name, hasPart, and hasValue

• Removed "Employee Directory" from HR launchpad    [Issue #4483](https://github.com/semanticarts/dca/issues/4483) · [PR #4650](https://github.com/semanticarts/dca/pull/4650)
  - No longer accessible via the HR menu for all users
  - Improved focus on core HR functions within the launchpad
  - Reordered HR menu items
    - Moved "Pay Period" and "Employee Table" to earlier positions in the menu
    - Enhanced navigation for frequent HR tasks

• Keep timecard earned revenue in sync when task assignments change  [Issue #4554](https://github.com/semanticarts/dca/issues/4554) · [PR #4574](https://github.com/semanticarts/dca/pull/4574) · [PR #4629](https://github.com/semanticarts/dca/pull/4629)
  - Recalculates earned revenue based on the new task assignment's billing rate and timecard duration
  - Ensures consistency across all affected timecards by updating their earnings automatically

• Split employee full name into first/last in payroll exports and fix earned revenue view placement; capitalize tooltips  [Issue #4557](https://github.com/semanticarts/dca/issues/4557) · [PR #63](https://github.com/semanticarts/gistProfSrv/pull/63) · [PR #4545](https://github.com/semanticarts/dca/pull/4545) · [PR #4644](https://github.com/semanticarts/dca/pull/4644) · [PR #4678](https://github.com/semanticarts/dca/pull/4678)
  - Payroll export and payroll view now provide separate First name and Last name fields instead of a single Employee name
  - Earned Revenue pop-out is correctly placed and parameterized for clarity
  - Separate person names into stored first, middle, and last fields for payroll accuracy
    - People with two-part or three-part names get first, middle, and last name values saved separately
    - Payroll periods now read employee first and last names from stored name fields instead of splitting the display name each time
    - Keeps payroll name display consistent across reports
  - Add pay structure setup to employee and contractor records for accurate calculations
    - Employee and contractor forms include a Pay Structure section for setting pay type, start/end dates, and share percentage
    - Payroll now uses the active pay structure for each person, ensuring hybrid and consultant pay are calculated accurately

• Added Pay Structure Assignment to employee and contractor records    [Issue #4593](https://github.com/semanticarts/dca/issues/4593) · [PR #4678](https://github.com/semanticarts/dca/pull/4678)
  - Introduced in Employee and Contractor forms for setting pay type, start/end dates, and share percentage
  - Updated payroll calculations to use active pay structures, replacing hardcoded values
  - Removed hardcoded 10% value from payroll view
    - Ensured hybrid and consultant pay are calculated dynamically based on current pay structures
    - Enhanced accuracy of payroll processing by linking directly to defined pay types

• Burn chart categories now configurable per project  [Issue #4615](https://github.com/semanticarts/dca/issues/4615)
  - Users select "Show" or "Do not show" for each project
  - Automates inclusion/exclusion from burn charts queries

• Show all active employees and task assignments in the EER vs AER view  [Issue #4617](https://github.com/semanticarts/dca/issues/4617) · [PR #4648](https://github.com/semanticarts/dca/pull/4648)
  - Removed filters for specific employee positions
  - Updated query to include all active employees by default

• Balance sheet queries now accurately calculate net income for a specified year  [Issue #4632](https://github.com/semanticarts/dca/issues/4632) · [PR #137](https://github.com/semanticarts/QuickBooks/pull/137) · [PR #4654](https://github.com/semanticarts/dca/pull/4654)
  - Updated JEs retrieval to include only those within the specific year
  - Revised views display accurate yearly net income calculations

• Regenerated chart of accounts from QuickBooks export  [Issue #4633](https://github.com/semanticarts/dca/issues/4633) · [PR #138](https://github.com/semanticarts/QuickBooks/pull/138) · [PR #4654](https://github.com/semanticarts/dca/pull/4654)
  - Updated chart of accounts triples in the QuickBooks repo
  - Ensured all referenced accounts from the latest QuickBooks export are included

• Burn charts now use accounting-day dates and sort correctly  [Issue #4635](https://github.com/semanticarts/dca/issues/4635) · [PR #4677](https://github.com/semanticarts/dca/pull/4677)
  - Burn chart lines align with accounting-calendar weeks
  - Weekly values for actuals, projections, and budgets are calculated based on accounting-day sequences

• Added `TimeAllocation` labor agreement term with weekly hours magnitude    [Issue #4638](https://github.com/semanticarts/dca/issues/4638) · [PR #4674](https://github.com/semanticarts/dca/pull/4674)
  - Updated position form to include weekly hours input
  - Modified utilization and capacity calculation queries to consider weekly hours
  - Position assignment forms now require weekly expected and chargeable hours
    - Default values for both hours fields set by Dave

• Sent update emails to Rebecca and JT on user request status  [Issue #4641](https://github.com/semanticarts/dca/issues/4641)
  - Included current issues and progress stages for each request
  - Automated weekly scheduling for future updates

• Added Total Sales Expense View    [Issue #4642](https://github.com/semanticarts/dca/issues/4642) · [PR #4669](https://github.com/semanticarts/dca/pull/4669)
  - Combines out-of-pocket sales and marketing expenses from QuickBooks with labor costs and commissions
  - Displays total sales spend by pay period in a single view

• Add a company-wide earned revenue chart to accounting reports    [Issue #4643](https://github.com/semanticarts/dca/issues/4643) · [PR #4694](https://github.com/semanticarts/dca/pull/4694)
  - Displays actual and expected burn for the current year
  - Available from accounting reports for authorized users

• Implemented seamless coexistence of new and old commission structures  [Issue #4671](https://github.com/semanticarts/dca/issues/4671)
  - Developed a dual-computation engine to handle both current and legacy formulas
  - Configurable settings allow selection of applicable commission rules per pay period

• Updated PayStructure instance categories for hybrid and consultant roles  [Issue #4687](https://github.com/semanticarts/dca/issues/4687)
  - Added saox:_PayType_hybrid category to SAO ontology
  - Revised URI from saox:_PayType_Hybrid to align with standards

• Defaulted time field to PM for hours 1-5   [Issue #4705](https://github.com/semanticarts/dca/issues/4705) · [PR #4706](https://github.com/semanticarts/dca/pull/4706)
  - Applied to bare hours (`2`), partial times (`2:`), and short times (`2:30`)
  - Ignored leading and trailing spaces during interpretation
