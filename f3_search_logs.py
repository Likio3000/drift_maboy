import json
import re

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
