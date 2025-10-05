# Hito 1 – Repository Setup and Project Definition

Student: Niklas Schuerrle  
Email: niklas733@correo.ugr.es  
Project: ExpenseTracker

---

## Overview Milestone 1

This milestone sets up the development environment and defines the project that will be deployed to the cloud during the course.

## Git environement Setup

1. **Verify Git to be installed on my system**  
    
    `git --version`
2. **Generate SSH Key Pair and Add to GitHub** 

    `ssh-keygen -t ed25519 -C "niklas733@correo.ugr.es"` 

    then added the Public key from the *.pub ssh file
2. **Configure Git Identity**

    `git config --global user.name "Niklas Schuerrle"`
    
    `git config --global user.email "niklas733@correo.ugr.es"`
4. **Update GitHub Profile**
    - Updated Name, location and activated 2-Factor-Athentication
    - Screenshots in docs/screenshots/

## Repository Structure

ExpenseTracker/
├── .gitignore
├── LICENSE
├── README.md
└── docs/
    ├── hito1.md
    └── screenshots/

## Project Definition
The ExpenseTracker is a simple cloud-based web application that allows users to record, manage, and analyze their daily expenses.
The goal is to demonstrate how a small-scale application can be designed, deployed, and managed in a cloud environment.  
The project will include a backend service for storing and retrieving data, a cloud database for persistent storage, and basic functionality to visualize or summarize expenses.
It focuses on applying core cloud concepts such as scalability, security, and data accessibility.

## Screenshots
- [updated GitHub profile](screenshots/git_profile.png) 
- [Enabled 2FA](screenshots/enabled_2FA.png)
- [Public SSH key](screenshots/ssh_key.png)

## Summary
