package smart_doc_bot.security

# Default deny
default allow = false

# Allow access if user has required permissions
allow {
    input.method == "GET"
    input.path = ["api", "v1", "health"]
}

allow {
    input.method == "POST"
    input.path = ["api", "v1", "auth", "login"]
}

allow {
    input.method == "POST"
    input.path = ["api", "v1", "auth", "register"]
}

# Document access policies
allow {
    input.method == "GET"
    input.path = ["api", "v1", "documents"]
    has_permission(input.user, "documents:read")
}

allow {
    input.method == "POST"
    input.path = ["api", "v1", "documents", "upload"]
    has_permission(input.user, "documents:create")
}

allow {
    input.method == "DELETE"
    input.path = ["api", "v1", "documents", "id"]
    has_permission(input.user, "documents:delete")
}

# Agent access policies
allow {
    input.method == "POST"
    input.path = ["api", "v1", "agents", "process"]
    has_permission(input.user, "agents:execute")
}

allow {
    input.method == "GET"
    input.path = ["api", "v1", "agents", "traces"]
    has_permission(input.user, "agents:read")
}

# Analytics access policies
allow {
    input.method == "GET"
    input.path = ["api", "v1", "analytics"]
    has_permission(input.user, "analytics:read")
}

# Admin access policies
allow {
    input.method == "GET"
    input.path = ["api", "v1", "admin"]
    is_admin(input.user)
}

# Helper functions
has_permission(user, permission) {
    user.roles[_] == "admin"
}

has_permission(user, permission) {
    user.permissions[_] == permission
}

has_permission(user, permission) {
    user.permissions[_] == "*"
}

is_admin(user) {
    user.roles[_] == "admin"
}

is_admin(user) {
    user.is_superuser == true
}
