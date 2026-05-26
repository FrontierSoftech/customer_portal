app_name = "customer_portal"
app_title = "Customer Portal"
app_publisher = "Frontiers of Technology"
app_description = "Configurable Customer Portal for Frappe"
app_email = "dev@frontiersoftech.com"
app_license = "MIT"

add_to_apps_screen = [
    {
        "name": "customer_portal",
        "logo": "/assets/customer_portal/dashboard/favicon.svg",
        "title": "Customer Portal",
        "route": "/portal",
        "has_permission": "customer_portal.api.portal.has_app_permission",
    }
]

website_route_rules = [
    {
        "from_route": "/dashboard/<path:app_path>",
        "to_route": "dashboard",
    },
    {
        "from_route": "/portal/<path:app_path>",
        "to_route": "portal",
    },
]

after_install = "customer_portal.setup.after_install"
