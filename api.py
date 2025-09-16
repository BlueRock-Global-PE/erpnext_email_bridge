import frappe
from frappe import _
from email_bridge.email_handler import MiddlewareEmailHandler
from email_bridge.scheduled_tasks import manual_email_sync

@frappe.whitelist()
def test_middleware_connection():
    """Test connection to middleware API"""
    try:
        handler = MiddlewareEmailHandler()
        
        # Test a simple connection
        import requests
        response = requests.get(f"{handler.middleware_url}/api/email/status", timeout=10)
        
        if response.status_code == 200:
            return {"success": True, "message": "Middleware connection successful", "data": response.json()}
        else:
            return {"success": False, "message": f"Middleware returned status {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "message": f"Connection failed: {str(e)}"}


@frappe.whitelist()
def sync_user_emails(user_email, folder="inbox", limit=50):
    """Manually sync emails for a specific user"""
    try:
        manual_email_sync(user_email, folder, int(limit))
        return {"success": True, "message": f"Email sync initiated for {user_email}"}
        
    except Exception as e:
        frappe.log_error(f"Manual email sync failed: {str(e)}", "Email Sync API Error")
        return {"success": False, "message": f"Sync failed: {str(e)}"}


@frappe.whitelist()
def send_test_email(to_email, subject="Test Email from ERPNext", message="This is a test email sent through the email bridge."):
    """Send a test email through the middleware"""
    try:
        handler = MiddlewareEmailHandler()
        
        # Get current user's email as sender
        sender_email = frappe.session.user
        if sender_email == "Administrator":
            sender_email = frappe.get_value("Email Account", {"default_outgoing": 1}, "email_id")
            if not sender_email:
                sender_email = "noreply@paragonmfgcorp.com"  # fallback
        
        success, result = handler.send_email(
            sender_email=sender_email,
            recipients=[to_email],
            subject=subject,
            message=message
        )
        
        if success:
            return {"success": True, "message": "Test email sent successfully"}
        else:
            return {"success": False, "message": f"Failed to send test email: {result}"}
            
    except Exception as e:
        frappe.log_error(f"Test email failed: {str(e)}", "Test Email Error")
        return {"success": False, "message": f"Test email failed: {str(e)}"}