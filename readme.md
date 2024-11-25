# Solana Transaction Monitor

## Description

This Python script monitors a specific Solana account for new transactions and inspects them for specific log messages indicating certain events, such as `"FillPerpOrder"` or `"RevertFill"`. When such an event is detected, the script plays a sound and sends an email notification to alert the user.

The script runs periodically (every 10 minutes by default) and can be customized to monitor different accounts, search for different log messages, and adjust the notification settings.

## Features

- **Periodic Monitoring**: Fetches the latest transactions for a specified Solana account at regular intervals.
- **Asynchronous Processing**: Utilizes asynchronous programming to efficiently handle network I/O.
- **Customizable Search Terms**: Allows you to specify which log messages to search for within transactions.
- **Email Notifications**: Sends an email when a matching transaction is detected.
- **Sound Alerts**: Plays a sound to notify you immediately upon detecting a matching transaction.
- **Concurrent Workers**: Supports concurrent transaction inspections to speed up the monitoring process.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Script Variables](#script-variables)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
- [Example](#example)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Prerequisites

- **Python 3.7 or higher**
- **Helius RPC URL**: A free-tier [Helius](https://www.helius.dev/) RPC URL for Solana.
- **Email Account**: Gmail account for sending email notifications (other providers can be used with adjustments).
- **Required Python Packages**:
  - `asyncio`
  - `pandas`
  - `solders`
  - `solana`
  - `sounddevice`
  - `ssl`
  - `smtplib`
  - `email`
  - `logging`
  - `re`

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/solana-transaction-monitor.git
   cd solana-transaction-monitor
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   If a `requirements.txt` file is not provided, you can install the packages directly:

   ```bash
   pip install asyncio pandas solders solana sounddevice
   ```

4. **Set Environment Variables**

   Set the necessary environment variables for email and RPC access:

   - **Unix/Linux/macOS**

     ```bash
     export SENDER_EMAIL='your-email@example.com'
     export EMAIL_PASSWORD='your-email-password'
     export HELIUS_RPC_URL='https://your.helius.rpc.url'
     ```

   - **Windows (Command Prompt)**

     ```cmd
     set SENDER_EMAIL=your-email@example.com
     set EMAIL_PASSWORD=your-email-password
     set HELIUS_RPC_URL=https://your.helius.rpc.url
     ```

## Configuration

### Environment Variables

- **SENDER_EMAIL**: Your email address used to send notifications (e.g., `example@gmail.com`).
- **EMAIL_PASSWORD**: Your email account password or an app-specific password if using Gmail with 2FA.
- **HELIUS_RPC_URL**: Your Helius RPC endpoint URL.

### Script Variables

Open the script (`final_version10.py`) and adjust the following variables as needed:

- **FREQUENCY_SECONDS**: Set the frequency in seconds for how often the script checks for new transactions.

  ```python
  FREQUENCY_SECONDS = 600  # Default is 600 seconds (10 minutes)
  ```

- **HARDCODED_ACCOUNT**: Replace with the public key of the Solana account you want to monitor.

  ```python
  HARDCODED_ACCOUNT = "Your_Solana_Account_Public_Key"
  ```

- **LOG_SEARCH_TERMS**: Define the list of log messages you want to search for in transactions.

  ```python
  LOG_SEARCH_TERMS = ["FillPerpOrder", "RevertFill"]
  ```

- **EMAIL_SUBJECT** and **EMAIL_BODY**: Customize the email subject and body content.

  ```python
  EMAIL_SUBJECT = "New Transaction Detected"
  EMAIL_BODY = "A new transaction has been detected for the tracked account."
  ```

- **RECEIVER_EMAIL**: Set the email address where you want to receive notifications.

  ```python
  RECEIVER_EMAIL = "recipient@example.com"
  ```

- **TEST_SIGNATURES**: (Optional) Include specific transaction signatures for testing purposes.

  ```python
  TEST_SIGNATURES = [
      "Signature1",
      "Signature2",
  ]
  ```

## Usage

Run the script using Python:

```bash
python final_version10.py
```

### Command-Line Arguments

The script supports several optional command-line arguments:

- **--rpc_override**: Specify a different RPC endpoint.

  ```bash
  python final_version10.py --rpc_override "https://your.custom.rpc.url"
  ```

- **--before_sig**: Fetch transactions that occurred before a specific signature.

  ```bash
  python final_version10.py --before_sig "SpecificSignature"
  ```

- **--workers**: Set the number of concurrent workers for fetching transactions (default is 5).

  ```bash
  python final_version10.py --workers 10
  ```

- **--include_test_sigs**: Include test signatures defined in `TEST_SIGNATURES` for inspection.

  ```bash
  python final_version10.py --include_test_sigs
  ```

## Example

To run the script with test signatures included and using 10 workers:

```bash
python final_version10.py --include_test_sigs --workers 10
```

## Troubleshooting

- **Module Not Found Errors**: Ensure all required Python packages are installed. Install missing packages using `pip`.

  ```bash
  pip install package-name
  ```

- **Email Sending Issues**: Verify that `SENDER_EMAIL` and `EMAIL_PASSWORD` are correctly set. For Gmail accounts:

  - Ensure that [Less Secure App Access](https://myaccount.google.com/lesssecureapps) is enabled.
  - If using 2FA, create an [App Password](https://support.google.com/accounts/answer/185833).

- **Sound Playback Issues**: Ensure your system supports audio output and that the `sounddevice` package is properly installed.

- **RPC Connection Errors**: Check that `HELIUS_RPC_URL` is correctly set and that your network allows outbound connections to the RPC endpoint.

- **Permission Errors**: Run the script with appropriate permissions or adjust your system's security settings.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Solana Developers**: For providing robust tools and documentation.
- **Helius**: For offering accessible Solana RPC services.
- **OpenAI**: For assistance in code generation and optimization.
- **Community Contributors**: For feedback and improvements.

---

*Note: Replace placeholder text like `Your_Solana_Account_Public_Key`, `your-email@example.com`, and repository URLs with your actual information.*