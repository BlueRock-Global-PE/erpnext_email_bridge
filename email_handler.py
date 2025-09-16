import frappe
import requests
import json
from frappe.email.doctype.email_account.email_account import EmailAccount
from frappe import _
import logging

logger = logging.getLogger(__name__)

class MiddlewareEmailHandler:
    """Handles email operations through our middleware API"""
    
    def __init__(self):
        self.middleware_url = frappe.get_site_config().get("middleware_url", "https://api.paragonmfgcorp.com")
        self.timeout = 30
    
    def send_email(self, sender_email, recipients, subject, message, cc=None, bcc=None, attachments=None):
        """Send email via middleware API"""
        try:
            # Prepare email data
            email_data = {
                "sender_email": sender_email,
                "to": [{"address": email, "name": email} for email in (recipients if isinstance(recipients, list) else [recipients])],
                "subject": subject,
                "body": message,
                "body_type": "HTML"
            }
            
            # Add CC if provided
            if cc:
                email_data["cc"] = [{"address": email, "name": email} for email in (cc if isinstance(cc, list) else [cc])]
            
            # Add BCC if provided  
            if bcc:
                email_data["bcc"] = [{"address": email, "name": email} for email in (bcc if isinstance(bcc, list) else [bcc])]
            
            # Add attachments if provided
            if attachments:
                email_data["attachments"] = attachments
            
            # Send to middleware
            response = requests.post(
                f"{self.middleware_url}/api/email/outbound",
                json=email_data,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Email sent successfully via middleware: {subject}")
                return True, result.get("message", "Email sent successfully")
            else:
                error_msg = f"Middleware error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Failed to send email via middleware: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def sync_inbound_emails(self, user_email, folder="inbox", limit=50, since_hours=24):
        """Sync inbound emails from middleware"""
        try:
            sync_data = {
                "user_email": user_email,
                "folder": folder,
                "limit": limit,
                "since_hours": since_hours
            }
            
            response = requests.post(
                f"{self.middleware_url}/api/email/inbound/sync",
                json=sync_data,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Email sync completed for {user_email}")
                return True, result.get("message", "Sync completed successfully")
            else:
                error_msg = f"Sync error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Failed to sync emails: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


def override_email_sending():
    """Override ERPNext's email sending mechanism"""
    
    # Monkey patch the send method of EmailAccount
    original_send = EmailAccount.send
    
    def custom_send(self, message):
        """Custom send method that uses our middleware"""
        try:
            handler = MiddlewareEmailHandler()
            
            # Extract recipients
            recipients = []
            if hasattr(message, 'recipients') and message.recipients:
                recipients = message.recipients
            elif hasattr(message, 'to') and message.to:
                recipients = message.to if isinstance(message.to, list) else [message.to]
            
            # Get sender email
            sender_email = getattr(message, 'sender', None) or self.email_id
            
            # Get CC recipients
            cc = getattr(message, 'cc', None)
            if cc:
                cc = cc if isinstance(cc, list) else [cc]
            
            # Get BCC recipients
            bcc = getattr(message, 'bcc', None) 
            if bcc:
                bcc = bcc if isinstance(bcc, list) else [bcc]
            
            # Send via middleware
            success, result = handler.send_email(
                sender_email=sender_email,
                recipients=recipients,
                subject=getattr(message, 'subject', ''),
                message=getattr(message, 'message', ''),
                cc=cc,
                bcc=bcc
            )
            
            if success:
                # Create Communication record in ERPNext
                create_outbound_communication(sender_email, recipients, message.subject, message.message, cc, bcc)
                return True
            else:
                frappe.throw(_(f"Failed to send email: {result}"))
                
        except Exception as e:
            frappe.log_error(f"Email sending failed: {str(e)}", "Email Bridge Error")
            frappe.throw(_(f"Email sending failed: {str(e)}"))
            return False
    
    # Apply the monkey patch
    EmailAccount.send = custom_send


def create_outbound_communication(sender, recipients, subject, message, cc=None, bcc=None):
    """Create a Communication record for outbound emails"""
    try:
        comm_doc = frappe.get_doc({
            "doctype": "Communication",
            "communication_type": "Communication", 
            "communication_medium": "Email",
            "sender": sender,
            "recipients": ", ".join(recipients) if isinstance(recipients, list) else recipients,
            "cc": ", ".join(cc) if cc else "",
            "bcc": ", ".join(bcc) if bcc else "",
            "subject": subject,
            "content": message,
            "sent_or_received": "Sent",
            "status": "Linked"
        })
        
        comm_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Failed to create communication record: {str(e)}", "Communication Error")


# Initialize the override when the module is imported
override_email_sending()