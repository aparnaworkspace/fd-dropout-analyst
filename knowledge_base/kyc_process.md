# KYC Process for FD Booking — India Regulatory Context

## Regulatory Basis
KYC for FD bookings is governed by:
- RBI Master Direction on KYC (updated 2023): DBR.AML.BC.No.81/14.01.001/2015-16
- Prevention of Money Laundering Act (PMLA) 2002
- Aadhaar (Targeted Delivery) Amendment Act 2019 — enables OTP-based eKYC

## Documents Required
Full KYC (amounts above Rs 50,000):
- PAN Card (mandatory — linked to TDS deduction)
- Aadhaar Card (address + identity proof)
- Cancelled cheque or bank statement (payout account linking)
- Live photograph (selfie with liveness check)

OTP-based eKYC (amounts up to Rs 50,000):
- Aadhaar-linked mobile number for OTP
- PAN Card
- No physical documents required

## KYC Pathways on Digital Platforms
1. Video KYC (V-CIP — Video based Customer Identification Process):
   - RBI circular dated January 9, 2020 (RBI/2019-20/138)
   - Requires live video call with bank agent
   - Takes 5-15 minutes
   - Available only during bank business hours — major friction point
   - Failure rate: ~25% on first attempt due to connectivity or agent unavailability

2. Aadhaar OTP eKYC:
   - Instant, no human agent required
   - Limited to Rs 50,000 per FD
   - Requires active Aadhaar-mobile linkage — ~30% of Tier 2/3 users have
     inactive or unlinked mobile numbers

3. Offline KYC (branch visit):
   - Zero digital friction but eliminates the entire value proposition
   - Used as fallback — signals complete digital funnel failure

## Conversion Impact Data
Industry benchmark for KYC completion rates on Indian digital FD platforms:
- Overall KYC initiation to completion: 55-65%
- Drop-off at document upload step: 18-22%
- Drop-off at video KYC scheduling: 12-15%
- Drop-off due to name mismatch (PAN vs Aadhaar): 8-10%

KYC abandonment accounts for 35-45% of total FD booking drop-offs.
Users who raise support queries during KYC have 3x higher churn rate.

## Tier 2/3 Specific Failure Modes
- Slow internet (2G/3G) causing document upload timeouts on 10MB+ PDF uploads
- Older Android devices (pre-2019) failing liveness detection algorithms
- Name discrepancies between legacy PAN cards and Aadhaar (common in UP, Bihar,
  MP — states with highest SFB FD potential)
- Lack of awareness that cancelled cheque can be replaced by bank statement
  (reduces drop-off by ~12% when communicated proactively)