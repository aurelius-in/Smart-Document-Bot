// Sample data for the AI Document Agent showpiece

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
    name: 'Financial Advisory Services Agreement - Global Financial Services',
    type: 'Financial Agreement',
    scenario: 'finance',
    content: `FINANCIAL ADVISORY SERVICES AGREEMENT

Agreement No: FSA-2024-0015
Effective Date: January 15, 2024
Document Version: 2.1

This Financial Advisory Services Agreement (the "Agreement") is entered into as of January 15, 2024 (the "Effective Date") by and between:

Global Financial Services, Inc., a Delaware corporation with its principal place of business at 123 Wall Street, Suite 1500, New York, NY 10001 ("Provider" or "Advisor")

and

Global Investment Partners, LLC, a New York limited liability company with its principal place of business at 456 Park Avenue, 25th Floor, New York, NY 10022 ("Client" or "Investor")

WHEREAS, Client desires to engage Provider to provide comprehensive financial advisory and investment management services; and

WHEREAS, Provider is registered as an investment adviser with the Securities and Exchange Commission and is qualified to provide such services;

NOW, THEREFORE, in consideration of the mutual promises and covenants contained herein, the parties agree as follows:

ARTICLE I - SERVICES AND SCOPE

1.1 Advisory Services. Provider shall provide the following financial advisory services to Client:
   (a) Portfolio management and asset allocation strategies
   (b) Investment research and analysis
   (c) Risk assessment and management
   (d) Compliance monitoring and regulatory reporting
   (e) Quarterly performance reviews and reporting
   (f) Tax-efficient investment planning

1.2 Investment Authority. Client hereby grants Provider discretionary authority to manage Client's investment portfolio in accordance with the investment objectives and risk parameters established in Schedule A hereto.

ARTICLE II - TERM AND TERMINATION

2.1 Term. This Agreement shall commence on the Effective Date and continue for a period of three (3) years, unless terminated earlier in accordance with the provisions of this Article II.

2.2 Termination by Either Party. Either party may terminate this Agreement upon thirty (30) days written notice to the other party.

2.3 Effect of Termination. Upon termination, Provider shall:
   (a) Provide a final accounting of all transactions
   (b) Transfer all client assets to Client or Client's designated custodian
   (c) Return all client records and documents

ARTICLE III - COMPENSATION AND FEES

3.1 Advisory Fees. Client shall pay Provider an annual advisory fee of $300,000, payable in monthly installments of $25,000, due within thirty (30) days of invoice.

3.2 Fee Calculation. Advisory fees are calculated based on the market value of assets under management as of the last business day of each month.

3.3 Additional Services. Any additional services not covered by this Agreement shall be billed at Provider's standard hourly rates.

ARTICLE IV - CONFIDENTIALITY AND PRIVACY

4.1 Confidential Information. Both parties acknowledge that they may have access to confidential and proprietary information of the other party and agree to maintain strict confidentiality of such information.

4.2 Privacy Protection. Provider shall comply with all applicable privacy laws, including but not limited to the Gramm-Leach-Bliley Act and Regulation S-P.

4.3 Data Security. Provider shall implement and maintain appropriate technical and organizational measures to protect client data against unauthorized access, alteration, disclosure, or destruction.

ARTICLE V - COMPLIANCE AND REGULATORY MATTERS

5.1 Regulatory Compliance. Provider represents and warrants that it is registered as an investment adviser with the Securities and Exchange Commission under the Investment Advisers Act of 1940.

5.2 Fiduciary Duty. Provider acknowledges its fiduciary duty to act in the best interests of Client and to provide investment advice that is suitable for Client's investment objectives and risk tolerance.

5.3 Code of Ethics. Provider shall maintain and enforce a code of ethics that addresses conflicts of interest and personal trading by advisory personnel.

ARTICLE VI - RISK MANAGEMENT

6.1 Risk Assessment. Provider shall conduct ongoing risk assessments of Client's portfolio and provide monthly risk management reports.

6.2 Investment Guidelines. All investments shall be made in accordance with the investment guidelines set forth in Schedule B hereto.

6.3 Diversification. Provider shall maintain appropriate portfolio diversification to manage investment risk.

ARTICLE VII - REPORTS AND COMMUNICATIONS

7.1 Quarterly Reports. Provider shall provide quarterly performance reports including:
   (a) Portfolio performance analysis
   (b) Asset allocation review
   (c) Risk metrics and analysis
   (d) Market commentary and outlook

7.2 Annual Review. Provider shall conduct an annual comprehensive review of Client's investment objectives and portfolio strategy.

ARTICLE VIII - LIMITATION OF LIABILITY

8.1 Standard of Care. Provider shall exercise the care, skill, prudence, and diligence under the circumstances then prevailing that a prudent person acting in a like capacity and familiar with such matters would use.

8.2 Limitation of Liability. Provider's liability to Client shall be limited to the amount of advisory fees paid by Client in the twelve (12) months preceding any claim, except in cases of gross negligence or willful misconduct.

8.3 Indemnification. Client shall indemnify and hold harmless Provider from and against any claims arising from Client's breach of this Agreement.

ARTICLE IX - MISCELLANEOUS

9.1 Governing Law. This Agreement shall be governed by and construed in accordance with the laws of the State of New York.

9.2 Dispute Resolution. Any disputes arising under this Agreement shall be resolved through binding arbitration in New York, New York, in accordance with the rules of the American Arbitration Association.

9.3 Entire Agreement. This Agreement constitutes the entire understanding between the parties and supersedes all prior agreements and understandings.

9.4 Amendments. This Agreement may be amended only by written agreement signed by both parties.

9.5 Notices. All notices shall be in writing and delivered to the addresses set forth above or to such other addresses as the parties may designate in writing.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

Global Financial Services, Inc.

By: _________________________
Name: Sarah M. Johnson
Title: Chief Executive Officer
Date: January 15, 2024

Global Investment Partners, LLC

By: _________________________
Name: Michael R. Chen
Title: Managing Director
Date: January 15, 2024

SCHEDULE A - INVESTMENT OBJECTIVES AND RISK PARAMETERS
[To be attached]

SCHEDULE B - INVESTMENT GUIDELINES
[To be attached]`,
          entities: [
        { id: '1', text: 'Global Financial Services, Inc.', type: 'ORGANIZATION', start: 200, end: 230, confidence: 0.95, metadata: { industry: 'Financial Services', jurisdiction: 'Delaware' } },
        { id: '2', text: 'Global Investment Partners, LLC', type: 'ORGANIZATION', start: 280, end: 315, confidence: 0.93, metadata: { industry: 'Investment Management', jurisdiction: 'New York' } },
        { id: '3', text: 'January 15, 2024', type: 'DATE', start: 130, end: 145, confidence: 0.98, metadata: { dateType: 'Effective Date', format: 'MM/DD/YYYY' } },
        { id: '4', text: '$300,000', type: 'MONEY', start: 1200, end: 1209, confidence: 0.96, metadata: { currency: 'USD', frequency: 'Annual', type: 'Advisory Fee' } },
        { id: '5', text: '$25,000', type: 'MONEY', start: 1210, end: 1218, confidence: 0.96, metadata: { currency: 'USD', frequency: 'Monthly', type: 'Installment' } },
        { id: '6', text: 'three (3) years', type: 'CONTRACT_TERM', start: 800, end: 815, confidence: 0.89, metadata: { termType: 'Duration', value: '3 years' } },
        { id: '7', text: 'thirty (30) days', type: 'CONTRACT_TERM', start: 850, end: 865, confidence: 0.91, metadata: { termType: 'Notice Period', value: '30 days' } },
        { id: '8', text: 'Securities and Exchange Commission', type: 'COMPLIANCE_ITEM', start: 1800, end: 1835, confidence: 0.87, metadata: { regulator: 'SEC', jurisdiction: 'Federal', requirement: 'Registration' } },
        { id: '9', text: 'Investment Advisers Act of 1940', type: 'COMPLIANCE_ITEM', start: 1840, end: 1870, confidence: 0.92, metadata: { regulation: 'Investment Advisers Act', year: '1940', scope: 'Federal' } },
        { id: '10', text: 'Sarah M. Johnson', type: 'PERSON', start: 3200, end: 3215, confidence: 0.94, metadata: { role: 'CEO', organization: 'Global Financial Services', signature: 'Authorized' } },
        { id: '11', text: 'Michael R. Chen', type: 'PERSON', start: 3300, end: 3315, confidence: 0.94, metadata: { role: 'Managing Director', organization: 'Global Investment Partners', signature: 'Authorized' } },
        { id: '12', text: 'Chief Executive Officer', type: 'CONTRACT_TERM', start: 3220, end: 3245, confidence: 0.88, metadata: { titleType: 'Executive', level: 'C-Suite' } },
        { id: '13', text: 'Managing Director', type: 'CONTRACT_TERM', start: 3320, end: 3338, confidence: 0.88, metadata: { titleType: 'Executive', level: 'Senior Management' } },
        { id: '14', text: 'FSA-2024-0015', type: 'CONTRACT_TERM', start: 110, end: 125, confidence: 0.97, metadata: { documentType: 'Agreement Number', year: '2024', sequence: '0015' } },
        { id: '15', text: '123 Wall Street, Suite 1500, New York, NY 10001', type: 'LOCATION', start: 240, end: 280, confidence: 0.96, metadata: { addressType: 'Business Address', city: 'New York', state: 'NY', zip: '10001' } },
        { id: '16', text: '456 Park Avenue, 25th Floor, New York, NY 10022', type: 'LOCATION', start: 320, end: 360, confidence: 0.95, metadata: { addressType: 'Business Address', city: 'New York', state: 'NY', zip: '10022' } },
        { id: '17', text: 'portfolio management and asset allocation strategies', type: 'CONTRACT_TERM', start: 800, end: 850, confidence: 0.91, metadata: { serviceType: 'Investment Management', category: 'Core Services' } },
        { id: '18', text: 'Gramm-Leach-Bliley Act', type: 'COMPLIANCE_ITEM', start: 1900, end: 1925, confidence: 0.89, metadata: { regulation: 'GLBA', year: '1999', focus: 'Privacy Protection' } },
        { id: '19', text: 'Regulation S-P', type: 'COMPLIANCE_ITEM', start: 1930, end: 1940, confidence: 0.87, metadata: { regulation: 'Reg S-P', focus: 'Privacy of Consumer Financial Information' } },
        { id: '20', text: 'State of New York', type: 'LOCATION', start: 2500, end: 2515, confidence: 0.98, metadata: { jurisdiction: 'Governing Law', type: 'State Law' } }
      ],
          highlights: ['1', '2', '4', '5', '8', '9', '10', '11', '14'],
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
