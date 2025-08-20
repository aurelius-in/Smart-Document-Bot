package smart_doc_bot.compliance

# GDPR Compliance Policies
gdpr_data_retention_allowed {
    input.data_type == "personal_data"
    input.retention_days <= 90
}

gdpr_data_processing_allowed {
    input.purpose == "legitimate_interest"
    input.consent_given == true
}

gdpr_data_transfer_allowed {
    input.destination == "EU"
}

gdpr_data_transfer_allowed {
    input.destination == "US"
    input.adequacy_decision == true
}

# HIPAA Compliance Policies
hipaa_phi_access_allowed {
    input.user_role == "healthcare_provider"
    input.purpose == "treatment"
}

hipaa_phi_access_allowed {
    input.user_role == "healthcare_provider"
    input.purpose == "payment"
}

hipaa_phi_access_allowed {
    input.user_role == "healthcare_provider"
    input.purpose == "healthcare_operations"
}

hipaa_audit_required {
    input.phi_accessed == true
}

# SOX Compliance Policies
sox_financial_data_access_allowed {
    input.user_role == "auditor"
    input.purpose == "financial_audit"
}

sox_financial_data_access_allowed {
    input.user_role == "finance_manager"
    input.purpose == "financial_reporting"
}

sox_audit_trail_required {
    input.financial_data_accessed == true
}

# Data Classification Policies
data_classification_required {
    input.data_type == "sensitive"
    input.classification_level != ""
}

data_encryption_required {
    input.data_type == "sensitive"
    input.encryption_enabled == true
}

# Access Control Policies
access_control_required {
    input.resource_type == "document"
    input.user_has_permission == true
}

access_control_required {
    input.resource_type == "document"
    input.user_owns_resource == true
}

# Audit Policies
audit_logging_required {
    input.action == "read"
    input.resource_type == "sensitive"
}

audit_logging_required {
    input.action == "write"
    input.resource_type == "sensitive"
}

audit_logging_required {
    input.action == "delete"
    input.resource_type == "sensitive"
}

# Default deny for sensitive operations
default sensitive_operation_allowed = false

sensitive_operation_allowed {
    input.operation == "data_export"
    input.user_role == "admin"
    input.audit_logged == true
}

sensitive_operation_allowed {
    input.operation == "data_deletion"
    input.user_role == "admin"
    input.confirmation_received == true
    input.audit_logged == true
}
