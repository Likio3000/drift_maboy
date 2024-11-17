# Description:
# This script monitors a Solana account for new transactions. It periodically checks for new transactions
# on the specified user account and sends a notification (sound alert and email) if a new transaction is detected.
# The frequency of checks and the user account to monitor can be set via variables at the beginning of the script.

import pandas as pd
from solana.rpc.async_api import AsyncClient
import os
from solders.pubkey import Pubkey
import asyncio
from transaction_fetch import transaction_history_for_account
import argparse
import logging
from httpx import ConnectTimeout, ReadTimeout, RequestError
from solana.exceptions import SolanaRpcException
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Variables to be set
USER_ACCOUNT = '6mt1N452W4YMJZBLjbA8dQ22LQcE1YuJZ9WmNiD1fJWp'  # Replace with desired public key
CHECK_FREQUENCY = 60 # In seconds
EMAIL_SUBJECT = "New Transaction Detected"
EMAIL_BODY = "A new transaction has been detected for the tracked account."
RECEIVER_EMAIL = "xxx@gmail.com"
TIMEZONE = "Europe/Berlin"

def send_email_notification():
    sender_email = os.environ.get('SENDER_EMAIL')
    receiver_email = RECEIVER_EMAIL
    password = os.environ.get('EMAIL_PASSWORD')

    if not sender_email or not password:
        logger.error("Email credentials are not set in environment variables.")
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
        logger.info("Email sent successfully.")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

async def main():
    parser = argparse.ArgumentParser(description='Fetch new transactions for a given user account.')

    parser.add_argument('--rpc', type=str, default='https://api.mainnet-beta.solana.com', help='RPC endpoint override')
    parser.add_argument('--limit', type=int, default=1, help='Limit for number of transactions')  # Only need the latest transaction
    parser.add_argument('--max_limit', type=int, default=50, help='Maximum limit for number of transactions')
    parser.add_argument('--before_sig', type=str, default='', help='Fetch transactions before this signature')
    parser.add_argument('--num_tx_details', type=int, default=0, help='Number of transactions to fetch details for (0 to skip)')

    args = parser.parse_args()

    rpc_override = args.rpc

    before_sig = args.before_sig
    num_tx_details = args.num_tx_details

    last_signature = None

    # Initialize connection
    connection = AsyncClient(rpc_override)

    try:
        while True:
            try:
                before_sig1 = None
                if args.before_sig != '':
                    before_sig1 = str(args.before_sig)

                res2 = await transaction_history_for_account(
                    connection, Pubkey.from_string(USER_ACCOUNT), before_sig1, args.limit, args.max_limit
                )
                t = pd.DataFrame(res2)
                if 'blockTime' not in t.columns or t.empty:
                    logger.info("No transactions found.")
                else:
                    # Convert blockTime to datetime in desired time zone
                    t['date'] = pd.to_datetime(t['blockTime'], unit='s', utc=True).dt.tz_convert(TIMEZONE)
                    t['day'] = t['date'].apply(lambda x: x.date())
                    t['day'] = t['date'].dt.date
                    t['hour'] = t['date'].dt.hour
                    t['minute'] = t['date'].dt.minute

                    print(f"\n\n")                              # Console output format
                    for index, row in t.iterrows():
                        logger.info(f"Last Signature: {row['signature']} \n {' '*28}| Status: {row['confirmationStatus']} | Last Signature Date: {row['day']} {row['hour']:02d}:{row['minute']:02d} \n")


                    latest_signature = t['signature'].iloc[0]

                    if last_signature is None:                    # 1: Scenario where its our first seen signature
                        last_signature = latest_signature
                    else:
                        if latest_signature != last_signature:    # 2: Scenario where we have found a new TX!
                            logger.info("New transaction detected!")
                            # Play a sound
                            os.system("paplay /usr/share/sounds/freedesktop/stereo/complete.oga")
                            # Send email notification
                            send_email_notification()
                            # Update last_signature
                            last_signature = latest_signature
                        else:                                     # 3: Scenario where we dont find a new TX :(
                            logger.info("No new transactions.")

            except (ConnectTimeout, ReadTimeout, RequestError) as e:
                logger.error(f"Network error occurred: {e}. Retrying after a delay.")
                # Optionally, close and reopen connection
                await connection.close()
                await asyncio.sleep(5)  # Wait before reconnecting
                connection = AsyncClient(rpc_override)
            except SolanaRpcException as e:
                logger.error(f"Solana RPC Exception occurred: {e}. Retrying after a delay.")
                # Close and reopen connection
                await connection.close()
                await asyncio.sleep(5)
                connection = AsyncClient(rpc_override)
            except asyncio.exceptions.CancelledError:
                logger.error("Asyncio CancelledError occurred. Retrying after a delay.")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}. Continuing loop.")
                await asyncio.sleep(5)

            await asyncio.sleep(CHECK_FREQUENCY)  # Wait for the specified frequency
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())
