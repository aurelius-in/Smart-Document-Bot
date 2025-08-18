// Sample data for the Smart Document Bot showpiece

export interface SampleDocument {
  id: string;
  name: string;
  type: string;
  scenario: string;
  content: string;
  entities: Array<{
    id: string;
    text: string;
    type: 'PERSON' | 'ORGANIZATION' | 'LOCATION' | 'MONEY' | 'DATE' | 'CONTRACT_TERM' | 'RISK_FACTOR' | 'COMPLIANCE_ITEM';
    start: number;
    end: number;
    confidence: number;
    metadata?: Record<string, any>;
  }>;
  highlights: string[];
  metadata: {
    uploadDate: string;
    fileSize: string;
    pages: number;
    language: string;
    riskLevel: 'low' | 'medium' | 'high';
    complianceScore: number;
  };
}

export interface SampleScenario {
  id: string;
  name: string;
  description: string;
  icon: string;
  documents: string[];
  policies: string[];
  sampleQuestions: string[];
}

export interface SamplePolicy {
  id: string;
  name: string;
  description: string;
  icon: string;
  regulations: string[];
  requirements: string[];
  riskFactors: string[];
}

export const sampleDocuments: SampleDocument[] = [
  {
    id: 'finance-agreement-1',
    name: 'Financial Services Agreement - ACME Corp',
    type: 'Financial Agreement',
    scenario: 'finance',
    content: `FINANCIAL SERVICES AGREEMENT

This Financial Services Agreement (the "Agreement") is entered into as of January 15, 2024 (the "Effective Date") by and between:

ACME Financial Services, Inc., a Delaware corporation with its principal place of business at 123 Wall Street, New York, NY 10001 ("Provider")

and

Global Investment Partners, LLC, a New York limited liability company with its principal place of business at 456 Park Avenue, New York, NY 10022 ("Client")

1. SERVICES
Provider shall provide comprehensive financial advisory services including portfolio management, risk assessment, and compliance monitoring.

2. TERM
This Agreement shall commence on the Effective Date and continue for a period of three (3) years unless terminated earlier in accordance with Section 8.

3. COMPENSATION
Client shall pay Provider a monthly fee of $25,000 for services rendered, payable within 30 days of invoice.

4. CONFIDENTIALITY
Both parties agree to maintain strict confidentiality of all proprietary information shared during the term of this Agreement.

5. COMPLIANCE
Provider shall comply with all applicable SEC regulations, including but not limited to the Investment Advisers Act of 1940.

6. RISK MANAGEMENT
Provider shall implement comprehensive risk management procedures and provide monthly risk assessment reports.

7. DATA PROTECTION
All client data shall be protected in accordance with applicable data protection laws and industry best practices.

8. TERMINATION
Either party may terminate this Agreement with thirty (30) days written notice to the other party.

9. LIABILITY
Provider's liability shall be limited to the amount of fees paid by Client in the twelve months preceding any claim.

10. GOVERNING LAW
This Agreement shall be governed by the laws of the State of New York.`,
    entities: [
      { id: '1', text: 'ACME Financial Services, Inc.', type: 'ORGANIZATION', start: 150, end: 180, confidence: 0.95 },
      { id: '2', text: 'Global Investment Partners, LLC', type: 'ORGANIZATION', start: 200, end: 235, confidence: 0.93 },
      { id: '3', text: 'January 15, 2024', type: 'DATE', start: 80, end: 95, confidence: 0.98 },
      { id: '4', text: '$25,000', type: 'MONEY', start: 450, end: 458, confidence: 0.96 },
      { id: '5', text: 'three (3) years', type: 'CONTRACT_TERM', start: 380, end: 395, confidence: 0.89 },
      { id: '6', text: 'thirty (30) days', type: 'CONTRACT_TERM', start: 750, end: 765, confidence: 0.91 },
      { id: '7', text: 'SEC regulations', type: 'COMPLIANCE_ITEM', start: 520, end: 535, confidence: 0.87 },
      { id: '8', text: 'Investment Advisers Act of 1940', type: 'COMPLIANCE_ITEM', start: 540, end: 570, confidence: 0.92 }
    ],
    highlights: ['1', '2', '4', '7', '8'],
    metadata: {
      uploadDate: '2024-01-15T10:30:00Z',
      fileSize: '2.3 MB',
      pages: 3,
      language: 'English',
      riskLevel: 'medium',
      complianceScore: 87
    }
  },
  {
    id: 'healthcare-hipaa-1',
    name: 'Patient Data Processing Agreement - MedTech Solutions',
    type: 'Healthcare Agreement',
    scenario: 'healthcare',
    content: `PATIENT DATA PROCESSING AGREEMENT

This Patient Data Processing Agreement (the "Agreement") is entered into as of March 1, 2024 (the "Effective Date") by and between:

MedTech Solutions, Inc., a California corporation with its principal place of business at 789 Healthcare Blvd, San Francisco, CA 94102 ("Processor")

and

City General Hospital, a non-profit healthcare organization with its principal place of business at 321 Medical Center Dr, San Francisco, CA 94103 ("Controller")

1. PURPOSE
Processor shall process patient health information on behalf of Controller in accordance with HIPAA regulations and this Agreement.

2. DEFINITIONS
"Protected Health Information" or "PHI" shall have the meaning set forth in 45 CFR §160.103.

3. OBLIGATIONS OF PROCESSOR
Processor shall:
a) Use and disclose PHI only as permitted by this Agreement
b) Implement appropriate safeguards to protect PHI
c) Report any security incidents within 24 hours
d) Ensure workforce members receive HIPAA training

4. SECURITY MEASURES
Processor shall implement administrative, physical, and technical safeguards that meet or exceed HIPAA Security Rule requirements.

5. BREACH NOTIFICATION
Processor shall notify Controller of any breach of unsecured PHI within 60 days of discovery.

6. TERM AND TERMINATION
This Agreement shall remain in effect until terminated by either party with 30 days written notice.

7. RETURN OR DESTRUCTION OF PHI
Upon termination, Processor shall return or destroy all PHI and retain no copies.

8. COMPLIANCE WITH LAWS
Both parties shall comply with all applicable federal and state laws, including HIPAA and HITECH Act.`,
    entities: [
      { id: '1', text: 'MedTech Solutions, Inc.', type: 'ORGANIZATION', start: 120, end: 145, confidence: 0.94 },
      { id: '2', text: 'City General Hospital', type: 'ORGANIZATION', start: 170, end: 190, confidence: 0.96 },
      { id: '3', text: 'March 1, 2024', type: 'DATE', start: 80, end: 92, confidence: 0.97 },
      { id: '4', text: 'HIPAA regulations', type: 'COMPLIANCE_ITEM', start: 280, end: 295, confidence: 0.93 },
      { id: '5', text: 'Protected Health Information', type: 'COMPLIANCE_ITEM', start: 320, end: 345, confidence: 0.91 },
      { id: '6', text: '24 hours', type: 'CONTRACT_TERM', start: 480, end: 490, confidence: 0.88 },
      { id: '7', text: '60 days', type: 'CONTRACT_TERM', start: 650, end: 658, confidence: 0.89 },
      { id: '8', text: '30 days', type: 'CONTRACT_TERM', start: 720, end: 728, confidence: 0.90 }
    ],
    highlights: ['1', '2', '4', '5', '7'],
    metadata: {
      uploadDate: '2024-03-01T14:15:00Z',
      fileSize: '1.8 MB',
      pages: 2,
      language: 'English',
      riskLevel: 'high',
      complianceScore: 94
    }
  },
  {
    id: 'insurance-policy-1',
    name: 'Cyber Liability Insurance Policy - TechStart Inc',
    type: 'Insurance Policy',
    scenario: 'insurance',
    content: `CYBER LIABILITY INSURANCE POLICY

Policy Number: CL-2024-001
Effective Date: February 15, 2024
Insured: TechStart Inc.
Address: 555 Innovation Way, Austin, TX 78701

COVERAGE SUMMARY
This policy provides coverage for cyber liability risks including:
- Data breach response costs
- Business interruption losses
- Cyber extortion payments
- Regulatory fines and penalties

LIMITS OF LIABILITY
- Per occurrence: $2,000,000
- Aggregate limit: $5,000,000
- Deductible: $25,000 per claim

COVERED PERILS
1. Data Breach Response
   - Forensic investigation costs
   - Legal expenses
   - Notification costs
   - Credit monitoring services

2. Business Interruption
   - Lost income due to cyber attack
   - Extra expenses to restore operations
   - Contingent business interruption

3. Cyber Extortion
   - Ransomware payments
   - Extortion demands
   - Negotiation costs

4. Regulatory Actions
   - Fines and penalties
   - Defense costs
   - Settlement payments

EXCLUSIONS
- Acts of war or terrorism
- Intentional acts by insured
- Prior known circumstances
- Bodily injury or property damage

DUTIES IN THE EVENT OF A CLAIM
1. Immediate notification to insurer
2. Preservation of evidence
3. Cooperation with investigation
4. No admission of liability

TERM
This policy is effective for one year from the effective date unless cancelled.`,
    entities: [
      { id: '1', text: 'TechStart Inc.', type: 'ORGANIZATION', start: 120, end: 132, confidence: 0.95 },
      { id: '2', text: 'February 15, 2024', type: 'DATE', start: 80, end: 95, confidence: 0.98 },
      { id: '3', text: '$2,000,000', type: 'MONEY', start: 280, end: 291, confidence: 0.96 },
      { id: '4', text: '$5,000,000', type: 'MONEY', start: 295, end: 306, confidence: 0.96 },
      { id: '5', text: '$25,000', type: 'MONEY', start: 310, end: 317, confidence: 0.94 },
      { id: '6', text: 'one year', type: 'CONTRACT_TERM', start: 850, end: 858, confidence: 0.92 },
      { id: '7', text: 'Data breach response costs', type: 'RISK_FACTOR', start: 200, end: 225, confidence: 0.89 },
      { id: '8', text: 'Ransomware payments', type: 'RISK_FACTOR', start: 450, end: 468, confidence: 0.87 }
    ],
    highlights: ['1', '3', '4', '7', '8'],
    metadata: {
      uploadDate: '2024-02-15T09:45:00Z',
      fileSize: '3.1 MB',
      pages: 4,
      language: 'English',
      riskLevel: 'medium',
      complianceScore: 82
    }
  },
  {
    id: 'legal-contract-1',
    name: 'Software Licensing Agreement - Enterprise Corp',
    type: 'Legal Contract',
    scenario: 'legal',
    content: `SOFTWARE LICENSING AGREEMENT

This Software Licensing Agreement (the "Agreement") is entered into as of April 10, 2024 (the "Effective Date") by and between:

Enterprise Software Solutions, Inc., a Delaware corporation ("Licensor")

and

Global Manufacturing Corp, a New Jersey corporation ("Licensee")

1. GRANT OF LICENSE
Licensor grants Licensee a non-exclusive, non-transferable license to use the Software for internal business purposes.

2. LICENSE FEES
Licensee shall pay Licensor an annual license fee of $150,000, payable in quarterly installments of $37,500.

3. TERM
This Agreement shall commence on the Effective Date and continue for a period of five (5) years, unless terminated earlier.

4. INTELLECTUAL PROPERTY
All intellectual property rights in the Software remain with Licensor. Licensee shall not reverse engineer or modify the Software.

5. CONFIDENTIALITY
Both parties shall maintain the confidentiality of proprietary information exchanged under this Agreement.

6. WARRANTY
Licensor warrants that the Software will perform substantially in accordance with the documentation for 90 days from delivery.

7. LIMITATION OF LIABILITY
Licensor's liability shall be limited to the amount of license fees paid by Licensee in the 12 months preceding any claim.

8. TERMINATION
Either party may terminate this Agreement with 60 days written notice for material breach.

9. GOVERNING LAW
This Agreement shall be governed by the laws of the State of Delaware.

10. DISPUTE RESOLUTION
Any disputes shall be resolved through binding arbitration in accordance with AAA rules.`,
    entities: [
      { id: '1', text: 'Enterprise Software Solutions, Inc.', type: 'ORGANIZATION', start: 120, end: 155, confidence: 0.94 },
      { id: '2', text: 'Global Manufacturing Corp', type: 'ORGANIZATION', start: 170, end: 195, confidence: 0.93 },
      { id: '3', text: 'April 10, 2024', type: 'DATE', start: 80, end: 92, confidence: 0.97 },
      { id: '4', text: '$150,000', type: 'MONEY', start: 280, end: 288, confidence: 0.95 },
      { id: '5', text: '$37,500', type: 'MONEY', start: 295, end: 302, confidence: 0.94 },
      { id: '6', text: 'five (5) years', type: 'CONTRACT_TERM', start: 380, end: 392, confidence: 0.91 },
      { id: '7', text: '90 days', type: 'CONTRACT_TERM', start: 580, end: 587, confidence: 0.89 },
      { id: '8', text: '60 days', type: 'CONTRACT_TERM', start: 750, end: 757, confidence: 0.90 }
    ],
    highlights: ['1', '2', '4', '5', '6'],
    metadata: {
      uploadDate: '2024-04-10T11:20:00Z',
      fileSize: '2.7 MB',
      pages: 3,
      language: 'English',
      riskLevel: 'low',
      complianceScore: 91
    }
  }
];

export const sampleScenarios: SampleScenario[] = [
  {
    id: 'finance',
    name: 'Finance & Banking',
    description: 'SEC regulations, banking compliance, financial reporting',
    icon: '🏦',
    documents: ['finance-agreement-1'],
    policies: ['sec', 'sox', 'generic'],
    sampleQuestions: [
      'What are the key financial terms in this agreement?',
      'What SEC compliance requirements are mentioned?',
      'What are the termination conditions?',
      'What is the compensation structure?',
      'What risk management procedures are outlined?'
    ]
  },
  {
    id: 'healthcare',
    name: 'Healthcare',
    description: 'HIPAA compliance, medical records, patient privacy',
    icon: '🏥',
    documents: ['healthcare-hipaa-1'],
    policies: ['hipaa', 'generic'],
    sampleQuestions: [
      'What HIPAA requirements are specified?',
      'How is patient data protected?',
      'What are the breach notification procedures?',
      'What security measures are required?',
      'What are the data retention requirements?'
    ]
  },
  {
    id: 'insurance',
    name: 'Insurance',
    description: 'Policy compliance, claims processing, regulatory reporting',
    icon: '🛡️',
    documents: ['insurance-policy-1'],
    policies: ['generic'],
    sampleQuestions: [
      'What are the coverage limits?',
      'What cyber risks are covered?',
      'What are the claim notification requirements?',
      'What exclusions apply?',
      'What are the policy terms?'
    ]
  },
  {
    id: 'legal',
    name: 'Legal & Compliance',
    description: 'Contract analysis, legal compliance, regulatory frameworks',
    icon: '⚖️',
    documents: ['legal-contract-1'],
    policies: ['generic'],
    sampleQuestions: [
      'What are the license terms?',
      'What are the payment obligations?',
      'What intellectual property rights are defined?',
      'What are the termination conditions?',
      'What dispute resolution procedures apply?'
    ]
  }
];

export const samplePolicies: SamplePolicy[] = [
  {
    id: 'generic',
    name: 'Generic Compliance',
    description: 'General regulatory compliance framework',
    icon: '📋',
    regulations: ['General Business Law', 'Contract Law', 'Data Protection'],
    requirements: [
      'Document retention policies',
      'Data security measures',
      'Regular compliance audits',
      'Employee training programs'
    ],
    riskFactors: [
      'Contractual non-compliance',
      'Data security breaches',
      'Regulatory violations',
      'Operational risks'
    ]
  },
  {
    id: 'hipaa',
    name: 'HIPAA',
    description: 'Healthcare privacy and security standards',
    icon: '🏥',
    regulations: ['HIPAA Privacy Rule', 'HIPAA Security Rule', 'HITECH Act'],
    requirements: [
      'Patient data encryption',
      'Access controls and authentication',
      'Breach notification procedures',
      'Workforce training on HIPAA',
      'Business associate agreements'
    ],
    riskFactors: [
      'Unauthorized PHI access',
      'Data breach incidents',
      'Non-compliance with security standards',
      'Failure to report breaches'
    ]
  },
  {
    id: 'sec',
    name: 'SEC Regulations',
    description: 'Securities and Exchange Commission compliance',
    icon: '📊',
    regulations: ['Investment Advisers Act', 'Securities Act', 'Exchange Act'],
    requirements: [
      'Fiduciary duty compliance',
      'Disclosure requirements',
      'Record keeping standards',
      'Anti-fraud provisions',
      'Registration requirements'
    ],
    riskFactors: [
      'Investment fraud',
      'Inadequate disclosures',
      'Conflicts of interest',
      'Regulatory enforcement actions'
    ]
  },
  {
    id: 'gdpr',
    name: 'GDPR',
    description: 'General Data Protection Regulation',
    icon: '🌍',
    regulations: ['GDPR', 'Data Protection Act'],
    requirements: [
      'Data subject rights',
      'Consent management',
      'Data minimization',
      'Privacy by design',
      'Breach notification within 72 hours'
    ],
    riskFactors: [
      'Data subject complaints',
      'Regulatory fines up to 4% of global revenue',
      'Data processing violations',
      'Cross-border data transfers'
    ]
  },
  {
    id: 'sox',
    name: 'SOX',
    description: 'Sarbanes-Oxley Act compliance',
    icon: '📈',
    regulations: ['Sarbanes-Oxley Act', 'PCAOB Standards'],
    requirements: [
      'Internal control over financial reporting',
      'CEO/CFO certifications',
      'Audit committee independence',
      'Whistleblower protection',
      'Document retention policies'
    ],
    riskFactors: [
      'Financial reporting errors',
      'Internal control weaknesses',
      'Audit failures',
      'Executive liability'
    ]
  }
];

export const sampleQAPairs = [
  {
    question: "What are the key financial terms in this agreement?",
    answer: "The key financial terms include a monthly fee of $25,000 for services, payable within 30 days of invoice. The agreement has a three-year term with early termination options.",
    citations: ['finance-agreement-1'],
    confidence: 0.94,
    agent: 'qa'
  },
  {
    question: "What HIPAA requirements are specified?",
    answer: "The agreement specifies HIPAA compliance requirements including appropriate safeguards for PHI, 24-hour security incident reporting, workforce HIPAA training, and breach notification within 60 days.",
    citations: ['healthcare-hipaa-1'],
    confidence: 0.91,
    agent: 'qa'
  },
  {
    question: "What are the coverage limits for cyber liability?",
    answer: "The cyber liability policy provides $2,000,000 per occurrence and $5,000,000 aggregate limit, with a $25,000 deductible per claim.",
    citations: ['insurance-policy-1'],
    confidence: 0.96,
    agent: 'qa'
  },
  {
    question: "What are the license fees and payment terms?",
    answer: "The annual license fee is $150,000, payable in quarterly installments of $37,500. The agreement has a five-year term.",
    citations: ['legal-contract-1'],
    confidence: 0.93,
    agent: 'qa'
  }
];

export const demoMetrics = {
  documentsProcessed: 1247,
  avgProcessingTime: 2.3,
  accuracyRate: 94.2,
  policyViolations: 23,
  humanOverrides: 8,
  systemUptime: 99.8,
  agentPerformance: {
    classifier: 96,
    entity: 94,
    risk: 89,
    qa: 92,
    compare: 91,
    audit: 95,
    summarizer: 93,
    translator: 88,
    sentiment: 90
  },
  complianceRates: {
    hipaa: 98.5,
    gdpr: 97.2,
    sox: 96.8,
    sec: 95.4,
    'pci-dss': 99.1,
    'iso-27001': 94.7
  }
};

export const getDocumentById = (id: string): SampleDocument | undefined => {
  return sampleDocuments.find(doc => doc.id === id);
};

export const getScenarioById = (id: string): SampleScenario | undefined => {
  return sampleScenarios.find(scenario => scenario.id === id);
};

export const getPolicyById = (id: string): SamplePolicy | undefined => {
  return samplePolicies.find(policy => policy.id === id);
};
