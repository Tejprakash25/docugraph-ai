# SYNTHETIC TEST DATA — CLOUD HOSTING AND MANAGED OPERATIONS AGREEMENT

**Fictional document. Not legal advice. Not a real contract.**

**Agreement ID:** DG-SAMPLE-002
**Effective Date:** February 2, 2026

## 1. Parties and purpose

This fictional agreement is between **Blue Oak Robotics Corporation**, a
fictional California corporation located at 700 Mission Comet Avenue, San
Francisco, California 94105 (“Blue Oak”), and **Lumen Harbor Systems Ltd.**, a
fictional Washington corporation located at 19 Rainier Exchange Road, Seattle,
Washington 98101 (“Lumen Harbor”). It describes synthetic cloud hosting and
managed operations services for testing DocuGraph AI. No party or term is real.

Blue Oak appoints Lumen Harbor to host a non-production document intelligence
platform, operate its supporting services, and provide incident coordination.
Lumen Harbor will provision isolated development and production accounts,
configure network boundaries, monitor service health, and maintain deployment
runbooks. **Talia Nguyen** is Blue Oak’s service owner and **Elias Mercer** is
Lumen Harbor’s service owner.

## 2. Operating responsibilities

Lumen Harbor will maintain the platform during the support window of 08:00 to
18:00 Pacific Time on business days. Critical availability incidents will be
acknowledged within thirty minutes and assigned an incident lead. High-severity
incidents will be acknowledged within two hours. Lumen Harbor will provide a
monthly service report containing uptime, incidents, capacity indicators, and
planned maintenance.

Blue Oak is responsible for the accuracy and legality of documents it uploads,
the identities of its users, and its instructions for retention. Blue Oak will
not upload payment-card data, government identity numbers, health records, or
regulated data unless the Parties sign a separate written addendum. Lumen
Harbor may reject an upload that violates this restriction or creates a clear
security risk.

## 3. Environments and change control

The development and production environments will use separate credentials,
network policies, and storage locations. Production changes require a ticket,
peer review, a rollback description, and approval from Talia Nguyen or her
delegate. Emergency changes may be made to contain an outage, but Lumen Harbor
will document the change and review it within two business days.

Lumen Harbor will retain deployment logs for ninety days and operational audit
logs for one year. Logs must not contain raw document contents, API keys,
passwords, access tokens, or private encryption keys. Diagnostic samples must
be redacted before being shared with Blue Oak.

## 4. Security controls

Lumen Harbor will use role-based access control, multi-factor authentication,
short-lived service credentials where technically available, encrypted network
connections, encrypted storage, vulnerability scanning, and dependency patching
based on severity. Administrative access will be reviewed quarterly. Personnel
leaving the project will have access removed promptly.

If Lumen Harbor detects suspected compromise, it will isolate affected
resources, preserve relevant evidence, and notify Blue Oak through the incident
contacts. The notice will state the approximate discovery time, affected
systems, known data categories, containment steps, and next update time. Blue
Oak will provide reasonable cooperation and will not independently alter
forensic evidence during an active investigation without coordination.

## 5. Fees and service credits

Blue Oak will pay a fictional onboarding fee of **USD 12,750**, a monthly
operations fee of **USD 4,850**, and variable cloud costs capped at **USD 2,000
per month** unless Blue Oak approves a higher cap in writing. Lumen Harbor will
invoice at the beginning of each month, payable within thirty days.

If monthly availability falls below 99.5% because of a Lumen Harbor-controlled
failure, Blue Oak may receive a service credit of five percent of the monthly
operations fee. Credits are the exclusive remedy for service-level misses,
except where a limitation cannot lawfully apply.

## 6. Confidentiality and data rights

Blue Oak owns its documents, extracted facts, metadata, and query history.
Lumen Harbor may process them only to operate the contracted service. Lumen
Harbor may use aggregated operational metrics that cannot reasonably identify
Blue Oak or its documents. Each Party will protect confidential information,
limit access to people with a need to know, and return or delete it at the end
of the engagement.

Confidentiality does not cover information independently known, publicly
available without breach, independently developed, or lawfully obtained without
restriction. Required legal disclosures will be limited to the required scope
when permitted.

## 7. Termination and transition

The initial term is eighteen months. Either Party may terminate for convenience
with forty-five days’ notice. A material breach may be terminated after fifteen
days to cure. For a serious security breach that is not contained promptly,
Blue Oak may suspend access and terminate after written notice.

At termination, Lumen Harbor will provide an export of Blue Oak’s documents and
metadata in a mutually agreed format, delete active copies within thirty days,
and provide a deletion confirmation. Backups will expire under the standard
backup cycle and will remain inaccessible except for disaster recovery.

## 8. Warranty, liability, and general terms

Lumen Harbor warrants that it will provide the services with reasonable skill
and care. Blue Oak warrants that its instructions and documents do not violate
rights of third parties. Neither Party is responsible for indirect losses. Total
liability is capped at fees paid in the prior six months, except for fraud,
willful misconduct, confidentiality violations, or infringement.

The Parties are independent contractors. Neither Party may assign this
agreement without consent except to a successor. Washington law governs this
fictional agreement. Service disputes will be escalated first to Talia Nguyen
and Elias Mercer. Written amendments and approved change orders are required.

**BLUE OAK ROBOTICS CORPORATION**
Name: Talia Nguyen
Title: Director of Platform Operations
Signature: ____________________  Date: ______________

**LUMEN HARBOR SYSTEMS LTD.**
Name: Elias Mercer
Title: Chief Operating Officer
Signature: ____________________  Date: ______________
