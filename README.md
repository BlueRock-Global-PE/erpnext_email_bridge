# ERPNext Email Bridge

Microsoft 365 Email Integration via Middleware for ERPNext

## Description

This custom ERPNext app integrates Microsoft 365 email services through a middleware API, bypassing SMTP port restrictions while maintaining full ERPNext email functionality.

## Features

- Routes Microsoft 365 emails through Graph API via middleware
- Preserves ERPNext's email UI and CRM integration  
- Automatic email linking to Contacts and Customers
- Scheduled background email synchronization
- Fallback to standard ERPNext email for non-Microsoft accounts

## Installation

1. Add this app to your ERPNext instance:
```bash
bench get-app https://github.com/BlueRock-Global-PE/erpnext_email_bridge.git
bench --site [site-name] install-app erpnext_email_bridge
```

2. Configure your middleware URL in site config:
```bash
bench --site [site-name] set-config middleware_url "https://api.paragonmfgcorp.com"
```

3. Migrate your site:
```bash
bench --site [site-name] migrate
```

## Requirements

- ERPNext v14+ or v15+
- Python 3.10+
- Middleware API with Microsoft Graph integration
- Microsoft 365 with proper Azure app registration

## Configuration

The app automatically detects Microsoft 365 email accounts and routes them through your middleware. Configure your email accounts normally in ERPNext - the app handles the routing transparently.

## API Endpoints

The app provides several API endpoints for testing and manual operations:

- `email_bridge.api.test_middleware_connection` - Test middleware connectivity
- `email_bridge.api.sync_user_emails` - Manually sync emails for a user
- `email_bridge.api.send_test_email` - Send a test email

## License

MIT License

## Support

For issues and support, please contact BlueRock Global PE or create an issue on GitHub.
