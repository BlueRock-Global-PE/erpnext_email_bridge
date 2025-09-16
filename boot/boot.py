import frappe

def boot_session(bootinfo):
    """Add email bridge configuration to boot session"""
    
    bootinfo.email_bridge = {
        "middleware_url": frappe.get_site_config().get("middleware_url", "https://api.paragonmfgcorp.com"),
        "enabled": True
    }