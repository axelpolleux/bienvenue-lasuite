# Bienvenue à La Suite

> **A modular onboarding widget/template ecosystem for [La Suite Numérique](https://lasuite.numerique.gouv.fr), powered by [Grist](https://www.getgrist.com).**

[![Status: Concept](https://img.shields.io/badge/status-concept%20%2F%20hackathon-blue.svg)](#)
[![Accessibility: RGAA / WCAG 2.1 AA](https://img.shields.io/badge/accessibility-RGAA%20%2F%20WCAG%20AA-blueviolet.svg)](#-accessibility--inclusivity-rgaa--a11y)
[![Powered by: Grist](https://img.shields.io/badge/database-Grist-orange.svg)](https://www.getgrist.com/)
[![License: GPL-2.0](https://img.shields.io/badge/license-GPL--2.0-green.svg)](./LICENSE)

---

## Executive Summary

**Bienvenue à La Suite** is an accessible, modular onboarding widget/template designed for French public sector organizations deploying _La Suite Numérique_. It streamlines and demystifies the newcomer arrival process through a centralized, interactive checklist and progress bar.

Built with an **accessibility** mindset, the experience helps every agent to get their administrative tasks, for the first month.

By using **Grist** as an open-source, relational database backend, it allows HR and IT teams to maintain a **Universal Base Template** (administrative accounts, equipment, accessibility requests, core Suite apps, etc.) while letting individual departments append or modify **Role-Specific Onboarding Modules** (specific tools, compliance, local contacts).

Managers and mentors gain real-time visibility into each agent's onboarding journey, ensuring no administrative, security, or accessibility requirement falls through the cracks.

---

## Key Objectives

```
   ┌─────────────────────────────────────────────────────────────┐
   │                  Bienvenue à La Suite                       │
   └──────────────┬───────────────────────────────┬──────────────┘
                  │                               │
         ┌────────▼────────┐             ┌────────▼────────┐
         │  For Newcomers  │             │  For Managers   │
         └────────┬────────┘             └────────┬────────┘
                  │                               │
  • Guided Step-by-Step Checklist  • Real-Time Progress Overview
  • Administrative & IT Setup      • Customized Department Tasks
  • Accommodation Requests         • Templates
  • Interactive "La Suite" Demos   • Instant Visibility on Blockers
  • Track Personal Progress
```

1. **Accessibility & Inclusivity First (RGAA / a11y)**:
   - ? Full compliance with French public administration accessibility rules (RGAA 4.1 / WCAG 2.1 AA).
2. **Streamline Administrative Onboarding**:
   - Workstation & peripherals configuration.
   - Network & secure Wi-Fi access setup.
   - Account provisioning across La Suite tools (AgentConnect / ProConnect, Tchap, Nextcloud/Docs, Grist, Webmail).
3. **Accelerate Tool Adoption**:
   - Interactive discovery tasks that guide agents through their first actions on La Suite.
4. **Dual-Perspective Tracking**:
   - **Agent View**: Interactive, keyboard-accessible checklist with clear progress percentage, deadlines, and direct links to guides.
   - **Manager / RH View**: High-level supervision dashboard tracking onboarding status across teams and new recruits.
5. **Modular & Scalable Hierarchy**:
   - **Global Core Template**: Universal steps shared across public administrations.
   - **Departmental / Pole Extensions**: Tailored tasks for specific divisions (e.g., IT, Legal, Field Operations, Regional Offices).
