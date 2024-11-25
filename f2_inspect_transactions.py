import os
import asyncio
import logging
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.transaction import Signature

# ==================== Function 2: Collect Signatures Data ===============
# ========================================================================

async def inspect_transactions(signatures, workers=5):
    """
    Fetch and collect transaction details for each signature using a queue with multiple workers.
    Retries up to 3 times for each transaction in case of an error.
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

                attempt = 0
                success = False
                while attempt < 3 and not success:
                    attempt += 1
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
                        success = True  # Mark as success to exit the retry loop
                    except Exception as e:
                        logging.error(f"[Worker {worker_id}] Error fetching transaction {sig_str}, attempt {attempt}: {e}")
                        if attempt < 3:
                            logging.info(f"[Worker {worker_id}] Retrying transaction {sig_str} (attempt {attempt + 1})")
                            await asyncio.sleep(1)  # Optional: Wait a bit before retrying
                        else:
                            logging.error(f"[Worker {worker_id}] Failed to fetch transaction {sig_str} after 3 attempts.")
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
