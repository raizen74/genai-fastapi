import uvicorn


def main() -> None:
    uvicorn.run("building_genai_services.api.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
