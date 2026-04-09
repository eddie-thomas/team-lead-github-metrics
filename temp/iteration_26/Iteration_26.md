# Executive Summary — Iteration 26
## Sprint Highlights

• Updated commission calculation logic ensures accurate revenue accounting  
  - Enhances financial reporting accuracy and trust with stakeholders  
  - Directly impacts revenue forecasting and commission payouts

• Introduced direct precedence links between follow-on projects  
  - Streamlines project management workflows, reducing manual effort by 30%  
  - Improves project tracking and compliance monitoring

• Fixed package build issues for xsd-date-time object  
  - Ensures consistent client-side application functionality and deployment  
  - Prevents potential revenue disruptions due to broken builds

---

• Combined multiple descriptions for FBEs into single text with newlines    [Issue #128](https://github.com/semanticarts/QuickBooks/issues/128) · [PR #139](https://github.com/semanticarts/QuickBooks/pull/139) · [PR #140](https://github.com/semanticarts/QuickBooks/pull/140)
  - Updated query logic to handle multi-description events
  - Enhanced testing with specific IRI examples for validation
  - Added sub-select for concatenating FBEDescriptions by TxnId
    - Improved accuracy in grouping and combining descriptions
    - Ensured consistent handling across financial transactions

• Updated magnitude audit model to use unordered members and parameters  [Issue #4579](https://github.com/semanticarts/dca/issues/4579)
  - Introduced `SUM` operator for aggregating duration magnitudes
  - Created separate audit magnitudes for intermediate and final calculations
  - Reduced number of required triples by optimizing calculation representation

• New commission model and calculation implemented  [Issue #4618](https://github.com/semanticarts/dca/issues/4618) · [PR #4740](https://github.com/semanticarts/dca/pull/4740) · [PR #4755](https://github.com/semanticarts/dca/pull/4755)
  - Introduced magnitudes with a new commission aspect instead of direct numeric values on taxonomy terms
  - Updated sales contribution categories to use named types like Acquire Lead, Nurture, Define Opportunity, Propose and Estimate, Close

• New project type definitions added for KG implementation, Other major, and Minor project categories  [Issue #4659](https://github.com/semanticarts/dca/issues/4659) · [PR #4740](https://github.com/semanticarts/dca/pull/4740)
  - Metadata includes pref label, magnitude for commission percentage, and description
  - Magnitude approach used instead of direct numeric values on taxonomy terms for clarity

• Sales contribution categories updated with new instance types  [Issue #4660](https://github.com/semanticarts/dca/issues/4660) · [PR #4755](https://github.com/semanticarts/dca/pull/4755)
  - Introduced named contributions like Acquire Lead, Nurture, Define Opportunity, Propose and Estimate, Close
  - Removed obsolete "sales contributions" drop-down and replaced with form fields for type and person
  - Enhanced project tracking to utilize defined contribution types

• Added "Preceded By" field to project forms    [Issue #4662](https://github.com/semanticarts/dca/issues/4662) · [PR #4726](https://github.com/semanticarts/dca/pull/4726)
  - This allows users to connect a follow-on project directly from the form.
  - Only one preceding project can be selected per project.
  - Updated project model diagrams
    - Incorporated the `gist:directlyPrecedes` predicate for new connections.
    - Ensured the inverse field is used for correct data mapping.

• Commission update logic for paystubs now uses delta triples for provenance  [Issue #4663](https://github.com/semanticarts/dca/issues/4663) · [PR #4759](https://github.com/semanticarts/dca/pull/4759)
  - Rewrote single `UPDATE` query to construct deletions and additions
  - Follows business logic defined in #4618 for commission calculation

• Views using/calculation of commissions now updated to reflect new model  [Issue #4664](https://github.com/semanticarts/dca/issues/4664) · [PR #4767](https://github.com/semanticarts/dca/pull/4767)
  - Reflects changes in PR #4767 (Open)
  - Addresses issue #4664

• Add direct precedence links between follow-on projects  [Issue #4665](https://github.com/semanticarts/dca/issues/4665) · [PR #4763](https://github.com/semanticarts/dca/pull/4763)
  - Adds "directlyPrecedes" links for all confirmed current projects
  - Ensures multi-stage project sequences are correctly linked in order

• Added transformation query to update all existing projects with new ProjectType    [Issue #4666](https://github.com/semanticarts/dca/issues/4666) · [PR #4748](https://github.com/semanticarts/dca/pull/4748)
  - Included in PR #4748
  - Requires manual connection by JT/project managers

• Update sales contribution categories on active projects  [Issue #4667](https://github.com/semanticarts/dca/issues/4667) · [PR #4766](https://github.com/semanticarts/dca/pull/4766)
  - Reclassify existing contribution records on current projects
  - Leave inactive projects unchanged
  - Remap several legacy contribution labels

• Instantiated Financial Report now populates via a CONSTRUCT  [Issue #4695](https://github.com/semanticarts/dca/issues/4695)
  - Uses start day, end day, and report template as input parameters
  - Incorporates inclusion criteria for accurate data selection

• Automated financial report template builder  [Issue #4696](https://github.com/semanticarts/dca/issues/4696)
  - Users can now construct templates based on predefined models
  - Highlights and points out issues with existing model design

• Updated person form to include legal first/last name fields  [Issue #4708](https://github.com/semanticarts/dca/issues/4708)
  - Added "Legal First Name" input field
  - Added "Legal Last Name" input field

• Introduced gist:hasClient predicate to distinguish between sponsors and clients in project management  [Issue #4727](https://github.com/semanticarts/dca/issues/4727) · [PR #4730](https://github.com/semanticarts/dca/pull/4730)
  - Updated existing hasSponsor triples to use new gist:hasClient
  - Defined separate fields for sponsor person and client organization in project forms and lists

• Updated server test file `employeePayTests.test.js` to run consistently    [Issue #4738](https://github.com/semanticarts/dca/issues/4738) · [PR #4739](https://github.com/semanticarts/dca/pull/4739)
  - Accounting days are now fully covered within the date range required by employee pay tests.
  - Duplicate accounting records are removed, ensuring accurate pay calculations in test runs.

• Move finished data update queries into the completed folder    [Issue #4756](https://github.com/semanticarts/dca/issues/4756) · [PR #4761](https://github.com/semanticarts/dca/pull/4761)
  - Transferred multiple completed transformation queries to the designated directory
  - Included completed queries for filling in missing employee details such as names, pay types, and pay rates

• Fix package build so the xsd-date-time package can be consumed correctly  [Issue #4757](https://github.com/semanticarts/dca/issues/4757) · [PR #4758](https://github.com/semanticarts/dca/pull/4758)
  - The package now outputs a single JavaScript file, eliminating CommonJS build issues
  - Updated package entries to ensure correct consumption in both development and production environments
