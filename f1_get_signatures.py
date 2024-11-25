import logging
from config import HARDCODED_ACCOUNT
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solders.signature import Signature
from transaction_fetch import transaction_history_for_account



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