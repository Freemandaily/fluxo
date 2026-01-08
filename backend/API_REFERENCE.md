# Fluxo API Integration Guide

**Version:** 1.0.0  
**Date:** January 8, 2026  
**Base URL:** `http://localhost:8080` (Development) / `https://fluxo-231046660634.europe-west1.run.app` (Production)

---

## 📖 Overview

This API provides access to Fluxo's AI Automation-as-a-Service platform. It includes endpoints for wallet monitoring, portfolio analysis, yield farming opportunities, on-chain transaction history, and risk assessment.

### 🔄 Asynchronous Task Pattern

Many endpoints in this API (Portfolio, Yield, On-Chain, Risk) trigger long-running AI analysis tasks. These endpoints follow an asynchronous pattern:

1.  **Trigger**: Call the endpoint (e.g., `/analyze`). It returns a `task_id` immediately.
2.  **Poll**: Periodically call the corresponding status endpoint (e.g., `/status/{task_id}`) using the `task_id`.
3.  **Result**: When the status is `"SUCCESS"` (or `"completed"`), the response will contain the final analysis data.

---

## 🔔 Alerts & Monitoring API

Manage wallet tracking and retrieve system alerts.

### 1. Add Wallet to Tracking
Registers a wallet address for periodic monitoring (runs every 15 minutes).

*   **Endpoint:** `POST /api/alerts/add/track-wallet`
*   **Parameters:**
    *   `wallet_address` (query, string, required): The EVM wallet address to track.

**Response:**
```json
{
  "success": true,
  "message": "Wallet added to monitoring",
  "data": {
    "wallet_address": "0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64",
    "total_tracked": 15,
    "monitoring_interval": "15 minutes",
    "next_check": "Within 15 minutes"
  }
}
```

### 2. Remove Wallet from Tracking
Stops continuous monitoring for the specified wallet.

*   **Endpoint:** `DELETE /api/alerts/remove/track-wallet`
*   **Parameters:**
    *   `wallet_address` (query, string, required): The EVM wallet address to remove.

**Response:**
```json
{
  "success": true,
  "message": "Wallet removed from monitoring",
  "data": {
    "wallet_address": "0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64",
    "total_tracked": 14
  }
}
```

### 3. Fetch Alerts
Retrieve generated alerts for a specific wallet.

*   **Endpoint:** `GET /api/alerts/fetch`
*   **Parameters:**
    *   `wallet_address` (query, string, optional): Filter alerts by this wallet address.
    *   `limit` (query, integer, optional): Max number of alerts to return (Default: 50).

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 5 alerts",
  "data": {
    "wallet_address": "0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64",
    "alerts": [
      {
        "alert_id": "uuid-string",
        "title": "High Risk Detected",
        "message": "Portfolio concentration exceeds 60%",
        "severity": "high",
        "timestamp": "2024-01-01T12:00:00Z"
      }
    ]
  }
}
```

### 4. Fetch Undelivered Alerts
Get alerts that have not yet been delivered to external channels (e.g., x402).

*   **Endpoint:** `GET /api/alerts/undelivered`
*   **Parameters:**
    *   `wallet_address` (query, string, required): The wallet address to check.

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 2 undelivered alerts",
  "data": {
    "alerts": [ ... ],
    "total": 2
  }
}
```

### 5. Mark Alert as Delivered
Confirm that an alert has been successfully delivered to the user.

*   **Endpoint:** `POST /api/alerts/mark-delivered/{alert_id}`
*   **Parameters:**
    *   `alert_id` (path, string, required): The unique ID of the alert.
    *   `wallet_address` (query, string, required): The wallet address associated with the alert.
    *   `delivery_method` (query, string, required): The method used (e.g., "x402", "frontend_toast").

**Response:**
```json
{
  "success": true,
  "message": "Alert marked as delivered",
  "data": {
    "alert_id": "uuid-string",
    "delivery_method": "x402"
  }
}
```

### 6. Fetch Tracked Wallets
Get the list of all currently monitored wallets.

*   **Endpoint:** `GET /api/alerts/fetch/tracked-wallets`
*   **Parameters:** None

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 15 tracked wallets",
  "data": {
    "total_tracked": 15,
    "wallets": ["0x...", "0x..."],
    "monitoring_interval": "15 minutes"
  }
}
```

---

## 💼 Portfolio Agent API

Retrieve portfolio balances and positions.

### 7. Get User Portfolio (Trigger)
Fetches portfolio data including token holdings and protocol positions.

*   **Endpoint:** `GET /api/v1/agent/portfolio`
*   **Parameters:**
    *   `address` (query, string, required): The wallet address to analyze.

**Response:**
```json
{
  "success": true,
  "message": "User Portfolio Data",
  "data": {
    "task_id": null, 
    "result": [
      {
        "token_symbol": "MNT",
        "balance": 5000,
        "value_usd": 3500,
        "protocol": "wallet"
      }
    ]
  }
}
```
*Note: If `task_id` is returned instead of `null`, use the status endpoint below.*

### 8. Get Portfolio Task Status
Check the status of an asynchronous portfolio task.

*   **Endpoint:** `GET /api/v1/agent/status/{task_id}`
*   **Parameters:**
    *   `task_id` (path, string, required): The ID returned by the portfolio endpoint.

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "SUCCESS",
  "result": [ ...portfolio data... ]
}
```

---

## 🌾 Yield Agent API

Discover yield farming opportunities in the Mantle ecosystem.

### 9. Get Yield Opportunities (Trigger)
Initiates a background task to find yield opportunities.

*   **Endpoint:** `GET /agent/yield`
*   **Parameters:** None

**Response:**
```json
{
  "agent": "yield ",
  "task_id": "uuid-string-for-task"
}
```

### 10. Get Yield Task Status
Retrieve the results of the yield analysis.

*   **Endpoint:** `GET /agent/yield/status/{task_id}`
*   **Parameters:**
    *   `task_id` (path, string, required): The ID returned by the yield endpoint.

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "SUCCESS",
  "result": [
    {
      "protocol": "Merchant Moe",
      "symbol": "MOE",
      "apy": 45.2,
      "tvl": 5000000
    }
  ]
}
```

---

## 🔗 On-Chain Agent API

Analyze user transaction history.

### 11. Fetch User Transactions (Trigger)
Starts an asynchronous job to fetch and analyze transactions.

*   **Endpoint:** `GET /api/agent/onchain/transactions`
*   **Parameters:**
    *   `wallet_address` (query, string, required): The wallet address to analyze.

**Response:**
```json
{
  "success": true,
  "message": "Fetch Transactions For 0x...",
  "data": {
    "task_id": "uuid-string",
    "check_status": "/api/agent/onchain/status/uuid-string"
  }
}
```

### 12. Get On-Chain Task Status
Retrieve transaction analysis results.

*   **Endpoint:** `GET /api/agent/onchain/status/{task_id}`
*   **Parameters:**
    *   `task_id` (path, string, required): The ID returned by the transactions endpoint.

**Response:**
```json
{
  "success": true,
  "message": "Task completed",
  "data": {
    "task_id": "uuid-string",
    "status": "completed",
    "result": [ ...transactions... ]
  }
}
```

---

## 🛡️ Risk Agent API

Perform comprehensive risk analysis (Concentration, Liquidity, Volatility).

### 13. Analyze Risk (Trigger)
Initiates a deep risk analysis job for a wallet.

*   **Endpoint:** `POST /api/agent/risk/analyze`
*   **Parameters:**
    *   `wallet_address` (query, string, required): The wallet address to analyze.
    *   `market_correlation` (query, float, optional): Market correlation factor (0.0 - 1.0).

**Response:**
```json
{
  "success": true,
  "message": "Enhanced risk analysis started",
  "data": {
    "task_id": "uuid-string",
    "status": "processing",
    "wallet_address": "0x...",
    "check_status": "/api/agent/risk/status/uuid-string"
  }
}
```

### 14. Get Risk Task Status
Retrieve the detailed risk analysis report.

*   **Endpoint:** `GET /api/agent/risk/status/{task_id}`
*   **Parameters:**
    *   `task_id` (path, string, required): The ID returned by the analyze endpoint.

**Response:**
```json
{
  "success": true,
  "message": "Task status retrieved",
  "data": {
    "task_id": "uuid-string",
    "status": "SUCCESS",
    "result": {
      "risk_score": 45.5,
      "risk_level": "medium",
      "recommendations": ["Diversify holdings", "Reduce exposure to low liquidity tokens"],
      "risk_factors": {
        "concentration": 80,
        "liquidity": 20
      }
    }
  }
}
```