from app.evaluation.metrics import run_fixture_evaluation


def main() -> None:
    report = run_fixture_evaluation()
    print(
        f"Evaluated {report['document_count']} fixtures | "
        f"normalized accuracy={report.get('normalized_field_accuracy'):.3f}"
    )


if __name__ == "__main__":
    main()
