from typing import Optional, Tuple
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.document import Document


class CompanyCompleter(Completer):
    def __init__(self, companies):
        self.companies = companies

    def get_completions(self, document: Document, complete_event):
        text = document.text.lower()
        for ticker, name in self.companies:
            if text in ticker.lower() or text in name.lower():
                display_text = f"{ticker} - {name}"
                yield Completion(display_text, start_position=-len(text))


class CompanyInput:
    def __init__(self, companyList) -> Optional[Tuple[str, str]]:
        self.companyList = companyList

    def run(self):
        completer = CompanyCompleter(self.companyList)
        userInput = prompt(
            "Type to search tickers/companies. Tab/Arrow keys to select: \n",
            completer=completer,
            complete_style=CompleteStyle.COLUMN,
        )

        # Match selected input back to the original tuple
        for ticker, name in self.companyList:
            display = f"{ticker} - {name}"
            if userInput == display:
                return (ticker, name)

        return None  # If somehow input doesn't match


# Example usage:
if __name__ == "__main__":
    companies = [
        ("AAPL", "Apple Inc."),
        ("GOOGL", "Alphabet Inc."),
        ("MSFT", "Microsoft Corporation"),
        ("AMZN", "Amazon.com, Inc."),
        ("TSLA", "Tesla, Inc.")
    ]
    selector = CompanyInput(companies)
    result = selector.run()
    print("You selected:", result)
