# TaxSaathi - Day 1: menu

print("=== TaxSaathi ===")

while True:
    print("\n1. What is old vs new regime?")
    print("2. Which ITR form should I file?")
    print("3. How much tax do I pay?")
    print("4. Exit")

    choice = input("Your choice (1-4): ").strip()

    if choice == "1":
        print("New regime is the default: lower rates, fewer deductions.")
        print("Old regime: higher rates, but deductions like 80C and HRA.")
    elif choice == "2":
        print("Only salary income: usually ITR-1.")
        print("Capital gains: ITR-2. Business or freelance income: ITR-3 or ITR-4.")
    elif choice == "3":
        print("Coming on Day 2.")
    elif choice == "4":
        print("Thank you!")
        break
    else:
        print("Invalid choice. Enter 1 to 4.")