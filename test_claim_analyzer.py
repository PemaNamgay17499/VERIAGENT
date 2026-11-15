from config import get_gemini_client, GEMINI_MODEL
from processing.claim_analyzer import analyze_claim


def main():

    client = get_gemini_client()

    claim = (
        "Artificial intelligence improves student "
        "academic performance."
    )

    print("\nVERIAGENT - CLAIM ANALYZER")
    print("=" * 45)

    print("\nSubmitted Claim:")
    print(claim)

    print("\nAnalyzing claim...")

    result = analyze_claim(
        client,
        GEMINI_MODEL,
        claim
    )

    print("\nCLAIM ANALYSIS RESULTS")
    print("=" * 45)

    for key, value in result.items():
        print(f"\n{key.replace('_', ' ').title()}:")

        if isinstance(value, list):
            for item in value:
                print(f"  - {item}")
        else:
            print(f"  {value}")


if __name__ == "__main__":
    main()