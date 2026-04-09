# Executive Summary — Iteration 25
## Sprint Highlights

• Introduced Total Sales Expense View, combining sales expenses and labor costs for accurate financial reporting  
  - Enables better tracking of sales-related expenditures and commission payments

• Defaulted time field entries between 1 and 5 to PM, improving data consistency in time recordings  
  - Ensures more reasonable default times without manual corrections

• Updated hybrid/consultant categories in PayStructure instance (model update)  
  - Standardized pay type classifications for clearer payroll management

---

• APR calculation logic updated for dynamic labor agreements  [Issue #4063](https://github.com/semanticarts/dca/issues/4063) · [PR #4127](https://github.com/semanticarts/dca/pull/4127) · [PR #4631](https://github.com/semanticarts/dca/pull/4631)
  - Introduced new LaborAgreementTerm subclass for ActualPayRate
  - Retroactively added paystub APRs to existing Labor Agreements
  - Automated creation of new temporal APR records during payroll runs

• Burnchart views now display updated names and descriptions  [Issue #4311](https://github.com/semanticarts/dca/issues/4311) · [PR #4651](https://github.com/semanticarts/dca/pull/4651)
  - "Burnchart Details" renamed to "Time Charge Details" with new description: "A detailed view of all time charges submitted by SA employees."
  - "Burnchart Hours Summary" renamed to "Hours by Week and Category" with new description: "Group the hours by week and category for better overview."

• Burn chart query now supports optional time card charging to projects  [Issue #4338](https://github.com/semanticarts/dca/issues/4338)
  - Updated `sa-view:_burn_chart` to include optional time card selection
  - Projects without time entries will still appear in burn charts

• New EER vs AER view with pay period breakdown sub-view added  [Issue #4443](https://github.com/semanticarts/dca/issues/4443) · [PR #4428](https://github.com/semanticarts/dca/pull/4428) · [PR #4648](https://github.com/semanticarts/dca/pull/4648) · [PR #4672](https://github.com/semanticarts/dca/pull/4672)
  - Closes #4309
  - Removed employee and task filters for broader data visibility
  - Updated EER vs AER view to include all active employees and tasks
    - PR #4672 (Merged): Eddie thomas/4443 4617 eer vs aer fixes
    - Excluded advisory work from earned revenue totals

• Addressed issues with duplicate predicates in ontology mappings  [Issue #4468](https://github.com/semanticarts/dca/issues/4468)
  - Identified 651 instances of overlapping properties across namespaces
  - Updated predicate resolution logic to ensure consistent handling

• Removed "Employee Directory" from HR launchpad  [Issue #4483](https://github.com/semanticarts/dca/issues/4483) · [PR #4650](https://github.com/semanticarts/dca/pull/4650)
  - This change removes an unnecessary entry to streamline the HR menu
  - Updated menu order places "Pay Period" and "Employee Table" at the top for easier access

• Keep timecard earned revenue in sync when task assignments change  [Issue #4554](https://github.com/semanticarts/dca/issues/4554) · [PR #4574](https://github.com/semanticarts/dca/pull/4574) · [PR #4629](https://github.com/semanticarts/dca/pull/4629)
  - Recalculates earned revenue based on the new task's billing rate and timecard duration
  - Ensures consistency in financial records by automatically updating revenue for affected timecards

• Split employee full name into first/last in payroll exports  [Issue #4557](https://github.com/semanticarts/dca/issues/4557) · [PR #63](https://github.com/semanticarts/gistProfSrv/pull/63) · [PR #4545](https://github.com/semanticarts/dca/pull/4545) · [PR #4644](https://github.com/semanticarts/dca/pull/4644) · [PR #4678](https://github.com/semanticarts/dca/pull/4678)
  - Payroll export now includes separate First Name and Last Name fields
  - Adjusted payroll view to display names using stored first and last name values
  - Enhanced pay structure setup for employees and contractors
    - Added Pay Structure section on employee and contractor forms
    - Payroll calculations now use the active pay structure for each person

• Added Pay Structure Assignment node to handle employee pay types    [Issue #4593](https://github.com/semanticarts/dca/issues/4593) · [PR #4678](https://github.com/semanticarts/dca/pull/4678)
  - Enhanced payroll view to use active pay structures
  - Updated forms to include pay type, start/end dates, and share percentage
  - Removed hardcoded values in payroll calculations
    - Utilized dynamic pay structures for accurate hybrid and consultant pay calculations

• Burn chart category field added to project form    [Issue #4615](https://github.com/semanticarts/dca/issues/4615)
  - Enables automatic inclusion of projects in burn charts
  - Reduces manual effort required for query updates

• All active employees are now included in the Employee Earned Revenue (EER) vs Actual Earned Revenue (AER) report    [Issue #4617](https://github.com/semanticarts/dca/issues/4617) · [PR #4648](https://github.com/semanticarts/dca/pull/4648)
  - Removed filters for specific employee roles and tasks
  - Simplifies query logic for more comprehensive reporting

• Balance sheet queries now accurately calculate net income for a specified year  [Issue #4632](https://github.com/semanticarts/dca/issues/4632) · [PR #137](https://github.com/semanticarts/QuickBooks/pull/137) · [PR #4654](https://github.com/semanticarts/dca/pull/4654)
  - Updated calculation logic to reflect year-specific data
  - Redesigned views to display net income correctly

• Regenerated chart of accounts based on new QuickBooks export  [Issue #4633](https://github.com/semanticarts/dca/issues/4633) · [PR #138](https://github.com/semanticarts/QuickBooks/pull/138) · [PR #4654](https://github.com/semanticarts/dca/pull/4654)
  - Retrieved latest export from JT or Amanda
  - Updated chart of accounts triples in the QuickBooks repo
  - Correctly calculating net income in balance sheet queries
    - Fixed view to display only relevant net income accounts
    - Eliminated display of legacy accounts contributing to net income

• Burn charts now use accounting-day dates and sort correctly  [Issue #4635](https://github.com/semanticarts/dca/issues/4635) · [PR #4677](https://github.com/semanticarts/dca/pull/4677)
  - Burn chart lines now use accounting-day dates instead of calendar timestamps
  - Actual, expected, projected, and total budget lines build week-by-week values from accounting-day sequences through the project end date

• Reevaluate 2024 and 2025 QB data in AGraph after pipeline updates    [Issue #4636](https://github.com/semanticarts/dca/issues/4636)
  - Issues #4633 and #4632 have been addressed
  - Results to be compared with P&L and balance sheet PDFs for accuracy

• Introduced `TimeAllocation` labor agreement term with weekly hour magnitude    [Issue #4638](https://github.com/semanticarts/dca/issues/4638) · [PR #4674](https://github.com/semanticarts/dca/pull/4674)
  - Updated position form to include weekly expected hours
  - Defaulted both expected and chargeable hours on new positions
  - Enhanced consultant utilization and capacity calculations
    - Incorporated `TimeAllocation` into calculation logic
    - Ensured part-time employees like Phil are accurately accounted for

• User request progress notification emails for Rebecca and JT    [Issue #4641](https://github.com/semanticarts/dca/issues/4641)
  - Sent near the end of each sprint
  - Includes current status and outstanding issues

• Add Total Sales Expense View    [Issue #4642](https://github.com/semanticarts/dca/issues/4642) · [PR #4669](https://github.com/semanticarts/dca/pull/4669)
  - Combines out-of-pocket sales and marketing expenses from QuickBooks with actual labor costs from sales projects
  - Includes commissions earned during the pay period

• Add a company-wide earned revenue chart to accounting reports  [Issue #4643](https://github.com/semanticarts/dca/issues/4643) · [PR #4694](https://github.com/semanticarts/dca/pull/4694)
  - Shows both actual burn and expected burn for the current year
  - Available from accounting reports, accessible by authorized users

• Commission calculation method for past pay periods remains unchanged  [Issue #4671](https://github.com/semanticarts/dca/issues/4671)
  - Historical commission data will be preserved without modification
  - New and old commission structures coexist without interference

• Updated hybrid/consultant categories in PayStructure instance (model update)  [Issue #4687](https://github.com/semanticarts/dca/issues/4687)
  - Added PayStructure type to SAO ontology
  - Migrated taxonomy categories from `saox:_PayType_Hybrid` to `saox:_PayType_hybrid`
  - Created new category for consulting pay types

• Defaulted time field entries between 1 and 5 to PM  [Issue #4705](https://github.com/semanticarts/dca/issues/4705) · [PR #4706](https://github.com/semanticarts/dca/pull/4706)
  - Applied to bare hours, partial times, and short times like `2`, `2:3`
  - Ignored leading and trailing spaces in time interpretation
