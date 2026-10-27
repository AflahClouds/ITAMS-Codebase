# Data Model: Standards Remediation

No new table or destructive data migration.

- Category.category_name, Brand.brand_name, Vendor.name, PurchaseMode.purchase_mode: nonblank normalized name; trim and collapse whitespace, compare case-insensitively, preserve display casing. Existing PK/reference identity remains stable.
- Model: existing nullable Brand FK remains for historical readability. New supported creation requires one valid Brand; explicit null/clear is rejected on supported writes. Existing legacy rows remain readable and can receive an explicit valid Brand. Identity is Brand plus normalized model_name; exclude self during updates. No Category relation is introduced.
- AuditLog: existing actor, username, action, module, date, old/new minimized values and source-IP projection. Add access records for direct audit reads, conflict-rejection records, and inherited Setting mutation records. Never store Setting values or returned AuditLog payloads. No recursive read logging.
- Setting: existing key/value storage and Admin-only mutations. Mutation and required audit share one transaction; failed audit leaves the previous record intact.
- PDF/Excel exports: transient representations only. All user strings stay literal. Existing numbers, booleans, date/datetime values and nulls remain typed in Excel. Existing authorized record scope and ordering remain intact.

Asset status, condition, Custodian, Procurement links and custody history do not change in this feature.
