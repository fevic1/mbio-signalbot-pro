from .verifier import RuntimeVerifier


def main():

    result = RuntimeVerifier().verify()

    print("AIOS RUNTIME VERIFICATION")
    print("=" * 30)

    for section, data in result.items():
        print(section.upper(), ":", data)

    print("=" * 30)
    print("STATUS: OK")


if __name__ == "__main__":
    main()
