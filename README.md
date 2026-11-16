
# Sportsbook Quality Engineering

[![Sportsbook QA Tests](https://github.com/exal-rom/sportsbook-quality-engineering/actions/workflows/tests.yml/badge.svg)](https://github.com/exal-rom/sportsbook-quality-engineering/actions/workflows/tests.yml)

**Specification-driven, risk-based quality engineering for sportsbook applications.**

A Python and pytest project demonstrating how sportsbook business requirements can be translated into repeatable, automated verification.

The project currently includes a lightweight in-memory sportsbook simulator, 27 automated tests, and continuous integration using GitHub Actions.

## 1. Project Objective

The purpose of this project is to demonstrate a quality engineering approach in which testing is derived from **business specifications and expected outcomes**, rather than simply reproducing the behaviour of an existing implementation.

In sportsbook applications, an HTTP success response or a successfully executed function does not necessarily mean that a business transaction has completed correctly.

For example, a bet placement request might return successfully while:

- The bet has not been recorded.
- The bet has an incorrect status.
- The customer's balance has not been debited.
- The bet is missing from the customer's Open Bets.
- The bet is incorrectly associated with another customer.
- A rejected placement has incorrectly modified the customer's balance.

These are business-critical failures that may not be detected by checking technical responses alone.

This project focuses on verifying the complete expected business outcome.

## 2. The Business Problem

### BET-001: Successful Bet Placement

**Priority: P0 — Business Critical**

Given:
- A customer with sufficient available funds.
- An available sportsbook selection.
- A positive stake within the permitted financial limits.
- A potential liability within the configured maximum.

When:
- The customer submits a bet placement request.

Then:
1. The bet must be accepted.
2. A unique Bet ID must be generated.
3. The bet must be associated with the correct customer.
4. The bet must have status `OPEN`.
5. The accepted stake and odds must be recorded correctly.
6. The stake must be debited immediately from the available balance.
7. The bet must appear in the customer's Open Bets.
8. The bet must not appear in another customer's Open Bets.

The expected outcome is not merely successful execution of the placement operation. It is a consistent business state across the bet record, customer ownership, Open Bets retrieval and available balance.

### Financial Rejection Rules

Placement must be rejected when:

- The selection is unavailable.
- The stake is zero or negative.
- The stake exceeds the available balance.
- The stake exceeds the maximum permitted stake.
- The potential liability exceeds the configured maximum liability.

For every rejected placement:

- No bet must be created.
- No stake must be debited.
- The available balance must remain unchanged.
- No additional bet must appear in Open Bets.

For this simulator, potential liability is calculated as:

`potential_liability = stake * (odds - 1)`

This represents potential net winnings for a single bet at decimal odds.

## 3. Quality Engineering Approach

### Specification Before Implementation

The test scenarios were developed from the expected sportsbook behaviour.

The implementation was then built to satisfy those expectations.

This separation is important because implementation-driven testing can unintentionally validate what the software currently does rather than what the business requires.

The approach follows four principles:

**1. Business outcomes over technical success**

A successful technical response is not sufficient evidence that the business transaction completed correctly.

**2. Risk-based verification**

Financial integrity, bet ownership, acceptance conditions and transaction state receive priority because failures in these areas can have significant business consequences.

**3. Deterministic and repeatable testing**

Each test establishes known preconditions and verifies explicit expected outcomes.

**4. Independent acceptance criteria**

Business requirements define the expected behaviour. Implementation details should not determine what is considered correct.

## 4. Implemented Components

### Domain Models

The simulator contains three principal domain models.

**Selection**
- Selection ID
- Decimal odds
- Availability status

**Account**
- Account ID
- Available balance
- Maximum stake
- Maximum liability

**Bet**
- Unique Bet ID
- Customer ID
- Selection ID
- Stake
- Odds
- Status

Python `Decimal` is used for financial values to avoid the precision problems associated with binary floating-point arithmetic.

### Placement Logic

The placement component:

1. Validates selection availability.
2. Validates the stake against the account's financial constraints.
3. Rejects invalid placement attempts.
4. Generates a unique Bet ID for accepted bets.
5. Creates a bet with status `OPEN`.
6. Saves the bet in the repository.
7. Debits the accepted stake from the available balance.

### Bet Repository

An in-memory repository provides:

- Bet storage.
- Retrieval by Bet ID.
- Customer-specific Open Bets retrieval.

Open Bets are filtered by both customer ownership and `OPEN` status.

This demonstrates business-level customer isolation within the repository. It does not yet implement authentication or production access controls.

## 5. Automated Test Coverage

The current suite contains **27 pytest test cases**, including parametrized scenarios.

| Verification area | What is tested |
|---|---|
| Domain models | Correct construction and attributes |
| Selection validation | Available and unavailable selections |
| Financial validation | Valid and invalid stake conditions |
| Available balance | Insufficient funds prevent placement |
| Maximum stake | Stakes above the limit are rejected |
| Maximum liability | Excessive liability prevents placement |
| Invalid stakes | Zero and negative amounts are rejected |
| Successful placement | Bet creation, status and recorded details |
| Bet ID uniqueness | Separate placements generate distinct IDs |
| Customer isolation | Open Bets are filtered by customer |
| Immediate debit | Accepted stakes reduce available balance |
| Consecutive placement | Subsequent requests use the updated balance |
| Rejected placement | No debit and no new Open Bet |
| Boundary values | Exact permitted financial limits are accepted |

### Example: Consecutive Bet Placement

Initial conditions:

- Available balance: £100
- First stake: £60
- Second stake: £60
- Other financial limits permit both individual stake amounts.

Expected behaviour:

| Step | Action | Expected result |
|---|---|---|
| 1 | Place first £60 bet | Accepted |
| 2 | Check available balance | £40 |
| 3 | Attempt second £60 bet | Rejected |
| 4 | Check available balance | Still £40 |
| 5 | Retrieve customer's Open Bets | Only the first bet |

This scenario verifies that the financial consequence of the first transaction affects the eligibility of subsequent transactions.

It also verifies that a rejected transaction does not create an additional bet or debit the account.

### Boundary Value Analysis

The suite verifies acceptance at exact permitted limits, including:

- Stake equal to available balance.
- Stake equal to maximum stake.
- Potential liability equal to maximum liability.

It also verifies rejection when financial limits are exceeded.

This helps identify incorrect comparison operators and boundary-handling defects.

### Parametrized Testing

Pytest parametrization allows multiple business scenarios to be verified using a common test structure.

This reduces duplication while preserving explicit inputs and expected outcomes.

## 6. Test Execution Results

### Local Execution

The suite was executed successfully in a Windows development environment using Python and pytest.

**Result: 27 passed**

### GitHub Actions

The project also runs automatically in GitHub Actions.

The CI workflow:

1. Checks out the repository.
2. Configures Python 3.12.
3. Installs dependencies from `requirements.txt`.
4. Executes the pytest suite.
5. Records the execution result.

The first successful GitHub Actions execution produced:

| Metric | Result |
|---|---|
| Platform | Ubuntu Linux |
| Python | 3.12.16 |
| Pytest | 9.2.0 |
| Tests collected | 27 |
| Passed | 27 |
| Failed | 0 |
| Test execution time | 0.20 seconds |
| CI job duration | 12 seconds |

These results demonstrate that the suite can execute successfully in a clean CI environment independently of the original Windows development machine.

The badge at the top of this README displays the latest workflow status.

## 7. Project Structure

```text
sportsbook-quality-engineering/
├── .github/
│   └── workflows/
│       └── tests.yml
├── framework/
│   ├── models/
│   │   ├── account.py
│   │   ├── bet.py
│   │   └── selection.py
│   ├── bet_repository.py
│   └── placement.py
├── tests/
│   ├── test_bet_model.py
│   ├── test_bet_repository.py
│   ├── test_framework_setup.py
│   ├── test_placement_validation.py
│   └── test_selection_model.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## 8. Running the Tests

### Prerequisites

- Python 3.12
- Git
- pip

Clone the repository:

```bash
git clone https://github.com/exal-rom/sportsbook-quality-engineering.git
cd sportsbook-quality-engineering
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Execute the suite:

```bash
python -m pytest -v
```

The same test command is executed by GitHub Actions.

## 9. Scope and Limitations

This project is currently a **business-rule simulator with automated Python tests**.

It is not presented as a production sportsbook application or a completed end-to-end automation framework.

Current limitations include:

- In-memory storage rather than durable persistence.
- No HTTP API endpoints.
- No browser-based Open Bets verification.
- No authentication or authorization layer.
- No concurrent placement or transactional rollback handling.
- No integration with a real wallet or sportsbook platform.

The simulator currently records the accepted bet and debits the in-memory balance sequentially. A production implementation would need transactional guarantees to prevent inconsistent financial states.

The distinction between customer identity and account identity is maintained in the domain models, but production identity and account ownership checks are outside the current scope.

### Bet Lifecycle Boundaries

Bet placement, resulting and settlement are distinct business responsibilities.

The current implementation focuses on placement.

Future lifecycle functionality may include:

- Bet resulting.
- Settlement.
- Voided and cancelled bets.
- Stake refunds.
- Financial reconciliation.

For example, voiding or cancelling a previously accepted bet should return the appropriate stake to the customer's account, according to the applicable sportsbook rules.

Such behaviour belongs to a separate lifecycle operation rather than the placement function.

## 10. Future Development

The next phase will focus on evolving the project from an in-memory simulator into a more independent QA automation architecture.

Planned areas include:

1. Separating the simulator from the automation framework.
2. Introducing HTTP API endpoints.
3. Implementing API clients and reusable pytest fixtures.
4. Verifying business outcomes through independent API calls.
5. Adding browser-based verification of customer Open Bets.
6. Improving test reporting and requirement traceability.
7. Extending coverage to selected sportsbook lifecycle scenarios.

The objective is to preserve the same specification-driven acceptance criteria while verifying behaviour through increasingly independent system interfaces.

## 11. Key Engineering Principle

**Quality is not established by the number of tests executed or by the absence of reported defects.**

A successful test execution provides evidence only for the requirements and conditions that have actually been verified.

In a sportsbook environment, effective quality engineering requires understanding the business transaction, identifying its critical risks, defining expected outcomes and verifying that the resulting system state is consistent.

This project demonstrates that approach through a small, deliberately scoped and executable sportsbook example.

---

**Technology:** Python 3.12 · pytest · GitHub Actions

**Focus:** Specification-driven testing · Risk-based quality engineering · Sportsbook business rules · Financial integrity · CI/CD
