from app.records import load_records, get_record, search_records, format_record


def show_all():
    for record in load_records():
        print(format_record(record))
        print()


def search_menu():
    keyword = input("Search for (example: 80C, ITR, rebate): ").strip()
    results = search_records(keyword)
    if not results:
        print("I don't know. Please check incometax.gov.in.")
        return
    for record in results:
        print(format_record(record))
        print()


def id_menu():
    record_id = input("Enter record id (example: R08): ").strip()
    record = get_record(record_id)
    if record is None:
        print("No record found with that id.")
    else:
        print(format_record(record))


def main():
    while True:
        print("\n=== TaxSaathi ===")
        print("1. Show all tax records")
        print("2. Search records")
        print("3. Get record by id")
        print("4. Exit")

        choice = input("Your choice (1-4): ").strip()

        if choice == "1":
            show_all()
        elif choice == "2":
            search_menu()
        elif choice == "3":
            id_menu()
        elif choice == "4":
            print("Thank you!")
            break
        else:
            print("Invalid choice. Enter 1 to 4.")


if __name__ == "__main__":
    main()