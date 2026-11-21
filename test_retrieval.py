from app.vectorstore import get_collection


def main():
    collection = get_collection()

    questions = [
        "Who issues Form 16?",
        "Who gives Form 16 to employees?",
        "Who provides Form 16?",
        "Does the employer issue Form 16?"
    ]

    for question in questions:
        result = collection.query(
            query_texts=[question],
            n_results=1
        )

        distance = result["distances"][0][0]
        score = round(1 - distance, 3)

        print("\nQuestion:", question)
        print("Score:", score)
        print("Text:", result["documents"][0][0])


if __name__ == "__main__":
    main()
