import frappe
from email_bridge.email_handler import MiddlewareEmailHandler

def sync_all_configured_emails():
    """Scheduled task to sync emails from all configured email accounts"""
    
    # Get all configured email accounts that should sync
    email_accounts = frappe.get_all("Email Account", 
        filters={"enable_incoming": 1, "use_imap": 1},
        fields=["name", "email_id", "service"]
    )
    
    handler = MiddlewareEmailHandler()
    
    for account in email_accounts:
        try:
            # Only sync Microsoft 365 accounts through our middleware
            if "office365" in account.get("service", "").lower() or "microsoft" in account.get("service", "").lower():
                success, message = handler.sync_inbound_emails(
                    user_email=account.email_id,
                    folder="inbox",
                    limit=20,  # Sync last 20 emails
                    since_hours=2  # Only emails from last 2 hours
                )
                
                if success:
                    frappe.logger().info(f"Successfully synced emails for {account.email_id}")
                else:
                    frappe.logger().error(f"Failed to sync emails for {account.email_id}: {message}")
                    
        except Exception as e:
            frappe.log_error(f"Email sync error for {account.email_id}: {str(e)}", "Email Sync Error")


def manual_email_sync(user_email, folder="inbox", limit=50):
    """Manually trigger email sync for a specific user"""
    
    handler = MiddlewareEmailHandler()
    
    try:
        success, message = handler.sync_inbound_emails(user_email, folder, limit, since_hours=24)
        
        if success:
            frappe.msgprint(f"Email sync completed successfully for {user_email}")
        else:
            frappe.throw(f"Email sync failed: {message}")
            
    except Exception as e:
        frappe.throw(f"Email sync error: {str(e)}")