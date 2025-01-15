#!/usr/bin/env python3
# agents/cognitive_interface_agent_v2.py
# Version: 1.1.0
# Purpose: Main script for managing user interactions and coordinating modules.

import logging
from agents.data_management import save_dialog_history, load_dialog_history
from agents.external_interactions import query_ddgr, restart_tor, check_tor_connection
from agents.cognitive_logic import preprocess_query, process_search_results

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load dialog history
dialog_history = load_dialog_history()

def main():
    logger.info("Starting cognitive interface agent.")
    use_tor = False
    while True:
        user_input = input("You: ")
        if user_input in ["/debug"]:
            logger.setLevel(logging.DEBUG)
            logger.info("Debug mode enabled.")
        elif user_input in ["/tn", "/toron"]:
            use_tor = True
            logger.info("TOR mode enabled.")
        elif user_input in ["/tf", "/toroff"]:
            use_tor = False
            logger.info("TOR mode disabled.")
        elif user_input == "/exit":
            save_dialog_history(dialog_history)
            logger.info("Exiting agent. Dialog history saved.")
            break
        else:
            preprocessed = preprocess_query(user_input)
            logger.debug(f"Preprocessed query: {preprocessed}")
            for query in preprocessed["queries"]:
                results = query_ddgr(query, use_tor=use_tor)
                if results:
                    response = process_search_results(results, preprocessed["instruction"])
                    print(f"Agent: {response}")
                else:
                    print("Agent: No results available. Try again.")

if __name__ == "__main__":
    main()
