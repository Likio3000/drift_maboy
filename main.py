from f1_get_signatures import fetch_last_10_signatures
from f2_inspect_transactions import inspect_transactions
from f3_search_logs import search_logs
from f4_send_email import send_email_notification
from f5_pc_notification_style import play_sequence

import config
import asyncio
import json
import argparse
from datetime import datetime
import logging



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


# ==================== One Cycle Flow Function:  ==================
# =================================================================
async def run_cycle(args):
    try:
        # Fetch the latest signatures
        signatures = await fetch_last_10_signatures(args)

        # If the user wants to include test signatures, add them to the list
        if args.include_test_sigs:
            logging.info("Including test signatures for inspection.")
            signatures.extend(config.TEST_SIGNATURES)

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
                matching_logs = search_logs(transaction_strings, config.LOG_SEARCH_TERMS)

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
        logging.info(f"Cycle completed. Sleeping for {config.FREQUENCY_SECONDS} seconds.\n")
        await asyncio.sleep(config.FREQUENCY_SECONDS)


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
# python main.py --include_test_sigs

# For standard use just use:
# python main.py

# =================================================
