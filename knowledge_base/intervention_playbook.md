# Intervention Playbook — FD Dropout Cohorts

## Communication Channel Performance in Indian Fintech (2024)
WhatsApp Business API: 87% open rate, 23% click-through rate
Push notification: 45% open rate, 8% click-through rate
Email: 22% open rate, 3% click-through rate
SMS: 65% open rate, 4% click-through rate

Recommendation: WhatsApp is the primary intervention channel for all cohorts
for Tier 2/3 users. Push notification for Tier 1. Email only as follow-up.

## WhatsApp Business API — Compliance Note
All WhatsApp Business messages require pre-approved templates under Meta's
WhatsApp Business Policy. Templates must be submitted for approval 24-48 hours
before use. Promotional messages require user opt-in (double opt-in recommended
for RBI compliance).

---

## Cohort 1: KYC Dropout
Root cause: Technical or process friction at document submission stage
User intent level: HIGH — they started KYC, they want to invest
Intervention urgency: CRITICAL — act within 2 hours of abandonment

Recommended intervention sequence:
Step 1 (T+2 hours): WhatsApp template message
  "Hi [Name], your FD booking at [Bank] is 80% complete. You stopped at the
  document upload step. Here's a 3-step guide to finish in 5 minutes: [link]"

Step 2 (T+24 hours, if no action): Video KYC callback offer
  "Skip document upload entirely — complete your KYC via a 5-minute video call.
  Book a slot here: [link]"

Step 3 (T+48 hours, if support query raised): Human agent assignment
  Assign dedicated support agent via in-app chat. Response SLA: 2 hours.

Step 4 (T+72 hours, no response): Rate lock offer
  "Lock [rate]% p.a. from [Bank] for the next 48 hours — complete KYC to claim."

Expected reactivation: 35-45% with T+2hr WhatsApp, drops to 12-18% after 24hrs.
Do not send more than 3 messages — increases uninstall risk above 3 touches.

---

## Cohort 2: Comparison Paralysis
Root cause: Choice overload — too many options, no clear recommendation
User intent level: MEDIUM-HIGH — they're interested but cognitively stuck
Intervention urgency: MEDIUM — act within 48 hours, before intent cools

Recommended intervention sequence:
Step 1 (T+48 hours of inactivity): Personalized recommendation push
  "Based on your searches, [Bank] at [rate]% for [tenor] months is the best
  match for your goal. 2,400 users booked this FD this week."
  Key: remove choice. Present ONE option, not a comparison.

Step 2 (T+72 hours): Rate lock offer
  "Rates change frequently. Lock [rate]% p.a. from [Bank] for 48 hours — 
  no commitment until you complete booking."
  Psychological mechanism: loss aversion. Works better than positive framing.

Step 3 (T+7 days): Social proof + simplified display
  Reduce comparison view to top 3 options only. Add "Most popular this week" tag.

Expected reactivation: 25-35% with personalized single recommendation.
Avoid: sending full comparison table again — reinforces the paralysis.

---

## Cohort 3: Overwhelmed First-Timer
Root cause: Financial literacy gap + fear of making wrong first investment decision
User intent level: MEDIUM — emotionally engaged, needs reassurance not urgency
Intervention urgency: MEDIUM — act within 72 hours

Recommended intervention sequence:
Step 1 (T+72 hours): Educational WhatsApp sequence
  Message 1: "Your money is insured up to Rs 5 lakh by DICGC — a government
  body. Even if the bank faces issues, your deposit is protected."
  Message 2 (next day): "Starting with Rs 10,000 for 6 months is completely
  normal. 68% of first-time FD investors on our platform start under Rs 25,000."

Step 2: Vernacular language detection
  If city is in UP, Bihar, MP, or Rajasthan — trigger Hindi interface prompt.
  "क्या आप हिंदी में जारी रखना चाहेंगे?" (Would you like to continue in Hindi?)
  Hindi interface increases first-timer completion by 22%.

Step 3: Peer story content
  "Rahul from Lucknow started his first FD with Rs 15,000 at Ujjivan SFB.
  He earned Rs 1,237 in 12 months — more than his savings account would have paid."

Expected reactivation: 30-40% with DICGC education + vernacular nudge combination.

---

## Cohort 4: Silent Churner
Root cause: Low-intent visit — browsing, not buying. No strong trigger to convert.
User intent level: LOW — do not over-invest in reactivation
Intervention urgency: LOW — batch weekly, not individual triggers

Recommended intervention sequence:
Step 1 (Weekly batch): Rate change notification only if rates increase
  "FD rates just went up. [Bank] now offers [rate]% p.a. — higher than last week."
  Only send if there is a genuine rate change. Crying wolf kills open rates.

Step 2: Festive/seasonal triggers
  Diwali, financial year-end (March), and salary credit dates (1st-5th of month)
  are highest-conversion moments for this cohort.

Step 3: Single-option simplified offer
  Do not send comparison tables. Send one offer with a clear CTA.

What NOT to do:
- Do not trigger KYC reminders — they never started KYC
- Do not send more than 1 message per week — uninstall risk increases sharply
- Do not assign human agents — cost does not justify reactivation rate

Expected reactivation: 10-15%. Accept this. Reallocate budget to KYC Dropout
and Comparison Paralysis cohorts which have 3-4x better ROI on intervention spend.

## Budget Allocation Recommendation
Given fixed re-engagement budget, prioritise as follows:
1. KYC Dropout: 50% of budget (highest intent, highest reactivation rate)
2. Comparison Paralysis: 30% of budget
3. Overwhelmed First-Timer: 15% of budget
4. Silent Churner: 5% of budget (batch only, minimal spend)