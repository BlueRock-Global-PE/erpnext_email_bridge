// Email Bridge Frontend Integration

frappe.ready(function() {
    // Add custom email bridge functionality to the frontend if needed
    console.log("Email Bridge loaded");
});

// Function to test middleware connection
function test_middleware_connection() {
    frappe.call({
        method: "email_bridge.api.test_middleware_connection",
        callback: function(r) {
            if (r.message.success) {
                frappe.msgprint("Middleware connection successful!");
            } else {
                frappe.msgprint("Middleware connection failed: " + r.message.message, "Connection Error");
            }
        }
    });
}

// Function to manually sync emails
function sync_user_emails(user_email) {
    frappe.call({
        method: "email_bridge.api.sync_user_emails",
        args: {
            user_email: user_email,
            folder: "inbox", 
            limit: 50
        },
        callback: function(r) {
            if (r.message.success) {
                frappe.msgprint("Email sync completed successfully!");
            } else {
                frappe.msgprint("Email sync failed: " + r.message.message, "Sync Error");
            }
        }
    });
}