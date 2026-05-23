import frappe
from frappe import _


def has_app_permission():
    return True


_DOCTYPE_ICONS = {
    # Sales
    "Quotation":            "clipboard",
    "Sales Order":          "shopping-cart",
    "Sales Invoice":        "file-minus",
    "Delivery Note":        "truck",
    "Return":               "corner-down-left",
    # Purchase
    "Purchase Order":       "package",
    "Purchase Invoice":     "credit-card",
    "Purchase Receipt":     "download",
    "Material Request":     "shopping-bag",
    "Supplier Quotation":   "clipboard",
    # Payments
    "Payment Entry":        "dollar-sign",
    "Payment Request":      "send",
    "Journal Entry":        "book",
    # CRM
    "Lead":                 "user-plus",
    "Opportunity":          "target",
    "Customer":             "users",
    "Contact":              "user",
    "Supplier":             "briefcase",
    # Projects & Tasks
    "Project":              "folder",
    "Task":                 "check-square",
    "Milestone":            "flag",
    "Timesheet":            "clock",
    # Support
    "Issue":                "alert-circle",
    "Warranty Claim":       "shield",
    "Maintenance Schedule": "tool",
    "Maintenance Visit":    "tool",
    # HR
    "Expense Claim":        "file-minus",
    "Leave Application":    "calendar",
    "Job Application":      "user",
    "Appraisal":            "star",
    # Inventory
    "Item":                 "box",
    "Stock Entry":          "layers",
    "Batch":                "grid",
    # Documents
    "Contract":             "file",
    "Quality Inspection":   "check-circle",
}


@frappe.whitelist(allow_guest=False)
def get_portal_config():
    settings = frappe.get_single("CP Portal Settings")
    result = {
        "portal_title": settings.portal_title or "Customer Portal",
        "doctypes": []
    }
    for row in settings.doctypes:
        if row.doctype_name:
            result["doctypes"].append({
                "doctype_name": row.doctype_name,
                "label": row.doctype_name,
                "icon": _DOCTYPE_ICONS.get(row.doctype_name, "file-text"),
            })
    return result


@frappe.whitelist(allow_guest=False)
def get_list_fields(doctype_name):
    """Return filterable/sortable fields for a doctype (used by portal view controls)."""
    _assert_doctype_configured(doctype_name)
    meta = frappe.get_meta(doctype_name)

    ALLOWED_TYPES = {
        "Data", "Small Text", "Text", "Select", "Link", "Dynamic Link",
        "Int", "Float", "Currency", "Percent", "Date", "Datetime", "Check",
    }
    doc_fields = []
    for field in meta.fields:
        if field.fieldtype in ALLOWED_TYPES and field.label and field.fieldname:
            doc_fields.append({
                "label": field.label,
                "value": field.fieldname,
                "fieldtype": field.fieldtype,
                "options": field.options or "",
            })

    standard = [
        {"label": "ID", "value": "name", "fieldtype": "Data", "options": ""},
        {"label": "Created", "value": "creation", "fieldtype": "Datetime", "options": ""},
        {"label": "Modified", "value": "modified", "fieldtype": "Datetime", "options": ""},
        {"label": "Owner", "value": "owner", "fieldtype": "Data", "options": ""},
    ]
    return doc_fields + standard


@frappe.whitelist(allow_guest=False)
def get_records(doctype_name, page_length=20, start=0, search=None, status_filter=None,
                order_by="modified desc", field_filters=None, extra_fields=None):
    _assert_doctype_configured(doctype_name)
    user = frappe.session.user

    base_filters = _build_user_filter(doctype_name, user)
    if base_filters is None:
        return {"records": [], "title_field": "name", "status_field": "", "total_count": 0}

    title_field = _guess_title_field(doctype_name)
    status_field = _guess_status_field(doctype_name)

    fields = list({"name", "creation", "modified", title_field, status_field} - {""})
    fields = [f for f in fields if f and frappe.db.has_column(doctype_name, f)]

    # Add user-selected extra column fields
    if extra_fields:
        import json as _json2
        try:
            ef = _json2.loads(extra_fields) if isinstance(extra_fields, str) else extra_fields
            for f in (ef or []):
                if f and frappe.db.has_column(doctype_name, f) and f not in fields:
                    fields.append(f)
        except Exception:
            pass

    # Parse field_filters (from view-control Filter popover)
    parsed_field_filters = {}
    if field_filters:
        import json as _json
        try:
            parsed_field_filters = _json.loads(field_filters) if isinstance(field_filters, str) else field_filters
        except Exception:
            parsed_field_filters = {}

    # Merge field_filters into the fields to fetch
    for fname in parsed_field_filters:
        if frappe.db.has_column(doctype_name, fname) and fname not in fields:
            fields.append(fname)

    # Build search/status extra conditions and merge with base filter
    extra = []
    if search and title_field and frappe.db.has_column(doctype_name, title_field):
        extra.append([title_field, "like", f"%{search}%"])
    if status_filter and status_field and frappe.db.has_column(doctype_name, status_field):
        extra.append([status_field, "=", status_filter])

    # Apply field_filters
    for fname, condition in parsed_field_filters.items():
        if not frappe.db.has_column(doctype_name, fname):
            continue
        if isinstance(condition, list) and len(condition) == 2:
            extra.append([fname, condition[0], condition[1]])
        elif isinstance(condition, str):
            extra.append([fname, "=", condition])

    combined_filters = _merge_filters(base_filters, extra)

    try:
        records = frappe.get_list(
            doctype_name,
            filters=combined_filters,
            fields=fields,
            page_length=int(page_length),
            start=int(start),
            order_by=order_by,
            ignore_permissions=True,
        )
        total_count = frappe.db.count(doctype_name, filters=combined_filters)
    except Exception as e:
        frappe.log_error(f"Customer Portal get_records error: {e}")
        frappe.throw(_("Could not fetch records"))

    return {
        "records": records,
        "title_field": title_field,
        "status_field": status_field,
        "total_count": total_count,
    }


@frappe.whitelist(allow_guest=False)
def get_record(doctype_name, name):
    _assert_doctype_configured(doctype_name)
    user = frappe.session.user
    _assert_user_can_access(doctype_name, name, user)

    doc = frappe.get_doc(doctype_name, name)
    communications = frappe.get_all(
        "Communication",
        filters={
            "reference_doctype": doctype_name,
            "reference_name": name,
            "communication_type": "Communication",
        },
        fields=["name", "sender", "recipients", "subject", "content", "creation", "sent_or_received"],
        order_by="creation asc",
    )

    for comm in communications:
        comm["attachments"] = frappe.get_all(
            "File",
            filters={"attached_to_doctype": "Communication", "attached_to_name": comm["name"]},
            fields=["file_name", "file_url", "file_size"],
        )

    return {"doc": doc.as_dict(), "communications": communications}


@frappe.whitelist(allow_guest=False)
def send_reply(doctype_name, name, message, attachments=None):
    _assert_doctype_configured(doctype_name)
    user = frappe.session.user
    _assert_user_can_access(doctype_name, name, user)

    doc = frappe.get_doc(doctype_name, name)
    title_field = _guess_title_field(doctype_name)

    comm = frappe.new_doc("Communication")
    comm.communication_type = "Communication"
    comm.communication_medium = "Email"
    comm.sent_or_received = "Sent"
    comm.sender = user
    comm.subject = f"Re: {doc.get(title_field) or name}"
    comm.content = message
    comm.reference_doctype = doctype_name
    comm.reference_name = name
    comm.insert(ignore_permissions=True)

    # Link pre-uploaded files to this communication
    if attachments:
        import json
        file_urls = json.loads(attachments) if isinstance(attachments, str) else attachments
        for file_url in file_urls:
            file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
            if file_name:
                frappe.db.set_value(
                    "File", file_name,
                    {"attached_to_doctype": "Communication", "attached_to_name": comm.name},
                    update_modified=False,
                )

    return comm.name


def _get_default_print_format(doctype):
    """Return the default print format for a doctype (reads Property Setter, then DocType)."""
    pf = frappe.db.get_value(
        "Property Setter",
        {"doc_type": doctype, "property": "default_print_format"},
        "value",
    )
    if not pf:
        pf = frappe.db.get_value("DocType", doctype, "default_print_format")
    return pf or None


@frappe.whitelist(allow_guest=False)
def get_project_tasks(name):
    """Return tasks (with milestones) for a Project, filtering hidden records."""
    _assert_doctype_configured("Project")
    _assert_user_can_access("Project", name, frappe.session.user)

    tasks = frappe.get_all(
        "Task",
        filters=[
            ["project", "=", name],
            ["custom_hide_from_customer", "=", 0],
        ],
        fields=["name", "subject", "status", "progress", "exp_start_date", "exp_end_date", "is_milestone"],
        order_by="idx asc, creation asc",
        ignore_permissions=True,
    )

    for task in tasks:
        task["milestones"] = frappe.get_all(
            "Milestone",
            filters=[
                ["task", "=", task["name"]],
                ["custom_hide_from_customer", "=", 0],
            ],
            fields=["name", "subject", "status", "exp_end_date", "progress"],
            order_by="idx asc, creation asc",
            ignore_permissions=True,
        )

    return tasks


@frappe.whitelist(allow_guest=False)
def get_task_milestones(name):
    """Return milestones for a Task (via task field), filtering hidden records."""
    _assert_user_can_access("Task", name, frappe.session.user)

    return frappe.get_all(
        "Milestone",
        filters=[
            ["task", "=", name],
            ["custom_hide_from_customer", "=", 0],
        ],
        fields=["name", "subject", "status", "exp_end_date", "progress"],
        order_by="idx asc, creation asc",
        ignore_permissions=True,
    )


@frappe.whitelist(allow_guest=False)
def download_quotation_pdf(name):
    """Stream the Quotation as a PDF using the doctype's default print format."""
    _assert_doctype_configured("Quotation")
    _assert_user_can_access("Quotation", name, frappe.session.user)

    print_format = _get_default_print_format("Quotation")

    frappe.flags.ignore_print_permissions = True
    try:
        html = frappe.get_print("Quotation", name, print_format=print_format)
    finally:
        frappe.flags.ignore_print_permissions = False

    pdf_content = frappe.utils.pdf.get_pdf(
        html,
        options={"load-error-handling": "ignore"},
    )

    safe_name = name.replace("/", "-").replace(" ", "-")
    frappe.local.response.filename = f"{safe_name}.pdf"
    frappe.local.response.filecontent = pdf_content
    frappe.local.response.type = "pdf"


@frappe.whitelist(allow_guest=False)
def quotation_action(name, action, remarks=None):
    """Customer approves or rejects a Quotation. action must be 'Approved' or 'Rejected'."""
    if action not in ("Approved", "Rejected"):
        frappe.throw(_("Invalid action"))

    _assert_doctype_configured("Quotation")
    user = frappe.session.user
    _assert_user_can_access("Quotation", name, user)

    current = frappe.db.get_value("Quotation", name, ["customer_approval", "docstatus"], as_dict=True)
    if current.docstatus == 2:
        frappe.throw(_("Cannot act on a cancelled quotation"))
    if current.customer_approval in ("Approved", "Rejected"):
        frappe.throw(_(f"Quotation has already been {current.customer_approval.lower()}"))

    frappe.db.set_value(
        "Quotation", name,
        {
            "customer_approval": action,
            "customer_approval_date": frappe.utils.now(),
            "customer_approval_remarks": remarks or "",
        },
        update_modified=True,
    )
    frappe.db.commit()
    return action


# ── Internal helpers ──────────────────────────────────────────────────────────

def _assert_doctype_configured(doctype_name):
    settings = frappe.get_single("CP Portal Settings")
    names = [r.doctype_name for r in settings.doctypes]
    if doctype_name not in names:
        frappe.throw(_("Doctype not configured in portal"))


def _get_customer_for_user(user):
    """User → Customer resolution. Checks (in order):
    1. Customer portal_users child table (Portal User)
    2. Contact → Dynamic Link → Customer
    """
    # 1. Customer portal_users (Portal User child table on Customer doctype)
    customer = frappe.db.get_value(
        "Portal User",
        {"parenttype": "Customer", "user": user},
        "parent",
    )
    if customer:
        return customer

    # 2. All contacts with this email → Dynamic Link → Customer
    contacts = set()
    for name in frappe.get_all("Contact", filters={"email_id": user}, pluck="name"):
        contacts.add(name)
    for parent in frappe.get_all("Contact Email", filters={"email_id": user}, pluck="parent"):
        contacts.add(parent)

    for contact in contacts:
        customer = frappe.db.get_value(
            "Dynamic Link",
            {"parenttype": "Contact", "parent": contact, "link_doctype": "Customer"},
            "link_name",
        )
        if customer:
            return customer

    return None


def _merge_filters(base, extra):
    """Combine a base filter (dict or list) with extra list-format conditions."""
    if not extra:
        return base
    if isinstance(base, list):
        return base + extra
    # Convert dict to list format, then append extras
    result = [
        [k, "=", v] if not isinstance(v, (list, tuple)) else [k] + list(v)
        for k, v in base.items()
    ]
    return result + extra


def _build_user_filter(doctype_name, user):
    """
    Auto-detect the best filter for the doctype + user combination.
    Priority:
      1. Customer field (party_name / customer) — covers Project, Quotation, etc.
      2. Task  — traverse Project.customer chain
      3. Milestone — traverse Task → Project.customer chain
      4. Portal Users child table (field named 'users' with a 'user' column)
      5. Owner field
    Returns None to signal "no access / empty result".
    """
    # 1. Customer field — highest priority so records appear for every portal user
    #    of that customer regardless of per-record user assignments.
    customer = _get_customer_for_user(user)
    if customer:
        for fname in ("party_name", "customer"):
            if frappe.db.has_column(doctype_name, fname):
                return {fname: customer}

    # 2. Task — filter by customer's projects
    if doctype_name == "Task":
        if not customer:
            return None
        project_names = frappe.get_all(
            "Project",
            filters={"customer": customer},
            pluck="name",
            ignore_permissions=True,
        )
        if not project_names:
            return None
        return [
            ["project", "in", project_names],
            ["custom_hide_from_customer", "=", 0],
        ]

    # 3. Milestone — filter by customer's tasks (via projects)
    if doctype_name == "Milestone":
        if not customer:
            return None
        project_names = frappe.get_all(
            "Project",
            filters={"customer": customer},
            pluck="name",
            ignore_permissions=True,
        )
        if not project_names:
            return None
        task_names = frappe.get_all(
            "Task",
            filters=[
                ["project", "in", project_names],
                ["custom_hide_from_customer", "=", 0],
            ],
            pluck="name",
            ignore_permissions=True,
        )
        if not task_names:
            return None
        return [
            ["task", "in", task_names],
            ["custom_hide_from_customer", "=", 0],
        ]

    # 4. Portal Users child table (for non-customer doctypes that manage their
    #    own user access list via a 'users' table with a 'user' column)
    meta = frappe.get_meta(doctype_name)
    users_field = meta.get_field("users")
    if users_field and users_field.fieldtype == "Table":
        child_doctype = users_field.options
        child_meta = frappe.get_meta(child_doctype)
        user_col = next((f.fieldname for f in child_meta.fields if f.fieldname == "user"), None)
        if user_col:
            parent_names = frappe.get_all(
                child_doctype,
                filters={user_col: user, "parenttype": doctype_name},
                pluck="parent",
                ignore_permissions=True,
            )
            if parent_names:
                return {"name": ["in", parent_names]}

    # 5. Owner field
    return {"owner": user}


def _assert_user_can_access(doctype_name, name, user):
    """Raises PermissionError if the user cannot access the given record."""
    filters = _build_user_filter(doctype_name, user)
    if filters is None:
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    # Append name condition regardless of whether filters is a dict or list
    if isinstance(filters, list):
        check_filters = filters + [["name", "=", name]]
    else:
        check_filters = {**filters, "name": name}

    check = frappe.get_all(
        doctype_name,
        filters=check_filters,
        pluck="name",
        ignore_permissions=True,
        limit=1,
    )
    if not check:
        frappe.throw(_("Not permitted"), frappe.PermissionError)


def _guess_title_field(doctype_name):
    """Return the most likely human-readable title field for a doctype."""
    meta = frappe.get_meta(doctype_name)
    for fname in ("subject", "title", "project_name", "customer_name", "name"):
        if fname == "name" or meta.get_field(fname):
            return fname
    return "name"


def _guess_status_field(doctype_name):
    """Return the status field if it exists, else empty string."""
    meta = frappe.get_meta(doctype_name)
    return "status" if meta.get_field("status") else ""

