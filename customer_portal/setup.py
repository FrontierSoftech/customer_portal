import frappe

def after_install():
    create_default_settings()
    create_quotation_approval_fields()
    create_milestone_hide_field()

def create_default_settings():
    if not frappe.db.exists("CP Portal Settings"):
        doc = frappe.new_doc("CP Portal Settings")
        doc.portal_title = "Customer Portal"
        doc.insert(ignore_permissions=True)

def create_quotation_approval_fields():
    fields = [
        {
            "fieldname": "customer_approval",
            "fieldtype": "Select",
            "label": "Customer Approval",
            "options": "\nPending\nApproved\nRejected",
            "insert_after": "status",
            "read_only": 1,
        },
        {
            "fieldname": "customer_approval_date",
            "fieldtype": "Datetime",
            "label": "Customer Approval Date",
            "insert_after": "customer_approval",
            "read_only": 1,
        },
        {
            "fieldname": "customer_approval_remarks",
            "fieldtype": "Small Text",
            "label": "Customer Approval Remarks",
            "insert_after": "customer_approval_date",
            "read_only": 1,
        },
    ]
    for f in fields:
        if not frappe.db.exists("Custom Field", {"dt": "Quotation", "fieldname": f["fieldname"]}):
            frappe.get_doc({"doctype": "Custom Field", "dt": "Quotation", **f}).insert(ignore_permissions=True)
    frappe.db.commit()


def create_milestone_hide_field():
    if not frappe.db.exists("Custom Field", {"dt": "Milestone", "fieldname": "custom_hide_from_customer"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Milestone",
            "fieldname": "custom_hide_from_customer",
            "fieldtype": "Check",
            "label": "Hide from Customer",
            "insert_after": "status",
            "default": "0",
        }).insert(ignore_permissions=True)
        frappe.db.commit()
