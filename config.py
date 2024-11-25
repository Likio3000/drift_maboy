
# ==================== Frequency Configuration ====================
# Set the frequency in seconds. For every minute, set to 60.
FREQUENCY_SECONDS = 600

# ==================== Public key Configuration ====================
# Ensure you copy your subaccount Public address
HARDCODED_ACCOUNT = "A5oadvsuiMmnRTmN2p8U4hMxU3a91GLSTCsWeGsjNZpL"

# Some specific signatures for testing (set some signatures where of trades in which you got filled; through Drift UI you can pick them under ""TRADES""")                                                                              # DELETE DELETE DELETE DELETE DELETE DELETE DELETE
TEST_SIGNATURES = [                                                                                                        
    "5v5byP2bk3D2Y52c5R8MH4QwoZ4xppfRkXdZCvfF1XkW513RdG29sqUbFPpxwkF2UVy82F6FCpB5AhSNgviLs1tX",                        
    "WgDUqy9MTVPP9qzs1RT6vKovTL3m2L5ze9MSrVLQtUefQdQhoXr2RTQqPnJMa879HEQBzj29mCeN69wpiBmzv58"                          
]

# Define the words or phrases to search for within log messages; Program names for getting filled are:
LOG_SEARCH_TERMS = ["FillPerpOrder", "RevertFill"]

# Define Email settings
EMAIL_SUBJECT = "New Transaction Detected"
EMAIL_BODY = "A new transaction has been detected for the tracked account."
RECEIVER_EMAIL = "put your email@something.com"