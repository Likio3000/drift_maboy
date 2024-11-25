import asyncio
import os
import json
import argparse
from datetime import datetime

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib

import pandas as pd
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solders.signature import Signature

from transaction_fetch import transaction_history_for_account
from sound_go_beep import play_sequence

import logging
import re

# ==================== Usage ====================
# Ensure you have set the following environment variables before running:
# - SENDER_EMAIL: Your email address (e.g., example@gmail.com)
# - EMAIL_PASSWORD: Your email password or app-specific password (on your google account, on security, you can create a login password for your app)
# - HELIUS_RPC_URL: Your free tier HELIUS rpc url, if you use free public rpc you may need to slow down the signatures inspections yourself

# Example command to run the script with test signatures included:
# python final_version10.py --include_test_sigs


# ==================== Frequency Configuration ====================
# Set the frequency in seconds. For every minute, set to 60.
FREQUENCY_SECONDS = 600

# ==================== Public key Configuration ====================
# Ensure you copy your subaccount Public address
HARDCODED_ACCOUNT = "ELT8NKTqWjgjPHmVAAw3xYPLBcub3LtgCnCoW8iUCiHa"

# Some specific signatures for testing (set some signatures where of trades in which you got filled 100% through Drift UI you can pick them under ""TRADES""")                                                                              # DELETE DELETE DELETE DELETE DELETE DELETE DELETE
TEST_SIGNATURES = [                                                                                                        
    "3J3heawQL6otmmHbaUy4AHcFwZ1cMdMjzV7nq3KzrahRUyb2R9wGZCBHc17GZ6HSqSUYF9mimqmxZETUV6oT4QS9",                        
    "xi7zwtGaYCCaNsWR3zoPA38PU1SBzFqgTHHhxVhA65E9mp1cR42z8J4o2LKcq1dRj8RP6Nswa3eAdza1qziYRf6"                          
]

# Define the words or phrases to search for within log messages
LOG_SEARCH_TERMS = ["FillPerpOrder", "RevertFill"]

# Define Email settings
EMAIL_SUBJECT = "New Transaction Detected"
EMAIL_BODY = "A new transaction has been detected for the tracked account."
RECEIVER_EMAIL = "likio3000@gmail.com"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_arguments():
    parser = argparse.ArgumentParser(description="Fetch and inspect Solana account transactions for specific keywords.")
    parser.add_argument(
        "--rpc_override",
        type=str,
        default="https://api.mainnet-beta.solana.com",
        help="RPC endpoint to use.",
    )
    parser.add_argument(
        "--before_sig",
        type=str,
        default="",
        help="Signature to fetch transactions before.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of concurrent workers for fetching transactions.",
    )
    parser.add_argument(
        "--include_test_sigs",
        action='store_true',
        help="Include specific test signatures in the inspection.",
    )
    return parser.parse_args()


# ==================== Function 1: Get Signatures ====================
# Get the latest 10 signatures or the given HARDCODED account
# ====================================================================

async def fetch_last_10_signatures(args):
    try:
        account_pubkey = Pubkey.from_string(HARDCODED_ACCOUNT)
    except ValueError:
        logging.error("Invalid hardcoded account public key.")
        return []

    limit = 10
    before_sig = args.before_sig if args.before_sig else None

    logging.info(f"Fetching the last {limit} signatures for account: {HARDCODED_ACCOUNT}")
    logging.info(f"RPC Endpoint: {args.rpc_override}")
    logging.info("Fetching transaction history...")

    async with AsyncClient(args.rpc_override) as connection:
        try:
            signatures_data = await transaction_history_for_account(
                connection,
                account_pubkey,
                before_sig,
                limit,
                MAX_LIMIT=10  
            )
        except Exception as e:
            logging.error(f"Error fetching transaction history: {e}")
            return []

        if not signatures_data:
            logging.info("No signatures found for the given account.")
            return []
        else:
            logging.info("Last 10 Signatures:")
            signatures_list = []
            for idx, sig in enumerate(signatures_data, 1):
                # Extract and collect only the 'signature' field
                signature = sig.get('signature') if isinstance(sig, dict) else sig
                if signature:
                    logging.info(f"{idx}. {signature}")
                    signatures_list.append(signature)
                else:
                    logging.warning(f"{idx}. Signature field not found in the transaction data.")

            return signatures_list

# ==================== Function 2: Collect Signatures Data ===============
# ========================================================================

async def inspect_transactions(signatures, workers=5):
    """
    Fetch and collect transaction details for each signature using a queue with multiple workers.
    """
    # Your custom RPC endpoint for fetching transaction details
    rpc_url = os.environ.get('HELIUS_RPC_URL')
    transaction_details_list = []

    logging.info("Starting transaction inspection with multiple workers...")

    # Initialize the queue and enqueue all signatures
    queue = asyncio.Queue()
    for sig in signatures:
        await queue.put(sig)

    async def worker(worker_id):
        async with AsyncClient(rpc_url) as client:
            while not queue.empty():
                sig_str = await queue.get()
                try:
                    # Convert the transaction signature string to a Signature object
                    transaction_signature = Signature.from_string(sig_str)
                except ValueError:
                    logging.error(f"[Worker {worker_id}] Invalid signature format: {sig_str}")
                    queue.task_done()
                    continue

                try:
                    response = await client.get_transaction(
                        transaction_signature,
                        encoding="json",
                        max_supported_transaction_version=0  # Specify the supported transaction version
                    )

                    transaction_details = response.value

                    if transaction_details:
                        logging.info(f"[Worker {worker_id}] Transaction {sig_str[:15]} details fetched successfully.")
                        transaction_details_list.append(transaction_details)
                    else:
                        logging.warning(f"[Worker {worker_id}] Transaction {sig_str[:15]} not found or not finalized.")
                except Exception as e:
                    logging.error(f"[Worker {worker_id}] Error fetching transaction {sig_str}: {e}")

                queue.task_done()

                
    # Start multiple worker tasks
    worker_tasks = []
    for i in range(workers):
        task = asyncio.create_task(worker(i + 1))
        worker_tasks.append(task)

    # Wait until all tasks are done
    await queue.join()

    # Cancel worker tasks
    for task in worker_tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled
    await asyncio.gather(*worker_tasks, return_exceptions=True)

    logging.info("Completed inspecting transactions.")
    return transaction_details_list


# ==================== Function 3: Search Particular Words  ==========================
# ====================================================================================

def search_keywords_in_transaction(transaction, keywords):
    """
    Recursively search for any of the keywords in the transaction JSON data.
    Returns True if any keyword is found in any key or value, else False.
    """
    if isinstance(transaction, dict):
        for key, value in transaction.items():
            # Check if the key contains any keyword
            if any(keyword in key for keyword in keywords):
                return True
            # Recursively check the value
            if search_keywords_in_transaction(value, keywords):
                return True
    elif isinstance(transaction, list):
        for item in transaction:
            if search_keywords_in_transaction(item, keywords):
                return True
    elif isinstance(transaction, str):
        # Check if any keyword is present in the string
        if any(keyword in transaction for keyword in keywords):
            return True
    # For other data types (int, float, etc.), no action is needed
    return False

def extract_log_messages(txn_str):
    """
    Extracts log messages from a transaction string using regex.
    """
    # Regex pattern to find log_messages: Some([...])
    pattern = r'log_messages:\s*Some\(\[(.*?)\]\)'
    match = re.search(pattern, txn_str, re.DOTALL)
    if match:
        logs_str = match.group(1)
        # Regex to extract individual log messages within quotes
        log_pattern = r'"(.*?)"'
        logs = re.findall(log_pattern, logs_str)
        return logs
    return []

def extract_field(txn_str, field_name):
    """
    Extracts a numerical field (like slot or block_time) from the transaction string.
    """
    pattern = rf'{field_name}:\s*(\d+)'
    match = re.search(pattern, txn_str)
    return match.group(1) if match else None

def extract_signature(txn_str):
    """
    Extracts the first signature from the transaction string.
    """
    pattern = r'signatures:\s*\["(.*?)"\]'
    match = re.search(pattern, txn_str)
    return match.group(1) if match else None

def search_logs(transactions, terms):
    """
    Searches for specified terms within the log messages of each transaction.
    """
    results = []
    for txn_str in transactions:
        # Extract log messages
        log_messages = extract_log_messages(txn_str)
        if not log_messages:
            continue

        # Extract other relevant fields
        slot = extract_field(txn_str, 'slot')
        signature = extract_signature(txn_str)
        block_time = extract_field(txn_str, 'block_time')

        # Search for terms within log messages
        for log in log_messages:
            for term in terms:
                if term in log:
                    result = {
                        "slot": slot,
                        "signature": signature,
                        "block_time": block_time,
                        "found_term": term,
                        "log": log
                    }
                    results.append(result)
    return results


# ==================== Function 4: Send email ====================
# ================================================================
# Email functionality

def send_email_notification():
    sender_email = os.environ.get('SENDER_EMAIL')
    receiver_email = RECEIVER_EMAIL
    password = os.environ.get('EMAIL_PASSWORD')

    if not sender_email or not password:
        logging.error("Email credentials are not set in environment variables.")
        return

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = EMAIL_SUBJECT

    # Add body to the email
    message.attach(MIMEText(EMAIL_BODY, "plain"))

    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")


# ==================== One Cycle Flow Function:  ==================
# =================================================================
async def run_cycle(args):
    try:
        # Fetch the latest signatures
        signatures = await fetch_last_10_signatures(args)

        # If the user wants to include test signatures, add them to the list
        if args.include_test_sigs:
            logging.info("Including test signatures for inspection.")
            signatures.extend(TEST_SIGNATURES)

        if signatures:
            # Inspect transactions with the specified number of workers
            transaction_details = await inspect_transactions(signatures, workers=args.workers)

            if transaction_details:
                # Save all transaction details
                with open("transaction_details.json", "w") as f:
                    json.dump(transaction_details, f, indent=4, default=str)
                logging.info("All transaction details saved to transaction_details.json")

                # Convert transaction_details to string representations for log processing
                transaction_strings = [json.dumps(tx, default=str) for tx in transaction_details]

                # Execute the log search
                matching_logs = search_logs(transaction_strings, LOG_SEARCH_TERMS)

                # Output the log search results
                if matching_logs:
                    logging.info("\nMatching Log Messages:")
                    for match in matching_logs:
                        logging.info(f"Slot: {match['slot']}")
                        logging.info(f"Signature: {match['signature']}")
                        logging.info(f"Block Time: {match['block_time']}")
                        logging.info(f"Found Term: {match['found_term']}")
                        logging.info(f"Log Message: {match['log']}")
                        logging.info("-" * 80)
                    # Play a sound
                    play_sequence()
                    # Send an email
                    send_email_notification()
                else:
                    logging.info("No matching log messages found.")
            else:
                logging.info("No transaction details to display.")
        else:
            logging.info("No signatures to inspect.")
    except Exception as e:
        logging.error(f"An error occurred during the cycle: {e}")


# ==================== Periodic Runs Orquestrator Function ====================
# =============================================================================

async def periodic_runner(args):
    while True:
        logging.info("Starting a new cycle of transaction inspection.")
        await run_cycle(args)
        logging.info(f"Cycle completed. Sleeping for {FREQUENCY_SECONDS} seconds.\n")
        await asyncio.sleep(FREQUENCY_SECONDS)


# ==================== MAIN Function: Putting it all together ====================
# ================================================================================

def main():
    args = parse_arguments()

    try:
        asyncio.run(periodic_runner(args))
    except KeyboardInterrupt:
        logging.info("Operation cancelled by user. Exiting gracefully.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

# ==================== Usage ====================
# Example command to run the script with test signatures included:
# python final_version10.py --include_test_sigs

# =================================================
