import frappe

no_cache = 1


def get_context(context):
    frappe.db.commit()
    context.boot = get_boot()
    return context


def get_boot():
    return frappe._dict(
        {
            "site_name": frappe.local.site,
            "csrf_token": frappe.sessions.get_csrf_token(),
            "session_user": frappe.session.user,
            "full_name": frappe.db.get_value("User", frappe.session.user, "full_name") or "",
        }
    )
