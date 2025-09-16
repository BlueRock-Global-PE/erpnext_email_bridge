import frappe
from frappe.email.doctype.email_account.email_account import EmailAccount
from email_bridge.email_handler import MiddlewareEmailHandler

class CustomEmailAccount(EmailAccount):
    """Custom Email Account that uses our middleware for Microsoft 365"""
    
    def send(self, message):
        """Override send method to use middleware for Microsoft 365 accounts"""
        
        # Check if this is a Microsoft 365 account
        if self.is_microsoft_account():
            return self.send_via_middleware(message)
        else:
            # Fall back to default ERPNext behavior for other email providers
            return super().send(message)
    
    def is_microsoft_account(self):
        """Check if this is a Microsoft 365 account"""
        microsoft_indicators = ["office365", "microsoft", "outlook.office365.com", "smtp.office365.com"]
        
        smtp_server = getattr(self, 'smtp_server', '').lower()
        service = getattr(self, 'service', '').lower()
        
        return any(indicator in smtp_server or indicator in service for indicator in microsoft_indicators)
    
    def send_via_middleware(self, message):
        """Send email via our middleware"""
        try:
            handler = MiddlewareEmailHandler()
            
            # Extract email data from message object
            recipients = getattr(message, 'recipients', [])
            if not isinstance(recipients, list):
                recipients = [recipients] if recipients else []
            
            success, result = handler.send_email(
                sender_email=self.email_id,
                recipients=recipients,
                subject=getattr(message, 'subject', ''),
                message=getattr(message, 'message', ''),
                cc=getattr(message, 'cc', None),
                bcc=getattr(message, 'bcc', None)
            )
            
            if not success:
                frappe.throw(f"Failed to send email via middleware: {result}")
                
            return True
            
        except Exception as e:
            frappe.log_error(f"Middleware email sending failed: {str(e)}", "Email Bridge Error")
            frappe.throw(f"Email sending failed: {str(e)}")
            return False
    
    def receive(self, test_mails=None):
        """Override receive method to use middleware for Microsoft 365 accounts"""
        
        if self.is_microsoft_account() and self.enable_incoming:
            return self.receive_via_middleware()
        else:
            # Fall back to default ERPNext behavior
            return super().receive(test_mails)
    
    def receive_via_middleware(self):
        """Receive emails via our middleware"""
        try:
            handler = MiddlewareEmailHandler()
            
            success, result = handler.sync_inbound_emails(
                user_email=self.email_id,
                folder="inbox",
                limit=50,
                since_hours=24
            )
            
            if not success:
                frappe.log_error(f"Email sync failed: {result}", "Email Sync Error")
                
            return success
            
        except Exception as e:
            frappe.log_error(f"Email receiving failed: {str(e)}", "Email Bridge Error")
            return False