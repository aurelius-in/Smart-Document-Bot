-- AI Document Agent Database Initialization Script
-- This script creates the database schema and initial data

-- Create database if it doesn't exist
-- Note: This should be run as a superuser or database owner
-- CREATE DATABASE ai_document_agent;

-- Connect to the database
-- \c ai_document_agent;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create custom types
CREATE TYPE document_status AS ENUM ('pending', 'processing', 'completed', 'failed');
CREATE TYPE agent_type AS ENUM ('orchestrator', 'ingestion', 'classifier', 'entity', 'risk', 'qa', 'compare', 'audit', 'summarizer', 'translator', 'sentiment');
CREATE TYPE severity_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE user_role AS ENUM ('user', 'manager', 'admin');

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    role user_role DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create user_roles junction table
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    content TEXT,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    doc_type VARCHAR(50),
    domain VARCHAR(100),
    processing_status document_status DEFAULT 'pending',
    processing_result JSONB,
    confidence_score FLOAT,
    risk_score FLOAT,
    metadata JSONB,
    tags JSONB,
    entities JSONB,
    clauses JSONB,
    risks JSONB,
    qa_pairs JSONB,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INTEGER REFERENCES users(id) NOT NULL
);

-- Create tags table
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create document_tags junction table
CREATE TABLE IF NOT EXISTS document_tags (
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (document_id, tag_id)
);

-- Create compliance_frameworks table
CREATE TABLE IF NOT EXISTS compliance_frameworks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    version VARCHAR(20),
    requirements JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create document_compliance_frameworks junction table
CREATE TABLE IF NOT EXISTS document_compliance_frameworks (
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    framework_id INTEGER REFERENCES compliance_frameworks(id) ON DELETE CASCADE,
    PRIMARY KEY (document_id, framework_id)
);

-- Create processing_history table
CREATE TABLE IF NOT EXISTS processing_history (
    id SERIAL PRIMARY KEY,
    processing_id VARCHAR(100) UNIQUE NOT NULL,
    workflow_id VARCHAR(100),
    current_stage VARCHAR(100),
    completed_stages JSONB,
    failed_stages JSONB,
    total_execution_time FLOAT,
    progress_percentage FLOAT DEFAULT 0.0,
    status document_status DEFAULT 'pending',
    result JSONB,
    confidence FLOAT,
    rationale TEXT,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    document_id INTEGER REFERENCES documents(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL
);

-- Create agent_executions table
CREATE TABLE IF NOT EXISTS agent_executions (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    agent_type agent_type NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    input_size INTEGER,
    output_size INTEGER,
    execution_time FLOAT,
    memory_usage FLOAT,
    cpu_usage FLOAT,
    status document_status DEFAULT 'pending',
    confidence FLOAT,
    output JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_history_id INTEGER REFERENCES processing_history(id) NOT NULL
);

-- Create document_comparisons table
CREATE TABLE IF NOT EXISTS document_comparisons (
    id SERIAL PRIMARY KEY,
    comparison_id VARCHAR(100) UNIQUE NOT NULL,
    comparison_type VARCHAR(50) NOT NULL,
    similarity_score FLOAT,
    differences JSONB,
    risk_changes JSONB,
    status document_status DEFAULT 'pending',
    result JSONB,
    confidence FLOAT,
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    document_a_id INTEGER REFERENCES documents(id) NOT NULL,
    document_b_id INTEGER REFERENCES documents(id) NOT NULL,
    created_by INTEGER REFERENCES users(id) NOT NULL
);

-- Create audit_events table
CREATE TABLE IF NOT EXISTS audit_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100) UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL,
    severity severity_level DEFAULT 'low',
    description TEXT NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    document_id INTEGER REFERENCES documents(id)
);

-- Create system_metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_id VARCHAR(100) UNIQUE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    labels JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    unit VARCHAR(20)
);

-- Create workflow_templates table
CREATE TABLE IF NOT EXISTS workflow_templates (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    stages JSONB NOT NULL,
    agent_config JSONB,
    workflow_config JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) NOT NULL
);

-- Create knowledge_base table
CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    kb_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    domain VARCHAR(100),
    content TEXT NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    vector_embedding vector(1536), -- OpenAI embedding dimension
    source VARCHAR(255),
    version VARCHAR(20) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) NOT NULL
);

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    notification_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal',
    is_read BOOLEAN DEFAULT false,
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    document_id INTEGER REFERENCES documents(id)
);

-- Create api_logs table
CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    method VARCHAR(10) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time FLOAT,
    request_size INTEGER,
    response_size INTEGER,
    ip_address INET,
    user_agent TEXT,
    request_headers JSONB,
    request_body TEXT,
    response_body TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id)
);

-- Create system_configurations table
CREATE TABLE IF NOT EXISTS system_configurations (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by ON documents(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at ON documents(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_processing_history_document_id ON processing_history(document_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_processing_history_id ON agent_executions(processing_history_id);
CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp ON audit_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_events_user_id ON audit_events(user_id);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_vector ON knowledge_base USING ivfflat (vector_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_api_logs_timestamp ON api_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint);

-- Insert default roles
INSERT INTO roles (name, description, permissions) VALUES
('admin', 'Administrator with full access', '["*"]'),
('manager', 'Manager with limited admin access', '["read", "write", "analyze", "audit"]'),
('user', 'Regular user with basic access', '["read", "write", "analyze"]')
ON CONFLICT (name) DO NOTHING;

-- Insert default admin user (password: admin123)
INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser, role) VALUES
('admin@example.com', crypt('admin123', gen_salt('bf')), 'System Administrator', true, true, 'admin')
ON CONFLICT (email) DO NOTHING;

-- Insert default compliance frameworks
INSERT INTO compliance_frameworks (name, description, version) VALUES
('GDPR', 'General Data Protection Regulation', '2018'),
('HIPAA', 'Health Insurance Portability and Accountability Act', '1996'),
('SOX', 'Sarbanes-Oxley Act', '2002'),
('PCI-DSS', 'Payment Card Industry Data Security Standard', '4.0')
ON CONFLICT (name) DO NOTHING;

-- Insert default tags
INSERT INTO tags (name, description, color) VALUES
('contract', 'Legal contracts', '#2196F3'),
('invoice', 'Financial invoices', '#4CAF50'),
('policy', 'Company policies', '#FF9800'),
('report', 'Business reports', '#9C27B0'),
('compliance', 'Compliance documents', '#F44336')
ON CONFLICT (name) DO NOTHING;

-- Insert default system configurations
INSERT INTO system_configurations (config_key, config_value, config_type, description) VALUES
('max_file_size', '52428800', 'integer', 'Maximum file upload size in bytes'),
('allowed_file_types', '["pdf", "docx", "txt", "csv", "xlsx"]', 'json', 'Allowed file types for upload'),
('agent_timeout', '300', 'integer', 'Agent execution timeout in seconds'),
('confidence_threshold', '0.7', 'float', 'Minimum confidence threshold for agent results'),
('audit_retention_days', '90', 'integer', 'Number of days to retain audit logs'),
('enable_monitoring', 'true', 'boolean', 'Enable system monitoring'),
('enable_pii_redaction', 'true', 'boolean', 'Enable PII redaction in logs')
ON CONFLICT (config_key) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_templates_updated_at BEFORE UPDATE ON workflow_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_configurations_updated_at BEFORE UPDATE ON system_configurations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions to application user (adjust username as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_document_agent_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_document_agent_user;

-- Create view for document summary
CREATE OR REPLACE VIEW document_summary AS
SELECT 
    d.id,
    d.filename,
    d.doc_type,
    d.processing_status,
    d.confidence_score,
    d.risk_score,
    d.uploaded_at,
    u.full_name as uploaded_by_name,
    COUNT(DISTINCT dt.tag_id) as tag_count,
    COUNT(DISTINCT dcf.framework_id) as compliance_framework_count
FROM documents d
LEFT JOIN users u ON d.uploaded_by = u.id
LEFT JOIN document_tags dt ON d.id = dt.document_id
LEFT JOIN document_compliance_frameworks dcf ON d.id = dcf.document_id
GROUP BY d.id, d.filename, d.doc_type, d.processing_status, d.confidence_score, d.risk_score, d.uploaded_at, u.full_name;

-- Create view for system health
CREATE OR REPLACE VIEW system_health AS
SELECT 
    'documents' as component,
    COUNT(*) as total_count,
    COUNT(CASE WHEN processing_status = 'completed' THEN 1 END) as completed_count,
    COUNT(CASE WHEN processing_status = 'failed' THEN 1 END) as failed_count,
    AVG(confidence_score) as avg_confidence
FROM documents
UNION ALL
SELECT 
    'users' as component,
    COUNT(*) as total_count,
    COUNT(CASE WHEN is_active = true THEN 1 END) as completed_count,
    COUNT(CASE WHEN is_active = false THEN 1 END) as failed_count,
    NULL as avg_confidence
FROM users;

-- Create function to clean old audit logs
CREATE OR REPLACE FUNCTION clean_old_audit_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
    retention_days INTEGER;
BEGIN
    -- Get retention period from configuration
    SELECT config_value::INTEGER INTO retention_days 
    FROM system_configurations 
    WHERE config_key = 'audit_retention_days';
    
    -- Default to 90 days if not configured
    IF retention_days IS NULL THEN
        retention_days := 90;
    END IF;
    
    -- Delete old audit logs
    DELETE FROM audit_events 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 day' * retention_days;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get document statistics
CREATE OR REPLACE FUNCTION get_document_statistics(
    start_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP - INTERVAL '30 days',
    end_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
)
RETURNS TABLE (
    total_documents BIGINT,
    completed_documents BIGINT,
    failed_documents BIGINT,
    avg_processing_time FLOAT,
    avg_confidence_score FLOAT,
    total_file_size BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_documents,
        COUNT(CASE WHEN d.processing_status = 'completed' THEN 1 END)::BIGINT as completed_documents,
        COUNT(CASE WHEN d.processing_status = 'failed' THEN 1 END)::BIGINT as failed_documents,
        AVG(ph.total_execution_time) as avg_processing_time,
        AVG(d.confidence_score) as avg_confidence_score,
        SUM(d.file_size)::BIGINT as total_file_size
    FROM documents d
    LEFT JOIN processing_history ph ON d.id = ph.document_id
    WHERE d.uploaded_at BETWEEN start_date AND end_date;
END;
$$ LANGUAGE plpgsql;

-- Create function to search documents by content similarity
CREATE OR REPLACE FUNCTION search_documents_by_similarity(
    search_text TEXT,
    similarity_threshold FLOAT DEFAULT 0.8,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    document_id INTEGER,
    filename VARCHAR(255),
    similarity_score FLOAT,
    content_preview TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id as document_id,
        d.filename,
        d.confidence_score as similarity_score,
        LEFT(d.content, 200) as content_preview
    FROM documents d
    WHERE d.processing_status = 'completed'
    AND d.content ILIKE '%' || search_text || '%'
    ORDER BY d.confidence_score DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get agent performance metrics
CREATE OR REPLACE FUNCTION get_agent_performance_metrics(
    start_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP - INTERVAL '7 days',
    end_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
)
RETURNS TABLE (
    agent_type TEXT,
    total_executions BIGINT,
    successful_executions BIGINT,
    avg_execution_time FLOAT,
    avg_confidence FLOAT,
    avg_memory_usage FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ae.agent_type::TEXT,
        COUNT(*)::BIGINT as total_executions,
        COUNT(CASE WHEN ae.status = 'completed' THEN 1 END)::BIGINT as successful_executions,
        AVG(ae.execution_time) as avg_execution_time,
        AVG(ae.confidence) as avg_confidence,
        AVG(ae.memory_usage) as avg_memory_usage
    FROM agent_executions ae
    WHERE ae.started_at BETWEEN start_date AND end_date
    GROUP BY ae.agent_type
    ORDER BY total_executions DESC;
END;
$$ LANGUAGE plpgsql;

-- Create indexes for the new functions
CREATE INDEX IF NOT EXISTS idx_documents_content_gin ON documents USING gin(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_agent_executions_started_at ON agent_executions(started_at);
CREATE INDEX IF NOT EXISTS idx_processing_history_started_at ON processing_history(started_at);

-- Insert sample workflow template
INSERT INTO workflow_templates (template_id, name, description, stages, agent_config, created_by) VALUES
('default-workflow', 'Default Document Processing Workflow', 'Standard workflow for processing documents', 
'[
    {"name": "ingestion", "agent": "ingestion", "order": 1, "required": true},
    {"name": "classification", "agent": "classifier", "order": 2, "required": true},
    {"name": "entity_extraction", "agent": "entity", "order": 3, "required": true},
    {"name": "risk_assessment", "agent": "risk", "order": 4, "required": true},
    {"name": "summarization", "agent": "summarizer", "order": 5, "required": false},
    {"name": "audit_logging", "agent": "audit", "order": 6, "required": true}
]',
'{
    "ingestion": {"timeout": 60, "max_retries": 3},
    "classifier": {"timeout": 30, "max_retries": 2},
    "entity": {"timeout": 45, "max_retries": 2},
    "risk": {"timeout": 60, "max_retries": 3},
    "summarizer": {"timeout": 90, "max_retries": 2},
    "audit": {"timeout": 10, "max_retries": 1}
}',
(SELECT id FROM users WHERE email = 'admin@example.com' LIMIT 1))
ON CONFLICT (template_id) DO NOTHING;

-- Create a function to automatically assign tags based on content
CREATE OR REPLACE FUNCTION auto_assign_tags(document_id INTEGER)
RETURNS VOID AS $$
DECLARE
    doc_content TEXT;
    tag_id INTEGER;
BEGIN
    -- Get document content
    SELECT content INTO doc_content FROM documents WHERE id = document_id;
    
    IF doc_content IS NULL THEN
        RETURN;
    END IF;
    
    -- Auto-assign tags based on content
    IF doc_content ILIKE '%contract%' OR doc_content ILIKE '%agreement%' THEN
        SELECT id INTO tag_id FROM tags WHERE name = 'contract';
        IF tag_id IS NOT NULL THEN
            INSERT INTO document_tags (document_id, tag_id) VALUES (document_id, tag_id) ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    IF doc_content ILIKE '%invoice%' OR doc_content ILIKE '%bill%' OR doc_content ILIKE '%payment%' THEN
        SELECT id INTO tag_id FROM tags WHERE name = 'invoice';
        IF tag_id IS NOT NULL THEN
            INSERT INTO document_tags (document_id, tag_id) VALUES (document_id, tag_id) ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    IF doc_content ILIKE '%policy%' OR doc_content ILIKE '%procedure%' OR doc_content ILIKE '%guideline%' THEN
        SELECT id INTO tag_id FROM tags WHERE name = 'policy';
        IF tag_id IS NOT NULL THEN
            INSERT INTO document_tags (document_id, tag_id) VALUES (document_id, tag_id) ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    IF doc_content ILIKE '%report%' OR doc_content ILIKE '%analysis%' OR doc_content ILIKE '%summary%' THEN
        SELECT id INTO tag_id FROM tags WHERE name = 'report';
        IF tag_id IS NOT NULL THEN
            INSERT INTO document_tags (document_id, tag_id) VALUES (document_id, tag_id) ON CONFLICT DO NOTHING;
        END IF;
    END IF;
    
    IF doc_content ILIKE '%gdpr%' OR doc_content ILIKE '%hipaa%' OR doc_content ILIKE '%sox%' OR doc_content ILIKE '%compliance%' THEN
        SELECT id INTO tag_id FROM tags WHERE name = 'compliance';
        IF tag_id IS NOT NULL THEN
            INSERT INTO document_tags (document_id, tag_id) VALUES (document_id, tag_id) ON CONFLICT DO NOTHING;
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-assign tags when document is processed
CREATE OR REPLACE FUNCTION trigger_auto_assign_tags()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.processing_status = 'completed' AND OLD.processing_status != 'completed' THEN
        PERFORM auto_assign_tags(NEW.id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_assign_tags_trigger
    AFTER UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION trigger_auto_assign_tags();

-- Final cleanup and optimization
VACUUM ANALYZE;

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully!';
    RAISE NOTICE 'Default admin user: admin@example.com / admin123';
    RAISE NOTICE 'Default roles, compliance frameworks, and tags have been created.';
END $$;
