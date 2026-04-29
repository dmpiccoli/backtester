# Systematic Trading Backtester & NAV Engine

A Python-based framework for **backtesting, portfolio management, and NAV calculation** of systematic trading strategies.

Designed with a **portfolio-centric architecture**, where each strategy operates as an independent “portfolio manager” with its own data, signals, and decision-making logic. This structure makes it particularly suitable for **macro, cross-asset, and multi-strategy workflows**.

> ⚠️ Work in progress — actively used for research and evolving over time.

---

## Overview

Unlike traditional backtesting frameworks that focus on isolated strategies, this project models each strategy as a **self-contained portfolio manager**:

- Each strategy maintains its own state, signals, and logic  
- Strategies operate directly on portfolios rather than individual trades  
- Portfolio-level decisions (allocation, rebalancing, risk) are first-class components  

This design allows for more natural implementation of:

- Cross-asset strategies  
- Macro-driven allocation  
- Multi-strategy portfolios  

---

## Architecture

Portfolio Manager → Portfolio → NAV / P&L Calculation

### Components

**Portfolio Manager**
- Contains trading logic and decision-making rules  
- Generates trades or target allocations  
- Can incorporate custom data and signals  

**Portfolio**
- Tracks positions and holdings  
- Computes:
  - NAV (Net Asset Value)
  - NAV per share (NAVPS)
  - Daily P&L  

---

## Usage

### 1. Research / Backtesting

- Define strategy logic inside the portfolio manager  
- Simulate trades and portfolio evolution over time  

### 2. Portfolio Replay / Live Simulation

- Load pre-generated trades from external sources  
- Feed trades into the portfolio engine to compute NAV and performance  

---

## Design Features

- Portfolio-first architecture (not trade-first)  
- Flexible support for multi-asset strategies  
- Separation between strategy logic and portfolio accounting  
- Daily NAV and P&L computation  

---

## Performance Considerations

The framework includes support for **vectorized initialization workflows**:

- The `once` method runs at the beginning of the backtest  
- Intended for one-time calculations using vectorized operations  
- Helps improve performance for large datasets  

---

## Roadmap / Work in Progress

- ~~Currency conversion support~~  
- Extension to additional asset classes (~~cash equities~~, options)  
- Strategy-on-strategy (hierarchical portfolio structures)  
- Standardization of required fields / parameters  
- Logging and diagnostics  
- Additional performance and analytics features  

---

## Motivation

Many backtesting tools focus on trade simulation but lack a clean abstraction for **portfolio-level decision-making**.

This project aims to:

- Treat strategies as portfolio managers  
- Emphasize allocation, aggregation, and NAV computation  
- Support realistic multi-strategy and cross-asset workflows  

---

## Disclaimer

This project is intended for **research and development purposes only** and does not constitute investment advice or a production-ready trading system.