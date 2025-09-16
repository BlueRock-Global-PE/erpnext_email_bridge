# Configuration for Email Bridge App

app_name = "email_bridge"
app_title = "Email Bridge"
app_publisher = "Paragon Manufacturing"
app_description = "Microsoft 365 Email Integration via Middleware"
app_email = "admin@paragonmfgcorp.com"
app_license = "MIT"

# Apps
required_apps = ["frappe", "erpnext"]

# DocTypes to include in fixtures
fixtures = []

# Scheduled Tasks
scheduler_events = {
    "cron": {
        # Sync emails every 15 minutes during business hours (9 AM to 6 PM)
        "*/15 9-18 * * 1-5": [
            "email_bridge.scheduled_tasks.sync_all_configured_emails"
        ]
    },
    "hourly": [
        # Also run hourly as backup
        "email_bridge.scheduled_tasks.sync_all_configured_emails"  
    ]
}

# Override ERPNext's email functionality
app_include_js = [
    "/assets/email_bridge/js/email_bridge.js"
]

# Boot session
boot_session = "email_bridge.boot.boot_session"

# Document Events - Hook into ERPNext's email events
doc_events = {
    "Communication": {
        "before_insert": "email_bridge.email_handler.before_communication_insert",
        "after_insert": "email_bridge.email_handler.after_communication_insert"
    }
}

# Override settings
override_doctype_class = {
    "Email Account": "email_bridge.overrides.email_account.CustomEmailAccount"
}

# Website Route Rules (if needed for webhook endpoints)
website_route_rules = [
    {"from_route": "/api/email-bridge/<path:app_path>", "to_route": "email-bridge"},
]