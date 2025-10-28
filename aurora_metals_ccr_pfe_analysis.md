# CCR Limits & PFE Analysis Report: Aurora Metals

**Date:** October 27, 2025  
**Counterparty:** Aurora Metals  
**Adaptiv Code:** AC003  
**Analysis Type:** Counterparty Credit Risk (CCR) - Limits, PFE & Exposure

---

## Executive Summary

🔴 **CRITICAL ALERT: LIMIT BREACH DETECTED**

Aurora Metals has breached their CCR limit with a utilization of **119.13%**, representing a **19.13% excess** over approved limits. Immediate risk mitigation actions are required.

**Key Risk Indicators:**
- ⚠️  Limit Status: **BREACH**
- ⚠️  Failed Trades: **2 trades** with operational issues
- ⚠️  Credit Rating: **BB** (Sub-investment grade)
- ⚠️  Sector: **Mining** (Cyclical, commodity-sensitive)

---

## 1. Counterparty Profile


**Entity Information:**
- **Full Name:** Aurora Metals
- **Adaptiv Code:** AC003
- **Sector:** Mining
- **Credit Rating:** BB
- **Country:** Canada
- **Region:** North America
- **Portfolio:** Commodities
- **Booking Location:** LDN
- **Risk Owner:** Desk C

**Risk Assessment:**
- Rating of **BB** indicates sub-investment grade credit quality
- Mining sector exposure creates commodity price sensitivity
- North America concentration risk

---

## 2. CCR Limit Status & Breach Analysis

### Current Limit Position

**Limit Structure:**
- **Approved CCR Limit:** $10,000,000
- **Limit Buffer:** $0.0
- **Effective Limit:** $10,000,000.0

### Exposure Metrics

**Expected Positive Exposure (EPE):** $8,339,204.84
- Primary metric for limit monitoring
- Current exposure: **119.13%** of limit
- **Breach Amount:** $-1,660,795.16

**Potential Future Exposure (PFE - 95% confidence):** $11,913,149.77
- Represents potential exposure under adverse market conditions
- PFE/Limit ratio: **119.13%**

**Exposure at Default (EAD):** $13,104,464.75
- Estimated exposure if counterparty defaults
- EAD/Limit ratio: **131.04%**

**Value at Risk (VaR - 99%):** $3,573,944.93
- Statistical worst-case scenario (1% probability)

**Stress Test Exposure:** $17,869,724.65
- Exposure under severe market stress scenarios
- Stress/Limit ratio: **178.70%**

### Breach Severity Analysis

**Status:** 🔴 **CRITICAL BREACH**

- **Breach Magnitude:** $-1,660,795.16 (19.13% over limit)
- **Breach Duration:** 2025-10-14 onwards
- **Regulatory Impact:** Requires immediate reporting and action plan
- **Capital Impact:** Additional capital charges may apply

### Limit Utilization Trend

As of: **2025-10-14**
- Current: **119.13%**
- Previous: See historical section below
- Trend: Deteriorating (breach status)

---

## 3. Trade Portfolio Analysis

### Portfolio Overview

**Trade Statistics:**
- **Total Active Trades:** 13
- **Unique Products:** 3
- **Asset Classes:** 1

**Notional Exposure:**
- **Total Notional:** $168,589,487.21
- **Average Trade Size:** $12,968,422.09
- **Minimum Notional:** $6,967,112.23
- **Maximum Notional:** $18,682,763.39

**Concentration Risk:**
- Largest trade represents **11.08%** of total notional
- Average trade size indicates diversified portfolio

### Mark-to-Market & P&L Analysis

**Current MTM Position:**
- **Total MTM:** $3,351,366.27
- **MTM as % of Notional:** 1.988%
- **Average MTM per Trade:** $257,797.41

**MTM Distribution:**
- **Positive MTM Trades:** 10 ($4,280,538.44)
- **Negative MTM Trades:** 3 ($-929,172.17)
- **Net MTM:** $3,351,366.27

**Profit & Loss:**
- **Total P&L:** $335,136.63
- **Average P&L per Trade:** $25,779.74

---

## 4. Asset Class & Product Distribution

### Asset Class Breakdown


**Commodities:**
- Trades: 13 (100.0% of portfolio)
- Notional: $168,589,487.21 (100.0%)
- MTM: $3,351,366.27
- P&L: $335,136.63
- Unique Products: 3
- Avg Notional: $12,968,422.09

### Top Products by Notional


**COMD SWAP** (Commodities):
- Trades: 8
- Notional: $108,613,210.21
- MTM: $2,832,308.38
- Avg Delta: -0.3250
- Avg Gamma: 0.0405

**COMD OPTION** (Commodities):
- Trades: 4
- Notional: $52,073,512.23
- MTM: $623,109.26
- Avg Delta: 0.1820
- Avg Gamma: 0.0474

**COMD FWD** (Commodities):
- Trades: 1
- Notional: $7,902,764.77
- MTM: $-104,051.38
- Avg Delta: 0.1935
- Avg Gamma: 0.0133

---

## 5. Collateral & Netting Analysis

### Netting Sets


**NS003:**
- CSA in place: No
- Collateralized: Yes
- Trades: 3
- Notional: $42,496,084.25
- MTM: $-59,331.27

**NS003:**
- CSA in place: Yes
- Collateralized: No
- Trades: 3
- Notional: $40,129,077.94
- MTM: $317,826.83

**NS001:**
- CSA in place: Yes
- Collateralized: Yes
- Trades: 2
- Notional: $33,169,992.94
- MTM: $583,117.45

**NS003:**
- CSA in place: Yes
- Collateralized: Yes
- Trades: 2
- Notional: $22,184,465.68
- MTM: $1,354,171.18

**NS003:**
- CSA in place: No
- Collateralized: No
- Trades: 1
- Notional: $13,751,592.80
- MTM: $133,776.43

**NS001:**
- CSA in place: No
- Collateralized: Yes
- Trades: 1
- Notional: $9,693,331.42
- MTM: $837,964.74

**NS001:**
- CSA in place: Yes
- Collateralized: No
- Trades: 1
- Notional: $7,164,942.18
- MTM: $183,840.90

---

## 6. Failed Trades & Operational Risk

🔴 **OPERATIONAL RISK ALERT: 2 FAILED TRADES**


**Trade ID: T00025**
- Product: COMD SWAP (Commodities)
- Notional: $7,164,942.18
- MTM: $183,840.90
- Trade Date: 2025-07-20
- Maturity: 2026-03-23
- Status: Failed

**Trade ID: T00079**
- Product: COMD SWAP (Commodities)
- Notional: $17,717,714.60
- MTM: $235,130.76
- Trade Date: 2025-10-05
- Maturity: 2027-06-16
- Status: Failed

**Operational Risk Impact:**
- Failed trade ratio: 15.38%
- Total failed notional: $24,882,656.78
- Requires investigation and resolution
- May indicate settlement, operational, or documentation issues

---

## 7. Market Risk Sensitivities (Greeks)


**Commodities Risk Profile:**
- **Total Delta:** -1.6783 (directional risk)
- **Total Gamma:** 0.5269 (convexity risk)
- **Total Vega:** $38,608.18 (volatility risk)
- **Delta Range:** -0.9666 to 0.6924
- **Average Delta:** -0.1291

---

## 8. Historical Limit Utilization Trend

**Recent History (5 data points):**


**2025-10-14:**
- EPE: $8,339,204.84
- PFE: $11,913,149.77
- Limit: $10,000,000
- Utilization: 119.13%
- Buffer: $0.00

**2025-10-13:**
- EPE: $8,087,066.99
- PFE: $11,552,952.85
- Limit: $10,000,000
- Utilization: 115.53%
- Buffer: $0.00

**2025-10-12:**
- EPE: $7,951,525.97
- PFE: $11,359,322.81
- Limit: $10,000,000
- Utilization: 113.59%
- Buffer: $0.00

**2025-10-11:**
- EPE: $7,871,171.22
- PFE: $11,244,530.31
- Limit: $10,000,000
- Utilization: 112.45%
- Buffer: $0.00

**2025-10-10:**
- EPE: $7,700,000.00
- PFE: $11,000,000.00
- Limit: $10,000,000
- Utilization: 110.00%
- Buffer: $0.00

---

## 9. Integrated View: Trades vs Limits

**Comprehensive Metrics:**
- Active Trades: 13
- Trade Notional: $168,589,487.21
- Trade MTM: $3,351,366.27
- EPE: $7,700,000.00
- PFE: $11,000,000.00
- CCR Limit: $10,000,000
- Utilization: 110.00%
- Avg Exposure per Trade: $592,307.69

---

## 10. Risk Assessment & Recommendations

### Risk Severity: 🔴 CRITICAL

**Primary Risk Factors:**

1. **Limit Breach (CRITICAL)**
   - Exceeds approved limit by 19.13%
   - Breach amount: $-1,660,795.16
   - Immediate escalation required

2. **Failed Trades (2 trades)**
   - 15.38% failure rate
   - Operational risk and settlement concerns
   - Requires investigation

3. **Credit Rating (BB - Sub-Investment Grade)**
   - Higher default probability
   - Increased capital requirements
   - Enhanced monitoring needed

4. **Sector Risk (Mining)**
   - Commodity price sensitivity
   - Cyclical sector exposure
   - Economic cycle dependent

5. **PFE Exposure**
   - PFE at 119.13% of limit
   - Stress exposure at 178.70% of limit
   - Tail risk concerns

### Immediate Actions Required

**Priority 1 (Immediate - Within 24 hours):**
1. ⚠️  **Escalate breach to Credit Risk Committee**
   - Document breach circumstances
   - Prepare action plan
   - Notify senior management

2. ⚠️  **Suspend new trading activity**
   - No new trades until within limit
   - Review existing trade pipeline
   - Communicate with trading desk

3. ⚠️  **Investigate failed trades**
   - Root cause analysis for 2 failed trades
   - Settlement status verification
   - Documentation review

**Priority 2 (Within 1 week):**
1. 📋 **Exposure reduction plan**
   - Target reduction: $-1,660,795.16
   - Identify trades for unwinding/hedging
   - Timeline: 30 days maximum

2. 📋 **Collateral review**
   - Assess collateral adequacy
   - Review CSA terms and thresholds
   - Consider additional collateral requirements

3. 📋 **Limit review**
   - Evaluate if limit is appropriate
   - Consider temporary or permanent limit adjustment
   - Document risk appetite rationale

**Priority 3 (Ongoing):**
1. 🔍 **Enhanced monitoring**
   - Daily limit utilization reporting
   - Real-time exposure tracking
   - Trade-by-trade approval process

2. 🔍 **Credit assessment**
   - Review credit rating and outlook
   - Monitor sector developments
   - Track commodity prices

3. 🔍 **Documentation**
   - Ensure all CSA/ISDA agreements current
   - Verify legal enforceability
   - Review netting opinions

### Proposed Limit Actions

**Option 1: Reduce Exposure (Recommended)**
- Target utilization: <90%
- Required reduction: $-660,795.16
- Method: Trade unwinding, hedging, novation
- Timeline: 30 days

**Option 2: Increase Limit (Requires Approval)**
- Proposed limit: $10,007,045.81
- Justification: [Business case required]
- Additional capital: [Calculate based on new limit]
- Approval level: Credit Risk Committee + Board

**Option 3: Enhanced Collateral**
- Require full collateralization
- Daily margining
- Reduce uncollateralized exposure

### Risk Outlook

**Short-term (1-3 months):**
- Breach resolution critical
- Enhanced monitoring required
- Trading restrictions in place

**Medium-term (3-12 months):**
- Normalize limit utilization
- Resume controlled trading activity
- Monitor credit quality

**Long-term (12+ months):**
- Review strategic relationship
- Assess concentration limits
- Consider relationship optimization

---

## 11. Regulatory & Capital Considerations

**Regulatory Reporting:**
- Breach must be reported to relevant authorities
- Large exposure reporting requirements
- Capital adequacy impact

**Capital Impact:**
- Current exposure: $13,104,464.75 EAD
- Risk weight: ~100% (BB rating)
- Additional capital for breach may apply
- CVA charges on derivative exposure

**Compliance Requirements:**
- Document breach and remediation plan
- Board/committee notification
- Audit trail for all decisions

---

## Appendices

### A. Key Definitions

**EPE (Expected Positive Exposure):** Average expected positive exposure over time, used for limit monitoring

**PFE (Potential Future Exposure):** Maximum expected exposure at a given confidence level (typically 95%)

**EAD (Exposure at Default):** Estimated exposure if counterparty defaults, used for capital calculations

**VaR (Value at Risk):** Maximum loss at given confidence level (typically 99%)

**CCR Limit:** Counterparty Credit Risk limit, approved maximum exposure

### B. Methodology Notes

- Exposures calculated using internal risk models
- Confidence levels: PFE (95%), VaR (99%)
- Stress scenarios based on historical market stress periods
- Collateral values marked-to-market daily

### C. Contact Information

**Risk Owner:** Desk C  
**Report Date:** October 27, 2025  
**Next Review:** Daily until breach resolved

---

**Document Classification:** CONFIDENTIAL - Risk Management Use Only  
**Distribution:** Credit Risk Committee, Trading Desk Head, Senior Management  

---

*This analysis is based on data as of 2025-10-14 and reflects the counterparty's credit profile at that time. Market conditions and exposures may have changed. This report is for internal risk management purposes only and should not be distributed externally.*
