import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--query", required=True)
    args = parser.parse_args()

    try:
        # import here so Playwright lives only in this process
        # Use the scheduler-specific pipeline to ensure DataFrame-friendly output
        from scraper.scraping_pipeline_scheduler import execute_scraping

        result = execute_scraping(args.url, args.query)

        # If result is a string that looks like JSON, parse it so worker emits structured JSON.
        out = result
        try:
            if isinstance(result, str) and result.strip().startswith(("[", "{")):
                parsed = json.loads(result)
                out = parsed
        except Exception:
            out = result

        # Emit structured JSON to stdout only
        json.dump(out, sys.stdout, ensure_ascii=False)

    except Exception as e:
        # Write error to stderr and exit non-zero
        sys.stderr.write(str(e))
        sys.exit(2)


if __name__ == "__main__":
    main()
