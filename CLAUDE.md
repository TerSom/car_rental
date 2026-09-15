# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment & Configuration

- Python virtual environment: `venvodoo18/` (Python 3.12)
- Configuration file: `odoo.conf` (port `8018`, DB user `odoo18`, addons: `addons,custom_addons`)

## Common Commands

### Running Odoo Server
- Start server: `./venvodoo18/bin/python odoo-bin -c odoo.conf`
- Start server with auto-reload: `./venvodoo18/bin/python odoo-bin -c odoo.conf --dev=reload`
- Install module into database: `./venvodoo18/bin/python odoo-bin -c odoo.conf -d <dbname> -i <module_name>`
- Update module in database: `./venvodoo18/bin/python odoo-bin -c odoo.conf -d <dbname> -u <module_name>`
- Update module and stop: `./venvodoo18/bin/python odoo-bin -c odoo.conf -d <dbname> -u <module_name> --stop-after-init`

### Testing
- Run all tests for module: `./venvodoo18/bin/python odoo-bin -c odoo.conf -d <dbname> --test-enable --stop-after-init -u <module_name>`
- Run tests by module tag: `./venvodoo18/bin/python odoo-bin -c odoo.conf -d <dbname> --test-enable --stop-after-init --test-tags /<module_name>`
- Run specific test class or method: `./venvodoo18/bin/python odoo-bin -c odoo.conf -d <dbname> --test-enable --stop-after-init --test-tags .<test_class>:<test_method>`

### Linting
- Configured via `ruff.toml` (Python 3.10+ target):
  - Lint check: `./venvodoo18/bin/ruff check .` or `ruff check custom_addons/<module_name>`
  - Lint fix: `./venvodoo18/bin/ruff check --fix .`

### Utilities & Scaffolding
- Scaffold new custom module: `./venvodoo18/bin/python odoo-bin scaffold <module_name> custom_addons/`
- Interactive Odoo shell: `./venvodoo18/bin/python odoo-bin shell -c odoo.conf -d <dbname>`

## Architecture

- **Core (`odoo/`)**: Core ERP framework, ORM engine, HTTP server, RPC layers.
- **Official Addons (`addons/`)**: Standard upstream Odoo modules.
- **Custom Addons (`custom_addons/`)**: Workspace custom modules (e.g. `car_rental`). All custom business code resides here.
- **Module Structure**:
  - `__manifest__.py`: Module metadata, dependencies (`depends`), view/data loading sequence (`data`).
  - `models/`: Python ORM models (`models.Model`), constraints, compute methods.
  - `views/`: XML action, menu, form, and tree/list definitions.
  - `security/`: Model access rules (`ir.model.access.csv`) and record rules.
  - `controllers/`: HTTP controllers and routing endpoints.

## Git Commit Conventions
- Do NOT add `Co-Authored-By: Claude` trailer or "Generated with Claude Code" footer to commit messages.
- Commit messages should be authored as if written by Terry directly — no AI attribution.
- Follow Odoo's official commit message structure: `[TAG] car_rental: short description (<50 chars)`
- Tags (pick the one that matches the change):
  - `[FIX]` bug fix
  - `[ADD]` adding new module/feature
  - `[IMP]` incremental improvement (most common during dev)
  - `[REF]` heavy refactor/rewrite
  - `[REM]` removing dead code, views, or files
  - `[MOV]` moving files (use `git mv`, keep content unchanged)
  - `[REV]` reverting a previous commit
- Keep the short description imperative and under 50 chars, e.g.:
  - `[ADD] car_rental: scaffold vehicle and rental order models`
  - `[FIX] car_rental: correct xpath for invoice button`
  - `[IMP] car_rental: add availability check on rental confirm`
- For non-trivial changes, add a body explaining WHY the change was made, not just WHAT changed.

## Code Style & File Naming (Odoo official convention)
- One file per main model group. File name matches the model name (dots → underscores).
  - Model `car.rental.vehicle` → `models/car_rental_vehicle.py`
  - Model `car.rental.order` → `models/car_rental_order.py`
  - If a file defines multiple models tied to one main model (e.g. an order + its lines), keep them in the same file named after the main model.
- Same pattern for views: `views/car_rental_vehicle_views.xml`, `views/car_rental_order_views.xml`.
- Security file stays `security/ir.model.access.csv` (+ `security/car_rental_security.xml` for record rules/groups if needed).
- XML record IDs: `<model_name>_<suffix>`, e.g. `car_rental_vehicle_view_form`, `car_rental_order_action`, `car_rental_menu_root`.
- Don't restructure/reformat existing files just to apply these rules — only apply to new files or code actually being modified (avoids noisy diffs).